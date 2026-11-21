#!/usr/bin/env python3
"""Validate OEE Workspace resource-map v3 shape and immutable release identities.

Standard-library only. No historical-schema adapter or moving-HEAD source fallback.
"""
from __future__ import annotations

import argparse
import functools
import importlib.util
import subprocess
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "resources" / "catalog"
MAPPINGS = ROOT / "resources" / "mappings"
RESOURCE_KINDS = {"book", "course-material", "interactive-tool", "documentation", "article", "video"}
RESOURCE_ROLES = {"reference", "practice", "optional"}
REVIEW_STATES = {"verified", "review-needed"}
COVERAGE = {"mapped", "partial", "unmapped"}
IDENTIFIER = re.compile(r"(?:B|R)[1-9][0-9]*\Z")
CODE = re.compile(r"([A-Z]{2,4})([1-9][0-9]*)\Z")
SHA = re.compile(r"[a-f0-9]{64}\Z")
RELEASE = re.compile(r"[0-9]{4}\.(?:0[1-9]|1[0-2])\.[1-9][0-9]*\Z")


class Check:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.incomplete: list[str] = []

    def error(self, location: str, msg: str):
        self.errors.append(f"{location}: {msg}")

    def warn(self, location: str, msg: str):
        self.warnings.append(f"{location}: {msg}")

    def missing(self, location: str, msg: str):
        self.incomplete.append(f"{location}: {msg}")


def text(value):
    return isinstance(value, str) and bool(value.strip())


def url(value):
    if not text(value):
        return False
    parsed = urlparse(value)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def load_json(path: Path, check: Check):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        check.error(str(path.relative_to(ROOT)), f"cannot read JSON: {exc}")
        return None


def validate_catalog(check: Check):
    result = {}
    for path in sorted(CATALOG.rglob("*.json")):
        loc = str(path.relative_to(ROOT))
        item = load_json(path, check)
        if not isinstance(item, dict):
            check.error(loc, "resource must be an object")
            continue
        rid = item.get("id")
        if not isinstance(rid, str) or not IDENTIFIER.fullmatch(rid):
            check.error(loc, "invalid resource ID")
            continue
        if rid != path.stem:
            check.error(loc, f"ID {rid} must match filename {path.stem}")
        if rid in result:
            check.error(loc, f"duplicate resource ID {rid}")
        result[rid] = item
        if item.get("kind") not in RESOURCE_KINDS or not text(item.get("title")):
            check.error(loc, "invalid kind or missing title")
        access = item.get("access")
        if not isinstance(access, dict) or access.get("mode") not in ("free", "paid", "mixed"):
            check.error(loc, "access.mode must be free, paid or mixed")
        else:
            for field in ("url", "freeMaterialsUrl"):
                if field in access and not url(access[field]):
                    check.error(loc, f"access.{field} must be an absolute http(s) URL")
            if access["mode"] == "free" and not url(access.get("url")):
                check.error(loc, "free resource must include a usable URL")
        verify = item.get("verification")
        if not isinstance(verify, dict) or verify.get("status") not in REVIEW_STATES or not text(verify.get("basis")):
            check.error(loc, "verification must include valid status and basis")
        elif verify["status"] == "verified" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(verify.get("checkedOn", ""))):
            check.error(loc, "verified resource must carry checkedOn YYYY-MM-DD")
        if "isbn13" in item and not re.fullmatch(r"\d{13}", str(item["isbn13"])):
            check.error(loc, "isbn13 must contain 13 digits")
    if not result:
        check.error("catalog", "no resources found")
    return result


