#!/usr/bin/env python3
"""WS-I05: independent, offline OEE Workspace release-readiness smoke.

Clone the supplied public Workspace and OEE checkouts into isolated,
untracked temporary repositories, then exercise the *actual* Python CLI
through subprocesses. The copy can run on Linux, macOS and Windows.

All network access needed to obtain public source repositories happens
before this script. It neither fetches a remote nor installs packages,
uses credentials, AI/model services, a private platform or paid resources.
This script is release evidence; it does not publish a package or tag.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import traceback

PIN = "67416343f3eab17ada5d3c79ae6cc782524c29ff"
SOURCE = "0xbuffdev/open-engineering-education"
SCHEMA = 2
FULL_SHA = re.compile(r"[a-f0-9]{40}\Z")


class SmokeFailure(Exception):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise SmokeFailure(detail)


def runner(argv: list[str], cwd: Path, *, expected: int = 0,
           env: dict[str, str] | None = None) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        argv, cwd=cwd, env=env, capture_output=True, timeout=120, check=False,
    )
    if completed.returncode != expected:
        out = completed.stdout.decode("utf-8", errors="replace")[-650:]
        err = completed.stderr.decode("utf-8", errors="replace")[-1000:]
        raise SmokeFailure(
            f"exit {completed.returncode}, expected {expected}, "
            f"argv={argv!r}; stdout={out!r}; stderr={err!r}"
        )
    return completed


def text(process: subprocess.CompletedProcess[bytes]) -> str:
    return process.stdout.decode("utf-8", errors="strict")


def git(repo: Path, *args: str) -> str:
    return text(runner(["git", "-C", str(repo), *args], repo)).strip()


def clone_local(source: Path, dest: Path) -> None:
    # A genuine standalone .git checkout: copies Git objects but no working
    # tree or untracked fixtures from either source checkout.
    runner(["git", "-c", "core.autocrlf=false", "clone", "--quiet",
            "--no-hardlinks", str(source), str(dest)], source)
    require((dest / ".git").exists(), f"new checkout is not a Git repository: {dest}")
    require(git(dest, "rev-parse", "HEAD") == git(source, "rev-parse", "HEAD"),
            "the independent clone does not check out the tested source commit")


def write_report(path: Path | None, result: dict) -> None:
    encoded = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if path is None:
        print(encoded, end="")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(encoded, encoding="utf-8", newline="\n")
        print(f"WS-I05 smoke report: {path} ({result['result']})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-source", type=Path, required=True,
                        help="locally checked-out public Workspace commit")
    parser.add_argument("--oee-source", type=Path, required=True,
                        help="trusted local OEE checkout with full history")
    parser.add_argument("--report", type=Path, default=None,
                        help="write JSON release evidence outside the learner data")
    args = parser.parse_args(argv)
    tested: list[dict] = []
    result = {
        "reportVersion": 1, "milestone": "WS-I05", "result": "incomplete",
        "sourcePin": PIN, "requiresPrivateServices": False,
        "requiresPaidResources": False, "publishesRelease": False,
        "platform": sys.platform, "checks": tested,
    }

    def gate(name: str, fn) -> None:
        fn()
        tested.append({"name": name, "state": "passed"})

    try:
        workspace_source = args.workspace_source.resolve(strict=True)
        oee_source = args.oee_source.resolve(strict=True)
        require((workspace_source / ".git").exists(), "Workspace source is not a clone")
        require((oee_source / ".git").exists(), "OEE source is not a clone")
        require(sys.version_info >= (3, 11), "Python 3.11+ is required")
        require(FULL_SHA.fullmatch(PIN) is not None, "pinned source must use a full SHA")
        result["workspaceSourceCommit"] = git(workspace_source, "rev-parse", "HEAD")
        result["oeeSourceCommit"] = git(oee_source, "rev-parse", "HEAD")

        with tempfile.TemporaryDirectory(prefix="oee release smoke ") as temp:
            base = Path(temp)
            workspace, oee = base / "workspace clone", base / "oee clone"
            learner = base / "private learner workspace"
            learner.mkdir()
            gate("WS-T01: fresh independent public-source Git clones", lambda: (
                clone_local(workspace_source, workspace),
                clone_local(oee_source, oee),
            ))
            require(git(oee, "cat-file", "-t", PIN + "^{commit}") == "commit",
                    "required pinned OEE commit is missing from clean clone")

            # No HTTP/Git remote is needed after local source is available.
            # These environment settings are a regression deterrent, not an
            # OS-level network sandbox for malicious child programs.
            offline = dict(os.environ)
            offline.update({
                "PYTHONIOENCODING": "utf-8",
                "GIT_TERMINAL_PROMPT": "0",
                "HTTP_PROXY": "http://127.0.0.1:9",
                "HTTPS_PROXY": "http://127.0.0.1:9",
                "ALL_PROXY": "http://127.0.0.1:9",
                "NO_PROXY": "",
                "PIP_NO_INDEX": "1",
                "OEE_REPO": str(oee),
            })
            offline.pop("OPENAI_API_KEY", None)
            offline.pop("ANTHROPIC_API_KEY", None)

            def cli(*args: str, expected: int = 0):
                return runner([sys.executable, "-m", "oee_workspace", *args],
                              workspace, expected=expected, env=offline)

            def tool(name: str, *args: str, expected: int = 0):
                return runner([sys.executable, "scripts/" + name, *args],
                              workspace, expected=expected, env=offline)

            source_option = ("--oee", str(oee))
            pinned_option = (*source_option, "--revision", PIN)
            dest_option = ("--dest", str(learner))

            map_path = workspace / "resources/mappings/SEF/SEF1.json"
            mapping = json.loads(map_path.read_text(encoding="utf-8"))
            require(mapping["schemaVersion"] == SCHEMA
                    and mapping["status"] == "reviewed"
                    and mapping["curriculum"]["revision"] == PIN
                    and mapping["curriculum"]["specification"] == "v0.2.0",
                    "SEF1 map is not reviewed v2 at the declared source commit")

            def validate_toolkit():
                result_cli = cli("doctor", *pinned_option)
                require(PIN in text(result_cli), "doctor omitted the source commit")
                cli("resources", "check", *source_option, "--map", str(map_path))
                tool("check-resources.py", *source_option)
            gate("WS-T09: pinned current-only Toolkit and resource check", validate_toolkit)

            historical = workspace / "tests/fixtures/resource-map-v1-SEF1.json"
            def refuse_old_map():
                for path in (historical, historical):
                    denied = cli("resources", "check", *source_option,
                                 "--map", str(path), expected=1)
                    require(b"WSC005" in denied.stderr, "unsupported map accepted")
                require(not (workspace / "resources/mappings/SEF/SEF2.json").exists(),
                        "unexpected active map created")
            gate("WS-T02/T03/T21: old resource map cannot enter active runtime", refuse_old_map)

            def missing_revision():
                denied = cli("doctor", *source_option, "--revision", "f" * 40,
                             expected=3)
                require(b"WSE003" in denied.stderr, "missing SHA was not incomplete")
                denied = cli("course", "add", "SEF1", *source_option,
                             "--revision", "f" * 40, *dest_option, expected=3)
                require(not (learner / "notes/SEF/SEF1").exists(),
                        "missing source created learner files")
            gate("WS-T05: missing source object cannot silently use HEAD", missing_revision)

            def rejected_old_course():
                tag = text(runner(
                    ["git", "-C", str(oee), "rev-parse", "--verify",
                     "refs/tags/v0.1.0^{commit}"], oee
                )).strip()
                require(FULL_SHA.fullmatch(tag) is not None,
                        "old-source rejection fixture tag missing")
                denied = cli("doctor", *source_option, "--revision", tag, expected=3)
                require(b"WSE003" in denied.stderr, "old source did not fail closed")
            gate("WS-T08: unsupported previous OEE source rejected", rejected_old_course)

            def repeatable_guide():
                argv = ("render-resource-guides.py", *source_option,
                        "--course", "SEF1", "--stdout")
                once = tool(*argv).stdout
                twice = tool(*argv).stdout
                require(once == twice and once.startswith(b"# SEF1"),
                        "guide generator is not byte-deterministic")
                checked = (workspace / "resources/guides/SEF/SEF1.md").read_text(
                    encoding="utf-8"
                ).replace("\r\n", "\n")
                require(once.decode("utf-8").replace("\r\n", "\n") == checked,
                        "committed guide differs from deterministic regeneration")
                tool("render-resource-guides.py", *source_option, "--check")
                result["generatedGuideSha256"] = hashlib.sha256(once).hexdigest()
            gate("WS-T19: regenerated public guide is byte-identical", repeatable_guide)

            def resource_claims():
                modules = mapping["modules"]
                partial = [m for m in modules if m["coverage"] == "partial"]
                require(len(partial) == 7 and all(m.get("gap") for m in partial),
                        "seven independently reviewed partial mapping gaps were lost")
                require(any(m["coverage"] == "mapped" for m in modules),
                        "reviewed mapped module missing")
                references = [r["resource"] for m in modules for r in m["resources"]]
                require(references.count("R89") >= 2 and references.count("B7") >= 2,
                        "shared catalogue identity was duplicated or lost")
                book = json.loads((workspace / "resources/catalog/books/B7.json")
                                  .read_text(encoding="utf-8"))
                free = json.loads((workspace / "resources/catalog/online/R89.json")
                                  .read_text(encoding="utf-8"))
                require(book["access"]["mode"] in ("paid", "mixed")
                        and free["access"]["mode"] == "free",
                        "access labels do not reflect optional paid/free alternatives")
                guide = (workspace / "resources/guides/SEF/SEF1.md").read_text(
                    encoding="utf-8")
                require("No book purchase is required" in guide
                        and "Free" in guide and "Partial" in guide
                        and "Optional" in guide,
                        "public guide conceals costs or partial gaps")
                for rid in set(references):
                    path = next(iter((workspace / "resources/catalog").rglob(
                        f"{rid}.json")), None)
                    require(path is not None, f"catalogue reference {rid} is absent")
                    info = json.loads(path.read_text(encoding="utf-8"))
                    require(info["id"] == rid, "catalogue identity mismatch")
                    verify = info["verification"]
                    require(verify["status"] in ("verified", "review-needed")
                            and verify.get("basis"), "editorial verification basis missing")
            gate("WS-T11–T15/WS-T23: optional, traceable public resource claims",
                 resource_claims)

            def mapped_course():
                cli("course", "add", "SEF1", *pinned_option, *dest_option)
                notes = learner / "notes/SEF/SEF1"
                require((notes / "reading-plan.md").exists()
                        and (notes / "summary.md").is_file(),
                        "reviewed course did not create expected files")
                generated = (notes / "reading-plan.md").read_text(
                    encoding="utf-8").replace("\r\n", "\n")
                original = (workspace / "resources/guides/SEF/SEF1.md").read_text(
                    encoding="utf-8").replace("\r\n", "\n")
                require(generated == original, "learner got a different reading plan")
                (notes / "resources.md").write_text(
                    "Private learner resources remain mine.\n", encoding="utf-8",
                )
                denied = cli("course", "add", "SEF1", *pinned_option,
                             *dest_option, expected=1)
                require(b"WSC004" in denied.stderr
                        and (notes / "resources.md").read_text(
                            encoding="utf-8") == "Private learner resources remain mine.\n",
                        "duplicate course initialization overwrote notes")
            gate("WS-T20: reviewed course generation preserves existing learner work",
                 mapped_course)

            def unmapped_course():
                cli("course", "add", "SEF2", *pinned_option, *dest_option)
                require((learner / "notes/SEF/SEF2/summary.md").is_file(),
                        "unmapped course did not scaffold")
                require(not (learner / "notes/SEF/SEF2/reading-plan.md").exists(),
                        "unmapped course fabricated a guide")
            gate("WS-T16/WS-T22: unmapped course has no invented reading or final lab",
                 unmapped_course)

            def project_gate():
                cli("course", "add", "SEF10", *pinned_option, *dest_option)
                project = learner / "projects/SEF10"
                require((project / "BRIEF.md").is_file()
                        and (project / "docs/design.md").is_file(),
                        "canonical OEE project course failed to scaffold")
                snapshot = (project / "BRIEF.md").read_bytes()
                denied = cli("course", "add", "ledgerlab", *pinned_option,
                             *dest_option, expected=1)
                require(b"WSC001" in denied.stderr,
                        "invented project alias was accepted")
                cli("course", "add", "SEF10", *pinned_option,
                    *dest_option, expected=1)
                require((project / "BRIEF.md").read_bytes() == snapshot,
                        "existing project data was overwritten")
            gate("WS-I12: canonical project type and bad alias rejection", project_gate)

            def immutable_oee_revision():
                from_status = git(oee, "status", "--porcelain")
                require(from_status == "", "clean external OEE clone already dirty")
                before = git(oee, "show", PIN + ":curriculum/SEF/SEF1.md")
                target = "git -C " + str(oee)
                runner(["git", "-C", str(oee),
                        "-c", "user.name=OEE Smoke",
                        "-c", "user.email=smoke@example.invalid",
                        "-c", "commit.gpgsign=false",
                        "commit", "--quiet", "--allow-empty", "-m",
                        "synthetic upstream HEAD movement"], oee)
                head = git(oee, "rev-parse", "HEAD")
                require(head != PIN and FULL_SHA.fullmatch(head) is not None,
                        "HEAD did not move during independent test")
                require(git(oee, "show", PIN + ":curriculum/SEF/SEF1.md") == before,
                        "upstream move changed pinned course data")
                # The guide stays pinned, even though HEAD is now different.
                tool("check-resources.py", *source_option)
                result_drift = json.loads(text(tool("report-oee-drift.py",
                    *source_option, "--course", "SEF1",
                    "--target-revision", head)))
                require(result_drift["results"][0]["pinnedRevision"] == PIN
                        and result_drift["targetRevision"] == head
                        and not result_drift["autoRemapped"]
                        and not result_drift["filesChanged"],
                        "HEAD movement automatically remapped source data")
                result["independentMovedOeeHead"] = head
            gate("WS-T04/T06/T07: moved HEAD cannot replace recorded OEE pin",
                 immutable_oee_revision)

            def source_status():
                args_export = [
                    sys.executable, "-m", "tooling.oee_toolkit", "export",
                    "--repo", str(oee), "--revision", PIN,
                    "--course", "SEF1", "--output", "-",
                ]
                exported = json.loads(text(runner(args_export, oee, env=offline)))
                require(exported["source"]["revision"] == PIN,
                        "pinned source identity has changed")
                require(exported["validation"]["manualReviewRequired"] is True,
                        "public Toolkit export wrongly grants automatic completion")
                require(exported["course"]["status"] in ("draft", "tested", "verified"),
                        "course status missing from canonical export")
                result["sourceCourseStatus"] = exported["course"]["status"]
            gate("WS-T24: published guide never promotes OEE course status",
                 source_status)

            def attempt_flow():
                def init():
                    output = cli("evidence", "init", *pinned_option, "--course",
                                 "SEF1", "--assessment", "SEF1-AS1", *dest_option)
                    require(b"Created" in output.stdout,
                            "evidence initialization lacks confirmation")
                init()
                init()
                record_dir = learner / "evidence/SEF/SEF1/SEF1-AS1"
                attempts = sorted(record_dir.glob("*.json"))
                require(len(attempts) == 2 and attempts[0].name != attempts[1].name,
                        "repeated evidence init reused a UUID")
                first = json.loads(attempts[0].read_text(encoding="utf-8"))
                other = json.loads(attempts[1].read_text(encoding="utf-8"))
                require(first["schemaVersion"] == 1
                        and first["course"]["revision"] == PIN
                        and first["evaluation"] is None
                        and first["attemptId"] != other["attemptId"],
                        "evidence init fabricated success or violated source identity")
                cli("evidence", "check", *source_option, "--path",
                    str(attempts[0]), *dest_option)
                progress = learner / "progress.md"
                progress.write_text("Private progress belongs to learner.\n",
                                    encoding="utf-8")
                status = cli("status", *source_option, *dest_option)
                require("attempt-recorded" in text(status)
                        and "Completion: not determined" in text(status),
                        "status promoted unreviewed evidence")
                require(progress.read_text(encoding="utf-8") ==
                        "Private progress belongs to learner.\n",
                        "status unexpectedly rewrote learner progress")

                artifact = learner / "labs/SEF/SEF1/test-evidence.txt"
                # Mutate only an independent synthetic attempt, not source.
                record = first.copy()
                record["artifacts"] = [{
                    "kind": "relative-path",
                    "value": "labs/SEF/SEF1/test-evidence.txt",
                    "sha256": "0" * 64,
                }]
                attempts[0].write_text(json.dumps(record), encoding="utf-8")
                missing = cli("evidence", "check", *source_option,
                              "--path", str(attempts[0]), *dest_option,
                              expected=3)
                require(b"WSE003" in missing.stderr,
                        "missing learner artifact was treated as valid")
                artifact.write_text("Deliberately different local data.\n",
                                    encoding="utf-8")
                tampered = cli("evidence", "check", *source_option,
                               "--path", str(attempts[0]), *dest_option,
                               expected=1)
                require(b"WSE007" in tampered.stderr,
                        "artifact hash mismatch was treated as valid")
                record["artifacts"][0]["sha256"] = hashlib.sha256(
                    artifact.read_bytes()).hexdigest()
                attempts[0].write_text(json.dumps(record), encoding="utf-8")
                cli("evidence", "check", *source_option, "--path",
                    str(attempts[0]), *dest_option)

                exported = cli("export", *source_option, *dest_option,
                               "--attempt", first["attemptId"],
                               "--output", "exports/selected.json")
                payload = json.loads((learner / "exports/selected.json")
                                     .read_text(encoding="utf-8"))
                require(len(payload["records"]) == 1
                        and payload["records"][0]["attempt"]["attemptId"] ==
                        first["attemptId"]
                        and other["attemptId"] not in json.dumps(payload)
                        and payload["artifactBytesIncluded"] is False,
                        "selected export included unrelated records or artifact content")
                denied = cli("export", *source_option, *dest_option,
                             "--attempt", first["attemptId"],
                             "--output", "exports/selected.json", expected=1)
                require(b"WSC004" in denied.stderr,
                        "export silently overwrote selected evidence file")
                require("Private progress belongs to learner" not in
                        json.dumps(payload), "progress unexpectedly leaked")
                require((learner / "progress.md").read_text(encoding="utf-8")
                        == "Private progress belongs to learner.\n",
                        "evidence flow modified progress")
            gate("Evidence/CLI: offline UUID, check, status and selected export",
                 attempt_flow)

            def source_integrity():
                require(git(workspace, "status", "--porcelain") == "",
                        "source Workspace clone unexpectedly changed")
                require(git(oee, "status", "--porcelain") == "",
                        "source OEE clone has dirty files after smoke")
                require(not (workspace / "scripts/new-course-workspace").exists()
                        and not (workspace / "scripts/new-project-workspace").exists(),
                        "obsolete Bash generation is still available")
                for name in ("README.md", "resources/README.md",
                             "evidence/README.md", "docs/AI-SAFETY.md",
                             "docs/OEE-UPSTREAM-DRIFT.md"):
                    require((workspace / name).is_file(),
                            f"public documentation missing: {name}")
            gate("Privacy/current-only: no source writes, wrappers or private services",
                 source_integrity)

        result["result"] = "passed"
        write_report(args.report, result)
        return 0
    except (SmokeFailure, OSError, subprocess.TimeoutExpired, UnicodeError,
            ValueError, KeyError, AssertionError) as exc:
        result["result"] = "failed"
        result["failure"] = {"type": type(exc).__name__, "message": str(exc)}
        write_report(args.report, result)
        print(f"release_smoke_failure: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
