#!/usr/bin/env python3
"""Render portable Markdown guides from the public OEE resource catalogue.

No third-party dependencies. The canonical OEE/module validation runs
separately through check-resources.py before generating these snapshots.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPINGS = ROOT / "resources" / "mappings"
CATALOG = ROOT / "resources" / "catalog"
GUIDES = ROOT / "resources" / "guides"
CATALOG_URL = "https://github.com/0xbuffdev/oee-workspace/blob/main/"


def load_catalog():
    result = {}
    for path in sorted(CATALOG.rglob("*.json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        rid = item["id"]
        if rid in result:
            raise ValueError("Duplicate resource: " + rid)
        result[rid] = (item, path.relative_to(ROOT).as_posix())
    return result


def describe_part(part):
    kind = part["type"]
    if kind in ("chapters", "projects"):
        noun = "Chapter" if kind == "chapters" else "Project"
        nums = part["numbers"]
        return (noun if len(nums) == 1 else noun + "s") + " " + ", ".join(str(n) for n in nums)
    if kind in ("section-titles", "topics"):
        noun = "Sections" if kind == "section-titles" else "Topics"
        return noun + " " + ", ".join("“" + title + "”" for title in part["titles"])
    if kind == "section-range":
        return "Sections “" + part["start"] + "” through “" + part["end"] + "”"
    raise ValueError("Unknown locator type: " + str(kind))


def access_label(item):
    access = item["access"]
    links = []
    if access.get("url"):
        links.append("[Official source](" + access["url"] + ")")
    if access.get("freeMaterialsUrl"):
        links.append("[Free companion materials](" + access["freeMaterialsUrl"] + ")")
    if not links:
        links.append("No public source link recorded")
    return access["mode"].capitalize() + " — " + " · ".join(links)


def render(mapping, catalog):
    canon = mapping["curriculum"]
    course = canon["course"]
    url = "https://github.com/" + canon["repository"] + "/blob/" + canon["revision"] + "/" + canon["path"]
    lines = [
        "# " + course + " — Resource study guide",
        "",
        "> " + mapping["status"].capitalize() + " resource guidance · [Canonical OEE course](" + url + ")",
        "",
        "This is a non-normative study aid. OEE defines the required outcomes, assessments, and labs. "
        "No book purchase is required. Check verification labels before following chapter references.",
        "",
        "**Curriculum revision:** " + canon["revision"],
        "",
        "**Map status:** " + mapping["status"].capitalize(),
    ]
    for module in mapping["modules"]:
        lines.extend(["", "## Module " + str(module["number"]) + " — " + module["title"], "",
                      "**Coverage:** " + module["coverage"].capitalize()])
        if module.get("gap"):
            lines.extend(["", "**Outstanding:** " + module["gap"]])
        for entry in module["resources"]:
            rid = entry["resource"]
            item, record_path = catalog[rid]
            lines.extend([
                "",
                "- **" + rid + " — " + item["title"] + "** — " + describe_part(entry["part"]) + ".",
                "  - Role: " + entry["role"].capitalize() + " · Mapping verification: " + entry["verification"].replace("-", " ").capitalize(),
                "  - Study purpose: " + entry["purpose"],
            ])
            lesson = entry.get("lesson")
            if lesson:
                lines.append("  - OEE lesson: " + str(lesson["number"]) + " — " + lesson["title"])
            lines.extend(["  - Access: " + access_label(item),
                          "  - [Catalogue record](" + CATALOG_URL + record_path + ")"])
    lines.extend([
        "",
        "## How to use this guide",
        "",
        "Read the canonical OEE module and lesson requirements first. Use these references as "
        "supporting explanations and practice, not substitutes for OEE labs or assessment evidence.",
        "",
        "A **Partial** module still needs editorial research. A **Review needed** reference may "
        "have unconfirmed section titles or edition-specific numbering. Do not assume that a "
        "paid book is essential or that an optional project satisfies a required OEE lab.",
        "",
        "When using this guide in a personal workspace, record your actual reading, editions and "
        "substitutions in the resources.md log. This guide is a versioned snapshot, not a progress log.",
        "",
    ])
    return "\n".join(lines)


def outputs(course_filter):
    catalog = load_catalog()
    found = False
    for path in sorted(MAPPINGS.rglob("*.json")):
        mapping = json.loads(path.read_text(encoding="utf-8"))
        code = mapping["curriculum"]["course"]
        if course_filter and code != course_filter:
            continue
        found = True
        program = re.match(r"^[A-Z]+", code).group()
        yield GUIDES / program / (code + ".md"), render(mapping, catalog)
    if course_filter and not found:
        raise ValueError("No public resource map exists for " + course_filter)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--write", action="store_true", help="regenerate all committed guides")
    modes.add_argument("--check", action="store_true", help="verify all guides match their mappings")
    modes.add_argument("--stdout", action="store_true", help="print one course guide")
    parser.add_argument("--course", help="course code (required with --stdout)")
    args = parser.parse_args()
    if args.stdout and not args.course:
        parser.error("--stdout requires --course")
    if args.course and not re.fullmatch(r"[A-Z]{2,4}[1-9][0-9]*", args.course):
        parser.error("invalid course code")
    if args.check and args.course:
        parser.error("--check validates all guides; omit --course")
    try:
        results = list(outputs(args.course))
        if args.stdout:
            if len(results) != 1:
                raise ValueError("Expected exactly one mapped course")
            sys.stdout.write(results[0][1])
            return 0
        expected = set()
        errors = []
        for path, content in results:
            expected.add(path.resolve())
            if args.write:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
                print("Generated " + str(path.relative_to(ROOT)))
            elif not path.is_file() or path.read_text(encoding="utf-8") != content:
                errors.append("Guide missing or stale: " + str(path.relative_to(ROOT)))
        if args.check:
            for path in sorted(GUIDES.rglob("*.md")):
                if path.resolve() not in expected:
                    errors.append("Unmapped guide: " + str(path.relative_to(ROOT)))
            for error in errors:
                print("ERROR: " + error, file=sys.stderr)
            print(f"Guide check: {len(results)} mapped course(s), {len(errors)} issue(s)")
        return 1 if errors else 0
    except (ValueError, KeyError, OSError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