def valid_part(part):
    if not isinstance(part, dict):
        return False
    kind = part.get("type")
    if kind in ("chapters", "projects"):
        nums = part.get("numbers")
        return set(part) == {"type", "numbers"} and isinstance(nums, list) and bool(nums) and all(type(x) is int and x > 0 for x in nums) and len(nums) == len(set(nums))
    if kind in ("section-titles", "topics"):
        values = part.get("titles")
        return set(part) == {"type", "titles"} and isinstance(values, list) and bool(values) and all(text(x) for x in values) and len(values) == len(set(values))
    if kind == "section-range":
        return set(part) == {"type", "start", "end"} and text(part.get("start")) and text(part.get("end"))
    return False


def known_fields(value, expected, loc, check):
    for key in sorted(set(value) - set(expected)):
        check.error(loc, f"unknown field {key!r}")


def validate_map_shape(mapping, catalog, check, loc):
    """Validate schema-v3 shape/catalogue; source references require release export."""
    before = len(check.errors)
    if not isinstance(mapping, dict):
        check.error(loc, "mapping must be an object")
        return False
    if type(mapping.get("schemaVersion")) is not int or mapping["schemaVersion"] != 3:
        check.error(loc, "unsupported_schema: only release-keyed resource-map v3 is accepted")
        return False
    known_fields(mapping, {"schemaVersion", "status", "curriculum", "modules", "notes"}, loc, check)
    if mapping.get("status") not in ("draft", "reviewed"):
        check.error(loc, "invalid map status")
    if "notes" in mapping and not isinstance(mapping["notes"], str):
        check.error(loc, "notes must be a string")
    canon = mapping.get("curriculum")
    if not isinstance(canon, dict):
        check.error(loc, "curriculum must be an object")
        return False
    known_fields(canon, {"repository", "releaseId", "manifestSha256", "courseSha256", "specification", "course", "path"}, loc, check)
    course = canon.get("course")
    match = CODE.fullmatch(course) if isinstance(course, str) else None
    if not match:
        check.error(loc, "invalid canonical course code")
        return False
    program = match.group(1)
    wanted = f"curriculum/{program}/{course}.md"
    if canon.get("repository") != "0xbuffdev/open-engineering-education":
        check.error(loc, "invalid canonical OEE repository")
    if canon.get("path") != wanted:
        check.error(loc, f"invalid canonical OEE path; expected {wanted}")
    if canon.get("specification") != "v0.2.0":
        check.error(loc, "unsupported_format: only OEE v0.2.0 is supported")
    release_id = canon.get("releaseId")
    if not isinstance(release_id, str) or not RELEASE.fullmatch(release_id):
        check.error(loc, "curriculum.releaseId must be YYYY.MM.N")
    for field in ("manifestSha256", "courseSha256"):
        value = canon.get(field)
        if not isinstance(value, str) or not SHA.fullmatch(value):
            check.error(loc, f"curriculum.{field} must be a full lowercase SHA-256")
    modules = mapping.get("modules")
    if not isinstance(modules, list) or not modules:
        check.error(loc, "modules must be a nonempty array")
        return False
    for index, module in enumerate(modules, start=1):
        ml = f"{loc}: module {index}"
        if not isinstance(module, dict):
            check.error(ml, "module must be an object")
            continue
        known_fields(module, {"number", "title", "coverage", "gap", "resources"}, ml, check)
        if type(module.get("number")) is not int or module["number"] != index:
            check.error(ml, "module numbers must be ordered and contiguous from 1")
        if not text(module.get("title")):
            check.error(ml, "missing module title")
        coverage = module.get("coverage")
        if coverage not in COVERAGE:
            check.error(ml, "invalid coverage")
        if coverage in ("partial", "unmapped") and not text(module.get("gap")):
            check.error(ml, f"{coverage} module requires an explicit gap")
        if "gap" in module and not text(module["gap"]):
            check.error(ml, "gap must contain explanatory text")
        entries = module.get("resources")
        if not isinstance(entries, list):
            check.error(ml, "resources must be an array")
            continue
        if coverage == "mapped" and not entries:
            check.error(ml, "mapped module requires resource anchors")
        if coverage == "unmapped" and entries:
            check.error(ml, "unmapped module cannot claim resources")
        seen = set()
        free_verified = False
        for ordinal, item in enumerate(entries, start=1):
            el = f"{ml}: entry {ordinal}"
            if not isinstance(item, dict):
                check.error(el, "resource entry must be an object")
                continue
            known_fields(item, {"resource", "role", "part", "purpose", "verification",
                                "lesson", "outcomeIds", "assessmentIds"}, el, check)
            rid = item.get("resource")
            record = catalog.get(rid) if isinstance(rid, str) else None
            if record is None:
                check.error(el, f"unknown catalogue resource {rid!r}")
            if item.get("role") not in RESOURCE_ROLES or not text(item.get("purpose")):
                check.error(el, "invalid role or missing purpose")
            state = item.get("verification")
            if state not in REVIEW_STATES:
                check.error(el, "invalid mapping verification")
            if state == "verified" and record and record.get("verification", {}).get("status") != "verified":
                check.error(el, "catalogue cannot support verified mapping claim")
            part = item.get("part")
            if not valid_part(part):
                check.error(el, "invalid chapter/project/section locator")
            lesson = item.get("lesson")
            if lesson is not None:
                if not isinstance(lesson, dict):
                    check.error(el, "lesson must be an object")
                else:
                    known_fields(lesson, {"number", "title"}, el + ": lesson", check)
                    if type(lesson.get("number")) is not int or lesson["number"] < 1 or not text(lesson.get("title")):
                        check.error(el, "invalid revision-scoped lesson locator")
            for field, suffix in (("outcomeIds", "O"), ("assessmentIds", "AS")):
                if field in item:
                    ids = item[field]
                    pattern = re.compile(rf"{re.escape(course)}-{suffix}[1-9][0-9]*\Z")
                    if not isinstance(ids, list) or not ids or any(
                            not isinstance(value, str) or not pattern.fullmatch(value) for value in ids):
                        check.error(el, f"{field} must contain canonical {course} IDs")
                    elif len(ids) != len(set(ids)):
                        check.error(el, f"duplicate {field}")
            key = (str(rid), json.dumps(part, sort_keys=True), json.dumps(lesson, sort_keys=True))
            if key in seen:
                check.error(el, "duplicate resource/part/lesson reference")
            seen.add(key)
            if record and state == "verified" and record.get("access", {}).get("mode") in ("free", "mixed"):
                free_verified = True
        if coverage == "mapped" and not free_verified:
            check.error(ml, "mapped coverage requires verified free/companion anchor")
        if coverage == "partial" and text(module.get("gap")):
            check.warn(ml, module["gap"])
    return len(check.errors) == before


