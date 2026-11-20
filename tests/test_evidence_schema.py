"""WS-I06: strict Evidence 0002 schema and immutable OEE reference fixtures.

The tests compare canonical source IDs through the Toolkit export consumer.
Production validation, filesystem statuses and learner progress belong to WS-I07.
The jsonschema dependency is for schema CONTRACT TESTS only, not learner runtime.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:  # Existing stdlib-only suites remain runnable offline.
    Draft202012Validator = None
    FormatChecker = None

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "evidence"
SCHEMA = ROOT / "evidence" / "schemas" / "attempt-v1.schema.json"
PIN = "67416343f3eab17ada5d3c79ae6cc782524c29ff"
OEE = Path(os.environ.get("OEE_REPO", ROOT / "_oee")).resolve()
sys.path.insert(0, str(ROOT / "scripts"))
import importlib.util  # noqa: E402


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(
        "evidence_pinned_source_reader", ROOT / "scripts" / name
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def examples(directory: str):
    return sorted((FIXTURES / directory).glob("*.json"))


@unittest.skipUnless(Draft202012Validator is not None,
                     "jsonschema 4.23 is a contract test dependency; CI installs it")
class EvidenceSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = read(SCHEMA)
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema, format_checker=FormatChecker())

    def assertValid(self, record):
        issues = sorted(self.validator.iter_errors(record), key=lambda e: str(e.path))
        self.assertEqual(issues, [], [str(i) for i in issues])

    def assertInvalid(self, record):
        self.assertFalse(self.validator.is_valid(record), record)

    def test_active_schema_is_v1_and_current_specification_only(self):
        self.assertEqual(self.schema["$schema"],
                         "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(self.schema["properties"]["schemaVersion"]["const"], 1)
        self.assertEqual(self.schema["$defs"]["course"]["properties"]["specification"]["const"],
                         "v0.2.0")
        self.assertFalse(self.schema["additionalProperties"])
        self.assertFalse(self.schema["$defs"]["evaluation"]["additionalProperties"])
        self.assertTrue({"course", "assessmentId", "outcomeIds", "artifacts",
                         "observations", "evaluation"}.issubset(self.schema["required"]))

    def test_four_valid_format_fixtures(self):
        self.assertEqual(len(examples("valid")), 4)
        for path in examples("valid"):
            with self.subTest(fixture=path.name):
                self.assertValid(read(path))

    def test_all_structurally_invalid_fixtures_rejected(self):
        self.assertEqual(len(examples("invalid-schema")), 10)
        for path in examples("invalid-schema"):
            with self.subTest(fixture=path.name):
                self.assertInvalid(read(path))

    def test_reference_failures_are_still_structurally_valid(self):
        # Source and filesystem checks are beyond JSON Schema's authority.
        self.assertEqual(len(examples("invalid-reference")), 6)
        for path in examples("invalid-reference"):
            with self.subTest(fixture=path.name):
                self.assertValid(read(path))

    def test_v4_uuid_required(self):
        valid = read(FIXTURES / "valid" / "SEF1-AS1-unreviewed.json")
        for value in (
            "11111111-2222-1333-8444-555555555555",
            "11111111-2222-4333-7444-555555555555",
            "main", "A" * 36,
        ):
            with self.subTest(uuid=value):
                bad = {**valid, "attemptId": value}
                self.assertInvalid(bad)

    def test_parent_path_windows_drive_and_symlink_indirection_require_checks(self):
        record = read(FIXTURES / "valid" / "SEF10-AS2-unreviewed.json")
        for value in (
            "../private.txt", "labs/../secrets.txt", "/etc/passwd",
            r"C:\Windows\system.ini", "notes//capture.md", "./secret.txt"
        ):
            with self.subTest(value=value):
                changed = json.loads(json.dumps(record))
                changed["artifacts"][0]["value"] = value
                self.assertInvalid(changed)
        # JSON Schema can check text paths, not whether real filesystem nodes
        # are symlinks. WS-I07 must resolve and verify actual artifacts.

    def test_unreviewed_automated_observation_is_not_evaluation(self):
        record = read(FIXTURES / "valid" / "SEF10-AS2-unreviewed.json")
        self.assertEqual(record["observations"][0]["kind"], "automated-check")
        self.assertIsNone(record["evaluation"])
        self.assertValid(record)
        claimed = json.loads(json.dumps(record))
        claimed["evaluation"] = {
            "decision": "met", "evaluatorKind": "automated-check",
            "reviewerLabel": "CI", "reviewedAt": record["recordedAt"],
            "criteriaSummary": "A passing test", "limitations": ""
        }
        self.assertInvalid(claimed)

    def test_self_and_human_claims_are_distinguishable_not_verified(self):
        self_review = read(FIXTURES / "valid" / "SEF1-AS2-self-review.json")
        human = read(FIXTURES / "valid" / "SEF10-AS3-claimed-human-review.json")
        self.assertEqual(self_review["evaluation"]["evaluatorKind"], "self")
        self.assertEqual(human["evaluation"]["evaluatorKind"], "human")
        self.assertValid(self_review)
        self.assertValid(human)
        # A mutable local field never authenticates the named reviewer.

    def test_fixture_ids_are_unique(self):
        uuids = [read(p)["attemptId"] for directory in
                 ("valid", "invalid-schema", "invalid-reference")
                 for p in examples(directory)]
        # Negative cases deliberately mutate a valid fixture, so only records
        # in the active *valid* suite are required to have unique IDs.
        active = [read(p)["attemptId"] for p in examples("valid")]
        self.assertEqual(len(active), len(set(active)))
        self.assertGreater(len(uuids), len(active))


@unittest.skipUnless(
    (OEE / "tooling" / "oee_toolkit" / "__main__.py").is_file(),
    "requires local OEE Toolkit Git checkout; CI supplies _oee",
)
class PinnedEvidenceReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reader = load_script("check-resources.py")
        cls.source = {}
        for course in ("SEF1", "SEF10"):
            exported = cls.reader.read_pinned_export(OEE, PIN, course)
            cls.source[course] = cls.reader.load_consumer().check_export(
                exported, PIN
            )

    def verify_reference(self, record):
        """Test-only export seam, not a shipped evidence validator."""
        course = record["course"]
        code = course["code"]
        if code not in self.source:
            return "missing_source"
        canonical = self.source[code]
        source = canonical["source"]
        if (course["repository"] != source["repository"] or
            course["revision"] != source["revision"] or
            course["specification"] != source["specification"] or
            course["path"] != source["coursePath"]):
            return "invalid_source"
        assessment = canonical["assessments"].get(record["assessmentId"])
        if assessment is None or not assessment["required"]:
            return "invalid_assessment"
        outcomes = record["outcomeIds"]
        if not set(outcomes).issubset(assessment["outcomeIds"]):
            return "invalid_outcome"
        return "matched"

    def test_real_sef1_and_sef10_attempts_match_current_pinned_export(self):
        for path in examples("valid"):
            with self.subTest(fixture=path.name):
                record = read(path)
                self.assertEqual(self.verify_reference(record), "matched")
                self.assertEqual(record["course"]["revision"], PIN)

    def test_invalid_source_and_assessment_references_are_rejected(self):
        expected = {
            "wrong-revision-SEF1.json": "invalid_source",
            "wrong-course-path-SEF1.json": "invalid_source",
            "unknown-assessment-SEF1.json": "invalid_assessment",
            "foreign-outcome-SEF1.json": "invalid_outcome",
        }
        for name, result in expected.items():
            with self.subTest(fixture=name):
                record = read(FIXTURES / "invalid-reference" / name)
                self.assertEqual(self.verify_reference(record), result)

    def test_source_pin_is_required_not_implicit_head(self):
        with self.assertRaises(self.reader.PinnedSourceError) as ctx:
            self.reader.read_pinned_export(OEE, "f" * 40, "SEF1")
        self.assertEqual(ctx.exception.category, "source_missing")

    def test_missing_artifact_and_mismatched_hash_are_not_schema_errors(self):
        missing = read(FIXTURES / "invalid-reference" /
                       "missing-artifact-SEF10.json")
        tampered = read(FIXTURES / "invalid-reference" /
                        "mismatched-artifact-hash-SEF10.json")
        self.assertEqual(self.verify_reference(missing), "matched")
        self.assertEqual(self.verify_reference(tampered), "matched")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            missing_file = root / missing["artifacts"][0]["value"]
            self.assertFalse(missing_file.exists())
            target = root / tampered["artifacts"][0]["value"]
            target.parent.mkdir(parents=True)
            target.write_text("Synthetic test output", encoding="utf-8")
            expected = tampered["artifacts"][0]["sha256"]
            self.assertNotEqual(hashlib.sha256(target.read_bytes()).hexdigest(), expected)
        # WS-I07 implements path containment, symlink safety and hash status.

    def test_two_separate_required_assessments_for_one_outcome_are_not_collapsed(self):
        # SEF10-O3 must be addressed by both AS2 and AS3; one record is not
        # automatically a completion decision for that outcome.
        coverage = self.source["SEF10"]["assessments"]
        assessments = {
            ident for ident, entry in coverage.items()
            if entry["required"] and "SEF10-O3" in entry["outcomeIds"]
        }
        self.assertEqual(assessments, {"SEF10-AS2", "SEF10-AS3"})
        single = read(FIXTURES / "valid" / "SEF10-AS2-unreviewed.json")
        self.assertEqual(single["assessmentId"], "SEF10-AS2")
        self.assertIsNone(single["evaluation"])


if __name__ == "__main__":
    unittest.main()
