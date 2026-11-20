"""Offline, learner-owned evidence operations (Workspace Evidence Contract 0002).

One active attempt format (v1) for OEE v0.2.0. This module validates
local JSON records and references a trusted pinned OEE Toolkit export.
It never grades, executes learner commands, fetches links or uploads data.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
from uuid import UUID

SOURCE = "0xbuffdev/open-engineering-education"
SPECIFICATION = "v0.2.0"
COURSE = re.compile(r"(SEF|APP|SYS|AI|SEC)[1-9][0-9]*\Z")
SHA = re.compile(r"[a-f0-9]{40}\Z")
HASH = re.compile(r"[a-f0-9]{64}\Z")
UTC = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z\Z")
SOURCE_ROOT = Path(__file__).resolve().parents[1]
MAX_RECORD_BYTES = 2_000_000


class EvidenceIssue(Exception):
    def __init__(self, code: str, kind: str, description: str):
        super().__init__(description)
        self.code, self.kind = code, kind

    def finding(self) -> dict:
        return {"code": self.code, "kind": self.kind, "message": str(self)}


def invalid(message: str, code: str = "WSE001") -> None:
    raise EvidenceIssue(code, "invalid", message)


def incomplete(message: str, code: str = "WSE003") -> None:
    raise EvidenceIssue(code, "incomplete", message)


def record_obj(value, allowed: set[str], required: set[str], label: str) -> dict:
    if type(value) is not dict:
        invalid(f"{label} must be an object")
    unknown, missing = set(value) - allowed, required - set(value)
    if unknown or missing:
        invalid(f"{label} has unknown fields {sorted(unknown)} or missing fields {sorted(missing)}")
    return value


def nonempty(value, label: str) -> str:
    if type(value) is not str or not value.strip():
        invalid(f"{label} must be a nonempty string")
    return value


def timestamp(value, label: str) -> str:
    if type(value) is not str or not UTC.fullmatch(value):
        invalid(f"{label} must be a UTC timestamp ending in Z")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        invalid(f"{label} has an invalid calendar date or time")
    return value


def uuid4(value: str) -> str:
    if type(value) is not str:
        invalid("attemptId must be a lower-case UUID v4")
    try:
        parsed = UUID(value)
    except (TypeError, ValueError, AttributeError):
        invalid("attemptId must be a UUID v4")
    if parsed.version != 4 or str(parsed) != value:
        invalid("attemptId must be a canonical lower-case UUID v4")
    return value


def relative_artifact(value: str) -> Path:
    """Reject absolute, traversal, Windows drive, control and empty segments."""
    if (type(value) is not str or not value or value.startswith("/") or
            "\\" in value or re.match(r"^[A-Za-z]:", value) or
            any(ord(char) < 32 or ord(char) == 127 for char in value)):
        invalid("unsafe relative artifact path", "WSE004")
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        invalid("relative artifact must not traverse directories", "WSE004")
    return Path(*parts)


def record_shape(record: dict) -> dict:
    """Enforce the current JSON Schema v1 constraints with Python stdlib.

    Full Draft 2020-12 schema equivalence is independently tested in CI.
    Cross-document references and real filesystem checks happen separately.
    """
    required = {"schemaVersion", "attemptId", "recordedAt", "course",
                "assessmentId", "outcomeIds", "artifacts", "observations",
                "evaluation"}
    record_obj(record, required | {"assistance"}, required, "record")
    if type(record["schemaVersion"]) is not int or record["schemaVersion"] != 1:
        invalid("only evidence schemaVersion 1 is supported", "WSE002")
    uuid4(record["attemptId"])
    timestamp(record["recordedAt"], "recordedAt")

    course = record_obj(record["course"],
                        {"repository", "revision", "specification", "path", "code"},
                        {"repository", "revision", "specification", "path", "code"},
                        "course")
    code = course["code"]
    matched = COURSE.fullmatch(code) if type(code) is str else None
    if not matched or course["repository"] != SOURCE or course["specification"] != SPECIFICATION:
        invalid("unsupported OEE source identity or specification", "WSE002")
    if type(course["revision"]) is not str or not SHA.fullmatch(course["revision"]):
        invalid("course revision must be a full lower-case Git SHA", "WSE002")
    if course["path"] != f"curriculum/{matched.group(1)}/{code}.md":
        invalid("course path does not match canonical code", "WSE005")

    assessment = f"{code}-AS"
    if (type(record["assessmentId"]) is not str or
            not re.fullmatch(re.escape(assessment) + r"[1-9][0-9]*", record["assessmentId"])):
        invalid("assessmentId must belong to course", "WSE005")
    outcomes = record["outcomeIds"]
    if (type(outcomes) is not list or not outcomes or
            any(type(item) is not str or not re.fullmatch(
                re.escape(code) + r"-O[1-9][0-9]*", item) for item in outcomes) or
            len(outcomes) != len(set(outcomes))):
        invalid("outcomeIds must be unique, nonempty course outcome IDs", "WSE005")

    artifacts = record["artifacts"]
    if type(artifacts) is not list:
        invalid("artifacts must be an array")
    for item in artifacts:
        if type(item) is not dict:
            invalid("artifact must be an object")
        kind = item.get("kind")
        if kind == "relative-path":
            record_obj(item, {"kind", "value", "sha256"}, {"kind", "value"}, "artifact")
            relative_artifact(item["value"])
            digest = item.get("sha256")
            if digest is not None and (type(digest) is not str or not HASH.fullmatch(digest)):
                invalid("artifact sha256 must be 64 lowercase hexadecimal characters")
        elif kind == "external-url":
            record_obj(item, {"kind", "value"}, {"kind", "value"}, "artifact")
            value = nonempty(item["value"], "external URL")
            if re.search(r"\s", value):
                invalid("external URL contains whitespace")
            try:
                parsed = urlsplit(value)
                port = parsed.port
            except ValueError:
                invalid("invalid external URL")
            if parsed.scheme not in ("https", "http") or not parsed.netloc or not parsed.hostname:
                invalid("only valid http(s) display URLs are accepted")
            if port is not None and not 0 < port < 65536:
                invalid("invalid external URL port")
        else:
            invalid("unknown artifact kind")
    observations = record["observations"]
    if type(observations) is not list:
        invalid("observations must be an array")
    for observation in observations:
        record_obj(observation, {"kind", "summary"},
                   {"kind", "summary"}, "observation")
        if observation["kind"] not in ("self-note", "automated-check"):
            invalid("unsupported observation kind")
        nonempty(observation["summary"], "observation summary")
    if "assistance" in record:
        assistance = record_obj(record["assistance"], {"declaredMode", "summary"},
                                {"declaredMode", "summary"}, "assistance")
        if assistance["declaredMode"] not in (
                "not-recorded", "independent", "collaborative", "delegated"):
            invalid("invalid assistance declaredMode")
        if type(assistance["summary"]) is not str or len(assistance["summary"]) > 2000:
            invalid("assistance summary must be at most 2000 characters")

    evaluation = record["evaluation"]
    if evaluation is not None:
        evaluation = record_obj(
            evaluation, {"decision", "evaluatorKind", "reviewerLabel",
                         "reviewedAt", "criteriaSummary", "limitations"},
            {"decision", "evaluatorKind", "reviewerLabel", "reviewedAt",
             "criteriaSummary", "limitations"}, "evaluation")
        if evaluation["decision"] not in ("met", "not-met", "insufficient"):
            invalid("invalid evaluation decision")
        if evaluation["evaluatorKind"] not in ("self", "human"):
            invalid("automated observations cannot create an evaluation", "WSE006")
        nonempty(evaluation["reviewerLabel"], "reviewerLabel")
        nonempty(evaluation["criteriaSummary"], "criteriaSummary")
        timestamp(evaluation["reviewedAt"], "reviewedAt")
        if type(evaluation["limitations"]) is not str:
            invalid("evaluation limitations must be a string")
    return record


def safe_file(root: Path, location: Path) -> tuple[Path, Path]:
    """Reject symlinks at every component and confine reads under workspace.

    The caller controls the trusted local workspace; this is a local file
    safety check, not a sandbox against concurrent hostile filesystem changes.
    """
    if root.is_symlink() or not root.is_dir():
        invalid("workspace must be an existing real directory", "WSE004")
    # Keep the caller's lexical root as well as its canonical resolved path.
    # macOS commonly aliases /var through /private/var. A caller may supply
    # an absolute filename under either spelling of that *same* root, without
    # granting access to paths outside the selected learner workspace.
    lexical_root = root.expanduser().absolute()
    canonical_root = lexical_root.resolve(strict=True)
    if location.is_absolute():
        try:
            rel = location.relative_to(lexical_root)
        except ValueError:
            try:
                rel = location.relative_to(canonical_root)
            except ValueError:
                # The incoming absolute path may use another spelling of the
                # selected *root* (e.g. /var versus /private/var on macOS).
                # Find the ancestor that points precisely to that root, then
                # inspect every remaining relative component for symlinks.
                alias = next(
                    (parent for parent in location.parents
                     if parent.resolve(strict=False) == canonical_root), None,
                )
                if alias is None:
                    invalid("path escapes selected workspace", "WSE004")
                rel = location.relative_to(alias)
    else:
        rel = location
    root = canonical_root
    if not rel.parts or any(part in (".", "..") for part in rel.parts):
        invalid("unsafe workspace path", "WSE004")
    candidate = root
    for component in rel.parts:
        candidate /= component
        if candidate.is_symlink():
            invalid("symlink traversal is not allowed", "WSE004")
    if not candidate.exists():
        incomplete("local artifact or record does not exist: " + rel.as_posix())
    if not candidate.is_file():
        invalid("artifact or record must be a regular file", "WSE004")
    return candidate, rel


def load_record(root: Path, path: Path) -> tuple[dict, Path]:
    filename, rel = safe_file(root, path)
    try:
        if filename.stat().st_size > MAX_RECORD_BYTES:
            invalid("evidence record exceeds local size limit")
        record = json.loads(filename.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, ValueError, OSError) as exc:
        invalid("evidence record is not valid UTF-8 JSON: " + type(exc).__name__)
    record_shape(record)
    c = record["course"]["code"]
    program = COURSE.fullmatch(c).group(1)
    expected = Path("evidence") / program / c / record["assessmentId"] / (record["attemptId"] + ".json")
    if rel != expected:
        invalid("record filename/directory disagrees with its canonical attempt identity",
                "WSE005")
    return record, rel


def load_reader():
    """Invoke the one Toolkit-backed pinned source adapter already in Workspace."""
    name = "oee_workspace_shared_source"
    existing = sys.modules.get(name)
    if existing:
        return existing
    spec = importlib.util.spec_from_file_location(
        name, SOURCE_ROOT / "scripts" / "check-resources.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def review_state(record: dict) -> dict:
    evaluation = record["evaluation"]
    if evaluation is None:
        return {"status": "attempt-recorded", "decision": None,
                "reviewerIdentityVerified": False}
    kind = evaluation["evaluatorKind"]
    return {"status": "self-assessed" if kind == "self" else "human-review-reported",
            "decision": evaluation["decision"], "reviewerIdentityVerified": False}


class EvidenceService:
    def __init__(self, workspace: Path, oee: Path):
        self.workspace = Path(workspace)
        self.oee = Path(oee)
        self._sources: dict[tuple[str, str], dict] = {}

    def source(self, code: str, revision: str) -> dict:
        key = (code, revision)
        if key not in self._sources:
            reader = load_reader()
            try:
                raw = reader.read_pinned_export(self.oee, revision, code)
                checked = reader.load_consumer().check_export(raw, revision)
                # This type came from the already validated Toolkit export,
                # never from a second Markdown parser or the moving worktree.
                checked["courseType"] = raw["course"]["type"]
            except reader.PinnedSourceError as exc:
                if exc.category in ("source_missing", "unsupported_format"):
                    incomplete("pinned OEE course source unavailable: " + exc.category, "WSE003")
                invalid("pinned OEE Toolkit export rejected: " + exc.category, "WSE005")
            except reader.load_consumer().ContractError as exc:
                if exc.category in ("missing_input", "unsupported_format"):
                    incomplete("unsupported pinned export: " + exc.code, "WSE003")
                invalid("invalid pinned export: " + exc.code, "WSE005")
            self._sources[key] = checked
        return self._sources[key]

    def check(self, path: Path, *, check_duplicates: bool = True) -> dict:
        """Check one existing record; do not write to the learner workspace."""
        result = {"outcome": "invalid", "record": None, "attemptId": None,
                  "course": None, "revision": None, "assessmentId": None,
                  "review": None, "findings": [], "sourceValidated": False}
        try:
            record, rel = load_record(self.workspace, Path(path))
            result.update({"record": rel.as_posix(), "attemptId": record["attemptId"],
                           "course": record["course"]["code"],
                           "revision": record["course"]["revision"],
                           "assessmentId": record["assessmentId"],
                           "review": review_state(record)})
            if check_duplicates and any(
                other.name == rel.name and
                other.relative_to(self.workspace) != rel
                for other in self.paths()
            ):
                invalid("attempt UUID exists in another evidence record", "WSE008")
            source = self.source(record["course"]["code"], record["course"]["revision"])
            origin = source["source"]
            if (origin["repository"] != record["course"]["repository"] or
                    origin["specification"] != record["course"]["specification"] or
                    origin["coursePath"] != record["course"]["path"]):
                invalid("record identity disagrees with pinned OEE export", "WSE005")
            assessment = source["assessments"].get(record["assessmentId"])
            if assessment is None or not assessment["required"]:
                invalid("assessment is not required in pinned OEE export", "WSE005")
            if not set(record["outcomeIds"]).issubset(assessment["outcomeIds"]):
                invalid("outcome IDs are not evaluated by selected assessment", "WSE005")
            result["sourceValidated"] = True
            for artifact in record["artifacts"]:
                if artifact["kind"] == "external-url":
                    continue  # Display reference only; never request the URL.
                filename, _ = safe_file(self.workspace, relative_artifact(artifact["value"]))
                if artifact.get("sha256") is not None:
                    try:
                        with filename.open("rb") as stream:
                            digest = hashlib.file_digest(stream, "sha256").hexdigest()
                    except OSError:
                        incomplete("cannot read local artifact to verify sha256", "WSE003")
                    if digest != artifact["sha256"]:
                        invalid("artifact sha256 does not match recorded digest", "WSE007")
            result["outcome"] = "valid"
        except EvidenceIssue as exc:
            result["outcome"] = exc.kind
            result["findings"] = [exc.finding()]
        return result

    def paths(self) -> list[Path]:
        """Discover only local records; never descend into external sources."""
        root = self.workspace / "evidence"
        if root.is_symlink():
            invalid("evidence root may not be a symlink", "WSE004")
        if not root.exists():
            return []
        if not root.is_dir():
            invalid("evidence root must be a directory", "WSE004")
        return sorted(root.rglob("*.json"))

    def status(self, course: str | None = None,
               revision: str | None = None) -> dict:
        """Read-only projections, never mastery or official completion claims.

        An explicitly selected course+revision also reports no-evidence
        assessments when there are no attempts. Sources are never inferred
        from the moving Git HEAD.
        """
        if (course is None) != (revision is None):
            invalid("status source scope needs both course and full revision", "WSE005")
        if course is not None:
            if not COURSE.fullmatch(course) or not SHA.fullmatch(revision):
                invalid("invalid explicit source scope", "WSE005")
            self.source(course, revision)
        # Scan duplicate identities in a single pass rather than O(N²).
        results = [self.check(path, check_duplicates=False) for path in self.paths()]
        grouped: dict[tuple[str, str], list[dict]] = {}
        duplicates: dict[str, list[dict]] = {}
        for item in results:
            if item["attemptId"]:
                duplicates.setdefault(item["attemptId"], []).append(item)
        for ident, matches in duplicates.items():
            if len(matches) > 1:
                for item in matches:
                    item["outcome"] = "invalid"
                    item["findings"].append({
                        "code": "WSE008", "kind": "invalid",
                        "message": "duplicate attemptId in selected learner workspace"
                    })
        for item in results:
            if item["outcome"] == "valid":
                grouped.setdefault((item["course"], item["revision"]), []).append(item)
        if course is not None:
            grouped.setdefault((course, revision), [])
        courses = []
        for (code, revision), items in sorted(grouped.items()):
            export = self.source(code, revision)
            assessment_rows = []
            for assessment_id, assessment in sorted(export["assessments"].items()):
                if not assessment["required"]:
                    continue
                matching = [item for item in items if item["assessmentId"] == assessment_id]
                has_decision = any(item["review"]["decision"] is not None for item in matching)
                assessment_rows.append({
                    "assessmentId": assessment_id,
                    "attempts": len(matching), "decisionRecorded": has_decision,
                    "reportedStates": (sorted(set(
                        item["review"]["status"] for item in matching
                    )) if matching else ["no-evidence"])
                })
            # The Toolkit consumer exposes validated assessments and outcomes;
            # derive the required coverage graph rather than trusting a separate
            # unvalidated status field or dropping any assessment per outcome.
            required_coverage = {
                ident: sorted(
                    assessment_id for assessment_id, assessment in
                    export["assessments"].items()
                    if assessment["required"] and ident in assessment["outcomeIds"]
                ) for ident in export["outcomes"]
            }
            outcome_rows = []
            for outcome_id, required_ids in sorted(required_coverage.items()):
                recorded = [row["assessmentId"] for row in assessment_rows
                            if row["assessmentId"] in required_ids and row["decisionRecorded"]]
                outcome_rows.append({
                    "outcomeId": outcome_id,
                    "requiredAssessmentIds": required_ids,
                    "decisionsRecordedFor": recorded,
                    "outstandingAssessmentIds": [
                        ident for ident in required_ids if ident not in recorded
                    ],
                })
            courses.append({
                "course": code, "revision": revision,
                "assessments": assessment_rows, "outcomes": outcome_rows,
                "allRequiredAssessmentDecisionsRecorded": all(
                    row["decisionRecorded"] for row in assessment_rows
                ),
                "completion": "not-determined",
                "reviewerIdentityVerified": False,
            })
        return {
            "records": results, "courses": courses,
            "counts": {state: sum(x["outcome"] == state for x in results)
                       for state in ("valid", "invalid", "incomplete")},
            "educationalAchievementDetermined": False,
        }

    def export_selected(self, paths: list[Path]) -> dict:
        """Return selected record JSON only; do not include artifact bytes or others."""
        if not paths:
            invalid("explicitly select one or more attempt records for export", "WSE009")
        selected = {}
        for path in paths:
            record, rel = load_record(self.workspace, Path(path))
            if rel.as_posix() in selected:
                invalid("duplicate selected record", "WSE009")
            report = self.check(rel)
            if report["outcome"] != "valid":
                issue = report["findings"][0]
                raise EvidenceIssue(issue["code"], report["outcome"], issue["message"])
            selected[rel.as_posix()] = record
        if len({item["attemptId"] for item in selected.values()}) != len(selected):
            invalid("duplicate attempt IDs in selected records", "WSE008")
        return {
            "exportVersion": 1, "selection": "explicit-records",
            "records": [{"path": name, "attempt": selected[name]} for name in sorted(selected)],
            "artifactBytesIncluded": False, "reviewerIdentityVerified": False,
            "educationalAchievementDetermined": False,
        }
