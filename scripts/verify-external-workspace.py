#!/usr/bin/env python3
"""REL-I04 independent, Git-free *consumer* smoke using a disposable signed release.

Publisher-only fixture creation reads one exact OEE Git commit. The test then
uses the installed Toolkit and Workspace CLI, a separately verified local
archive, one temporary lock, and disposable learner files. This DOES NOT
authorize, publish, install or distribute an official OEE curriculum release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

# This exact OEE PR #260 merge contains the full-current release consumer.
# It is a source fixture pin, NOT an official curriculum release identity.
FIXTURE_COMMIT = "216553f10d20ed5fcb40dda46a147c68d7895555"
FIXTURE_RELEASE = "2026.11.1"


def run(argv, *, cwd=None, env=None, expected=0):
    result = subprocess.run([str(value) for value in argv], cwd=cwd, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=180, check=False)
    if result.returncode != expected:
        raise AssertionError(
            f"exit {result.returncode} (wanted {expected}): "
            f"{' '.join(str(x) for x in argv)}: "
            + result.stderr.decode("utf-8", "replace")[:600])
    return result.stdout.decode("utf-8", "strict")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-source", type=Path, required=True,
                        help="reviewed Workspace checkout for test code and templates")
    parser.add_argument("--oee-source", type=Path, required=True,
                        help="exact publisher-only fixture Git checkout")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace_source.resolve(strict=True)
    oee_repo = args.oee_source.resolve(strict=True)
    require((workspace / "oee_workspace/__main__.py").is_file(),
            "Workspace CLI is missing")
    require((oee_repo / ".git").exists(), "source fixture must be a Git checkout")
    run(["git", "-C", oee_repo, "cat-file", "-t", FIXTURE_COMMIT])
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from oee_toolkit.core import canonical_json
    from oee_toolkit.release_archive import (
        build_archive, install_verified_archive, sign_candidate)
    from oee_toolkit.release_manifest import digest_manifest
    from oee_toolkit.source import GitSource

    with tempfile.TemporaryDirectory(prefix="oee-ws-rel-i04-") as folder:
        root = Path(folder)
        store = root / "trusted-test-only-store"
        store.mkdir()
        learner = root / "learner"
        learner.mkdir()
        # Publisher-only operations may use exact Git to build a disposable
        # complete-curriculum test archive. Never distribute this test key.
        manifest, archive = build_archive(
            GitSource(oee_repo, FIXTURE_COMMIT), FIXTURE_RELEASE)
        digest = digest_manifest(manifest)
        key = Ed25519PrivateKey.generate()
        private = key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption())
        public = key.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
        claims, signature = sign_candidate(archive, digest, private)
        install_verified_archive(archive, digest, claims, signature, public, store)
        lock = root / "oee-curriculum.lock.json"
        lock.write_bytes(canonical_json({
            "formatVersion": 1, "releaseId": FIXTURE_RELEASE,
            "manifestSha256": digest,
        }))
        shared = ["--lock", str(lock), "--store", str(store)]
        python = sys.executable
        env = {**os.environ, "PYTHONPATH": str(workspace)}
        # No OEE Git checkout path enters any of these consumer commands.
        def cli(*command, expected=0):
            return run([python, "-m", "oee_workspace", *command],
                       cwd=workspace, env=env, expected=expected)

        doctor = cli("doctor", *shared)
        require(FIXTURE_RELEASE in doctor, "doctor lacks release identity")
        first = run([python, "-I", str(workspace / "scripts/run-pinned-toolkit.py"), "export", "SEF1",
                     *shared, "--output", "-"], cwd=workspace, env=env)
        second = run([python, "-I", str(workspace / "scripts/run-pinned-toolkit.py"), "export", "SEF1",
                      *shared, "--output", "-"], cwd=workspace, env=env)
        require(first == second, "installed Toolkit export must be deterministic")
        exported = json.loads(first)
        require(exported["exportVersion"] == 2
                and exported["source"]["manifestSha256"] == digest
                and exported["course"]["code"] == "SEF1",
                "installed current-only export disagrees with the lock")
        cli("course", "add", "SEF1", *shared, "--dest", str(learner))
        notes = learner / "notes/SEF/SEF1"
        require((notes / "resources.md").is_file(), "notes missing")
        require(not (notes / "reading-plan.md").exists(),
                "a non-approved SEF1 guide was attached")
        own_notes = notes / "resources.md"
        own_notes.write_text("learner-owned, never overwritten", encoding="utf-8")
        cli("course", "add", "SEF1", *shared, "--dest", str(learner), expected=1)
        require(own_notes.read_text() == "learner-owned, never overwritten",
                "repeated generation overwrote learner work")
        cli("course", "add", "SEF10", *shared, "--dest", str(learner))
        require((learner / "projects/SEF10/BRIEF.md").is_file(),
                "canonical project course was not scaffolded")
        cli("evidence", "init", *shared, "--course", "SEF1",
            "--assessment", "SEF1-AS1", "--dest", str(learner))
        attempts = list((learner / "evidence/SEF/SEF1/SEF1-AS1").glob("*.json"))
        require(len(attempts) == 1, "one UUID attempt expected")
        attempt = json.loads(attempts[0].read_text())
        require(attempt["schemaVersion"] == 2
                and attempt["course"]["manifestSha256"] == digest
                and attempt["evaluation"] is None,
                "evidence attempt source identity or evaluation is incorrect")
        cli("evidence", "check", *shared, "--path", str(attempts[0]),
            "--dest", str(learner))
        status = cli("status", *shared, "--course", "SEF1", "--dest", str(learner))
        require("Completion: not determined" in status,
                "Workspace cannot award credit")
        cli("export", *shared, "--attempt", attempt["attemptId"],
            "--output", "selected-attempts.json", "--dest", str(learner))
        bundle = json.loads((learner / "selected-attempts.json").read_text())
        require(bundle["exportVersion"] == 2 and
                bundle["records"][0]["attempt"]["course"]["manifestSha256"] == digest,
                "learner-selected evidence output changed source identity")
        # Lock mismatch is incomplete, never a search for Git, HEAD or latest.
        wrong_lock = root / "wrong-lock.json"
        wrong_lock.write_bytes(canonical_json({
            "formatVersion": 1, "releaseId": FIXTURE_RELEASE,
            "manifestSha256": "f" * 64,
        }))
        cli("doctor", "--lock", str(wrong_lock), "--store", str(store), expected=3)
        cli("course", "add", "SEF2", "--lock", str(wrong_lock),
            "--store", str(store), "--dest", str(learner), expected=3)
        require(not (learner / "labs/SEF/SEF2").exists(),
                "failed release resolution wrote a learner course")
        # The official store remains unaffected; no keys/assets are reported.
        report = {
            "ticket": "REL-I04", "outcome": "passed",
            "candidateOnly": True, "officialReleasePublished": False,
            "workspaceSource": str(workspace),
            "fixtureOriginCommit": FIXTURE_COMMIT,
            "fixtureManifestSha256": digest,
            "toolkitExportSha256": hashlib.sha256(first.encode("utf-8")).hexdigest(),
            "checks": [
                "temporary-ed25519-signature-and-offline-install",
                "read-only-installed-release-determinism",
                "Git-free-CLI-and-project-scaffold",
                "learner-no-clobber-and-no-unapproved-reading-plan",
                "evidence-v2-init-check-status-and-selected-export",
                "mismatched-lock-fail-closed",
            ],
            "learnerDataExported": False, "privateServiceRequired": False,
        }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    print("REL-I04 disposable signed-release consumer smoke: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
