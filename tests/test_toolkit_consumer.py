"""REL-I04: strict v2 Toolkit export / release-keyed resource-map consumer tests."""
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

PIN = {"formatVersion": 1, "releaseId": "2026.11.1", "manifestSha256": "a" * 64}
COURSE_SHA = "b" * 64
ORIGIN = "c" * 40


def valid_export():
    source_path = "curriculum/SEF/SEF1.md"
    return {
        "exportVersion": 2,
        "source": {
            "repository": "0xbuffdev/open-engineering-education",
            "releaseId": PIN["releaseId"],
            "manifestSha256": PIN["manifestSha256"],
            "courseSha256": COURSE_SHA,
            "originCommit": ORIGIN,
            "specification": "v0.2.0",
            "coursePath": source_path,
        },
        "toolkit": {"toolVersion": "0.2.0", "ruleSetVersion": "v0.2.0-ot-i04"},
        "course": {"code": "SEF1", "program": "SEF", "type": "course",
                   "status": "draft", "prerequisites": []},
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
            {"number": 1, "title": "Observe", "outcomeIds": ["SEF1-O1"],
             "lessons": [{"ordinal": 1, "title": "Observe a case"},
                         {"ordinal": 2, "title": "Investigate"}]},
        ],
        "coverage": {"SEF1-O1": ["SEF1-AS1"]},
        "validation": {"structural": "passed", "manualReviewRequired": True},
    }


def valid_map():
    return {
        "schemaVersion": 3, "status": "draft",
        "curriculum": {
            "repository": "0xbuffdev/open-engineering-education",
            "releaseId": PIN["releaseId"],
            "manifestSha256": PIN["manifestSha256"],
            "courseSha256": COURSE_SHA,
            "specification": "v0.2.0",
            "course": "SEF1", "path": "curriculum/SEF/SEF1.md",
        },
        "modules": [{
            "number": 1, "title": "Observe", "coverage": "partial",
            "gap": "Resources need editorial confirmation",
            "resources": [{
                "resource": "R1", "role": "optional",
                "part": {"type": "topics", "titles": ["Observations"]},
                "purpose": "Background", "verification": "review-needed",
                "outcomeIds": ["SEF1-O1"], "assessmentIds": ["SEF1-AS1"],
                "lesson": {"number": 1, "title": "Observe a case"},
            }],
        }],
    }


