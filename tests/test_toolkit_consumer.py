"""Offline consumer contract tests; synthetic derived OEE exports only."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify-oee-export.py"
spec = importlib.util.spec_from_file_location("oee_export_consumer", SCRIPT)
consumer = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = consumer
spec.loader.exec_module(consumer)
PIN = "a" * 40


def valid_export():
    source_path = "curriculum/SEF/SEF1.md"
    return {
        "exportVersion": 1,
        "source": {
            "repository": "0xbuffdev/open-engineering-education",
            "revision": PIN,
            "specification": "v0.2.0",
            "coursePath": source_path,
        },
        "course": {
            "code": "SEF1", "program": "SEF", "type": "course",
            "status": "draft", "prerequisites": [],
        },
        "outcomes": [
            {"id": "SEF1-O1", "description": "Describe an observed behavior",
             "location": {"path": source_path, "line": 12}},
        ],
        "assessments": [
            {"id": "SEF1-AS1", "required": True, "outcomeIds": ["SEF1-O1"],
             "work": "Diagnose one failure", "criteria": "Public checks",
             "evidence": "Reproducible notes",
             "location": {"path": source_path, "line": 29}},
        ],
        "modules": [
            {"number": 1, "title": "Observe",
             "outcomeIds": ["SEF1-O1"],
             "lessons": [{"ordinal": 1, "title": "Observe a case"},
                         {"ordinal": 2, "title": "Investigate"}]},
        ],
        "coverage": {"SEF1-O1": ["SEF1-AS1"]},
        "validation": {"structural": "passed", "manualReviewRequired": True},
    }


def valid_map():
    return {
        "schemaVersion": 2,
        "status": "draft",
        "curriculum": {
            "repository": "0xbuffdev/open-engineering-education",
            "revision": PIN, "specification": "v0.2.0",
            "course": "SEF1", "path": "curriculum/SEF/SEF1.md",
        },
        "modules": [{
            "number": 1, "title": "Observe", "coverage": "partial",
            "gap": "Resources need verification",
            "resources": [{
                "resource": "R1", "role": "optional",
                "part": {"type": "topics", "titles": ["Observations"]},
                "purpose": "Background", "verification": "review-needed",
                "outcomeIds": ["SEF1-O1"], "assessmentIds": ["SEF1-AS1"],
                "lesson": {"number": 1, "title": "Observe a case"},
            }],
        }],
    }


class PinnedConsumerTests(unittest.TestCase):
    def test_supported_structural_export_and_matching_v2_map(self):
        checked = consumer.check_export(valid_export(), PIN)
        consumer.check_map(valid_map(), checked)
        self.assertEqual(checked["course"], "SEF1")

    def test_revision_is_selected_externally_not_accepted_from_export(self):
        with self.assertRaisesRegex(consumer.ContractError, "revision"):
            consumer.check_export(valid_export(), "b" * 40)

    def test_reject_legacy_export_generation_and_specification(self):
        for change in (
            lambda data: data.update(exportVersion=0),
            lambda data: data["source"].update(specification="v0.1.0"),
            lambda data: data["source"].update(repository="example/private"),
        ):
            with self.subTest(change=str(change)):
                data = valid_export()
                change(data)
                with self.assertRaises(consumer.ContractError) as caught:
                    consumer.check_export(data, PIN)
                self.assertEqual(caught.exception.category, "unsupported_format")

    def test_reject_old_map_without_conversion(self):
        mapping = valid_map()
        mapping["schemaVersion"] = 1
        with self.assertRaises(consumer.ContractError) as caught:
            consumer.check_map(mapping, consumer.check_export(valid_export(), PIN))
        self.assertEqual(caught.exception.category, "unsupported_format")

    def test_reject_map_from_wrong_source_commit(self):
        mapping = valid_map()
        mapping["curriculum"]["revision"] = "b" * 40
        with self.assertRaisesRegex(consumer.ContractError, "source identity"):
            consumer.check_map(mapping, consumer.check_export(valid_export(), PIN))

    def test_reject_unknown_outcome_and_assessment_refs(self):
        for field, value in (("outcomeIds", "SEF1-O99"),
                             ("assessmentIds", "SEF1-AS99")):
            mapping = valid_map()
            mapping["modules"][0]["resources"][0][field] = [value]
            with self.subTest(field=field):
                with self.assertRaisesRegex(consumer.ContractError, "unknown canonical"):
                    consumer.check_map(mapping, consumer.check_export(valid_export(), PIN))

    def test_reject_changed_module_title_even_with_same_number(self):
        mapping = valid_map()
        mapping["modules"][0]["title"] = "An unrelated module"
        with self.assertRaisesRegex(consumer.ContractError, "locator"):
            consumer.check_map(mapping, consumer.check_export(valid_export(), PIN))

    def test_reject_changed_lesson_locator(self):
        mapping = valid_map()
        mapping["modules"][0]["resources"][0]["lesson"]["title"] = "Unrelated"
        with self.assertRaisesRegex(consumer.ContractError, "lesson locator"):
            consumer.check_map(mapping, consumer.check_export(valid_export(), PIN))

    def test_required_coverage_cannot_be_invented_or_from_optional(self):
        for value in ([], ["SEF1-AS2"]):
            with self.subTest(value=value):
                data = valid_export()
                data["coverage"]["SEF1-O1"] = value
                with self.assertRaisesRegex(consumer.ContractError, "coverage mismatch"):
                    consumer.check_export(data, PIN)
        data = valid_export()
        data["assessments"][0]["required"] = False
        with self.assertRaises(consumer.ContractError):
            consumer.check_export(data, PIN)

    def test_reject_duplicate_outcomes_and_modules(self):
        data = valid_export()
        data["outcomes"].append(copy.deepcopy(data["outcomes"][0]))
        with self.assertRaisesRegex(consumer.ContractError, "duplicate outcome"):
            consumer.check_export(data, PIN)
        data = valid_export()
        data["modules"].append(copy.deepcopy(data["modules"][0]))
        with self.assertRaisesRegex(consumer.ContractError, "module number"):
            consumer.check_export(data, PIN)

    def test_incomplete_toolkit_validation_is_not_accepted(self):
        data = valid_export()
        data["validation"]["structural"] = "incomplete"
        with self.assertRaisesRegex(consumer.ContractError, "not structurally passed"):
            consumer.check_export(data, PIN)

    def test_cli_wrong_revision_and_old_map_are_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            exported = folder / "export.json"
            mapping = folder / "map.json"
            exported.write_text(json.dumps(valid_export()), encoding="utf-8")
            mapping.write_text(json.dumps(valid_map()), encoding="utf-8")
            cmd = [sys.executable, str(SCRIPT), "--export", str(exported),
                   "--revision", PIN, "--map", str(mapping), "--json"]
            good = subprocess.run(cmd, capture_output=True, text=True, check=False)
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            self.assertTrue(json.loads(good.stdout)["manualReviewRequired"])
            bad_pin = subprocess.run([*cmd[:cmd.index("--map")-2],
                                       "--revision", "b" * 40, "--json"],
                                      capture_output=True, text=True, check=False)
            self.assertNotEqual(bad_pin.returncode, 0)
            mapping.write_text(json.dumps({**valid_map(), "schemaVersion": 1}),
                               encoding="utf-8")
            old = subprocess.run(cmd, capture_output=True, text=True, check=False)
            self.assertEqual(old.returncode, 3)
            self.assertEqual(json.loads(old.stdout)["finding"]["category"],
                             "unsupported_format")


if __name__ == "__main__":
    unittest.main()
