"""REL-I04: Toolkit release subprocess boundary, with deterministic mocked exports."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_toolkit_consumer import PIN, valid_export, valid_map

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("workspace_release_checker",
                                                ROOT / "scripts/check-resources.py")
checker = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = checker
spec.loader.exec_module(checker)


class OfflineReleaseSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.lock = Path(self.temp.name) / "oee-curriculum.lock.json"
        self.lock.write_text(json.dumps(PIN), encoding="utf-8")
        self.store = Path(self.temp.name) / "store"
        self.store.mkdir()

    def mock_export(self, returncode=0, output=None, error=b""):
        encoded = json.dumps(valid_export()).encode("utf-8") if output is None else output
        return subprocess.CompletedProcess([], returncode, stdout=encoded, stderr=error)

    def test_only_installed_offline_toolkit_and_explicit_store(self):
        with patch.object(checker.subprocess, "run", return_value=self.mock_export()) as run:
            exported = checker.read_pinned_export(self.lock, self.store, "SEF1")
        self.assertEqual(exported["exportVersion"], 2)
        argv = run.call_args.args[0]
        self.assertEqual(argv[:4], [sys.executable, "-m", "oee_toolkit", "export"])
        self.assertEqual(argv[4], "SEF1")
        self.assertIn("--lock", argv)
        self.assertIn("--store", argv)
        self.assertIn("--output", argv)
        self.assertNotIn("--repo", argv)
        self.assertNotIn("--revision", argv)

    def test_full_release_identity_matches_reviewed_lock(self):
        with patch.object(checker.subprocess, "run", return_value=self.mock_export()):
            export = checker.check_pinned_map(valid_map(), self.lock, self.store)
        self.assertEqual(export["source"]["manifestSha256"], PIN["manifestSha256"])

    def test_missing_or_unsupported_installed_release_is_not_fallback(self):
        for rc in (2, 3):
            with patch.object(checker.subprocess, "run",
                              return_value=self.mock_export(rc, b"", b"missing release")):
                with self.assertRaises(checker.PinnedSourceError) as error:
                    checker.read_pinned_export(self.lock, self.store, "SEF1")
                self.assertIn(error.exception.category, ("unsupported_format", "source_missing"))

    def test_missing_store_and_lock_digest_have_distinct_diagnostics(self):
        cases = (
            (b"invalid_release: trusted release store is missing or symlinked",
             "store_missing", "check --store"),
            (b"invalid_release: pinned curriculum release is not installed",
             "lock_digest_not_found", PIN["manifestSha256"]),
        )
        for stderr, category, hint in cases:
            with self.subTest(category=category):
                with patch.object(checker.subprocess, "run",
                                  return_value=self.mock_export(3, b"", stderr)):
                    with self.assertRaises(checker.PinnedSourceError) as caught:
                        checker.read_pinned_export(self.lock, self.store, "SEF1")
                self.assertEqual(caught.exception.category, category)
                self.assertIn(hint, str(caught.exception))
        # Unexpected Toolkit exit-three errors remain explicitly incomplete.
        with patch.object(checker.subprocess, "run",
                          return_value=self.mock_export(
                              3, b"", b"invalid_release: source bytes altered"
                          )):
            with self.assertRaises(checker.PinnedSourceError) as caught:
                checker.read_pinned_export(self.lock, self.store, "SEF1")
        self.assertEqual(caught.exception.category, "source_missing")

    def test_malformed_toolkit_json_cannot_be_used(self):
        with patch.object(checker.subprocess, "run",
                          return_value=self.mock_export(0, b'{"exportVersion":')):
            with self.assertRaises(checker.PinnedSourceError):
                checker.read_pinned_export(self.lock, self.store, "SEF1")

    def test_map_wrong_manifest_refused_even_with_valid_export(self):
        mapping = valid_map()
        mapping["curriculum"]["manifestSha256"] = "e" * 64
        with patch.object(checker.subprocess, "run", return_value=self.mock_export()):
            with self.assertRaises(checker.load_consumer().ContractError):
                checker.check_pinned_map(mapping, self.lock, self.store)

    def test_missing_lock_fails_before_any_source_fallback(self):
        self.lock.unlink()
        with patch.object(checker.subprocess, "run", return_value=self.mock_export()):
            with self.assertRaises(checker.load_consumer().ContractError):
                checker.check_pinned_map(valid_map(), self.lock, self.store)

    def test_default_resources_check_is_catalog_only_while_unpublished(self):
        with patch.object(checker, "MAPPINGS", Path(self.temp.name) / "empty"):
            found = checker.Check()
            checker.validate_maps({}, found)
        self.assertEqual(found.errors, [])
        self.assertEqual(found.incomplete, [])

    def test_no_implicit_external_network_calls_or_git_source(self):
        src = (ROOT / "scripts/check-resources.py").read_text(encoding="utf-8")
        self.assertNotIn('["git"', src)
        self.assertNotIn('"-C",', src)
        self.assertNotIn('"--repo"', src)
        self.assertNotIn('"--revision"', src)


if __name__ == "__main__":
    unittest.main()