class ReleaseConsumerTests(unittest.TestCase):
    def test_current_export_and_map(self):
        checked = consumer.check_export(valid_export(), PIN)
        consumer.check_map(valid_map(), checked)
        self.assertEqual(checked["source"]["releaseId"], PIN["releaseId"])

    def test_changing_release_or_digest_is_rejected(self):
        for field, value in (("releaseId", "2026.11.2"),
                             ("manifestSha256", "e" * 64),
                             ("courseSha256", "f" * 64)):
            with self.subTest(field=field):
                data = valid_export()
                data["source"][field] = value
                if field == "courseSha256":
                    mapping = valid_map()
                    with self.assertRaises(consumer.ContractError):
                        consumer.check_map(mapping, consumer.check_export(data, PIN))
                else:
                    with self.assertRaises(consumer.ContractError):
                        consumer.check_export(data, PIN)

    def test_reject_version_one_git_source_and_unknown_rule_set(self):
        for mutate in (
            lambda d: d.update(exportVersion=1),
            lambda d: d["source"].update(revision="c" * 40),
            lambda d: d["source"].update(specification="v0.1.0"),
            lambda d: d["toolkit"].update(ruleSetVersion="unreviewed"),
            lambda d: d["toolkit"].update(legacyCompatibility=True),
        ):
            data = valid_export()
            mutate(data)
            with self.subTest(data=data), self.assertRaises(consumer.ContractError):
                consumer.check_export(data, PIN)

    def test_bad_release_identifiers(self):
        for value in ("main", "2026.13.1", "2026.11.0"):
            with self.subTest(value=value):
                data = valid_export()
                data["source"]["releaseId"] = value
                with self.assertRaises(consumer.ContractError):
                    consumer.check_export(data, PIN)
        for value in ("a" * 40, "A" * 64):
            data = valid_export()
            data["source"]["manifestSha256"] = value
            with self.assertRaises(consumer.ContractError):
                consumer.check_export(data, PIN)

    def test_unsupported_map_version_and_wrong_identity(self):
        for mutate in (
            lambda m: m.update(schemaVersion=2),
            lambda m: m["curriculum"].update(releaseId="2026.11.2"),
            lambda m: m["curriculum"].update(manifestSha256="d" * 64),
            lambda m: m["curriculum"].update(courseSha256="d" * 64),
        ):
            mapping = valid_map()
            mutate(mapping)
            with self.subTest(mapping=mapping), self.assertRaises(consumer.ContractError):
                consumer.check_map(mapping, consumer.check_export(valid_export(), PIN))

    def test_unknown_outcome_and_assessment_ids(self):
        for key, value in (("outcomeIds", "SEF1-O99"),
                           ("assessmentIds", "SEF1-AS99")):
            mapping = valid_map()
            mapping["modules"][0]["resources"][0][key] = [value]
            with self.assertRaises(consumer.ContractError):
                consumer.check_map(mapping, consumer.check_export(valid_export(), PIN))

    def test_module_title_lesson_locator_coverage_and_manual_review(self):
        mapping = valid_map()
        mapping["modules"][0]["title"] = "Different module"
        with self.assertRaises(consumer.ContractError):
            consumer.check_map(mapping, consumer.check_export(valid_export(), PIN))
        mapping = valid_map()
        mapping["modules"][0]["resources"][0]["lesson"]["title"] = "Invented"
        with self.assertRaises(consumer.ContractError):
            consumer.check_map(mapping, consumer.check_export(valid_export(), PIN))
        data = valid_export()
        data["coverage"]["SEF1-O1"] = []
        with self.assertRaises(consumer.ContractError):
            consumer.check_export(data, PIN)
        data = valid_export()
        data["validation"]["manualReviewRequired"] = False
        with self.assertRaises(consumer.ContractError):
            consumer.check_export(data, PIN)

    def test_reject_duplicates_and_foreign_ids(self):
        data = valid_export()
        data["outcomes"].append(copy.deepcopy(data["outcomes"][0]))
        with self.assertRaises(consumer.ContractError):
            consumer.check_export(data, PIN)
        data = valid_export()
        data["assessments"][0]["id"] = "APP1-AS1"
        with self.assertRaises(consumer.ContractError):
            consumer.check_export(data, PIN)

    def test_strict_lock_reader(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "oee-curriculum.lock.json"
            path.write_text(json.dumps(PIN), encoding="utf-8")
            self.assertEqual(consumer.load_lock(path), PIN)
            path.write_text('{"formatVersion":1,"formatVersion":1,"releaseId":"2026.11.1",'
                            '"manifestSha256":"' + "a" * 64 + '"}', encoding="utf-8")
            with self.assertRaises(consumer.ContractError):
                consumer.load_lock(path)
            path.write_text(json.dumps({**PIN, "revision": ORIGIN}), encoding="utf-8")
            with self.assertRaises(consumer.ContractError):
                consumer.load_lock(path)

    def test_standalone_contract_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            export = base / "course.json"
            lock = base / "oee-curriculum.lock.json"
            mapping = base / "map.json"
            export.write_text(json.dumps(valid_export()), encoding="utf-8")
            lock.write_text(json.dumps(PIN), encoding="utf-8")
            mapping.write_text(json.dumps(valid_map()), encoding="utf-8")
            cmd = [sys.executable, str(SCRIPT), "--export", str(export),
                   "--lock", str(lock), "--map", str(mapping), "--json"]
            good = subprocess.run(cmd, capture_output=True, text=True, check=False)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertEqual(json.loads(good.stdout)["releaseId"], PIN["releaseId"])
            wrong = json.loads(json.dumps(valid_export()))
            wrong["source"]["manifestSha256"] = "f" * 64
            export.write_text(json.dumps(wrong), encoding="utf-8")
            bad = subprocess.run(cmd, capture_output=True, text=True, check=False)
            self.assertEqual(bad.returncode, 1)


if __name__ == "__main__":
    unittest.main()
