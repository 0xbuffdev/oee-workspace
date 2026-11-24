"""Current-only, offline OEE Workspace command line (WS-I08).

python -m oee_workspace {doctor,course,resources,evidence,status,export}
Requires Python >= 3.11, an installed OEE Toolkit and a reviewed release
lock with an independently verified installed archive; no Git checkout. No curriculum Markdown parser, network, model, grader or daemon.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from uuid import uuid4

from .evidence import (
    COURSE, EvidenceIssue, EvidenceService, incomplete, invalid, load_reader,
    record_shape,
)
from .local import PublicationError, exists, publish, publish_file_new, workspace_root

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
MAPS = ROOT / "resources" / "mappings"


def source(service: EvidenceService, code: str) -> dict:
    if not isinstance(code, str) or not COURSE.fullmatch(code):
        invalid(f"unsupported canonical course code: {code}", "WSC001")
    return service.source(code)


def canonical_source(code: str, origin_commit: str) -> str:
    program = COURSE.fullmatch(code).group(1)
    return ("https://github.com/0xbuffdev/open-engineering-education/blob/"
            f"{origin_commit}/curriculum/{program}/{code}.md")


def learner_root(dest: Path) -> Path:
    try:
        return workspace_root(dest)
    except PublicationError as exc:
        invalid(str(exc), "WSC004")


def render(template: Path, values: dict[str, str]) -> str:
    if template.is_symlink() or not template.is_file():
        invalid(f"missing or symlinked generator template: {template}", "WSC004")
    contents = template.read_text(encoding="utf-8")
    for key, value in values.items():
        contents = contents.replace(f"<{key}>", value)
    return contents


def execute(script: str, args: list[str]) -> str:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *args],
        capture_output=True, text=True, timeout=120, check=False,
    )
    if result.returncode:
        if result.returncode == 3:
            incomplete(f"{script} cannot resolve the selected source: "
                       + result.stderr.strip()[:350], "WSC003")
        invalid(f"{script} rejected source/map: {result.stderr.strip()[:350]}", "WSC005")
    return result.stdout


def study_guide(code: str, checked: dict, lock: Path | None, store: Path | None) -> tuple[str | None, str]:
    """Use the established v2 renderer/validator, not a new course parser."""
    path = MAPS / COURSE.fullmatch(code).group(1) / f"{code}.json"
    if path.is_symlink():
        invalid("symlinked resource mapping cannot be published", "WSC005")
    if not path.exists():
        return None, "No public resource map exists for this course."
    if not path.is_file():
        invalid("resource map is not a file", "WSC005")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, ValueError):
        invalid("resource map is not valid JSON", "WSC005")
    if (type(data) is not dict or data.get("schemaVersion") != 3 or
            data.get("curriculum", {}).get("specification") != "v0.2.0"):
        invalid("only the current OEE v0.2.0 resource-map v3 is supported", "WSC005")
    canon = data["curriculum"]
    if canon.get("course") != code:
        invalid("resource map is attached to a different course", "WSC005")
    if data.get("status") not in ("draft", "reviewed"):
        invalid("unsupported resource map review status", "WSC005")
    if data["status"] == "draft":
        return None, "The selected resource map is not reviewed; no reading plan was generated."
    ident = checked["source"]
    if (canon.get("releaseId") != ident["releaseId"] or
            canon.get("manifestSha256") != ident["manifestSha256"] or
            canon.get("courseSha256") != ident["courseSha256"]):
        return None, "Reviewed map belongs to another immutable release; no reading plan was generated."

    # Perform the authoritative v2 and exact-OEE-commit validation once.
    # Reuse the repository-owned guide renderer in-process instead of parsing
    # output from a second subprocess. On Windows, a successful nested
    # subprocess can expose stdout=None even when the direct renderer works;
    # rendering from the same validated map avoids that failure mode and
    # remains byte-identical to scripts/render-resource-guides.py.
    execute("check-resources.py",
            ["--lock", str(lock or Path.cwd() / "oee-curriculum.lock.json"), "--course", code] +
            (["--store", str(store)] if store is not None else []))
    name = "oee_workspace_current_guide_renderer"
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / "render-resource-guides.py"
    )
    if spec is None or spec.loader is None:
        invalid("canonical guide renderer is unavailable", "WSC005")
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    try:
        guide = renderer.render(data, renderer.load_catalog(), ident)
    except (KeyError, ValueError, UnicodeError, OSError) as exc:
        invalid("canonical guide renderer rejected the validated map: "
                + str(exc)[:350], "WSC005")
    if not isinstance(guide, str) or not guide.startswith(f"# {code}"):
        invalid("renderer did not produce the expected canonical guide", "WSC005")
    return guide, "Reviewed, pinned optional study guide generated."


def doctor(args) -> None:
    # The probe course is a canonical OEE source, not an invented project alias.
    if sys.version_info < (3, 11):
        incomplete("Python >= 3.11 is required", "WSC003")
    checked = source(EvidenceService(Path.cwd(), args.lock, args.store), "SEF1")
    print("OEE Workspace doctor: passed (offline)")
    print(f"  Python: {sys.version_info.major}.{sys.version_info.minor}")
    print("  Toolkit: first-party, installed release")
    print(f"  Probe course: {checked['course']} @ {checked['source']['releaseId']}")
    print("  Checks: structural source only; educational review still required")


def course_add(args) -> None:
    root = learner_root(args.dest)
    service = EvidenceService(root, args.lock, args.store)
    checked = source(service, args.code)
    code = args.code
    program = COURSE.fullmatch(code).group(1)
    url = canonical_source(code, checked["source"]["originCommit"])
    destinations = [Path(area) / program / code
                    for area in ("labs", "exercises", "notes")]
    course_type = checked["courseType"]
    if course_type == "project":
        destinations.append(Path("projects") / code)
    elif course_type != "course":
        invalid("OEE source has unsupported course type", "WSC005")
    if any(exists(root / rel) for rel in destinations):
        raise EvidenceIssue(
            "WSC011", "conflict",
            f"course already exists in learner workspace: {code}; no files replaced",
        )

    guide, notice = study_guide(code, checked, args.lock, args.store)
    values = {"course": code, "course_link": url}
    with tempfile.TemporaryDirectory(prefix=".oee-stage-", dir=root) as tmp:
        stage = Path(tmp)
        for part in destinations:
            (stage / part).mkdir(parents=True)
        material = (
            ("lab-README.md", Path("labs") / program / code / "README.md"),
            ("exercises-README.md", Path("exercises") / program / code / "README.md"),
            ("resources.md", Path("notes") / program / code / "resources.md"),
            ("summary.md", Path("notes") / program / code / "summary.md"),
        )
        for template, path in material:
            (stage / path).write_text(
                render(TEMPLATES / "course-workspace" / template, values),
                encoding="utf-8", newline="\n",
            )
        if guide is not None:
            (stage / "notes" / program / code / "reading-plan.md").write_text(
                guide, encoding="utf-8", newline="\n")

        if course_type == "project":
            base = Path("projects") / code
            params = {"project_title": code, "brief_link": url}
            project_root = TEMPLATES / "project-workspace"
            (stage / base / "docs").mkdir()
            (stage / base / "README.md").write_text(
                render(project_root / "README.md", params), encoding="utf-8", newline="\n")
            for name in ("design.md", "evaluation.md", "retrospective.md"):
                (stage / base / "docs" / name).write_text(
                    render(project_root / name, params), encoding="utf-8", newline="\n")
            (stage / base / "BRIEF.md").write_text(
                f"# {code} project workspace\n\n"
                f"**Canonical OEE course:** [{code}]({url})\n"
                f"**OEE release:** {checked['source']['releaseId']} (manifest: {checked['source']['manifestSha256']})\n\n"
                "Follow the public project's outcomes, required assessments and "
                "defense criteria. These templates do not define separate graduation "
                "requirements or attest to learner achievement.\n",
                encoding="utf-8", newline="\n",
            )
        try:
            publish(root, stage, destinations)
        except PublicationError as exc:
            invalid(str(exc), "WSC004")
    print(f"Created {course_type} workspace: {code} @ {checked['source']['releaseId']}")
    for rel in destinations:
        print(f"  {rel.as_posix()}/")
    print(f"Canonical source: {url}")
    print(notice)


def resources_check(args) -> None:
    reader = load_reader()
    findings = reader.Check()
    catalog = reader.validate_catalog(findings)
    path = args.map
    if path.is_symlink() or not path.is_file():
        invalid(f"resource map must be an existing regular file: {path}", "WSC005")
    try:
        if path.stat().st_size > 2_000_000:
            invalid("resource map is too large", "WSC005")
        mapping = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError):
        invalid("resource map is not UTF-8 JSON", "WSC005")
    if not reader.validate_map_shape(mapping, catalog, findings, str(path)):
        invalid("resource mapping failed structural checks: "
                + "; ".join(findings.errors[:3]), "WSC005")
    if findings.errors:
        invalid("; ".join(findings.errors[:3]), "WSC005")
    try:
        reader.check_pinned_map(mapping, args.lock or Path.cwd() / "oee-curriculum.lock.json", args.store)
    except reader.PinnedSourceError as exc:
        if exc.category in ("source_missing", "store_missing",
                            "lock_digest_not_found", "unsupported_format"):
            incomplete("pinned source unavailable (" + exc.category
                       + "): " + str(exc), "WSC003")
        invalid("pinned source validation rejected: " + exc.category, "WSC005")
    except reader.load_consumer().ContractError as exc:
        if exc.category in ("missing_input", "unsupported_format"):
            incomplete("pinned export unavailable: " + exc.code, "WSC003")
        invalid("invalid resource mapping reference: " + exc.code, "WSC005")
    print("Resource mapping: structurally passed")
    print(f"  Canonical source: {mapping['curriculum']['course']} @ "
          f"{mapping['curriculum']['releaseId']}")
    print(f"  Editorial status: {mapping['status']}")
    if mapping["status"] != "reviewed":
        print("  Publication: not permitted until independent mapping review")
    print(f"  Outstanding mapping gaps: {len(findings.warnings)}")
    print("  This does not certify educational adequacy.")


def evidence_init(args) -> None:
    root = learner_root(args.dest)
    service = EvidenceService(root, args.lock, args.store)
    checked = source(service, args.course)
    assessment = checked["assessments"].get(args.assessment)
    if assessment is None or not assessment["required"]:
        invalid("assessment is not a required summative assessment in this OEE course",
                "WSC005")
    code = args.course
    program = COURSE.fullmatch(code).group(1)
    ident = str(uuid4())
    if any(path.stem == ident for path in service.paths()):
        invalid("generated attempt UUID collides with an existing learner attempt",
                "WSC004")
    payload = {
        "schemaVersion": 2,
        "attemptId": ident,
        "recordedAt": datetime.now(timezone.utc).replace(microsecond=0)
        .isoformat().replace("+00:00", "Z"),
        "course": {
            "repository": checked["source"]["repository"],
            "releaseId": checked["source"]["releaseId"],
            "manifestSha256": checked["source"]["manifestSha256"],
            "courseSha256": checked["source"]["courseSha256"],
            "specification": "v0.2.0",
            "path": checked["source"]["coursePath"], "code": code,
        },
        "assessmentId": args.assessment,
        "outcomeIds": list(assessment["outcomeIds"]),
        "artifacts": [], "observations": [], "evaluation": None,
    }
    record_shape(payload)
    relative = (Path("evidence") / program / code / args.assessment /
                f"{ident}.json")
    try:
        publish_file_new(root, relative,
                         (json.dumps(payload, sort_keys=True, indent=2)
                          + "\n").encode("utf-8"))
    except PublicationError as exc:
        invalid(str(exc), "WSC004")
    print(f"Created a new unreviewed evidence attempt: {relative.as_posix()}")
    print(f"Source: {code} @ {checked['source']['releaseId']}; assessment: {args.assessment}")
    print("No evaluation, grading or learner completion was inferred.")


def evidence_check(args) -> None:
    root = learner_root(args.dest)
    report = EvidenceService(root, args.lock, args.store).check(args.path)
    if report["outcome"] != "valid":
        item = report["findings"][0]
        raise EvidenceIssue(item["code"], report["outcome"], item["message"])
    print(f"Evidence record: valid structure and pinned references ({report['record']})")
    print(f"  Source: {report['course']} @ {report['releaseId']}")
    print(f"  Review: {report['review']['status']} "
          "(learner-reported; reviewer identity unverified)")
    print("  Educational achievement: not determined")


def status(args) -> None:
    root = learner_root(args.dest)
    projection = EvidenceService(root, args.lock, args.store).status(args.course)
    for item in projection["courses"]:
        print(f"{item['course']} @ {item['releaseId']}:")
        for row in item["assessments"]:
            print(f"  {row['assessmentId']}: "
                  f"{','.join(row['reportedStates'])} (attempts: {row['attempts']})")
        for row in item["outcomes"]:
            if row["outstandingAssessmentIds"]:
                print(f"  {row['outcomeId']} outstanding required decisions: "
                      + ", ".join(row["outstandingAssessmentIds"]))
        print("  Completion: not determined by Workspace")
    if not projection["courses"]:
        print("No valid assessment attempts found for a selected OEE source.")
    counts = projection["counts"]
    print("Record integrity: " + ", ".join(
        f"{key}={counts[key]}" for key in ("valid", "invalid", "incomplete")))
    print("Reported human reviews are not identity-verified.")
    if counts["invalid"]:
        invalid("one or more evidence records are invalid", "WSC005")
    if counts["incomplete"]:
        incomplete("one or more evidence records require missing sources/artifacts",
                   "WSC003")


def export(args) -> None:
    root = learner_root(args.dest)
    service = EvidenceService(root, args.lock, args.store)
    if not args.attempt:
        invalid("select one or more attempt UUIDs", "WSC009")
    if len(args.attempt) != len(set(args.attempt)):
        invalid("the same attempt was selected more than once", "WSC009")
    selected = []
    candidates = service.paths()
    for attempt in args.attempt:
        from .evidence import uuid4 as require_uuid
        require_uuid(attempt)
        matches = [p for p in candidates if p.stem == attempt]
        if not matches:
            incomplete(f"selected attempt {attempt} does not exist", "WSC003")
        if len(matches) > 1:
            invalid(f"duplicate selected attempt ID {attempt}", "WSC009")
        selected.append(matches[0])
    package = service.export_selected(selected)
    # This is a local export of explicitly selected JSON only. The scanner
    # covers known credential patterns, not arbitrary personal information.
    raw = json.dumps(package, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    if re.search(r"(?i)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
                 r"|\b(?:ghp_|github_pat_|xox[baprs]-|sk-proj-|AKIA[0-9A-Z]{16})"
                 r"|(?:password|api[_-]?key)\s*[:=]\s*\S+", raw):
        invalid("possible credential found in selected records; redact before export",
                "WSC010")
    output = args.output.expanduser()
    relative = output
    if output.is_absolute():
        try:
            relative = output.relative_to(root)
        except ValueError:
            invalid("export output must stay inside selected learner workspace",
                    "WSC004")
    if relative.suffix.lower() != ".json":
        invalid("local evidence export filename must end in .json", "WSC004")
    try:
        result = publish_file_new(root, relative, raw.encode("utf-8"))
    except PublicationError as exc:
        invalid(str(exc), "WSC004")
    print(f"Exported {len(selected)} explicitly selected attempt(s): "
          f"{result.relative_to(root).as_posix()}")
    print("No artifact bytes or unrelated workspace records included.")
    print("Review user-authored text for private data before sharing.")


def assessment_context(args) -> None:
    """Read original source-bound requirements; never grade or write records."""
    from .evidence import load_reader
    reader = load_reader()
    consumer = reader.load_consumer()
    lock = args.lock or Path.cwd() / "oee-curriculum.lock.json"
    try:
        expected = consumer.load_lock(lock)
        raw = reader.read_pinned_export(lock, args.store, args.code)
        consumer.check_export(raw, expected)
        if raw["course"]["code"] != args.code:
            raise ValueError("wrong course returned")
        context = reader.read_pinned_artifact(lock, args.store, args.code, "assessment-context")
        import runpy
        checker = runpy.run_path(str(ROOT / "scripts/verify-assessment-context.py"))
        hashes = checker["manifest_hashes"](raw["source"], args.store)
        checker["check_context"](context, raw, hashes)
    except reader.PinnedSourceError as exc:
        incomplete("assessment context unavailable: " + str(exc), "WSC003")
    except (consumer.ContractError, ValueError, OSError, TypeError, KeyError) as exc:
        invalid("assessment context rejected: " + str(exc), "WSC005")
    # ASCII escapes keep JSON portable even on Windows legacy stdout encodings.
    # JSON decoding restores the original Unicode Markdown without alteration.
    print(json.dumps(context, ensure_ascii=True, sort_keys=True, indent=2))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, prog="python -m oee_workspace")
    commands = p.add_subparsers(dest="command", required=True)

    def release_options(parser):
        parser.add_argument("--lock", type=Path, default=None,
                            help="reviewed release lock (default: ./oee-curriculum.lock.json)")
        parser.add_argument("--store", type=Path, default=None,
                            help="existing trusted installed-release cache")

    def dest_option(parser):
        parser.add_argument("--dest", type=Path, required=True,
                            help="existing learner-owned destination directory")

    doc = commands.add_parser("doctor", help="probe local Toolkit and exact course source")
    release_options(doc)
    doc.set_defaults(run=doctor)

    context = commands.add_parser("assessment-context", help="read verified original assessment requirements (JSON)")
    context.add_argument("code")
    release_options(context)
    context.set_defaults(run=assessment_context)

    course = commands.add_parser("course", help="course workspace operations")
    courses = course.add_subparsers(dest="course_command", required=True)
    add = courses.add_parser("add", help="stage a new canonical course workspace")
    add.add_argument("code")
    release_options(add)
    dest_option(add)
    add.set_defaults(run=course_add)

    resources = commands.add_parser("resources", help="public resource maps")
    resource_cmds = resources.add_subparsers(dest="resource_command", required=True)
    check = resource_cmds.add_parser("check", help="validate one exact-release-keyed v3 map")
    release_options(check)
    check.add_argument("--map", type=Path, required=True)
    check.set_defaults(run=resources_check)

    ev = commands.add_parser("evidence", help="learner assessment evidence")
    ev_cmds = ev.add_subparsers(dest="evidence_command", required=True)
    init = ev_cmds.add_parser("init", help="create fresh unreviewed UUID attempt")
    release_options(init)
    init.add_argument("--course", required=True)
    init.add_argument("--assessment", required=True)
    dest_option(init)
    init.set_defaults(run=evidence_init)
    ev_check = ev_cmds.add_parser("check", help="validate one local pinned attempt")
    release_options(ev_check)
    ev_check.add_argument("--path", type=Path, required=True)
    dest_option(ev_check)
    ev_check.set_defaults(run=evidence_check)

    status_command = commands.add_parser("status", help="read-only assessment projection")
    release_options(status_command)
    dest_option(status_command)
    status_command.add_argument("--course", help="optional empty-course projection")
    status_command.set_defaults(run=status)

    export_command = commands.add_parser("export", help="write selected local evidence JSON")
    release_options(export_command)
    dest_option(export_command)
    export_command.add_argument("--output", type=Path, required=True)
    export_command.add_argument("--attempt", action="append", required=True,
                                help="UUID to include; repeat for additional attempts")
    export_command.set_defaults(run=export)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if sys.version_info < (3, 11):
            incomplete("Python >= 3.11 is required", "WSC003")
        args.run(args)
    except EvidenceIssue as exc:
        print(f"{exc.code} [{exc.kind}]: {exc}", file=sys.stderr)
        return 3 if exc.kind == "incomplete" else 1
    except (PublicationError, FileExistsError, PermissionError) as exc:
        print(f"WSC004 [invalid]: {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError, UnicodeError, KeyError,
            subprocess.TimeoutExpired) as exc:
        print(f"WSC999 [internal]: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
