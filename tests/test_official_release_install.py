"""Negative and lock-contract checks for the official offline release installer."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/install-official-curriculum.py"
spec = importlib.util.spec_from_file_location("official_release_installer", SCRIPT)
assert spec is not None and spec.loader is not None
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class OfficialReleaseInstallerTests(unittest.TestCase):
    def test_committed_immutable_lock_is_exactly_approved(self):
        installer.validate_lock(SCRIPT.parents[1] / "oee-curriculum.lock.json")

    def test_refuses_wrong_digest_and_unsupported_lock(self):
        with tempfile.TemporaryDirectory() as folder:
            lock = Path(folder) / "lock.json"
            for data in (
                {"formatVersion": 1, "releaseId": "2026.11.1",
                 "manifestSha256": "f" * 64},
                {"formatVersion": 1, "releaseId": "2026.11.2",
                 "manifestSha256": installer.MANIFEST_SHA256},
                {"formatVersion": True, "releaseId": "2026.11.1",
                 "manifestSha256": installer.MANIFEST_SHA256},
                {"formatVersion": 1.0, "releaseId": "2026.11.1",
                 "manifestSha256": installer.MANIFEST_SHA256},
                {"formatVersion": 2, "releaseId": "2026.11.1",
                 "manifestSha256": installer.MANIFEST_SHA256},
                {"formatVersion": 1, "releaseId": "2026.11.1"},
            ):
                lock.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaises(ValueError):
                    installer.validate_lock(lock)

    def test_refuses_ambiguous_json_lock(self):
        with tempfile.TemporaryDirectory() as folder:
            lock = Path(folder) / "lock.json"
            lock.write_text(
                '{"formatVersion":1,"releaseId":"2026.11.1",'
                '"releaseId":"2026.11.1","manifestSha256":"'
                + installer.MANIFEST_SHA256 + '"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                installer.validate_lock(lock)

    def test_missing_release_files_cannot_be_trusted(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "official asset"):
                installer.read_and_hash_assets(Path(folder))

    def test_rejects_same_size_but_wrong_archive_checksum(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, (size, _) in installer.asset_specs().items():
                (root / name).write_bytes(b"x" * size)
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                installer.read_and_hash_assets(root)


if __name__ == "__main__":
    unittest.main()
