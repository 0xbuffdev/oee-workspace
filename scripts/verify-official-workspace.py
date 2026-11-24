#!/usr/bin/env python3
"""Independent Workspace acceptance against the REAL public OEE signed release.

No fixture signer, Git source checkout, learner files, secrets, hosted grading
or network fetch inside this test. GitHub Actions acquires audited release
assets first; this script requires those local assets and the official wheel.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

RELEASE = "2026.11.1"
MANIFEST_SHA256 = "57441494eb69c2ff9cb3f6029c8adc3c6a56f8c6ecabc43196c9b686e5959a6c"
FINGERPRINT = "0cbd8335bf39fab19b17a7bfaa33502d121d007fca4bddd5df0f43a9c814e2ef"


def require(condition: bool, description: str) -> None:
    if not condition:
        raise AssertionError(description)


def execute(args: list[str], *, cwd: Path, env: dict, expected: int = 0) -> str:
    result = subprocess.run(
        args, cwd=cwd, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=180, check=False,
    )
    if result.returncode != expected:
        raise AssertionError(
            f"unexpected exit {result.returncode} (expected {expected}) "
            f"for {args}: {result.stderr[:800]}"
        )
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    workspace = Path(__file__).resolve().parents[1]
    python = sys.executable
    environment = {**os.environ, "PYTHONPATH": str(workspace)}
    lock = workspace / "oee-curriculum.lock.json"
    require(lock.is_file(), "reviewed official release lock is missing")

    with tempfile.TemporaryDirectory(prefix="oee-ws-official-") as folder:
        root = Path(folder)
        store = root / "trusted-release-store"
        store.mkdir()
        learner = root / "learner"
        learner.mkdir()

        verified = execute([
            python, "-I", str(workspace / "scripts/install-official-curriculum.py"),
            "--artifacts", str(args.artifacts.resolve(strict=True)),
            "--lock", str(lock), "--store", str(store),
        ], cwd=workspace, env=environment)
        require("signature" in verified and MANIFEST_SHA256 in verified,
                "official signature or release installation not confirmed")

        shared = ["--lock", str(lock), "--store", str(store)]

        def cli(*args: str, expected: int = 0) -> str:
            return execute([python, "-m", "oee_workspace", *args],
                           cwd=workspace, env=environment, expected=expected)

        doctor = cli("doctor", *shared)
        require(f"SEF1 @ {RELEASE}" in doctor, "doctor did not inspect official release")

        one = execute([python, "-I", str(workspace / "scripts/run-pinned-toolkit.py"), "export", "SEF1",
                       *shared, "--output", "-"], cwd=workspace, env=environment)
        two = execute([python, "-I", str(workspace / "scripts/run-pinned-toolkit.py"), "export", "SEF1",
                       *shared, "--output", "-"], cwd=workspace, env=environment)
        require(one == two, "official Toolkit v2 export changed between runs")
        payload = json.loads(one)
        require(payload["exportVersion"] == 2 and
                payload["source"]["releaseId"] == RELEASE and
                payload["source"]["manifestSha256"] == MANIFEST_SHA256 and
                payload["course"]["code"] == "SEF1",
                "actual release export identity mismatch")

        cli("course", "add", "SEF1", *shared, "--dest", str(learner))
        note = learner / "notes/SEF/SEF1/resources.md"
        require(note.is_file(), "SEF1 notes file missing")
        require(not (learner / "notes/SEF/SEF1/reading-plan.md").exists(),
                "unapproved resource guide was attached")
        note.write_text("learner work must survive", encoding="utf-8")
        cli("course", "add", "SEF1", *shared, "--dest", str(learner), expected=1)
        require(note.read_text(encoding="utf-8") == "learner work must survive",
                "duplicate course command overwrote learner work")
        cli("course", "add", "SEF10", *shared, "--dest", str(learner))
        require((learner / "projects/SEF10/BRIEF.md").exists(),
                "SEF10 project scaffold absent")

        cli("evidence", "init", *shared, "--course", "SEF1",
            "--assessment", "SEF1-AS1", "--dest", str(learner))
        attempts = list((learner / "evidence/SEF/SEF1/SEF1-AS1").glob("*.json"))
        require(len(attempts) == 1, "unexpected official evidence attempt count")
        attempt = json.loads(attempts[0].read_text(encoding="utf-8"))
        require(attempt["schemaVersion"] == 2 and
                attempt["course"]["manifestSha256"] == MANIFEST_SHA256 and
                attempt["evaluation"] is None, "record inferred a grade or lost pin")
        cli("evidence", "check", *shared, "--path", str(attempts[0]),
            "--dest", str(learner))
        status = cli("status", *shared, "--course", "SEF1", "--dest", str(learner))
        require("Completion: not determined" in status,
                "Workspace must not infer course completion")
        cli("export", *shared, "--attempt", attempt["attemptId"],
            "--output", "selected-attempts.json", "--dest", str(learner))
        exported = json.loads((learner / "selected-attempts.json").read_text())
        require(exported["exportVersion"] == 2 and
                exported["records"][0]["attempt"]["course"]["manifestSha256"] ==
                MANIFEST_SHA256, "export lost source provenance")

        wrong = root / "wrong-lock.json"
        wrong.write_text(json.dumps({
            "formatVersion": 1, "releaseId": RELEASE,
            "manifestSha256": "f" * 64,
        }), encoding="utf-8")
        cli("doctor", "--lock", str(wrong), "--store", str(store), expected=3)
        cli("course", "add", "SEF2", "--lock", str(wrong),
            "--store", str(store), "--dest", str(learner), expected=3)
        require(not (learner / "labs/SEF/SEF2").exists(),
                "invalid lock generated learner files")

        report = {
            "officialRelease": True,
            "disposableFixture": False,
            "outcome": "passed",
            "releaseId": RELEASE,
            "manifestSha256": MANIFEST_SHA256,
            "publicKeyFingerprint": FINGERPRINT,
            "toolkit": "oee-toolkit 0.2.0",
            "toolkitExportSha256": hashlib.sha256(one.encode("utf-8")).hexdigest(),
            "checks": [
                "published-asset-byte-verification",
                "approved-steward-public-key-fingerprint",
                "official-ed25519-attestation-and-offline-install",
                "real-signed-v2-export-determinism",
                "workspace-doctor-course-generation-no-clobber",
                "evidence-v2-init-check-status-export",
                "corrupt-lock-refused-before-learner-writes",
                "no-unapproved-reading-plan",
            ],
            "learnerGradeInferred": False,
            "privateKeyAvailable": False,
        }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n",
                           encoding="utf-8", newline="\n")
    print("Official OEE 2026.11.1 Workspace three-platform acceptance: passed")
    print("Authentic signed release, no fixture/private key and no learner files modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
