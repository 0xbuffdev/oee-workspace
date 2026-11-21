"""REL-I04: current-only, no-Git learner CLI against synthetic Toolkit v2 contracts."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from oee_workspace import __main__ as cli
from oee_workspace import evidence as ev
from test_evidence_operations import FakeReader
from test_toolkit_consumer import PIN


class ReleaseCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "learner"
        self.root.mkdir()
        self.lock = Path(self.temp.name) / "oee-curriculum.lock.json"
        self.lock.write_text(json.dumps(PIN), encoding="utf-8")
        self.reader_patch = patch.object(ev, "load_reader", return_value=FakeReader)
        self.reader_patch.start()
        self.addCleanup(self.reader_patch.stop)

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli.main([*args])
        return code, out.getvalue(), err.getvalue()

    def selection(self):
        return ["--lock", str(self.lock)]

    def test_doctor_uses_release_identity_without_git_checkout(self):
        code, out, err = self.run_cli("doctor", *self.selection())
        self.assertEqual(code, 0, err)
        self.assertIn(PIN["releaseId"], out)
        self.assertIn("offline", out.lower())

    def test_old_revision_and_oee_flags_not_supported(self):
        with self.assertRaises(SystemExit) as e:
            cli.parser().parse_args(["doctor", "--revision", "a" * 40])
        self.assertEqual(e.exception.code, 2)
        with self.assertRaises(SystemExit):
            cli.parser().parse_args(["doctor", "--oee", "../open-engineering-education"])

    def test_missing_reviewed_lock_is_incomplete(self):
        self.lock.unlink()
        code, _, err = self.run_cli("doctor", *self.selection())
        self.assertEqual(code, 3, err)
        self.assertIn("WSE003", err)

    def test_course_add_never_replaces_learner_files(self):
        args = ("course", "add", "SEF1", *self.selection(), "--dest", str(self.root))
        code, out, err = self.run_cli(*args)
        self.assertEqual(code, 0, err)
        self.assertIn("No public resource map exists", out)
        notes = self.root / "notes/SEF/SEF1"
        self.assertFalse((notes / "reading-plan.md").exists())
        resources = notes / "resources.md"
        resources.write_text("learner notes", encoding="utf-8")
        code, _, _ = self.run_cli(*args)
        self.assertEqual(code, 1)
        self.assertEqual(resources.read_text(), "learner notes")

    def test_unknown_course_code_rejected_before_writes(self):
        code, _, _ = self.run_cli("course", "add", "wrong-code", *self.selection(),
                                  "--dest", str(self.root))
        self.assertEqual(code, 1)
        self.assertFalse((self.root / "labs/SEF").exists())

    def test_evidence_init_check_status_and_export(self):
        args = ("evidence", "init", *self.selection(), "--dest", str(self.root),
                "--course", "SEF1", "--assessment", "SEF1-AS1")
        code, out, err = self.run_cli(*args)
        self.assertEqual(code, 0, err)
        attempts = sorted((self.root / "evidence/SEF/SEF1/SEF1-AS1").glob("*.json"))
        self.assertEqual(len(attempts), 1)
        attempt = json.loads(attempts[0].read_text())
        self.assertEqual(attempt["schemaVersion"], 2)
        self.assertEqual(attempt["course"]["releaseId"], PIN["releaseId"])
        self.assertIsNone(attempt["evaluation"])
        code, out, err = self.run_cli("evidence", "check", *self.selection(),
                                      "--dest", str(self.root), "--path", str(attempts[0]))
        self.assertEqual(code, 0, err)
        code, out, err = self.run_cli("status", *self.selection(),
                                      "--dest", str(self.root), "--course", "SEF1")
        self.assertEqual(code, 0, err)
        self.assertIn("Completion: not determined", out)
        output = "evidence-export.json"
        code, out, err = self.run_cli("export", *self.selection(), "--dest", str(self.root),
                                      "--attempt", attempt["attemptId"], "--output", output)
        self.assertEqual(code, 0, err)
        bundle = json.loads((self.root / output).read_text())
        self.assertEqual(bundle["exportVersion"], 2)
        self.assertEqual(bundle["records"][0]["attempt"]["course"]["manifestSha256"],
                         PIN["manifestSha256"])
        code, _, _ = self.run_cli("export", *self.selection(), "--dest", str(self.root),
                                  "--attempt", attempt["attemptId"], "--output", output)
        self.assertEqual(code, 1)

    def test_resources_check_rejects_non_release_map(self):
        path = self.root / "map.json"
        path.write_text('{"schemaVersion":2}', encoding="utf-8")
        code, _, err = self.run_cli("resources", "check", *self.selection(), "--map", str(path))
        self.assertEqual(code, 1, err)


if __name__ == "__main__":
    unittest.main()
