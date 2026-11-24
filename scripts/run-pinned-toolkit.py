"""Run the reviewed installed Toolkit without cwd or PYTHONPATH imports."""
from __future__ import annotations

import importlib.metadata
import importlib.util
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
APPROVED = {
    "formatVersion": 1, "toolVersion": "0.2.0",
    "ruleSetVersion": "v0.2.0-ot-i04", "exportVersion": 2,
    "contextVersion": 1,
    "wheelSha256": "933d82a09f8ca01930a9a4e76b1bb399f2d10a940783a3bc6a39e7b5e9dc46f3",
    "stewardKeySha256": "0cbd8335bf39fab19b17a7bfaa33502d121d007fca4bddd5df0f43a9c814e2ef",
}


def unique_keys(pairs):
    data = {}
    for key, value in pairs:
        if key in data:
            raise ValueError("duplicate JSON property: " + key)
        data[key] = value
    return data


def selection():
    path = ROOT / "oee-toolkit.lock.json"
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 4096:
        raise ValueError("missing or unsafe Toolkit selection")
    data = json.loads(path.read_bytes().decode("utf-8"), object_pairs_hook=unique_keys)
    if data != APPROVED or any(type(data[k]) is not int for k in
                               ("formatVersion", "exportVersion", "contextVersion")):
        raise ValueError("unapproved Toolkit selection")
    return data


def verify_toolkit():
    pin = selection()
    if not sys.flags.isolated:
        raise ValueError("Toolkit requires isolated Python (-I)")
    dist = importlib.metadata.distribution("oee-toolkit")
    if dist.version != pin["toolVersion"]:
        raise ValueError("installed Toolkit distribution version mismatch")
    spec = importlib.util.find_spec("oee_toolkit")
    expected = Path(dist.locate_file("oee_toolkit/__init__.py")).resolve()
    if spec is None or spec.origin is None or Path(spec.origin).resolve() != expected:
        raise ValueError("installed Toolkit module does not belong to distribution")
    import oee_toolkit
    from oee_toolkit.core import RULE_SET_VERSION
    if oee_toolkit.__version__ != pin["toolVersion"] or RULE_SET_VERSION != pin["ruleSetVersion"]:
        raise ValueError("installed Toolkit module version mismatch")


if __name__ == "__main__":
    try:
        verify_toolkit()
    except (ValueError, OSError, ImportError) as exc:
        print("Toolkit identity rejected: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
    runpy.run_module("oee_toolkit", run_name="__main__", alter_sys=True)
