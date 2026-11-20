#!/usr/bin/env python3
"""Compare pinned Workspace v2 resource maps with an explicitly chosen OEE commit.

This is an ADVISORY, READ-ONLY report, not a resource-map migration command.
Pinned validation always uses the recorded Git commit. Target validation uses
only --target-revision, never an inferred HEAD or an untrusted export JSON.

Exit codes: 0 valid report (even when drift is found); 1 invalid pinned map;
3 unavailable/unsupported target; 4 unexpected tool failure.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "resources" / "mappings"
SHA = re.compile(r"[0-9a-f]{40}\Z")
CODE = re.compile(r"(SEF|APP|SYS|AI|SEC)[1-9][0-9]*\Z")


def load_checker():
    name = "oee_workspace_pinned_drift_checker"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / "check-resources.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def difference(kind: str, locator: str, before, after) -> dict:
    """An exact structural observation, never an inferred course equivalence."""
    return {"kind": kind, "locator": locator, "before": before, "after": after}


def compare_contracts(pinned: dict, target: dict, mapping: dict) -> tuple[list[dict], list[dict]]:
    """Compare two verified OEE exports, excluding incidental source line numbers.

    Module and lesson ordinals belong to a particular source revision.
    An identical title at a different ordinal is a *diagnostic hint*, not
    authorization to rewrite a resource locator.
    """
    changes: list[dict] = []

    def field(kind: str, locator: str, a, b) -> None:
        if a != b:
            changes.append(difference(kind, locator, a, b))

    for key in ("type", "status", "prerequisites"):
        field("course-" + key, "course." + key,
              pinned["course"].get(key), target["course"].get(key))

    for kind in ("outcomes", "assessments"):
        # The *canonical Toolkit export* contains ordered arrays, while the
        # validated consumer indexes those IDs. Index the already-verified
        # export here; never treat raw records as hashable dictionary keys.
        left = {item["id"]: item for item in pinned[kind]}
        right = {item["id"]: item for item in target[kind]}
        for ident in sorted(set(left) | set(right)):
            if ident not in left:
                field(kind[:-1] + "-added", ident, None, right[ident])
                continue
            if ident not in right:
                field(kind[:-1] + "-removed", ident, left[ident], None)
                continue
            fields = (("description",) if kind == "outcomes"
                      else ("required", "outcomeIds", "work", "criteria", "evidence"))
            for name in fields:
                field(kind[:-1] + "-" + name, ident + "." + name,
                      left[ident].get(name), right[ident].get(name))

    for ident in sorted(set(pinned["coverage"]) | set(target["coverage"])):
        field("required-coverage", "coverage." + ident,
              pinned["coverage"].get(ident), target["coverage"].get(ident))

    before_modules = {item["number"]: item for item in pinned["modules"]}
    after_modules = {item["number"]: item for item in target["modules"]}
    for number in sorted(set(before_modules) | set(after_modules)):
        label = f"module.{number}"
        if number not in before_modules:
            field("module-added", label, None, after_modules[number])
            continue
        if number not in after_modules:
            field("module-removed", label, before_modules[number], None)
            continue
        original, current = before_modules[number], after_modules[number]
        for name in ("title", "outcomeIds"):
            field("module-" + name, label + "." + name,
                  original.get(name), current.get(name))
        before_lessons = original["lessons"]
        after_lessons = current["lessons"]
        for ordinal in range(1, max(len(before_lessons), len(after_lessons)) + 1):
            old = before_lessons[ordinal - 1]["title"] if ordinal <= len(before_lessons) else None
            new = after_lessons[ordinal - 1]["title"] if ordinal <= len(after_lessons) else None
            field("lesson-title", label + f".lesson.{ordinal}", old, new)

    # Exact matching titles that changed ordinal are a signal for manual review,
    # never a silently inferred remapping. Duplicate titles are not guessed.
    originals = [m["title"] for m in pinned["modules"]]
    currents = [m["title"] for m in target["modules"]]
    for title in sorted(set(originals) & set(currents)):
        if originals.count(title) == currents.count(title) == 1:
            previous, present = originals.index(title) + 1, currents.index(title) + 1
            if previous != present:
                changes.append(difference("module-title-moved", title, previous, present))

    changed_outcomes = {
        item["locator"].split(".")[0] for item in changes
        if item["kind"].startswith("outcome-")
    }
    changed_assessments = {
        item["locator"].split(".")[0] for item in changes
        if item["kind"].startswith("assessment-")
    }
    changed_coverage = {
        item["locator"].split(".", 1)[1] for item in changes
        if item["kind"] == "required-coverage"
    }
    risks: list[dict] = []
    for module in mapping["modules"]:
        number = module["number"]
        old = before_modules.get(number)
        new = after_modules.get(number)
        reasons = []
        if not new or not old or new["title"] != old["title"]:
            reasons.append("module-locator-changed")
        elif new["lessons"] != old["lessons"]:
            reasons.append("lesson-order-or-content-changed")
        if old and new and old["outcomeIds"] != new["outcomeIds"]:
            reasons.append("module-outcome-links-changed")
        if old and set(old["outcomeIds"]) & changed_coverage:
            reasons.append("module-required-assessment-coverage-changed")
        for resource in module["resources"]:
            local = list(reasons)
            lesson = resource.get("lesson")
            if lesson and (not new or not isinstance(lesson.get("number"), int)
                           or lesson["number"] > len(new["lessons"])
                           or new["lessons"][lesson["number"] - 1]["title"] != lesson["title"]):
                local.append("resource-lesson-locator-changed")
            for ident in resource.get("outcomeIds", []):
                if ident not in {item["id"] for item in target["outcomes"]}:
                    local.append("referenced-outcome-removed:" + ident)
                elif ident in changed_outcomes:
                    local.append("referenced-outcome-definition-changed:" + ident)
                if ident in changed_coverage:
                    local.append("required-assessment-coverage-changed:" + ident)
            for ident in resource.get("assessmentIds", []):
                if ident not in {item["id"] for item in target["assessments"]}:
                    local.append("referenced-assessment-removed:" + ident)
                elif ident in changed_assessments:
                    local.append("referenced-assessment-definition-changed:" + ident)
            if local:
                risks.append({
                    "module": number, "resource": resource["resource"],
                    "reasons": sorted(set(local)),
                })
    changes.sort(key=lambda x: (x["kind"], x["locator"]))
    risks.sort(key=lambda x: (x["module"], x["resource"], x["reasons"]))
    return changes, risks


def inspect_map(mapping: dict, oee: Path, target_sha: str, checker) -> dict:
    """Validate the pinned source first, then compare a separately chosen target."""
    canon = mapping["curriculum"]
    code, pin = canon["course"], canon["revision"]
    base = {
        "course": code,
        "pinnedRevision": pin,
        "targetRevision": target_sha,
        "pinnedValidation": "passed",
        "targetValidation": "passed",
        "state": "unchanged",
        "reviewRequired": False,
        "autoRemapped": False,
        "assessmentCompletionDetermined": False,
        "changes": [],
        "resourceAssociationRisks": [],
    }
    # Do not mutate mapping, nor pretend that its pinned source is target HEAD.
    original = checker.read_pinned_export(oee, pin, code)
    checked = checker.load_consumer().check_export(original, pin)
    checker.load_consumer().check_map(mapping, checked)
    try:
        updated = checker.read_pinned_export(oee, target_sha, code)
        other = checker.load_consumer().check_export(updated, target_sha)
    except checker.PinnedSourceError as exc:
        base.update(state="target-unavailable", targetValidation="incomplete",
                    reviewRequired=True, targetFailure={
                        "category": exc.category, "message": str(exc),
                    })
        return base
    except checker.load_consumer().ContractError as exc:
        base.update(state="target-unavailable", targetValidation="incomplete",
                    reviewRequired=True, targetFailure=exc.as_dict())
        return base

    changes, risks = compare_contracts(original, updated, mapping)
    base["changes"] = changes
    base["resourceAssociationRisks"] = risks
    if changes or risks:
        base.update(state="drift-detected", reviewRequired=True)
    return base


def report(oee: Path, target_sha: str, maps: list[Path]) -> tuple[dict, int]:
    """Return one deterministic report with clear, separate validation states."""
    checker = load_checker()
    catalog_findings = checker.Check()
    catalog = checker.validate_catalog(catalog_findings)
    if catalog_findings.errors:
        raise ValueError("resource catalog invalid: " + "; ".join(catalog_findings.errors[:3]))
    rows = []
    result_code = 0
    for path in maps:
        try:
            mapping = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as exc:
            raise ValueError(f"cannot read resource map {path.name}: {type(exc).__name__}") from exc
        findings = checker.Check()
        if not checker.validate_map_shape(mapping, catalog, findings, str(path)):
            raise ValueError("invalid pinned map: " + "; ".join(findings.errors[:3]))
        canonical = mapping["curriculum"]
        matches = CODE.fullmatch(canonical["course"])
        if (not matches or path.parent.name != matches.group(1)
                or path.stem != canonical["course"]):
            raise ValueError("map path disagrees with canonical program/course")
        try:
            row = inspect_map(mapping, oee, target_sha, checker)
        except checker.PinnedSourceError as exc:
            raise ValueError("pinned source invalid or missing: " + str(exc)) from exc
        except checker.load_consumer().ContractError as exc:
            raise ValueError("pinned map references invalid: " + exc.code) from exc
        rows.append(row)
        if row["targetValidation"] == "incomplete":
            result_code = 3
    return {
        "reportVersion": 1, "mode": "advisory-only",
        "targetRevision": target_sha, "results": rows,
        "pinnedValidation": "passed",
        "upstreamReviewRequired": any(x["reviewRequired"] for x in rows),
        "autoRemapped": False, "filesChanged": False,
    }, result_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oee", type=Path, required=True,
                        help="trusted local OEE Toolkit Git checkout; no fetch")
    parser.add_argument("--target-revision", required=True,
                        help="explicit full OEE commit SHA for nonblocking drift comparison")
    parser.add_argument("--course",
                        help="optional mapped course code; defaults to all active maps")
    args = parser.parse_args(argv)
    if not SHA.fullmatch(args.target_revision):
        parser.error("--target-revision must be a full lowercase Git commit SHA")
    if args.course is not None and not CODE.fullmatch(args.course):
        parser.error("--course must be a canonical OEE course code")
    paths = sorted(MAPS.rglob("*.json"))
    if args.course:
        paths = [p for p in paths if p.stem == args.course]
    if not paths:
        print("drift_report_error: no active v2 maps selected", file=sys.stderr)
        return 1
    try:
        data, status = report(args.oee, args.target_revision, paths)
    except ValueError as exc:
        print("drift_report_error: " + str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"drift_report_tool_error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 4
    print(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
