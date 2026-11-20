"""WS-I07 domain tests: exact source, artifact safety, review projections and export."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from oee_workspace.evidence import (
    EvidenceIssue, EvidenceService, record_shape, relative_artifact, review_state,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "evidence"
OEE = Path(os.environ.get("OEE_REPO", ROOT / "_oee")).resolve()
PIN = "67416343f3eab17ada5d3c79ae6cc782524c29ff"


def read(name: str, category="valid"):
    return json.loads((FIXTURES / category / name).read_text(encoding="utf-8"))


class ShapeAndFilesystemTests(unittest.TestCase):
    def test_canonical_fixture_shapes_without_runtime_dependency(self):
        names = ["SEF1-AS1-unreviewed.json", "SEF1-AS2-self-review.json",
                 "SEF10-AS2-unreviewed.json",
                 "SEF10-AS3-claimed-human-review.json"]
        for name in names:
            with self.subTest(name=name):
                record = read(name)
                self.assertEqual(record_shape(record), record)

    def test_invalid_shape_fixtures_are_rejected_by_stdlib(self):
        for file in sorted((FIXTURES / "invalid-schema").glob("*.json")):
            with self.subTest(name=file.name):
                with self.assertRaises(EvidenceIssue):
                    record_shape(json.loads(file.read_text(encoding="utf-8")))

    def test_schema_valid_but_source_invalid_fixtures_parse(self):
        for file in sorted((FIXTURES / "invalid-reference").glob("*.json")):
            with self.subTest(name=file.name):
                record = json.loads(file.read_text(encoding="utf-8"))
                if file.name == "wrong-course-path-SEF1.json":
                    # Published JSON Schema cannot compare two fields, but
                    # the stdlib domain validator enforces their relationship.
                    with self.assertRaises(EvidenceIssue) as caught:
                        record_shape(record)
                    self.assertEqual(caught.exception.code, "WSE005")
                else:
                    record_shape(record)

    def test_attempt_display_review_state_never_authenticates_reviewer(self):
        unreviewed = read("SEF10-AS2-unreviewed.json")
        self.assertEqual(review_state(unreviewed)["status"], "attempt-recorded")
        self.assertIsNone(review_state(unreviewed)["decision"])
        reviewed = read("SEF1-AS2-self-review.json")
        self.assertEqual(review_state(reviewed)["status"], "self-assessed")
        claimed = read("SEF10-AS3-claimed-human-review.json")
        self.assertEqual(review_state(claimed)["status"], "human-review-reported")
        self.assertFalse(review_state(claimed)["reviewerIdentityVerified"])

    def test_unsafe_paths_are_not_treated_as_relative(self):
        for text in ("../private", "a/../private", "a//b", "./file", "/tmp/secret",
                     "C:/Users/user/secrets", r"notes\private", "a/\x00/file"):
            with self.subTest(path=text):
                with self.assertRaises(EvidenceIssue):
                    relative_artifact(text)


@unittest.skipUnless(
    (OEE / "tooling" / "oee_toolkit" / "__main__.py").is_file(),
    "pinned OEE Toolkit checkout required; CI supplies _oee",
)
class RealEvidenceOperationsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "learner"
        self.root.mkdir()
        self.service = EvidenceService(self.root, OEE)

    def install(self, name, category="valid", *, record=None):
        record = deepcopy(record if record is not None else read(name, category))
        code = record["course"]["code"]
        program = code.rstrip("0123456789")
        directory = (self.root / "evidence" / program / code /
                     record["assessmentId"])
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / (record["attemptId"] + ".json")
        path.write_text(json.dumps(record), encoding="utf-8")
        return path

    def build_artifact(self, name="projects/SEF10/tests/results.txt",
                       content=b"synthetic test output"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def test_real_fixed_commit_attempts_and_unverified_review_states(self):
        for name in ("SEF1-AS1-unreviewed.json", "SEF1-AS2-self-review.json",
                     "SEF10-AS3-claimed-human-review.json"):
            with self.subTest(name=name):
                record_path = self.install(name)
                if name == "SEF10-AS3-claimed-human-review.json":
                    self.build_artifact("projects/SEF10/docs/evaluation.md",
                                        b"synthetic review fixture, not actual proof")
                result = self.service.check(record_path)
                self.assertEqual(result["outcome"], "valid", result["findings"])
                self.assertEqual(result["revision"], PIN)
                self.assertTrue(result["sourceValidated"])
                self.assertFalse(result["review"]["reviewerIdentityVerified"])

    def test_missing_artifact_is_incomplete_and_hash_mismatch_invalid(self):
        missing = self.install("missing-artifact-SEF10.json", "invalid-reference")
        self.assertEqual(self.service.check(missing)["outcome"], "incomplete")
        mismatched = self.install("mismatched-artifact-hash-SEF10.json",
                                  "invalid-reference")
        self.build_artifact()
        result = self.service.check(mismatched)
        self.assertEqual(result["outcome"], "invalid")
        self.assertEqual(result["findings"][0]["code"], "WSE007")

    def test_good_sha256_matches_and_changed_file_invalidates(self):
        data = b"reproducible example, not genuine learner proof"
        self.build_artifact(content=data)
        record = read("SEF10-AS2-unreviewed.json")
        record["artifacts"][0]["sha256"] = hashlib.sha256(data).hexdigest()
        path = self.install("SEF10-AS2-unreviewed.json", record=record)
        self.assertEqual(self.service.check(path)["outcome"], "valid")
        self.build_artifact(content=data + b" - tampered")
        self.assertEqual(self.service.check(path)["outcome"], "invalid")

    def test_symlinked_artifact_rejected_even_when_target_inside_workspace(self):
        record = read("SEF10-AS2-unreviewed.json")
        target = self.build_artifact()
        alias = target.parent / "alias.txt"
        alias.symlink_to(target)
        record["artifacts"] = [{"kind": "relative-path",
                                "value": "projects/SEF10/tests/alias.txt"}]
        path = self.install("SEF10-AS2-unreviewed.json", record=record)
        result = self.service.check(path)
        self.assertEqual(result["outcome"], "invalid")
        self.assertEqual(result["findings"][0]["code"], "WSE004")

    def test_source_revision_and_assessment_reference_failures(self):
        cases = {
            "wrong-revision-SEF1.json": ("incomplete", "WSE003"),
            "wrong-course-path-SEF1.json": ("invalid", "WSE005"),
            "unknown-assessment-SEF1.json": ("invalid", "WSE005"),
            "foreign-outcome-SEF1.json": ("invalid", "WSE005"),
        }
        for name, expected in cases.items():
            with self.subTest(name=name):
                path = self.install(name, "invalid-reference")
                result = self.service.check(path)
                self.assertEqual((result["outcome"], result["findings"][0]["code"]),
                                 expected)
                # Isolate each malformed-reference fixture; they intentionally
                # reuse a UUID and must not create accidental duplicate IDs.
                path.unlink()

    def test_wrong_record_path_does_not_elevate_a_claim(self):
        path = self.install("SEF1-AS2-self-review.json")
        moved = path.with_name("someone-elses-id.json")
        path.rename(moved)
        result = self.service.check(moved)
        self.assertEqual(result["outcome"], "invalid")
        self.assertEqual(result["findings"][0]["code"], "WSE005")

    def test_read_only_status_exposes_all_required_assessment_gaps(self):
        self.install("SEF10-AS3-claimed-human-review.json")
        self.build_artifact("projects/SEF10/docs/evaluation.md", b"synthetic")
        snapshot = self.service.status()
        self.assertEqual(snapshot["counts"]["valid"], 1)
        course = next(c for c in snapshot["courses"] if c["course"] == "SEF10")
        self.assertFalse(course["allRequiredAssessmentDecisionsRecorded"])
        self.assertEqual(course["completion"], "not-determined")
        outcome = next(row for row in course["outcomes"] if row["outcomeId"] == "SEF10-O3")
        self.assertEqual(set(outcome["requiredAssessmentIds"]),
                         {"SEF10-AS2", "SEF10-AS3"})
        self.assertEqual(outcome["decisionsRecordedFor"], ["SEF10-AS3"])
        self.assertEqual(outcome["outstandingAssessmentIds"], ["SEF10-AS2"])
        self.assertFalse(snapshot["educationalAchievementDetermined"])

    def test_explicit_pinned_course_without_attempts_reports_no_evidence(self):
        snapshot = self.service.status("SEF1", PIN)
        self.assertEqual(snapshot["counts"]["valid"], 0)
        self.assertEqual(len(snapshot["courses"]), 1)
        course = snapshot["courses"][0]
        self.assertEqual(course["course"], "SEF1")
        self.assertTrue(all(row["reportedStates"] == ["no-evidence"]
                            for row in course["assessments"]))
        self.assertTrue(all(not row["decisionsRecordedFor"]
                            for row in course["outcomes"]))
        self.assertFalse(course["allRequiredAssessmentDecisionsRecorded"])
        self.assertEqual(course["completion"], "not-determined")

    def test_explicit_status_source_scope_rejects_head_fallback(self):
        with self.assertRaises(EvidenceIssue):
            self.service.status("SEF1", None)
        with self.assertRaises(EvidenceIssue) as caught:
            self.service.status("SEF1", "f" * 40)
        self.assertEqual(caught.exception.kind, "incomplete")

    def test_automated_observation_stays_attempt_recorded_without_decision(self):
        self.build_artifact()
        path = self.install("SEF10-AS2-unreviewed.json")
        checked = self.service.check(path)
        self.assertEqual(checked["outcome"], "valid")
        self.assertEqual(checked["review"]["status"], "attempt-recorded")
        self.assertIsNone(checked["review"]["decision"])

    def test_duplicate_ids_across_distinct_assessments_are_invalid_in_status(self):
        original = read("SEF1-AS1-unreviewed.json")
        first = self.install("SEF1-AS1-unreviewed.json", record=original)
        other = deepcopy(original)
        other["assessmentId"] = "SEF1-AS2"
        other["outcomeIds"] = ["SEF1-O3"]
        second = self.install("SEF1-AS1-unreviewed.json", record=other)
        self.assertNotEqual(first, second)
        snapshot = self.service.status()
        self.assertEqual(snapshot["counts"]["invalid"], 2)
        self.assertTrue(all(item["findings"][0]["code"] == "WSE008"
                            for item in snapshot["records"]))

    def test_standalone_check_rejects_duplicate_uuid_in_another_assessment(self):
        attempt = read("SEF1-AS1-unreviewed.json")
        first = self.install("SEF1-AS1-unreviewed.json", record=attempt)
        other = deepcopy(attempt)
        other["assessmentId"] = "SEF1-AS2"
        other["outcomeIds"] = ["SEF1-O3"]
        second = self.install("SEF1-AS1-unreviewed.json", record=other)
        for path in (first, second):
            with self.subTest(path=path):
                result = self.service.check(path)
                self.assertEqual(result["outcome"], "invalid")
                self.assertEqual(result["findings"][0]["code"], "WSE008")
        with self.assertRaises(EvidenceIssue) as caught:
            self.service.export_selected([first])
        self.assertEqual(caught.exception.code, "WSE008")

    def test_selective_export_excludes_unselected_records_and_artifact_bytes(self):
        selected = self.install("SEF1-AS1-unreviewed.json")
        omitted = self.install("SEF1-AS2-self-review.json")
        payload = self.service.export_selected([selected])
        self.assertEqual(payload["exportVersion"], 1)
        self.assertEqual(len(payload["records"]), 1)
        self.assertEqual(payload["records"][0]["attempt"]["attemptId"],
                         read("SEF1-AS1-unreviewed.json")["attemptId"])
        self.assertNotIn(str(self.root), json.dumps(payload))
        self.assertNotIn(omitted.name, json.dumps(payload))
        self.assertFalse(payload["artifactBytesIncluded"])
        self.assertFalse(payload["educationalAchievementDetermined"])

    def test_export_rejects_unselected_leak_and_bad_choices(self):
        selected = self.install("SEF1-AS1-unreviewed.json")
        with self.assertRaises(EvidenceIssue):
            self.service.export_selected([])
        with self.assertRaises(EvidenceIssue):
            self.service.export_selected([selected, selected])
        bad = self.install("wrong-revision-SEF1.json", "invalid-reference")
        with self.assertRaises(EvidenceIssue) as caught:
            self.service.export_selected([bad])
        self.assertEqual(caught.exception.kind, "incomplete")

    def test_status_never_rewrites_learner_progress_or_artifacts(self):
        prior = self.root / "progress.md"
        prior.write_text("My original notes", encoding="utf-8")
        self.install("SEF1-AS1-unreviewed.json")
        self.service.status()
        self.assertEqual(prior.read_text(encoding="utf-8"), "My original notes")
        self.assertFalse((self.root / "evidence-status.json").exists())

    def test_symlinked_record_is_refused(self):
        original = self.install("SEF1-AS1-unreviewed.json")
        alias = original.with_name("another-name.json")
        alias.symlink_to(original)
        snapshot = self.service.check(alias)
        self.assertEqual(snapshot["outcome"], "invalid")
        self.assertEqual(snapshot["findings"][0]["code"], "WSE004")


if __name__ == "__main__":
    unittest.main()
