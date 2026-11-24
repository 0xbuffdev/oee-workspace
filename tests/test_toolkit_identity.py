"""Software selection and module/distribution identity rejection."""
import json
from pathlib import Path
import runpy
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
module = runpy.run_path(str(ROOT / "scripts/run-pinned-toolkit.py"))
selection = module["selection"]
verify = module["verify_toolkit"]


class ToolkitIdentityTests(unittest.TestCase):
    def test_reviewed_selection(self):
        self.assertEqual(selection()["toolVersion"], "0.2.0")

    def test_changed_or_ambiguous_selection(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "oee-toolkit.lock.json"
            original = selection()
            with patch.dict(selection.__globals__, {"ROOT": Path(folder)}):
                for data in (
                    json.dumps({**original, "toolVersion": "0.1.0"}),
                    json.dumps({**original, "contextVersion": True}),
                    '{"formatVersion":1,' + json.dumps(original)[1:],
                    json.dumps({**original, "wheelSha256": "f" * 64}),
                ):
                    path.write_text(data, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        selection()

    def test_wrong_distribution_and_module_origin(self):
        with patch.object(module["sys"], "flags", SimpleNamespace(isolated=1)):
            with patch.object(module["importlib"].metadata, "distribution",
                              return_value=SimpleNamespace(version="0.1.0")):
                with self.assertRaisesRegex(ValueError, "distribution version"):
                    verify()
            dist = SimpleNamespace(version="0.2.0", locate_file=lambda p: ROOT / p)
            with (patch.object(module["importlib"].metadata, "distribution", return_value=dist),
                  patch.object(module["importlib"].util, "find_spec",
                               return_value=SimpleNamespace(origin=str(ROOT / "wrong.py")))):
                with self.assertRaisesRegex(ValueError, "does not belong"):
                    verify()
