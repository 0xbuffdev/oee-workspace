#!/usr/bin/env python3
"""Offline OEE Toolkit export consumer contract (WS-I11 / OT-I06).

Checks a *derived* OEE export v2 and optional Workspace v3 map against an
independently reviewed immutable release lock. Does not re-parse course Markdown, read moving HEAD,
grade learners, validate books, or recognize legacy source/map formats.

Full resource-map editorial validation remains WS-I03/WS-I01/WS-I02.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

SOURCE = "0xbuffdev/open-engineering-education"
SHA = re.compile(r"[0-9a-f]{64}\Z")
COMMIT = re.compile(r"[0-9a-f]{40}\Z")
RELEASE = re.compile(r"[0-9]{4}\.(?:0[1-9]|1[0-2])\.[1-9][0-9]*\Z")
CODE = re.compile(r"[A-Z]{2,6}[1-9][0-9]*\Z")
OUTCOME = re.compile(r"[A-Z]{2,6}[1-9][0-9]*-O[1-9][0-9]*\Z")
ASSESSMENT = re.compile(r"[A-Z]{2,6}[1-9][0-9]*-AS[1-9][0-9]*\Z")


class ContractError(Exception):
    def __init__(self, code: str, category: str, message: str):
        super().__init__(message)
        self.code = code
        self.category = category

    def as_dict(self) -> dict:
        return {"code": self.code, "category": self.category, "message": str(self)}


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise ContractError(code, "invalid_reference", message)


def obj(value, name: str) -> dict:
    require(type(value) is dict, "WSX001", f"{name} must be an object")
    return value


def array(value, name: str) -> list:
    require(type(value) is list, "WSX001", f"{name} must be an array")
    return value


def string(value, name: str) -> str:
    require(type(value) is str and bool(value.strip()), "WSX001",
            f"{name} must be a nonempty string")
    return value


def location(value, name: str) -> None:
    loc = obj(value, name)
    string(loc.get("path"), f"{name}.path")
    require(type(loc.get("line")) is int and loc["line"] > 0,
            "WSX001", f"{name}.line must be positive")


def unique(values: list[str], name: str) -> None:
    require(len(values) == len(set(values)), "WSX002", f"{name} contains duplicates")


def refs(value, pattern, name: str) -> list[str]:
    items = array(value, name)
    require(all(type(item) is str and pattern.fullmatch(item) for item in items),
            "WSX003", f"{name} contains invalid identifiers")
    unique(items, name)
    return items


def check_export(data: dict, expected: dict) -> dict:
    """Validate a supported, structurally complete OEE export without Markdown.

    A structural-consumer success is not proof of curriculum conformance.
    """
    obj(data, "export")
    require(set(data) == {"exportVersion", "source", "toolkit", "course",
                         "outcomes", "assessments", "modules", "coverage", "validation"},
            "WSX004", "unsupported Toolkit export properties")
    if type(data.get("exportVersion")) is not int or data["exportVersion"] != 2:
        raise ContractError("WSX004", "unsupported_format",
                            "requires exactly OEE Toolkit exportVersion 2")
    source = obj(data.get("source"), "source")
    require(set(source) == {"repository", "releaseId", "manifestSha256",
                            "specification", "coursePath", "courseSha256", "originCommit"},
            "WSX004", "unsupported Toolkit v2 source properties")
    if source.get("repository") != SOURCE or source.get("specification") != "v0.2.0":
        raise ContractError("WSX004", "unsupported_format",
                            "unsupported source repository/specification")
    require(type(expected) is dict and
            type(expected.get("releaseId")) is str and
            RELEASE.fullmatch(expected["releaseId"]) and
            type(expected.get("manifestSha256")) is str and
            SHA.fullmatch(expected["manifestSha256"]),
            "WSX005", "independent release lock identity is invalid")
    require(type(source.get("releaseId")) is str and
            RELEASE.fullmatch(source["releaseId"]) and
            type(source.get("manifestSha256")) is str and
            SHA.fullmatch(source["manifestSha256"]) and
            type(source.get("courseSha256")) is str and
            SHA.fullmatch(source["courseSha256"]) and
            type(source.get("originCommit")) is str and
            COMMIT.fullmatch(source["originCommit"]),
            "WSX005", "export release, course or provenance digest is invalid")
    require(source["releaseId"] == expected["releaseId"] and
            source["manifestSha256"] == expected["manifestSha256"],
            "WSX005", "export identity does not match independently selected release lock")
    toolkit = obj(data.get("toolkit"), "toolkit")
    require(set(toolkit) == {"toolVersion", "ruleSetVersion"},
            "WSX004", "unsupported Toolkit software identity properties")
    string(toolkit.get("toolVersion"), "toolkit.toolVersion")
    require(toolkit.get("ruleSetVersion") == "v0.2.0-ot-i04",
            "WSX004", "unsupported OEE Toolkit rule set")
    course = obj(data.get("course"), "course")
    code = course.get("code")
    require(type(code) is str and CODE.fullmatch(code), "WSX006", "invalid course code")
    program = re.match(r"^[A-Z]{2,6}", code).group()
    require(course.get("program") == program, "WSX006", "course program/code mismatch")
    require(source.get("coursePath") == f"curriculum/{program}/{code}.md",
            "WSX006", "course path/code mismatch")
    require(course.get("type") in ("course", "project") and
            course.get("status") in ("draft", "tested", "verified"),
            "WSX006", "invalid exported course type or status")
    refs(course.get("prerequisites"), CODE, "course.prerequisites")

    validation = obj(data.get("validation"), "validation")
    require(validation.get("structural") == "passed" and
            validation.get("manualReviewRequired") is True,
            "WSX007", "export is not structurally passed and marked for manual review")
    outcomes = {}
    for item in array(data.get("outcomes"), "outcomes"):
        item = obj(item, "outcome")
        ident = item.get("id")
        require(type(ident) is str and OUTCOME.fullmatch(ident) and
                ident.startswith(code + "-O"), "WSX008", "invalid/foreign outcome ID")
        require(ident not in outcomes, "WSX008", f"duplicate outcome {ident}")
        string(item.get("description"), "outcome.description")
        location(item.get("location"), "outcome.location")
        outcomes[ident] = item
    require(bool(outcomes), "WSX008", "no outcomes present")

    assessments = {}
    expected_coverage = {ident: set() for ident in outcomes}
    for item in array(data.get("assessments"), "assessments"):
        item = obj(item, "assessment")
        ident = item.get("id")
        require(type(ident) is str and ASSESSMENT.fullmatch(ident) and
                ident.startswith(code + "-AS"), "WSX009", "invalid/foreign assessment ID")
        require(ident not in assessments, "WSX009", f"duplicate assessment {ident}")
        require(type(item.get("required")) is bool, "WSX009",
                "required assessment flag must be boolean")
        for field in ("work", "criteria", "evidence"):
            string(item.get(field), f"assessment.{field}")
        location(item.get("location"), "assessment.location")
        links = refs(item.get("outcomeIds"), OUTCOME, "assessment.outcomeIds")
        require(bool(links) and set(links).issubset(outcomes), "WSX009",
                f"assessment {ident} references unknown outcomes")
        if item["required"]:
            for ref in links:
                expected_coverage[ref].add(ident)
        assessments[ident] = item
    require(bool(assessments), "WSX009", "no assessments present")

    coverage = obj(data.get("coverage"), "coverage")
    require(set(coverage) == set(outcomes), "WSX010",
            "coverage keys differ from canonical outcomes")
    for ident, required in expected_coverage.items():
        got = refs(coverage[ident], ASSESSMENT, f"coverage.{ident}")
        require(bool(required) and set(got) == required, "WSX010",
                f"required assessment coverage mismatch for {ident}")

    modules = {}
    for item in array(data.get("modules"), "modules"):
        item = obj(item, "module")
        number = item.get("number")
        require(type(number) is int and number >= 1 and number not in modules,
                "WSX011", "module number invalid or duplicated")
        string(item.get("title"), "module.title")
        linked_outcomes = refs(item.get("outcomeIds"), OUTCOME, "module.outcomeIds")
        require(set(linked_outcomes).issubset(outcomes), "WSX011",
                "module references unknown course outcomes")
        lessons = array(item.get("lessons"), "module.lessons")
        require(bool(lessons), "WSX011", "module has no ordered lessons")
        for index, lesson in enumerate(lessons, start=1):
            lesson = obj(lesson, "lesson")
            require(type(lesson.get("ordinal")) is int and lesson["ordinal"] == index,
                    "WSX011", "lesson order is not sequential")
            string(lesson.get("title"), "lesson.title")
        modules[number] = item
    require(list(modules) == list(range(1, len(modules) + 1)),
            "WSX011", "module order must be sequential from 1")
    return {
        "source": source, "course": code, "outcomes": outcomes,
        "assessments": assessments, "modules": modules,
    }


def check_map(mapping: dict, verified: dict) -> None:
    """Workspace v3 consumer seam; editorial checks remain in check-resources."""
    obj(mapping, "map")
    if type(mapping.get("schemaVersion")) is not int or mapping["schemaVersion"] != 3:
        raise ContractError("WSX012", "unsupported_format",
                            "only release-keyed resource-map schemaVersion 3 is supported")
    ref = obj(mapping.get("curriculum"), "map.curriculum")
    source = verified["source"]
    require(
        ref.get("repository") == SOURCE and
        ref.get("specification") == "v0.2.0" and
        ref.get("releaseId") == source["releaseId"] and
        ref.get("manifestSha256") == source["manifestSha256"] and
        ref.get("courseSha256") == source["courseSha256"] and
        ref.get("course") == verified["course"] and
        ref.get("path") == source["coursePath"],
        "WSX013", "resource-map source identity does not match pinned export",
    )
    require(mapping.get("status") in ("draft", "reviewed"), "WSX013",
            "resource-map status must be draft or reviewed")
    listed = array(mapping.get("modules"), "map.modules")
    expected = verified["modules"]
    require(len(listed) == len(expected), "WSX014",
            "resource-map module count differs from pinned export")
    for index, item in enumerate(listed, 1):
        module = obj(item, "map.module")
        current = expected[index]
        require(module.get("number") == index and
                module.get("title") == current["title"],
                "WSX014", f"resource-map module {index} locator differs from pinned source")
        for resource in array(module.get("resources"), "map.module.resources"):
            resource = obj(resource, "resource")
            for key, ids in (("outcomeIds", verified["outcomes"]),
                             ("assessmentIds", verified["assessments"])):
                if key in resource:
                    used = refs(resource[key],
                                OUTCOME if key == "outcomeIds" else ASSESSMENT,
                                f"resource.{key}")
                    require(set(used).issubset(ids), "WSX015",
                            f"unknown canonical ID in resource.{key}")
            if "lesson" in resource:
                lesson = obj(resource["lesson"], "resource.lesson")
                number = lesson.get("number")
                lessons = current["lessons"]
                require(type(number) is int and 1 <= number <= len(lessons) and
                        lesson.get("title") == lessons[number - 1]["title"],
                        "WSX016", "resource lesson locator differs from pinned source")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as exc:
        raise ContractError("WSX017", "missing_input",
                            f"cannot read valid JSON: {type(exc).__name__}") from exc


def load_lock(path: Path) -> dict:
    """Read only an explicit reviewed lock; Toolkit verifies it again offline."""
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 4096:
        raise ContractError("WSX017", "missing_input", "release lock is absent or unsafe")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON property")
            result[key] = value
        return result
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    except (ValueError, UnicodeError, OSError) as exc:
        raise ContractError("WSX017", "missing_input", "invalid release lock JSON") from exc
    if (type(value) is not dict or set(value) !=
            {"formatVersion", "releaseId", "manifestSha256"} or
            type(value["formatVersion"]) is not int or value["formatVersion"] != 1 or
            type(value["releaseId"]) is not str or not RELEASE.fullmatch(value["releaseId"]) or
            type(value["manifestSha256"]) is not str or
            not SHA.fullmatch(value["manifestSha256"])):
        raise ContractError("WSX004", "unsupported_format", "invalid current release lock")
    return value


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", type=Path, required=True,
                        help="first-party OEE Toolkit exportVersion 2 JSON")
    parser.add_argument("--lock", type=Path, required=True,
                        help="independently approved oee-curriculum.lock.json")
    parser.add_argument("--map", type=Path, help="optional release-keyed resource-map v3")
    parser.add_argument("--json", action="store_true", help="deterministic JSON result")
    args = parser.parse_args(argv)
    try:
        expected = load_lock(args.lock)
        validated = check_export(load_json(args.export), expected)
        if args.map:
            check_map(load_json(args.map), validated)
        result = {"outcome": "passed", "course": validated["course"],
                  "releaseId": expected["releaseId"],
                  "manifestSha256": expected["manifestSha256"],
                  "mapInspected": bool(args.map), "manualReviewRequired": True}
        status = 0
    except ContractError as exc:
        result = {"outcome": "incomplete" if exc.category in
                  ("unsupported_format", "missing_input") else "failed",
                  "mapInspected": bool(args.map),
                  "manualReviewRequired": True, "finding": exc.as_dict()}
        status = 3 if result["outcome"] == "incomplete" else 1
    if args.json:
        print(json.dumps(result, sort_keys=True, ensure_ascii=False,
                         separators=(",", ":")))
    elif status:
        print(f"{result['finding']['code']}: {result['finding']['message']}",
              file=sys.stderr)
    else:
        print(f"{result['course']} structurally compatible with release "
              f"{expected['releaseId']}; editorial and learner review still required.")
    return status


if __name__ == "__main__":
    sys.exit(main())
