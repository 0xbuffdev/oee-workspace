"""Verify Toolkit context v1 without reinterpreting academic Markdown."""
from __future__ import annotations

import hashlib
import json


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


def manifest_hashes(source, manifest):
    require(digest(canonical(manifest)) == source["manifestSha256"], "manifest digest mismatch")
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

    # Applicability belongs to the selected Toolkit, not a Workspace course index.
    ranges = context["reviewedRanges"]
    require(type(ranges) is list and context["applicability"] in
            ("source-indexed", "manual-resolution-required"), "invalid applicability")
    require(bool(ranges) == (context["applicability"] == "source-indexed"),
            "reviewed ranges disagree with applicability")
    seen = set()
    for row in ranges:
        require(type(row) is dict and set(row) == {"kind", "location", "assessmentIds", "sha256"},
                "invalid reviewed range")
        kind, location, applicable = row["kind"], row["location"], row["assessmentIds"]
        require(kind in ("completion-rules", "shared-rules", "assessment-definition", "optional-practice"),
                "invalid reviewed range kind")
        require(type(location) is dict and set(location) == {"path", "startLine", "endLine"},
                "invalid range location")
        path, start, end = location["path"], location["startLine"], location["endLine"]
        require(type(path) is str and path in documents and type(start) is int and
                type(end) is int and 1 <= start <= end <= len(documents[path]), "range outside source")
        key = (path, start, end)
        require(key not in seen, "duplicate reviewed range")
        seen.add(key)
        require(type(applicable) is list and all(type(i) is str for i in applicable)
                and len(applicable) == len(set(applicable)) and set(applicable) <= set(required),
                "invalid range assessment membership")
        require(bool(applicable) == (kind != "optional-practice"), "invalid optional applicability")
        require(all(path in item["sourcePaths"] for item in context["assessments"]
                    if item["assessmentId"] in applicable), "range document is not applicable")
        require(row["sha256"] == digest("".join(documents[path][start - 1:end]).encode("utf-8")),
                "reviewed range digest mismatch")
    return context
