"""WS-I11: immutable pin validation and read-only OEE upstream drift reporting.

Synthetic contract mutations are assessed independently from real pinned
exports; old course or map formats never become supported runtime inputs.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PIN = "67416343f3eab17ada5d3c79ae6cc782524c29ff"
OEE = Path(os.environ.get("OEE_REPO", ROOT / "_oee")).resolve()

spec = importlib.util.spec_from_file_location(
    "oee_workspace_drift_reporter", ROOT / "scripts" / "report-oee-drift.py"
)
drift = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = drift
spec.loader.exec_module(drift)

source_spec = importlib.util.spec_from_file_location(
    "oee_workspace_synthetic_consumer", ROOT / "tests" / "test_toolkit_consumer.py"
)
source_test = importlib.util.module_from_spec(source_spec)
sys.modules[source_spec.name] = source_test
source_spec.loader.exec_module(source_test)


def seed():
    return source_test.valid_export()


def mapping():
    return source_test.valid_map()


def changes_between(original, changed, resource_map=None):
    return drift.compare_contracts(original, changed, resource_map or mapping())


class SyntheticContractChanges(unittest.TestCase):
    def test_exact_same_structure_is_stable_and_repeatable(self):
        source = seed()
        a = changes_between(source, copy.deepcopy(source))
        b = changes_between(source, copy.deepcopy(source))
        self.assertEqual(a, ([], []))
        self.assertEqual(a, b)

    def test_changed_outcome_description_marks_explicit_references_for_review(self):
        target = seed()
        target["outcomes"][0]["description"] += "; additional outcome requirements"
        changes, risks = changes_between(seed(), target)
        self.assertIn("outcome-description", {c["kind"] for c in changes})
        self.assertEqual(risks[0]["resource"], "R1")
        self.assertIn("referenced-outcome-definition-changed:SEF1-O1",
                      risks[0]["reasons"])

    def test_changed_assessment_criteria_marks_resource_association(self):
        target = seed()
        target["assessments"][0]["criteria"] = "Stricter reproducibility evidence"
        changes, risks = changes_between(seed(), target)
        self.assertIn("assessment-criteria", {c["kind"] for c in changes})
        self.assertIn("referenced-assessment-definition-changed:SEF1-AS1",
                      risks[0]["reasons"])

    def test_changed_required_assessment_graph_does_not_collapse_or_remap(self):
        target = seed()
        second = copy.deepcopy(target["assessments"][0])
        second["id"] = "SEF1-AS2"
        second["required"] = True
        target["assessments"].append(second)
        target["coverage"]["SEF1-O1"] = ["SEF1-AS1", "SEF1-AS2"]
        changes, risks = changes_between(seed(), target)
        kinds = {c["kind"] for c in changes}
        self.assertIn("assessment-added", kinds)
        self.assertIn("required-coverage", kinds)
        self.assertIn("required-assessment-coverage-changed:SEF1-O1",
                      risks[0]["reasons"])
        self.assertEqual(mapping()["modules"][0]["resources"][0]["assessmentIds"],
                         ["SEF1-AS1"])

    def test_removed_assessment_is_not_inferred_from_new_one(self):
        target = seed()
        target["assessments"][0]["id"] = "SEF1-AS2"
        target["coverage"]["SEF1-O1"] = ["SEF1-AS2"]
        changes, risks = changes_between(seed(), target)
        self.assertIn("assessment-removed", {x["kind"] for x in changes})
        self.assertIn("referenced-assessment-removed:SEF1-AS1",
                      risks[0]["reasons"])

    def test_changed_lesson_ordinals_and_titles_flag_locator(self):
        target = seed()
        target["modules"][0]["lessons"][0]["title"] = "New foundational topic"
        changes, risks = changes_between(seed(), target)
        self.assertIn("lesson-title", {x["kind"] for x in changes})
        self.assertIn("resource-lesson-locator-changed", risks[0]["reasons"])

    def test_module_movement_is_hint_not_rewritten_reference(self):
        source = seed()
        second = copy.deepcopy(source["modules"][0])
        second["number"] = 2
        second["title"] = "New module"
        source["modules"].append(second)
        target = copy.deepcopy(source)
        target["modules"][0]["title"] = "New module"
        target["modules"][1]["title"] = "Observe"
        original_map = mapping()
        changes, risks = changes_between(source, target, original_map)
        events = [x for x in changes if x["kind"] == "module-title-moved"]
        self.assertEqual([(e["locator"], e["before"], e["after"]) for e in events],
                         [("New module", 2, 1), ("Observe", 1, 2)])
        self.assertIn("module-locator-changed", risks[0]["reasons"])
        self.assertEqual(original_map["modules"][0]["title"], "Observe")

    def test_source_line_offsets_alone_are_not_a_semantic_change(self):
        target = seed()
        target["outcomes"][0]["location"]["line"] = 200
        target["assessments"][0]["location"]["line"] = 300
        changes, risks = changes_between(seed(), target)
        self.assertEqual((changes, risks), ([], []))

    def test_course_status_change_is_advisory_not_course_completion(self):
        target = seed()
        target["course"]["status"] = "tested"
        changes, risks = changes_between(seed(), target)
        self.assertEqual([x["kind"] for x in changes], ["course-status"])
        self.assertEqual(risks, [])

    def test_deterministic_event_order_is_not_dict_insertion_order(self):
        target = seed()
        target["assessments"][0]["work"] = "New work"
        target["outcomes"][0]["description"] = "New outcome"
        changes, risks = changes_between(seed(), target)
        self.assertEqual(changes, sorted(changes,
                         key=lambda x: (x["kind"], x["locator"])))
        self.assertEqual(risks, sorted(risks,
                         key=lambda x: (x["module"], x["resource"], x["reasons"])))


class ReaderAndReportingTests(unittest.TestCase):
    def setUp(self):
        self.checker = drift.load_checker()

    def test_validated_export_is_bound_to_explicit_target_revision(self):
        original = seed()
        target = copy.deepcopy(original)
        target["source"]["revision"] = "b" * 40
        target["outcomes"][0]["description"] = "An updated outcome"
        captured = []
        def fake_reader(repo, revision, code):
            captured.append((revision, code))
            if revision == source_test.PIN:
                return copy.deepcopy(original)
            if revision == "b" * 40:
                return copy.deepcopy(target)
            raise AssertionError("unexpected HEAD fallback")
        with patch.object(self.checker, "read_pinned_export", side_effect=fake_reader):
            result = drift.inspect_map(mapping(), Path("fake-oee"),
                                       "b" * 40, self.checker)
        self.assertEqual(captured, [(source_test.PIN, "SEF1"), ("b" * 40, "SEF1")])
        self.assertEqual(result["state"], "drift-detected")
        self.assertTrue(result["reviewRequired"])
        self.assertFalse(result["autoRemapped"])
        self.assertEqual(mapping()["curriculum"]["revision"], source_test.PIN)

    def test_missing_target_does_not_break_valid_pinned_map_or_fake_success(self):
        source = seed()
        captured = []
        def fake_reader(repo, revision, code):
            captured.append(revision)
            if revision == source_test.PIN:
                return copy.deepcopy(source)
            raise self.checker.PinnedSourceError(
                "source_missing", "target git object not present"
            )
        with patch.object(self.checker, "read_pinned_export", side_effect=fake_reader):
            result = drift.inspect_map(mapping(), Path("fake-oee"), "f" * 40,
                                       self.checker)
        self.assertEqual(captured, [source_test.PIN, "f" * 40])
        self.assertEqual(result["pinnedValidation"], "passed")
        self.assertEqual(result["state"], "target-unavailable")
        self.assertEqual(result["targetValidation"], "incomplete")
        self.assertTrue(result["reviewRequired"])
        self.assertEqual(result["changes"], [])

    def test_unsupported_export_format_is_incomplete_not_compatibility(self):
        target = seed()
        target["source"]["revision"] = "b" * 40
        target["exportVersion"] = 0
        def fake_reader(repo, revision, code):
            return copy.deepcopy(seed() if revision == source_test.PIN else target)
        with patch.object(self.checker, "read_pinned_export", side_effect=fake_reader):
            result = drift.inspect_map(mapping(), Path("fake-oee"), "b" * 40,
                                       self.checker)
        self.assertEqual(result["state"], "target-unavailable")
        self.assertEqual(result["targetFailure"]["category"], "unsupported_format")

    def test_broken_pinned_map_fails_without_consulting_upstream(self):
        invalid = mapping()
        invalid["curriculum"]["revision"] = "f" * 40
        with patch.object(self.checker, "read_pinned_export",
                          side_effect=self.checker.PinnedSourceError(
                              "source_missing", "pinned source not found")) as reader:
            with self.assertRaises(self.checker.PinnedSourceError):
                drift.inspect_map(invalid, Path("fake-oee"), "b" * 40, self.checker)
            self.assertEqual(reader.call_count, 1)

    def test_unchanged_full_contract_is_valid_even_when_head_moves(self):
        original = seed()
        with patch.object(self.checker, "read_pinned_export",
                          return_value=copy.deepcopy(original)) as reader:
            result = drift.inspect_map(mapping(), Path("fake-oee"),
                                       source_test.PIN, self.checker)
        self.assertEqual(reader.call_count, 2)
        self.assertEqual(result["state"], "unchanged")
        self.assertFalse(result["reviewRequired"])

    def test_old_map_is_rejected_without_conversion(self):
        old = ROOT / "tests" / "fixtures" / "resource-map-v1-SEF1.json"
        with self.assertRaisesRegex(ValueError, "invalid pinned map"):
            drift.report(Path("fake-oee"), "b" * 40, [old])

    def test_report_does_not_change_map_file_bytes(self):
        source = seed()
        with tempfile.TemporaryDirectory() as dirname:
            testroot = Path(dirname)
            active = testroot / "SEF" / "SEF1.json"
            active.parent.mkdir()
            active.write_text(json.dumps(mapping()), encoding="utf-8")
            before = active.read_bytes()
            with patch.object(self.checker, "read_pinned_export",
                              return_value=copy.deepcopy(source)):
                # Fake map has a synthetic non-catalogue resource and cannot
                # pass repository catalog validation; the standalone
                # inspect_map seam is sufficient for no-write verification.
                drift.inspect_map(json.loads(active.read_text()), testroot,
                                  source_test.PIN, self.checker)
            self.assertEqual(active.read_bytes(), before)


@unittest.skipUnless(
    (OEE / "tooling" / "oee_toolkit" / "__main__.py").is_file(),
    "requires a trusted local OEE checkout; CI supplies _oee",
)
class RealPinnedExportDriftTests(unittest.TestCase):
    def test_actual_sef1_pin_matches_itself_independent_of_current_head(self):
        maps = [ROOT / "resources" / "mappings" / "SEF" / "SEF1.json"]
        before = maps[0].read_bytes()
        result, exit_code = drift.report(OEE, PIN, maps)
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["results"][0]["state"], "unchanged")
        self.assertFalse(result["upstreamReviewRequired"])
        self.assertEqual(result["results"][0]["changes"], [])
        self.assertFalse(result["autoRemapped"])
        self.assertFalse(result["filesChanged"])
        self.assertEqual(maps[0].read_bytes(), before)

    def test_explicit_missing_target_reports_incomplete_but_pin_remains_valid(self):
        maps = [ROOT / "resources" / "mappings" / "SEF" / "SEF1.json"]
        result, exit_code = drift.report(OEE, "f" * 40, maps)
        self.assertEqual(exit_code, 3)
        self.assertEqual(result["pinnedValidation"], "passed")
        self.assertEqual(result["results"][0]["state"], "target-unavailable")

    def test_current_checkout_head_is_explicit_target_not_map_source(self):
        head = subprocess.run(
            ["git", "-C", str(OEE), "rev-parse", "--verify", "HEAD^{commit}"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        self.assertRegex(head, r"^[0-9a-f]{40}$")
        maps = [ROOT / "resources" / "mappings" / "SEF" / "SEF1.json"]
        before = maps[0].read_bytes()
        result, status = drift.report(OEE, head, maps)
        self.assertIn(status, (0, 3))
        self.assertEqual(result["targetRevision"], head)
        self.assertEqual(result["results"][0]["pinnedRevision"], PIN)
        self.assertEqual(result["pinnedValidation"], "passed")
        self.assertFalse(result["filesChanged"])
        self.assertFalse(result["autoRemapped"])
        self.assertEqual(maps[0].read_bytes(), before)

    def test_report_command_refuses_implicit_head_and_write_options(self):
        cmd = [
            sys.executable, str(ROOT / "scripts" / "report-oee-drift.py"),
            "--oee", str(OEE), "--course", "SEF1",
        ]
        for args in ([], ["--target-revision", "HEAD"],
                     ["--target-revision", PIN, "--write"]):
            with self.subTest(args=args):
                proc = subprocess.run([*cmd, *args], cwd=ROOT,
                                      capture_output=True, check=False)
                self.assertEqual(proc.returncode, 2)
                self.assertEqual(proc.stdout, b"")

    def test_running_reporter_twice_produces_identical_json_bytes(self):
        command = [
            sys.executable, str(ROOT / "scripts" / "report-oee-drift.py"),
            "--oee", str(OEE), "--target-revision", PIN, "--course", "SEF1",
        ]
        one = subprocess.run(command, cwd=ROOT, capture_output=True, check=False)
        two = subprocess.run(command, cwd=ROOT, capture_output=True, check=False)
        self.assertEqual(one.returncode, 0, one.stderr)
        self.assertEqual(two.returncode, 0, two.stderr)
        self.assertEqual(one.stdout, two.stdout)
        self.assertEqual(json.loads(one.stdout)["results"][0]["state"], "unchanged")


if __name__ == "__main__":
    unittest.main()
