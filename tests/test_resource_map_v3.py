"""REL-I04: current-only release-keyed resource map contract."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("resource_check", ROOT / "scripts/check-resources.py")
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)
from test_toolkit_consumer import PIN, COURSE_SHA, valid_map

CATALOG = {
    "R1": {"access": {"mode": "free"},
           "verification": {"status": "verified", "basis": "Test"}}
}


class MapShapeTests(unittest.TestCase):
    def check(self, mapping):
        findings = validator.Check()
        valid = validator.validate_map_shape(mapping, CATALOG, findings, "test")
        return valid, findings

    def test_supported_map(self):
        self.assertTrue(self.check(valid_map())[0])

    def test_release_identity_required(self):
        for field, value in (
            ("releaseId", "main"), ("manifestSha256", "a" * 40),
            ("courseSha256", "B" * 64), ("repository", "private/course"),
            ("path", "curriculum/APP/APP1.md"),
            ("specification", "v0.1.0"),
        ):
            item = valid_map()
            item["curriculum"][field] = value
            with self.subTest(field=field):
                self.assertFalse(self.check(item)[0])

    def test_no_git_revision_or_old_schema(self):
        for mutation in (
            lambda m: m.update(schemaVersion=2),
            lambda m: m["curriculum"].update(revision="c" * 40),
            lambda m: m.update(unrecognized=True),
        ):
            item = valid_map()
            mutation(item)
            self.assertFalse(self.check(item)[0])

    def test_partial_and_unmapped_require_gaps(self):
        for coverage, resources in (
            ("partial", []), ("unmapped", []),
            ("unmapped", valid_map()["modules"][0]["resources"]),
            ("mapped", []),
        ):
            item = valid_map()
            item["modules"][0].update(coverage=coverage, resources=resources)
            item["modules"][0].pop("gap", None)
            self.assertFalse(self.check(item)[0])
        item = valid_map()
        item["modules"][0].update(coverage="unmapped", gap="No sources", resources=[])
        self.assertTrue(self.check(item)[0])

    def test_reject_duplicate_modules_resources_and_foreign_ids(self):
        item = valid_map()
        item["modules"].append(copy.deepcopy(item["modules"][0]))
        self.assertFalse(self.check(item)[0])
        item = valid_map()
        item["modules"][0]["resources"].append(copy.deepcopy(item["modules"][0]["resources"][0]))
        self.assertFalse(self.check(item)[0])
        item = valid_map()
        item["modules"][0]["resources"][0]["outcomeIds"] = ["APP1-O1"]
        self.assertFalse(self.check(item)[0])

    def test_only_release_keyed_schema_is_current(self):
        schema = json.loads((ROOT / "resources/schemas/course-map.schema.json").read_text())
        self.assertEqual(schema["properties"]["schemaVersion"]["const"], 3)
        props = schema["properties"]["curriculum"]
        self.assertEqual(set(props["required"]),
                         {"repository", "releaseId", "manifestSha256", "courseSha256",
                          "specification", "course", "path"})
        self.assertNotIn("revision", props["properties"])

    def test_sef1_review_saved_but_not_activated_without_official_release(self):
        self.assertFalse((ROOT / "resources/mappings/SEF/SEF1.json").exists())
        self.assertFalse((ROOT / "resources/guides/SEF/SEF1.md").exists())
        review = (ROOT / "resources/editorial/SEF1-REVIEW.md").read_text()
        self.assertIn("16-bit Hack", review)
        self.assertIn("eight-bit architecture", review)
        self.assertIn("not an active resource map", review)

    def test_unmapped_course_is_reported_without_touching_source(self):
        cmd = [sys.executable, str(ROOT / "scripts/check-resources.py"),
               "--course", "SEF2"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("unmapped course SEF2", proc.stderr)


if __name__ == "__main__":
    unittest.main()
