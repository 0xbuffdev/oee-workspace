"""REL-I04: immutable release-to-release drift is advisory and never repins maps."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_toolkit_consumer import PIN, valid_export, valid_map

ROOT = Path(__file__).resolve().parents[1]


def load_script(name, identity):
    spec = importlib.util.spec_from_file_location(identity, ROOT / "scripts" / name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


drift = load_script("report-oee-drift.py", "workspace_release_drift")
checker = load_script("check-resources.py", "workspace_release_checker")


def changes(original=None, updated=None, mapping=None):
    return drift.compare_contracts(
        original or valid_export(), updated or valid_export(), mapping or valid_map())


class DriftSemanticTests(unittest.TestCase):
    def test_unchanged_source_is_deterministic(self):
        one = changes()
        two = changes()
        self.assertEqual(one, two)
        self.assertEqual(one, ([], []))

    def test_outcome_change_reopens_resource_review(self):
        updated = valid_export()
        updated["outcomes"][0]["description"] = "Different engineering competency"
        differences, risks = changes(updated=updated)
        self.assertTrue(any(row["kind"] == "outcome-description" for row in differences))
        self.assertIn("referenced-outcome-definition-changed:SEF1-O1", risks[0]["reasons"])

    def test_assessment_criteria_change_reopens_resource_review(self):
        updated = valid_export()
        updated["assessments"][0]["criteria"] = "A new source criterion"
        differences, risks = changes(updated=updated)
        self.assertTrue(any("criteria" in row["kind"] for row in differences))
        self.assertTrue(any("assessment-definition-changed" in reason
                            for row in risks for reason in row["reasons"]))

    def test_lesson_locator_change_never_auto_remaps(self):
        updated = valid_export()
        updated["modules"][0]["lessons"][0]["title"] = "Different investigation"
        _, risks = changes(updated=updated)
        self.assertTrue(risks)

    def test_source_line_shifts_not_curriculum_drift(self):
        updated = valid_export()
        updated["outcomes"][0]["location"]["line"] += 100
        updated["assessments"][0]["location"]["line"] += 100
        self.assertEqual(changes(updated=updated), ([], []))


class ReleaseSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.current = self.root / "current.json"
        self.target = self.root / "target.json"
        self.current.write_text(json.dumps(PIN), encoding="utf-8")
        self.target_pin = {**PIN, "releaseId": "2026.11.2",
                           "manifestSha256": "f" * 64}
        self.target.write_text(json.dumps(self.target_pin), encoding="utf-8")
        self.map = valid_map()

    def exports(self, lock, store, code):
        self.assertEqual(code, "SEF1")
        if lock == self.current:
            return valid_export()
        item = copy.deepcopy(valid_export())
        item["source"]["releaseId"] = self.target_pin["releaseId"]
        item["source"]["manifestSha256"] = self.target_pin["manifestSha256"]
        return item

    def test_same_academic_content_new_release_requires_no_remap(self):
        original = copy.deepcopy(self.map)
        with patch.object(checker, "read_pinned_export", side_effect=self.exports):
            report = drift.inspect_map(self.map, self.current, None,
                                       self.target, None, checker)
        self.assertEqual(report["state"], "unchanged")
        self.assertFalse(report["reviewRequired"])
        self.assertFalse(report["autoRemapped"])
        self.assertEqual(self.map, original)

    def test_changed_course_bytes_always_require_manual_review(self):
        def changed(lock, store, code):
            item = self.exports(lock, store, code)
            if lock == self.target:
                item["source"]["courseSha256"] = "e" * 64
            return item
        with patch.object(checker, "read_pinned_export", side_effect=changed):
            report = drift.inspect_map(self.map, self.current, None,
                                       self.target, None, checker)
        self.assertEqual(report["state"], "source-bytes-changed")
        self.assertTrue(report["reviewRequired"])
        self.assertFalse(report["autoRemapped"])

    def test_missing_target_keeps_pinned_validation_and_no_map_mutation(self):
        original = copy.deepcopy(self.map)
        with patch.object(checker, "read_pinned_export", side_effect=self.exports):
            report = drift.inspect_map(self.map, self.current, None,
                                       self.root / "missing.json", None, checker)
        self.assertEqual(report["pinnedValidation"], "passed")
        self.assertEqual(report["targetValidation"], "incomplete")
        self.assertTrue(report["reviewRequired"])
        self.assertEqual(self.map, original)

    def test_invalid_pinned_lock_aborts_before_target(self):
        self.current.unlink()
        with patch.object(checker, "read_pinned_export", side_effect=self.exports):
            with self.assertRaises(checker.load_consumer().ContractError):
                drift.inspect_map(self.map, self.current, None,
                                  self.target, None, checker)


if __name__ == "__main__":
    unittest.main()
