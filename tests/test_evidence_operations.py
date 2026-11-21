"""REL-I04 learner evidence semantics against a single verified synthetic v2 export."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from oee_workspace import evidence as ev
from test_toolkit_consumer import PIN, valid_export
from test_evidence_schema import valid_attempt, COURSE_SHA


class FakeReader:
    class PinnedSourceError(Exception):
        category = "source_missing"

    @staticmethod
    def load_consumer():
        return _consumer()

    @staticmethod
    def read_pinned_export(lock, store, code):
        if code != "SEF1":
            raise AssertionError("fixture exports only SEF1")
        return valid_export()


def _consumer():
    import importlib.util
    script = Path(__file__).resolve().parents[1] / "scripts/verify-oee-export.py"
    spec = importlib.util.spec_from_file_location("test_evidence_release_consumer", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleaseEvidenceOperationsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "learner"
        self.root.mkdir()
        self.lock = Path(self.temp.name) / "oee-curriculum.lock.json"
        self.lock.write_text(json.dumps(PIN), encoding="utf-8")
        self.patch_reader = patch.object(ev, "load_reader", return_value=FakeReader)
        self.patch_reader.start()
        self.addCleanup(self.patch_reader.stop)
        self.service = ev.EvidenceService(self.root, self.lock)

    def install(self, record=None):
        record = valid_attempt() if record is None else record
        folder = self.root / "evidence/SEF/SEF1/SEF1-AS1"
        folder.mkdir(parents=True, exist_ok=True)
        file = folder / (record["attemptId"] + ".json")
        file.write_text(json.dumps(record), encoding="utf-8")
        return file

    def test_full_release_identification_and_valid_attempt(self):
        file = self.install()
        checked = self.service.check(file)
        self.assertEqual(checked["outcome"], "valid", checked)
        self.assertTrue(checked["sourceValidated"])
        self.assertEqual(checked["releaseId"], PIN["releaseId"])
        self.assertEqual(checked["manifestSha256"], PIN["manifestSha256"])
        self.assertEqual(checked["review"]["status"], "attempt-recorded")

    def test_wrong_digest_and_release_not_reinterpreted(self):
        for field, value in (("releaseId", "2026.11.2"),
                             ("manifestSha256", "f" * 64),
                             ("courseSha256", "e" * 64)):
            record = valid_attempt()
            record["course"][field] = value
            path = self.install(record)
            result = self.service.check(path)
            self.assertEqual(result["outcome"], "invalid", result)
            self.assertEqual(result["findings"][0]["code"], "WSE005")
            path.unlink()

    def test_unknown_assessment_and_outcome_not_auto_granted(self):
        record = valid_attempt()
        record["assessmentId"] = "SEF1-AS9"
        file = self.install(record)
        # Filename location must follow the submitted assessment ID.
        target = file.parent.parent / "SEF1-AS9" / file.name
        target.parent.mkdir(parents=True)
        file.rename(target)
        result = self.service.check(target)
        self.assertEqual(result["outcome"], "invalid", result)
        record = valid_attempt()
        record["outcomeIds"] = ["SEF1-O9"]
        file = self.install(record)
        self.assertEqual(self.service.check(file)["outcome"], "invalid")

    def test_missing_artifact_incomplete_without_file_mutation(self):
        record = valid_attempt()
        record["artifacts"] = [{"kind": "relative-path", "value": "notes/SEF/SEF1/missing.md"}]
        file = self.install(record)
        original = file.read_bytes()
        report = self.service.check(file)
        self.assertEqual(report["outcome"], "incomplete")
        self.assertEqual(file.read_bytes(), original)

    def test_artifact_hash_and_symlink_rejected(self):
        path = self.root / "notes/SEF/SEF1/example.md"
        path.parent.mkdir(parents=True)
        path.write_text("evidence", encoding="utf-8")
        record = valid_attempt()
        record["artifacts"] = [{"kind": "relative-path", "value": "notes/SEF/SEF1/example.md",
                                "sha256": hashlib.sha256(b"other").hexdigest()}]
        file = self.install(record)
        self.assertEqual(self.service.check(file)["outcome"], "invalid")
        record["artifacts"][0]["sha256"] = hashlib.sha256(b"evidence").hexdigest()
        file.write_text(json.dumps(record), encoding="utf-8")
        self.assertEqual(self.service.check(file)["outcome"], "valid")

    def test_no_evidence_projection_does_not_grant_completion(self):
        result = self.service.status("SEF1")
        self.assertEqual(result["counts"]["valid"], 0)
        self.assertEqual(result["courses"][0]["course"], "SEF1")
        self.assertEqual(result["courses"][0]["releaseId"], PIN["releaseId"])
        self.assertEqual(result["courses"][0]["completion"], "not-determined")
        self.assertEqual(result["courses"][0]["assessments"][0]["reportedStates"], ["no-evidence"])

    def test_immutable_selected_record_export_excludes_artifact_bytes(self):
        file = self.install()
        result = self.service.export_selected([file])
        self.assertEqual(result["exportVersion"], 2)
        self.assertEqual(len(result["records"]), 1)
        self.assertFalse(result["artifactBytesIncluded"])
        self.assertFalse(result["reviewerIdentityVerified"])
        with self.assertRaises(ev.EvidenceIssue):
            self.service.export_selected([file, file])

    def test_missing_lock_blocks_source_without_guessing(self):
        self.lock.unlink()
        with self.assertRaises(ev.EvidenceIssue) as caught:
            ev.EvidenceService(self.root, self.lock).source("SEF1")
        self.assertEqual(caught.exception.kind, "incomplete")


if __name__ == "__main__":
    unittest.main()
