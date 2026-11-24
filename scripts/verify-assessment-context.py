"""Verify Toolkit context v1 without reinterpreting academic Markdown."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":")) + "\n").encode("utf-8")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def lines(markdown):
    parts = markdown.split("\n")
    return [part + "\n" for part in parts[:-1]] + ([parts[-1]] if parts[-1] else [])


def manifest_hashes(source, store):
    if store is None:
        if os.name == "nt":
            require(bool(os.environ.get("LOCALAPPDATA")), "missing LOCALAPPDATA")
            root = Path(os.environ["LOCALAPPDATA"])
        elif sys.platform == "darwin":
            root = Path.home() / "Library/Caches"
        else:
            root = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
        store = root / "oee/curriculum-releases"
    path = store / source["manifestSha256"] / "release.json"
    require(not path.is_symlink() and path.is_file(), "manifest unavailable")
    data = path.read_bytes()
    require(digest(data) == source["manifestSha256"], "manifest digest mismatch")
    manifest = json.loads(data)
    require(manifest["releaseId"] == source["releaseId"] and
            manifest["source"]["commit"] == source["originCommit"], "manifest identity mismatch")
    return {entry["path"]: entry["sha256"] for entry in manifest["files"]}


def check_context(context, export, hashes):
    require(type(context) is dict and set(context) == {
        "contextVersion", "source", "toolkit", "courseExportSha256", "documents",
        "assessments", "reviewedRanges", "applicability", "manualReviewRequired",
        "contextSha256"}, "unsupported assessment context properties")
    require(type(context["contextVersion"]) is int and context["contextVersion"] == 1
            and context["manualReviewRequired"] is True, "unsupported context contract")
    require(context["source"] == export["source"] and context["toolkit"] == export["toolkit"],
            "context source/software mismatch")
    require(context["courseExportSha256"] == digest(canonical(export)), "course export digest mismatch")
    require(context["contextSha256"] == digest(canonical({
        key: value for key, value in context.items() if key != "contextSha256"
    })), "context digest mismatch")
    course_path = export["source"]["coursePath"]
    documents = {}
    require(type(context["documents"]) is list, "invalid context documents")
    for doc in context["documents"]:
        require(type(doc) is dict and set(doc) == {
            "path", "sha256", "startLine", "endLine", "markdown"}, "invalid document properties")
        path = doc["path"]
        require(type(path) is str and path in hashes and path not in documents,
                "unlisted or duplicate context document")
        require(type(doc["markdown"]) is str and doc["markdown"], "invalid document text")
        require(doc["sha256"] == hashes[path] == digest(doc["markdown"].encode("utf-8")),
                "document differs from selected manifest")
        doc_lines = lines(doc["markdown"])
        require(type(doc["startLine"]) is int and doc["startLine"] == 1 and
                type(doc["endLine"]) is int and doc["endLine"] == len(doc_lines),
                "document line range mismatch")
        documents[path] = doc_lines
    require(course_path in documents and hashes[course_path] == export["source"]["courseSha256"],
            "context lacks selected course")
    required = [item["id"] for item in export["assessments"] if item["required"]]
    used = set()
    require(type(context["assessments"]) is list, "invalid assessment context list")
    ids = []
    for item in context["assessments"]:
        require(type(item) is dict and set(item) == {"assessmentId", "sourcePaths"},
                "invalid assessment context entry")
        ids.append(item["assessmentId"])
        paths = item["sourcePaths"]
        require(type(paths) is list and paths and paths[0] == course_path and
                len(paths) == len(set(paths)) and set(paths) <= documents.keys(),
                "invalid assessment document references")
        used.update(paths)
    require(ids == required and used == documents.keys(), "assessment/document applicability mismatch")

    # Independently reviewed navigation index for the exact published SEF1.
    # Never apply it to an altered revision or to any other course.
    indexed = (export["source"]["courseSha256"] ==
               "87f557cac53f6d3aebfe0c808858b620acae7b3a8d50ea5ea468a0e2c2b953bb"
               and required == ["SEF1-AS1", "SEF1-AS2", "SEF1-AS3"]
               and len(documents) == 1)
    expected = [
        ("completion-rules", 172, 192, required),
        ("shared-rules", 194, 212, required),
        ("shared-rules", 214, 273, ["SEF1-AS3"]),
        ("assessment-definition", 277, 297, ["SEF1-AS1"]),
        ("assessment-definition", 299, 327, ["SEF1-AS2"]),
        ("assessment-definition", 329, 362, ["SEF1-AS3"]),
        ("optional-practice", 364, 388, []),
        ("completion-rules", 390, 398, required),
    ] if indexed else []
    require(context["applicability"] == ("source-indexed" if indexed else "manual-resolution-required"),
            "unreviewed context applicability")
    ranges = context["reviewedRanges"]
    require(type(ranges) is list and len(ranges) == len(expected), "unexpected reviewed ranges")
    for row, (kind, start, end, applicable) in zip(ranges, expected):
        require(end <= len(documents[course_path]), "range outside source")
        require(row == {"kind": kind, "location": {"path": course_path,
                    "startLine": start, "endLine": end}, "assessmentIds": applicable,
                    "sha256": digest("".join(documents[course_path][start - 1:end]).encode("utf-8"))}
                and type(row["location"]["startLine"]) is int
                and type(row["location"]["endLine"]) is int,
                "reviewed range digest or applicability mismatch")
    return context