@functools.lru_cache(maxsize=1)
def load_consumer():
    name = "oee_workspace_export_consumer"
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / "verify-oee-export.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class PinnedSourceError(Exception):
    """Typed failure to obtain a supported immutable OEE course export."""

    def __init__(self, category: str, detail: str):
        super().__init__(detail)
        self.category = category


def read_pinned_export(lock: Path, store: Path | None, course: str) -> dict:
    """Call only the installed first-party Toolkit release consumer (no Git)."""
    if not isinstance(course, str) or not CODE.fullmatch(course):
        raise PinnedSourceError("invalid_reference", "invalid canonical course code")
    # Toolkit enforces the reviewed lock, signature-installed store, and all
    # source bytes. No repository/local Git or moving-ref fallback exists.
    argv = [sys.executable, "-m", "oee_toolkit", "export", course,
            "--lock", str(lock), "--output", "-"]
    if store is not None:
        argv.extend(("--store", str(store)))
    try:
        result = subprocess.run(argv, capture_output=True, timeout=90, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PinnedSourceError("tool_error", f"Toolkit execution: {type(exc).__name__}") from exc
    if result.returncode:
        stderr = result.stderr.decode("utf-8", errors="replace")
        detail = " ".join(stderr.strip().splitlines()[:3])[:500] or "Toolkit release unavailable"
        if result.returncode in (2, 3):
            category = "source_missing" if result.returncode == 3 else "unsupported_format"
        elif result.returncode == 1:
            category = "invalid_reference"
        else:
            category = "tool_error"
        raise PinnedSourceError(category, detail)
    try:
        exported = json.loads(result.stdout.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise PinnedSourceError("tool_error", "invalid Toolkit export JSON") from exc
    if not isinstance(exported, dict):
        raise PinnedSourceError("tool_error", "Toolkit export must be an object")
    return exported


def check_pinned_map(mapping: dict, lock: Path, store: Path | None = None) -> dict:
    canon = mapping["curriculum"]
    consumer = load_consumer()
    expected = consumer.load_lock(lock)
    exported = read_pinned_export(lock, store, canon["course"])
    checked = consumer.check_export(exported, expected)
    consumer.check_map(mapping, checked)
    return checked


def validate_maps(catalog, check, course_filter=None, lock=None, store=None):
    paths = sorted(MAPPINGS.rglob("*.json"))
    if course_filter:
        paths = [p for p in paths if p.stem == course_filter]
    if not paths:
        if course_filter:
            check.error("mappings", f"unmapped course {course_filter}; no active release map")
        return
    selected_lock = lock if lock is not None else Path.cwd() / "oee-curriculum.lock.json"
    for path in paths:
        loc = str(path.relative_to(ROOT))
        mapping = load_json(path, check)
        if not validate_map_shape(mapping, catalog, check, loc):
            continue
        canon = mapping["curriculum"]
        course = canon["course"]
        program = CODE.fullmatch(course).group(1)
        if path.parent.name != program or path.stem != course:
            check.error(loc, f"map path must be mappings/{program}/{course}.json")
            continue
        try:
            check_pinned_map(mapping, selected_lock, store)
        except PinnedSourceError as exc:
            if exc.category in ("source_missing", "unsupported_format"):
                check.missing(loc, f"{exc.category}: {exc}")
            else:
                check.error(loc, f"{exc.category}: {exc}")
        except load_consumer().ContractError as exc:
            if exc.category in ("missing_input", "unsupported_format"):
                check.missing(loc, f"{exc.category}: {exc.code}: {exc}")
            else:
                check.error(loc, f"{exc.category}: {exc.code}: {exc}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, default=None,
                        help="reviewed project lock (default: current directory only)")
    parser.add_argument("--store", type=Path, default=None,
                        help="existing trusted installed-release store")
    parser.add_argument("--course", help="check one active v3 map")
    parser.add_argument("--json", action="store_true", help="machine-readable diagnostics")
    args = parser.parse_args()
    check = Check()
    catalog = validate_catalog(check)
    validate_maps(catalog, check, args.course, args.lock, args.store)
    status = "failed" if check.errors else "incomplete" if check.incomplete else "passed"
    if args.json:
        print(json.dumps({
            "outcome": status, "errors": check.errors,
            "incomplete": check.incomplete, "warnings": check.warnings,
            "cataloguedResources": len(catalog),
            "manualReviewRequired": True
        }, sort_keys=True, separators=(",", ":")))
    else:
        for warning in check.warnings:
            print(f"WARNING: {warning}", file=sys.stderr)
        for missing in check.incomplete:
            print(f"INCOMPLETE: {missing}", file=sys.stderr)
        for error in check.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Resource check: {len(catalog)} catalogue IDs, "
              f"{len(check.warnings)} warnings, {len(check.incomplete)} incomplete, "
              f"{len(check.errors)} errors")
        if not list(MAPPINGS.rglob("*.json")):
            print("No active release-keyed resource maps; catalog validation only.")
    return {"passed": 0, "failed": 1, "incomplete": 3}[status]


if __name__ == "__main__":
    raise SystemExit(main())
