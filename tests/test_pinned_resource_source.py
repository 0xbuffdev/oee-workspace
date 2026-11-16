"""WS-I01: verify revision-pinned OEE Toolkit exports without a legacy reader."""
from __future__ import annotations

import copy
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PIN = "cf7903f701582c7a1a3933d1eb65df0289e8a6aa"
OEE = Path(os.environ.get("OEE_REPO", str(ROOT / "_oee"))).resolve()
SPEC = importlib.util.spec_from_file_location(
    "workspace_pinned_resources", ROOT / "scripts" / "check-resources.py"
)
checker = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)


def unmapped(export):
    src, code = export["source"], export["course"]["code"]
    return {
        "schemaVersion": 2, "status": "draft",
        "curriculum": {
            "repository": src["repository"],
            "revision": src["revision"],
            "specification": src["specification"],
            "course": code, "path": src["coursePath"],
        },
        "modules": [
            {"number": item["number"], "title": item["title"],
             "coverage": "unmapped", "gap": "Source references require editorial review",
             "resources": []}
            for item in export["modules"]
        ],
    }


class SourceFailureTests(unittest.TestCase):
    def test_unknown_checkout_is_source_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(checker.PinnedSourceError) as caught:
                checker.read_pinned_export(Path(directory) / "not-a-checkout",
                                           PIN, "SEF1")
            self.assertEqual(caught.exception.category, "source_missing")

    def test_short_sha_and_branch_name_rejected(self):
        for ref in ("HEAD", "main", "a" * 7, "A" * 40):
            with self.subTest(ref=ref):
                with self.assertRaises(checker.PinnedSourceError) as caught:
                    checker.read_pinned_export(Path("."), ref, "SEF1")
                self.assertEqual(caught.exception.category, "unsupported_format")

    def test_unsupported_schema_is_not_converted(self):
        legacy = checker.load_json(
            ROOT / "tests" / "fixtures" / "resource-map-v1-SEF1.json",
            checker.Check(),
        )
        findings = checker.Check()
        self.assertFalse(checker.validate_map_shape(legacy, {}, findings, "legacy"))
        self.assertIn("unsupported_schema", findings.errors[0])

    def test_validator_has_one_markdown_parser_and_no_export_override(self):
        body = (ROOT / "scripts" / "check-resources.py").read_text(encoding="utf-8")
        self.assertNotIn("COURSE_MODULE =", body)
        self.assertNotIn('parser.add_argument("--export"', body)
        self.assertIn("tooling.oee_toolkit", body)


@unittest.skipUnless(
    (OEE / "tooling" / "oee_toolkit" / "__main__.py").is_file(),
    "needs local canonical OEE Toolkit checkout; resource CI supplies _oee",
)
class RealPinnedToolkitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.export = checker.read_pinned_export(OEE, PIN, "SEF1")
        cls.map = unmapped(cls.export)

    def test_map_matches_actual_pinned_source(self):
        findings = checker.Check()
        self.assertTrue(checker.validate_map_shape(self.map, {}, findings, "SEF1"),
                        findings.errors)
        validated = checker.check_pinned_map(self.map, OEE)
        self.assertEqual(validated["source"]["revision"], PIN)
        self.assertEqual(validated["course"], "SEF1")

    def test_selected_commit_missing_does_not_fall_back_to_head(self):
        altered = copy.deepcopy(self.map)
        altered["curriculum"]["revision"] = "f" * 40
        with self.assertRaises(checker.PinnedSourceError) as caught:
            checker.check_pinned_map(altered, OEE)
        self.assertEqual(caught.exception.category, "source_missing")

        with tempfile.TemporaryDirectory(dir=ROOT / "resources") as folder:
            maps = Path(folder)
            path = maps / "SEF" / "SEF1.json"
            path.parent.mkdir()
            import json
            path.write_text(json.dumps(altered), encoding="utf-8")
            with patch.object(checker, "MAPPINGS", maps):
                result = checker.Check()
                checker.validate_maps({}, result, "SEF1", OEE)
                self.assertEqual(result.errors, [])
                self.assertEqual(len(result.incomplete), 1)
                self.assertIn("source_missing", result.incomplete[0])

    def test_module_and_outcome_changes_are_rejected(self):
        broken = copy.deepcopy(self.map)
        broken["modules"][0]["title"] = "Different course topic"
        with self.assertRaisesRegex(checker.load_consumer().ContractError, "locator"):
            checker.check_pinned_map(broken, OEE)

        broken = copy.deepcopy(self.map)
        item = broken["modules"][0]
        item.update(coverage="partial", resources=[{
            "resource": "R1", "role": "optional", "purpose": "Synthetic test",
            "verification": "review-needed",
            "part": {"type": "topics", "titles": ["Topic"]},
            "outcomeIds": ["SEF1-O9999"], "assessmentIds": ["SEF1-AS9999"],
        }])
        with self.assertRaisesRegex(checker.load_consumer().ContractError, "unknown canonical"):
            checker.check_pinned_map(broken, OEE)

    def test_pinned_results_ignore_new_head_and_dirty_worktree(self):
        with tempfile.TemporaryDirectory() as folder:
            copied = Path(folder) / "oee"
            clone = subprocess.run(
                ["git", "clone", "--local", "--quiet", str(OEE), str(copied)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(clone.returncode, 0, clone.stderr)
            changed = subprocess.run([
                "git", "-C", str(copied),
                "-c", "user.name=Test",
                "-c", "user.email=test@example.invalid",
                "commit", "--quiet", "--allow-empty", "-m", "new moving head",
            ], capture_output=True, text=True, check=False)
            self.assertEqual(changed.returncode, 0, changed.stderr)
            current = subprocess.run(
                ["git", "-C", str(copied), "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True,
            ).stdout.strip()
            self.assertNotEqual(current, PIN)
            (copied / "curriculum" / "SEF" / "SEF1.md").write_text(
                "Dirty worktree must not affect the pinned course.",
                encoding="utf-8",
            )
            self.assertEqual(checker.read_pinned_export(copied, PIN, "SEF1"),
                             self.export)
            self.assertEqual(checker.check_pinned_map(self.map, copied)["source"]["revision"],
                             PIN)

    def test_unsupported_old_course_format_and_unknown_course(self):
        old = subprocess.run(
            ["git", "-C", str(OEE), "rev-parse", "v0.1.0^{commit}"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(old.returncode, 0, old.stderr)
        with self.assertRaises(checker.PinnedSourceError) as caught:
            checker.read_pinned_export(OEE, old.stdout.strip(), "SEF1")
        self.assertIn(caught.exception.category, {"source_missing", "unsupported_format"})
        with self.assertRaises(checker.PinnedSourceError) as missing:
            checker.read_pinned_export(OEE, PIN, "SEF9999")
        self.assertEqual(missing.exception.category, "source_missing")


if __name__ == "__main__":
    unittest.main()
