#!/usr/bin/env python3
"""WS-I03: schema-v2 shape and fail-closed source tests."""
import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("resource_check", ROOT / "scripts/check-resources.py")
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)
PIN = "a" * 40
CATALOG = {"R1": {"access": {"mode": "free"},
                   "verification": {"status": "review-needed", "basis": "Editorial review pending"}}}


def valid_map():
    return {"schemaVersion": 2, "status": "draft",
            "curriculum": {"repository": "0xbuffdev/open-engineering-education",
                           "revision": PIN, "specification": "v0.2.0",
                           "course": "SEF1", "path": "curriculum/SEF/SEF1.md"},
            "modules": [{"number": 1, "title": "Observe", "coverage": "partial",
                         "gap": "Needs reviewed free source",
                         "resources": [{"resource": "R1", "role": "optional",
                                        "part": {"type": "topics", "titles": ["Observe"]},
                                        "purpose": "Background", "verification": "review-needed",
                                        "outcomeIds": ["SEF1-O1"], "assessmentIds": ["SEF1-AS1"],
                                        "lesson": {"number": 1, "title": "Observe a case"}}]}]}


class ContractTests(unittest.TestCase):
    def check(self, mapping):
        findings = validator.Check()
        ok = validator.validate_map_shape(mapping, CATALOG, findings, "fixture")
        return ok, findings

    def test_valid_v2_shape(self):
        ok, findings = self.check(valid_map())
        self.assertTrue(ok, findings.errors)

    def test_legacy_sef1_fixture_is_unsupported_and_not_active(self):
        path = ROOT / "tests/fixtures/resource-map-v1-SEF1.json"
        legacy = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(legacy["modules"][0]["title"], "Inside the Machine")
        self.assertEqual(legacy["curriculum"]["revision"],
                         "938b5426716c5e5809f6dbf1997c4e50f263bea9")
        ok, findings = self.check(legacy)
        self.assertFalse(ok)
        self.assertIn("unsupported_schema", findings.errors[0])
        self.assertFalse((ROOT / "resources/mappings/SEF/SEF1.json").exists())

    def test_reject_unsupported_source_identity(self):
        for field, value in (("specification", "v0.1.0"), ("revision", "main"),
                             ("repository", "example/private"),
                             ("path", "curriculum/APP/APP1.md")):
            mapping = valid_map()
            mapping["curriculum"][field] = value
            with self.subTest(field=field):
                self.assertFalse(self.check(mapping)[0])

    def test_reject_bad_reference_shapes_and_extra_properties(self):
        mutations = [
            lambda m: m.update(legacy=True),
            lambda m: m["modules"][0].update(extra=True),
            lambda m: m["modules"][0]["resources"][0].update(outcomeIds=[]),
            lambda m: m["modules"][0]["resources"][0].update(outcomeIds=["APP1-O1"]),
            lambda m: m["modules"][0]["resources"][0].update(assessmentIds=["SEF1-AS1", "SEF1-AS1"]),
            lambda m: m["modules"][0]["resources"][0].update(verification="invented"),
        ]
        for fn in mutations:
            mapping = valid_map()
            fn(mapping)
            self.assertFalse(self.check(mapping)[0])

    def test_partial_and_unmapped_require_gaps(self):
        for coverage, resources in (("partial", []), ("unmapped", []),
                                    ("unmapped", valid_map()["modules"][0]["resources"]),
                                    ("mapped", [])):
            mapping = valid_map()
            module = mapping["modules"][0]
            module.update(coverage=coverage, resources=resources)
            module.pop("gap", None)
            self.assertFalse(self.check(mapping)[0])
        mapping = valid_map()
        mapping["modules"][0].update(coverage="unmapped", gap="Not mapped", resources=[])
        self.assertTrue(self.check(mapping)[0])

    def test_duplicate_module_and_resource_rejected(self):
        mapping = valid_map()
        mapping["modules"].append(copy.deepcopy(mapping["modules"][0]))
        self.assertFalse(self.check(mapping)[0])
        mapping = valid_map()
        mapping["modules"][0]["resources"].append(copy.deepcopy(mapping["modules"][0]["resources"][0]))
        self.assertFalse(self.check(mapping)[0])

    def test_only_v2_schema_is_active(self):
        schema = json.loads((ROOT / "resources/schemas/course-map.schema.json").read_text())
        self.assertEqual(schema["properties"]["schemaVersion"]["const"], 2)
        self.assertIn("specification", schema["properties"]["curriculum"]["required"])
        self.assertEqual(schema["properties"]["curriculum"]["properties"]["specification"]["const"], "v0.2.0")

    def test_no_map_is_catalog_only_and_sef1_is_unmapped(self):
        command = [sys.executable, str(ROOT / "scripts/check-resources.py")]
        clean = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(clean.returncode, 0, clean.stderr)
        self.assertIn("catalog validation only", clean.stdout)
        unmapped = subprocess.run([*command, "--course", "SEF1"], capture_output=True, text=True)
        self.assertNotEqual(unmapped.returncode, 0)
        self.assertIn("unmapped course", unmapped.stderr)


if __name__ == "__main__":
    unittest.main()
