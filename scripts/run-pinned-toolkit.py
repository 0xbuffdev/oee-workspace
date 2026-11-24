"""Run the reviewed installed Toolkit without cwd or PYTHONPATH imports."""
from __future__ import annotations

import argparse
import hashlib
import re
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {"formatVersion", "toolVersion", "ruleSetVersion", "exportVersion",
          "contextVersion", "wheelSha256", "wheelSize", "sdistSha256",
          "sdistSize", "stewardKeySha256"}


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
    if (type(data) is not dict or set(data) != FIELDS or
            any(type(data[k]) is not int or data[k] != expected
                for k, expected in (("formatVersion", 1), ("exportVersion", 2),
                                    ("contextVersion", 1))) or
            any(type(data[k]) is not str or not re.fullmatch(pattern, data[k])
                for k, pattern in (("toolVersion", r"[0-9]+\.[0-9]+\.[0-9]+"),
                                   ("ruleSetVersion", r"v[0-9]+\.[0-9]+\.[0-9]+-[a-z0-9-]+"),
                                   ("wheelSha256", r"[0-9a-f]{64}"),
                                   ("sdistSha256", r"[0-9a-f]{64}"),
                                   ("stewardKeySha256", r"[0-9a-f]{64}"))) or
            any(type(data[k]) is not int or not 0 < data[k] <= 16 * 1024 * 1024
                for k in ("wheelSize", "sdistSize"))):
        raise ValueError("invalid or unsupported Toolkit selection")
    return data


def software_assets(pin):
    version = pin["toolVersion"]
    return {
        f"oee_toolkit-{version}-py3-none-any.whl": (pin["wheelSize"], pin["wheelSha256"]),
        f"oee_toolkit-{version}.tar.gz": (pin["sdistSize"], pin["sdistSha256"]),
    }


def verified_asset(path, size, sha):
    if path.is_symlink() or not path.is_file() or path.stat().st_size != size:
        raise ValueError("missing or incorrect official asset size: " + path.name)
    data = path.read_bytes()
    if len(data) != size or hashlib.sha256(data).hexdigest() != sha:
        raise ValueError("official SHA-256 mismatch: " + path.name)
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


def manifest():
    parser = argparse.ArgumentParser()
    parser.add_argument("course")
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--store", type=Path)
    parser.add_argument("--output", choices=["-"], required=True)
    args = parser.parse_args(sys.argv[2:])
    from oee_toolkit.release_source import resolve_release
    from oee_toolkit.core import canonical_json
    source = resolve_release(args.lock, args.store)
    sys.stdout.buffer.write(canonical_json(source.manifest))


if __name__ == "__main__":
    try:
        if sys.argv[1:2] == ["--selected-version"]:
            print(selection()["toolVersion"])
            raise SystemExit(0)
        if sys.argv[1:2] == ["--verify-wheel"]:
            path = Path(sys.argv[2])
            pin = selection()
            name = f"oee_toolkit-{pin['toolVersion']}-py3-none-any.whl"
            if path.name != name:
                raise ValueError("unexpected Toolkit wheel filename")
            verified_asset(path, *software_assets(pin)[name])
            raise SystemExit(0)
        verify_toolkit()
        if sys.argv[1:2] == ["manifest"]:
            manifest()
            raise SystemExit(0)
    except (ValueError, OSError, ImportError, IndexError) as exc:
        print("Toolkit identity rejected: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
    runpy.run_module("oee_toolkit", run_name="__main__", alter_sys=True)
