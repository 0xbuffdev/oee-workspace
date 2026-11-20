"""WS-I08: offline Python CLI smoke tests using real immutable OEE Toolkit exports."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from oee_workspace import EvidenceService
from oee_workspace import local
from oee_workspace.__main__ import main as cli_main

ROOT = Path(__file__).resolve().parents[1]
OEE = Path(os.environ.get("OEE_REPO", ROOT / "_oee")).resolve()
PIN = "67416343f3eab17ada5d3c79ae6cc782524c29ff"


def enabled():
    return (OEE / "tooling" / "oee_toolkit" / "__main__.py").is_file()


class CliParserTests(unittest.TestCase):
    def test_standard_module_entry_point_and_usage_codes(self):
        for args in ([], ["course"], ["course", "add"],
                     ["doctor", "--oee", str(OEE)]):
            with self.subTest(args=args):
                result = subprocess.run(
                    [sys.executable, "-m", "oee_workspace", *args],
                    cwd=ROOT, capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, 2)
        result = subprocess.run(
            [sys.executable, "-m", "oee_workspace", "--help"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0)
        for command in ("doctor", "course", "resources", "evidence", "status", "export"):
            self.assertIn(command, result.stdout)

    def test_unreviewed_and_different_revision_maps_do_not_publish(self):
        import oee_workspace.__main__ as cli_module
        with tempfile.TemporaryDirectory() as name:
            base = Path(name)
            mapping_file = base / "SEF" / "SEF1.json"
            mapping_file.parent.mkdir()
            mapping = {
                "schemaVersion": 2, "status": "draft",
                "curriculum": {"course": "SEF1", "specification": "v0.2.0",
                               "revision": PIN},
            }
            with patch.object(cli_module, "MAPS", base):
                mapping_file.write_text(json.dumps(mapping), encoding="utf-8")
                guide, reason = cli_module.study_guide("SEF1", PIN, OEE)
                self.assertIsNone(guide)
                self.assertIn("not reviewed", reason)
                mapping["status"] = "reviewed"
                mapping_file.write_text(json.dumps(mapping), encoding="utf-8")
                guide, reason = cli_module.study_guide("SEF1", "f" * 40, OEE)
                self.assertIsNone(guide)
                self.assertIn("another source commit", reason)

    def test_atomic_no_clobber_file_publishing(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            rel = Path("evidence") / "sample.json"
            result = local.publish_file_new(root, rel, b"first\n")
            self.assertEqual(result.read_bytes(), b"first\n")
            with self.assertRaises(local.PublicationError):
                local.publish_file_new(root, rel, b"overwrite")
            self.assertEqual(result.read_bytes(), b"first\n")
            with patch.object(local.os, "link", side_effect=OSError("injected")):
                with self.assertRaises(local.PublicationError):
                    local.publish_file_new(root, Path("output.json"), b"not published")
            self.assertFalse((root / "output.json").exists())
            self.assertEqual(list(root.glob(".output.json.*.tmp")), [])

    def test_reject_symlinked_output_directory(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            target = root / "safe"
            target.mkdir()
            outside = root / "redirect"
            try:
                outside.symlink_to(target, target_is_directory=True)
            except OSError:
                self.skipTest("this platform account cannot create symlinks")
            with self.assertRaises(local.PublicationError):
                local.publish_file_new(root, Path("redirect") / "leak.json", b"private")
            self.assertFalse((target / "leak.json").exists())


@unittest.skipUnless(enabled(), "requires trusted local OEE Toolkit checkout, provided by CI")
class RealCliFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "learner"
        self.root.mkdir()

    def call(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            result = cli_main(list(args))
        return result, out.getvalue(), err.getvalue()

    def base(self):
        return ("--oee", str(OEE))

    def pinned(self):
        return (*self.base(), "--revision", PIN)

    def dest(self):
        return ("--dest", str(self.root))

    def test_doctor_checks_real_pinned_toolkit(self):
        code, out, err = self.call("doctor", *self.pinned())
        self.assertEqual(code, 0, err)
        self.assertIn("first-party", out)
        self.assertIn(PIN, out)
        code, _, err = self.call("doctor", *self.base(), "--revision", "f" * 40)
        self.assertEqual(code, 3)
        self.assertIn("WSE003", err)

    def test_course_add_unmapped_and_repeat_refused(self):
        code, out, err = self.call(
            "course", "add", "SEF2", *self.pinned(), *self.dest())
        self.assertEqual(code, 0, err)
        notes = self.root / "notes" / "SEF" / "SEF2"
        self.assertTrue((notes / "summary.md").is_file())
        self.assertFalse((notes / "reading-plan.md").exists())
        self.assertIn("No public resource map", out)
        (notes / "resources.md").write_text("learner-owned evidence", encoding="utf-8")
        code, _, err = self.call(
            "course", "add", "SEF2", *self.pinned(), *self.dest())
        self.assertEqual(code, 1)
        self.assertIn("WSC004", err)
        self.assertEqual((notes / "resources.md").read_text(), "learner-owned evidence")

    def test_course_add_reviewed_map_uses_exact_commit(self):
        code, out, err = self.call(
            "course", "add", "SEF1", *self.pinned(), *self.dest())
        self.assertEqual(code, 0, err)
        guide = self.root / "notes" / "SEF" / "SEF1" / "reading-plan.md"
        expected = ROOT / "resources" / "guides" / "SEF" / "SEF1.md"
        # Git may check out the committed Markdown with CRLF on Windows.
        # Compare its logical text; the renderer itself always emits LF.
        self.assertEqual(guide.read_text(encoding="utf-8"),
                         expected.read_text(encoding="utf-8"))
        self.assertIn("Reviewed", out)
        self.assertIn(PIN, guide.read_text(encoding="utf-8"))

    def test_project_type_discovered_from_toolkit_not_alias(self):
        code, out, err = self.call(
            "course", "add", "SEF10", *self.pinned(), *self.dest())
        self.assertEqual(code, 0, err)
        brief = self.root / "projects" / "SEF10" / "BRIEF.md"
        self.assertIn(PIN, brief.read_text())
        self.assertTrue((self.root / "projects" / "SEF10" / "docs" / "design.md").exists())
        self.assertTrue((self.root / "notes" / "SEF" / "SEF10" / "summary.md").exists())
        code, _, _ = self.call("course", "add", "ledgerlab", *self.pinned(), *self.dest())
        self.assertEqual(code, 1)
        self.assertFalse((self.root / "projects" / "ledgerlab").exists())

    def test_missing_revision_and_unsupported_code_cannot_write(self):
        code, _, err = self.call(
            "course", "add", "SEF1", *self.base(), "--revision", "f"*40,
            *self.dest())
        self.assertEqual(code, 3)
        self.assertFalse((self.root / "notes" / "SEF" / "SEF1").exists())
        code, _, err = self.call(
            "course", "add", "SEF9999", *self.pinned(), *self.dest())
        self.assertNotEqual(code, 0)
        self.assertFalse((self.root / "notes" / "SEF" / "SEF9999").exists())

    def test_resources_check_pinned_map_and_no_compatibility(self):
        mapping = ROOT / "resources" / "mappings" / "SEF" / "SEF1.json"
        code, out, err = self.call(
            "resources", "check", *self.base(), "--map", str(mapping))
        self.assertEqual(code, 0, err)
        self.assertIn("reviewed", out)
        historical = ROOT / "tests" / "fixtures" / "resource-map-v1-SEF1.json"
        code, _, err = self.call(
            "resources", "check", *self.base(), "--map", str(historical))
        self.assertEqual(code, 1)
        self.assertIn("WSC005", err)

    def create_attempt(self):
        directory = self.root / "evidence" / "SEF" / "SEF1" / "SEF1-AS1"
        before = set(directory.glob("*.json")) if directory.exists() else set()
        code, out, err = self.call(
            "evidence", "init", *self.pinned(), "--course", "SEF1",
            "--assessment", "SEF1-AS1", *self.dest())
        self.assertEqual(code, 0, err)
        added = set(directory.glob("*.json")) - before
        self.assertEqual(len(added), 1)
        return added.pop(), out

    def test_evidence_init_check_status_and_export_end_to_end(self):
        first, _ = self.create_attempt()
        second, _ = self.create_attempt()
        self.assertNotEqual(first, second)
        a = json.loads(first.read_text())
        b = json.loads(second.read_text())
        self.assertNotEqual(a["attemptId"], b["attemptId"])
        self.assertIsNone(a["evaluation"])
        self.assertEqual(a["outcomeIds"], ["SEF1-O1", "SEF1-O2"])
        code, out, err = self.call(
            "evidence", "check", *self.base(), "--path", str(first),
            *self.dest())
        self.assertEqual(code, 0, err)
        self.assertIn("attempt-recorded", out)

        progress = self.root / "progress.md"
        progress.write_text("private learner notes", encoding="utf-8")
        code, out, err = self.call("status", *self.base(), *self.dest())
        self.assertEqual(code, 0, err)
        self.assertIn("SEF1-AS1", out)
        self.assertIn("outstanding required decisions", out)
        self.assertEqual(progress.read_text(), "private learner notes")

        code, out, err = self.call(
            "export", *self.base(), *self.dest(),
            "--attempt", a["attemptId"], "--output", "exports/selected.json")
        self.assertEqual(code, 0, err)
        export = json.loads((self.root / "exports" / "selected.json").read_text())
        self.assertEqual(len(export["records"]), 1)
        self.assertEqual(export["records"][0]["attempt"]["attemptId"], a["attemptId"])
        self.assertNotIn(b["attemptId"], json.dumps(export))
        self.assertNotIn("private learner notes", json.dumps(export))
        code, _, err = self.call(
            "export", *self.base(), *self.dest(),
            "--attempt", a["attemptId"], "--output", "exports/selected.json")
        self.assertEqual(code, 1)
        self.assertIn("WSC004", err)

    def test_evidence_init_rejects_optional_or_unknown_assessment(self):
        code, _, err = self.call(
            "evidence", "init", *self.pinned(), "--course", "SEF1",
            "--assessment", "SEF1-AS999", *self.dest())
        self.assertEqual(code, 1)
        self.assertIn("WSC005", err)
        self.assertFalse((self.root / "evidence").exists())

    def test_empty_status_with_explicit_source(self):
        code, out, err = self.call(
            "status", *self.base(), *self.dest(),
            "--course", "SEF1", "--revision", PIN)
        self.assertEqual(code, 0, err)
        self.assertIn("no-evidence", out)
        self.assertIn("Completion: not determined", out)

    def test_invalid_local_artifact_and_bad_hash_are_not_passed(self):
        from oee_workspace.evidence import record_shape
        first, _ = self.create_attempt()
        data = json.loads(first.read_text())
        data["artifacts"] = [{
            "kind": "relative-path", "value": "labs/SEF/SEF1/missing.txt",
            "sha256": "0" * 64,
        }]
        record_shape(data)
        first.write_text(json.dumps(data), encoding="utf-8")
        code, _, err = self.call("evidence", "check", *self.base(),
                                 "--path", str(first), *self.dest())
        self.assertEqual(code, 3)
        self.assertIn("WSE003", err)
        artifact = self.root / "labs" / "SEF" / "SEF1" / "missing.txt"
        artifact.parent.mkdir(parents=True)
        artifact.write_text("tampered", encoding="utf-8")
        code, _, err = self.call("evidence", "check", *self.base(),
                                 "--path", str(first), *self.dest())
        self.assertEqual(code, 1)
        self.assertIn("WSE007", err)

    def test_export_refuses_external_path_and_suspected_secret(self):
        first, _ = self.create_attempt()
        ident = json.loads(first.read_text())["attemptId"]
        code, _, err = self.call(
            "export", *self.base(), *self.dest(),
            "--attempt", ident,
            "--output", str(Path(self.temp.name) / "outside.json"))
        self.assertEqual(code, 1)
        self.assertIn("WSC004", err)
        data = json.loads(first.read_text())
        data["observations"] = [{"kind": "self-note", "summary":
                                 "api_key = very-private-key"}]
        first.write_text(json.dumps(data), encoding="utf-8")
        code, _, err = self.call(
            "export", *self.base(), *self.dest(),
            "--attempt", ident, "--output", "exports/blocked.json")
        self.assertEqual(code, 1)
        self.assertIn("WSC010", err)
        self.assertFalse((self.root / "exports" / "blocked.json").exists())


if __name__ == "__main__":
    unittest.main()
