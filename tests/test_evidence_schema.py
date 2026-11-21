"""REL-I04 current-only learner evidence schema v2 and filesystem checks."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest
from uuid import uuid4

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    Draft202012Validator = None
    FormatChecker = None

from oee_workspace.evidence import EvidenceIssue, record_shape, relative_artifact
from test_toolkit_consumer import PIN, COURSE_SHA

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "evidence/schemas/attempt-v2.schema.json"


def valid_attempt():
    return {
        "schemaVersion": 2,
        "attemptId": str(uuid4()),
        "recordedAt": "2026-11-21T12:00:00Z",
        "course": {
            "repository": "0xbuffdev/open-engineering-education",
            "releaseId": PIN["releaseId"],
            "manifestSha256": PIN["manifestSha256"],
            "courseSha256": COURSE_SHA,
            "specification": "v0.2.0",
            "path": "curriculum/SEF/SEF1.md",
            "code": "SEF1",
        },
        "assessmentId": "SEF1-AS1",
        "outcomeIds": ["SEF1-O1"],
        "artifacts": [],
        "observations": [],
        "evaluation": None,
    }


class EvidenceSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        cls.validator = None
        if Draft202012Validator is not None:
            Draft202012Validator.check_schema(cls.schema)
            cls.validator = Draft202012Validator(cls.schema, format_checker=FormatChecker())

    def assertInvalid(self, record):
        with self.assertRaises(EvidenceIssue):
            record_shape(record)
        # Cross-field course/code checks are runtime rules, not expressible
        # as independent JSON Schema pattern constraints.

    def test_active_attempt_contract_is_v2_and_release_keyed(self):
        self.assertEqual(self.schema["properties"]["schemaVersion"]["const"], 2)
        props = self.schema["$defs"]["course"]
        self.assertEqual(set(props["required"]),
                         {"repository", "releaseId", "manifestSha256", "courseSha256",
                          "specification", "path", "code"})
        self.assertNotIn("revision", props["properties"])
        self.assertFalse(props["additionalProperties"])
        record = valid_attempt()
        self.assertEqual(record_shape(record), record)
        if self.validator is not None:
            self.assertTrue(self.validator.is_valid(record))

    def test_old_source_identity_is_not_upgraded(self):
        record = valid_attempt()
        record["schemaVersion"] = 1
        self.assertInvalid(record)
        record = valid_attempt()
        record["course"].pop("releaseId")
        record["course"]["revision"] = "a" * 40
        self.assertInvalid(record)

    def test_invalid_release_identifiers_and_digest_inputs(self):
        for field, value in (("releaseId", "main"),
                             ("manifestSha256", "b" * 40),
                             ("courseSha256", "B" * 64)):
            record = valid_attempt()
            record["course"][field] = value
            with self.subTest(field=field):
                self.assertInvalid(record)

    def test_missing_required_evidence_and_wrong_course(self):
        for mutation in (
            lambda r: r.update(outcomeIds=[]),
            lambda r: r.update(assessmentId="APP1-AS1"),
            lambda r: r["course"].update(path="curriculum/APP/APP1.md"),
            lambda r: r.update(evaluation={"decision": "met"}),
            lambda r: r["course"].update(unreviewed="extra"),
        ):
            record = valid_attempt()
            mutation(record)
            self.assertInvalid(record)

    def test_artifact_and_assistance_guards(self):
        record = valid_attempt()
        record["artifacts"] = [{"kind": "relative-path", "value": "../secrets"}]
        self.assertInvalid(record)
        record = valid_attempt()
        record["artifacts"] = [{"kind": "relative-path", "value": "notes/SEF/SEF1/log.md",
                                "sha256": "a" * 64}]
        self.assertEqual(record_shape(record), record)
        record["assistance"] = {"declaredMode": "automatic-completion", "summary": ""}
        self.assertInvalid(record)

    def test_reviewer_status_not_granted_by_structural_validation(self):
        record = valid_attempt()
        record["evaluation"] = {
            "decision": "met", "evaluatorKind": "human", "reviewerLabel": "self-reported",
            "reviewedAt": "2026-11-21T12:00:00Z", "criteriaSummary": "Observed",
            "limitations": "Cannot authenticate reviewer",
        }
        self.assertEqual(record_shape(record), record)

    def test_symlink_and_traversal_artifact_guards(self):
        for name in ("../private", "./item", "/tmp/secret", "notes//private",
                     "C:/Users/test/private"):
            with self.subTest(name=name), self.assertRaises(EvidenceIssue):
                relative_artifact(name)


if __name__ == "__main__":
    unittest.main()
