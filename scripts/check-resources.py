#!/usr/bin/env python3
"""Validate public resource records and maps against a local canonical OEE checkout.

Only Python 3 standard library is needed. JSON Schemas under resources/schemas
describe the interchange format; these checks additionally enforce OEE identity
and cross-file invariants that JSON Schema alone cannot express.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
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
COURSE_MODULE = re.compile(r"(?m)^### Module ([1-9][0-9]*) — ([^\n]+)$")
COURSE_LESSON = re.compile(r"(?m)^([1-9][0-9]*)\. \*\*(.*?)\*\* — \`(?:lesson|test|lab)\`$")
SHA = re.compile(r"[a-f0-9]{40}\Z")


class Check:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, location: str, msg: str):
        self.errors.append(f"{location}: {msg}")

    def warn(self, location: str, msg: str):
        self.warnings.append(f"{location}: {msg}")


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


def course_structure(path: Path, check: Check):
    try:
        body = path.read_text(encoding="utf-8")
    except OSError as exc:
        check.error(str(path), f"canonical OEE course not found: {exc}")
        return None
    heads = list(COURSE_MODULE.finditer(body))
    if not heads:
        check.error(str(path), "OEE course has no numbered module headings")
        return None
    modules = {}
    for index, match in enumerate(heads):
        number = int(match.group(1))
        boundary = heads[index + 1].start() if index + 1 < len(heads) else body.find("\n## Completion requirements", match.end())
        if boundary < 0:
            boundary = len(body)
        section = body[match.end():boundary]
        lessons = {int(m.group(1)): m.group(2) for m in COURSE_LESSON.finditer(section)}
        if number in modules:
            check.error(str(path), f"duplicate OEE module {number}")
        modules[number] = (match.group(2).strip(), lessons)
    return modules


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


def validate_maps(oee: Path, catalog: dict, check: Check, course_filter: str | None = None):
    paths = sorted(MAPPINGS.rglob("*.json"))
    if course_filter:
        paths = [p for p in paths if p.stem == course_filter]
    if not paths:
        check.error("mappings", "no mappings found")
    for path in paths:
        loc = str(path.relative_to(ROOT))
        mapping = load_json(path, check)
        if not isinstance(mapping, dict):
            check.error(loc, "mapping must be an object")
            continue
        if mapping.get("schemaVersion") != 1 or mapping.get("status") not in ("draft", "reviewed"):
            check.error(loc, "expected schemaVersion 1 and status draft/reviewed")
        canon = mapping.get("curriculum")
        if not isinstance(canon, dict):
            check.error(loc, "curriculum must be an object")
            continue
        course = canon.get("course")
        match = CODE.fullmatch(course) if isinstance(course, str) else None
        if not match:
            check.error(loc, "invalid canonical course code")
            continue
        program = match.group(1)
        wanted = f"curriculum/{program}/{course}.md"
        if path.parent.name != program or path.stem != course:
            check.error(loc, f"mapping path must be mappings/{program}/{course}.json")
        if canon.get("repository") != "0xbuffdev/open-engineering-education" or canon.get("path") != wanted:
            check.error(loc, f"curriculum repository/path must be canonical {wanted}")
            continue
        revision = canon.get("revision")
        if not isinstance(revision, str) or not SHA.fullmatch(revision):
            check.error(loc, "curriculum.revision must be a 40-character Git SHA")
        course_modules = course_structure(oee / wanted, check)
        if course_modules is None:
            continue
        module_items = mapping.get("modules")
        if not isinstance(module_items, list):
            check.error(loc, "modules must be an array")
            continue
        seen = set()
        for module in module_items:
            if not isinstance(module, dict):
                check.error(loc, "module must be an object")
                continue
            number = module.get("number")
            if type(number) is not int or number < 1 or number in seen:
                check.error(loc, f"invalid/duplicate module number {number!r}")
                continue
            seen.add(number)
            ml = f"{loc}: module {number}"
            if number not in course_modules:
                check.error(ml, "module not found in OEE")
                continue
            canonical_title, canonical_lessons = course_modules[number]
            if module.get("title") != canonical_title:
                check.error(ml, f"title differs from OEE ({canonical_title})")
            coverage = module.get("coverage")
            if coverage not in COVERAGE:
                check.error(ml, "invalid coverage")
            if coverage == "partial" and not text(module.get("gap")):
                check.error(ml, "partial module needs an explicit gap explanation")
            entries = module.get("resources")
            if not isinstance(entries, list):
                check.error(ml, "resources must be an array")
                continue
            if coverage == "mapped" and not entries:
                check.error(ml, "mapped module has no resources")
            if coverage == "unmapped" and entries:
                check.error(ml, "unmapped module should not carry resources")
            used = set()
            free_verified = False
            for entry in entries:
                if not isinstance(entry, dict):
                    check.error(ml, "resource entry must be an object")
                    continue
                rid = entry.get("resource")
                item = catalog.get(rid) if isinstance(rid, str) else None
                if not item:
                    check.error(ml, f"unknown resource {rid!r}")
                    continue
                role = entry.get("role")
                if role not in RESOURCE_ROLES or not text(entry.get("purpose")):
                    check.error(ml, f"{rid}: invalid role or missing purpose")
                status = entry.get("verification")
                if status not in REVIEW_STATES:
                    check.error(ml, f"{rid}: invalid verification state")
                if status == "verified" and item.get("verification", {}).get("status") != "verified":
                    check.error(ml, f"{rid}: cannot verify a map entry using unverified catalogue metadata")
                part = entry.get("part")
                if not valid_part(part):
                    check.error(ml, f"{rid}: invalid chapter/project/section locator")
                lesson = entry.get("lesson")
                if lesson is not None:
                    if not isinstance(lesson, dict) or type(lesson.get("number")) is not int or canonical_lessons.get(lesson["number"]) != lesson.get("title"):
                        check.error(ml, f"{rid}: lesson reference does not match canonical OEE")
                key = (rid, json.dumps(part, sort_keys=True), json.dumps(lesson, sort_keys=True))
                if key in used:
                    check.error(ml, f"{rid}: duplicate resource/locator/lesson entry")
                used.add(key)
                if status == "verified" and item.get("access", {}).get("mode") in ("free", "mixed"):
                    free_verified = True
            if coverage == "mapped" and not free_verified:
                check.error(ml, "mapped status needs at least one verified free/companion-material resource")
            if coverage == "partial":
                check.warn(ml, module.get("gap", "open coverage gap"))
        if set(course_modules) != seen:
            check.error(loc, f"module coverage differs from OEE: missing {sorted(set(course_modules)-seen)}, extra {sorted(seen-set(course_modules))}")
    try:
        head = subprocess.run(["git", "-C", str(oee), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        for path in paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            expected = data.get("curriculum", {}).get("revision")
            if expected and expected != head:
                check.warn(str(path.relative_to(ROOT)), f"source revision {expected[:12]} differs from local OEE HEAD {head[:12]}; structural checks still ran")
    except (OSError, subprocess.CalledProcessError, ValueError):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oee", type=Path, default=Path("../open-engineering-education"), help="path to a local canonical OEE checkout")
    parser.add_argument("--course", help="validate only the named course map")
    args = parser.parse_args()
    check = Check()
    catalog = validate_catalog(check)
    validate_maps(args.oee.resolve(), catalog, check, args.course)
    for warning in check.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    for error in check.errors:
        print(f"ERROR: {error}", file=sys.stderr)
    print(f"Resource check: {len(catalog)} catalogued IDs, {len(check.warnings)} warnings, {len(check.errors)} errors")
    return 1 if check.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
