# Learner-owned evidence records

OEE Workspace records assessment **attempts**, not credentials or automatic course completions. [OEE Evidence Rules](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/evidence-rules.md) govern the educational requirements. The non-normative [Workspace Evidence Contract 0002](https://github.com/0xbuffdev/context/blob/main/repos/oee-workspace/specs/0002-evidence-records.md) governs this implementation's interoperable JSON record.

## Current format

The only active format is [assessment attempt v1](schemas/attempt-v1.schema.json), expressed in JSON Schema Draft 2020-12. It accepts OEE source specification **v0.2.0 only**. No conversion or compatibility adapters are provided. An attempt records:

- A unique version-4 UUID `attemptId`, UTC `recordedAt`, exact 40-character OEE Git commit and canonical course path/code.
- One **required** summative `assessmentId` and a nonempty set of `outcomeIds` evaluated by that assessment.
- Optional relative artifact file paths (and SHA-256 where recorded), or display-only external HTTPS URLs. External references are never fetched automatically. Conceptual or observed performance may have no artifact files.
- Observations from `self-note` or `automated-check`; these **never** constitute an evaluation.
- Optional `assistance` disclosure (`not-recorded`, `independent`, `collaborative`, `delegated`) as descriptive metadata, not proof of any assistant policy.
- Required `evaluation` field, normally **null** until a deliberate `self` or `human` review is entered, with a criteria summary, date, decision and limitations.

**Reviewer identities are not verified.** A self-review is explicitly self-declared; even a record claiming human review does not authenticate its reviewer. No local record proves mastery, accreditation, OEE course readiness, or official completion.

## Intended learner paths

A learner-owned attempt is located at:

```text
evidence/<program>/<course>/<assessment>/<attemptId>.json
```

For example `evidence/SEF/SEF1/SEF1-AS1/68e5f624-bfb1-4c1e-8c87-486668f4884e.json`. A new attempt uses a fresh UUID; accepted records, evaluations, progress logs and learner artifacts must not be silently overwritten. A corrected review is recorded as another attempt with an explicit reference to the previous record.

Every source revision must exist in a **trusted local OEE checkout**. Path/assessment/outcome relationships must match the Toolkit export produced from that exact Git commit, not `HEAD`. `artifacts[].value` with `kind: relative-path` is resolved under the selected learner workspace. An absent artifact/source is incomplete; a mismatched hash is an integrity failure. Symlink traversal and containment must be checked on the real filesystem, not inferred from the string alone.

The **WS-I07 evidence operations are implemented** in [`oee_workspace/evidence.py`](../oee_workspace/evidence.py). They use Python's standard library plus the existing pinned Toolkit export consumer; they validate the real local filesystem and source/assessment relationships, produce read-only status projections, and assemble only explicitly selected attempt metadata for a future local export. They never run student code or fetch external URLs. **WS-I08 now supplies the cross-platform Python CLI and exclusive, no-clobber local attempt/export publication.** The schema alone still cannot establish an outcome's substantive adequacy or verify a reviewer's identity.

## Example fixture and testing

The [synthetic fixtures](../tests/fixtures/evidence/) exercise SEF1 conceptual attempts and SEF10 project attempts at pinned OEE commit `67416343f3eab17ada5d3c79ae6cc782524c29ff`. They include unreviewed attempts, self-review, an **unverified claimed human review**, malformed structures and reference/integrity failures. They do not represent actual learner achievements.

```bash
python3 -m pip install "jsonschema==4.23.0"
OEE_REPO=/path/to/open-engineering-education \
  python3 -m unittest discover -s tests -p 'test_evidence_schema.py' -v
```

`jsonschema` is a **test-only dependency** to exercise the published Draft 2020-12 contract. It is not required to create or study in a Workspace; ordinary runtime tools remain offline and standard-library-based. CI independently checks the real fixed-commit OEE Toolkit exports for SEF1 and SEF10.

For assistance and agent execution boundaries, see the
[AI and agent safety guide](../docs/AI-SAFETY.md). The optional
`assistance.declaredMode` is **self-reported metadata**. Neither its absence
nor any selected value establishes whether an external assistant was used,
that an assessment's restrictions were enforced, or that a reviewer is
authenticated.

## Privacy and status boundaries

Records live locally and require no login, remote upload, model or paid book. Do not write credentials, private datasets, personal logs, raw agent transcripts or assessment secrets to public evidence directories. External URL entries are display references, not fetched content or trustworthy independent evidence.

WS-I07 reports *attempt recorded*, *self-assessed*, *human-review reported* (identity unverified), and *no evidence* when a specific pinned course is requested without attempts. Each required assessment is considered separately, including outcomes evaluated by more than one required assessment. Even when all assessment decisions are present, Workspace does not automatically mark a course completed. Only explicitly selected attempt JSON enters a local export; no artifact file bytes, unrelated records, default telemetry, hidden upload, automatic execution or grading are included.

## Supported command-line operations

From the root of your learner Workspace with Python 3.11+, a trusted OEE
checkout and a full 40-character OEE source SHA:

```sh
python -m oee_workspace evidence init --oee ../open-engineering-education --revision 67416343f3eab17ada5d3c79ae6cc782524c29ff --course SEF1 --assessment SEF1-AS1 --dest .
python -m oee_workspace evidence check --oee ../open-engineering-education --path evidence/SEF/SEF1/SEF1-AS1/ATTEMPT-UUID.json --dest .
python -m oee_workspace status --oee ../open-engineering-education --dest .
python -m oee_workspace export --oee ../open-engineering-education --dest . --attempt ATTEMPT-UUID --output exports/selected.json
```

`evidence init` records a **fresh** UUID with all of the selected required
assessment's published outcome IDs and `evaluation: null`. It does not
fabricate observations, artifacts or a passing score. A previously created
attempt is never changed by the CLI. `status` reports the available records
and any missing review decisions; `export` includes only explicitly selected,
validated JSON metadata and never artifact bytes or unrelated workspace files.
Repeated export into an existing filename fails instead of replacing it.

The CLI uses exit codes 0 (success), 1 (invalid), 2 (bad arguments),
3 (missing/unsupported source or incomplete check) and 4 (unexpected fault).
No automatic assessment execution, AI-provider integration or hosted sync is
included. Local export performs a narrow common-credential check, **not**
general detection of all personal data: review free-text fields yourself before
sharing outside your workspace.

## Read-only Python operations

From a learner workspace's parent/source environment (or after adding this repository to `PYTHONPATH`):

```python
from pathlib import Path
from oee_workspace import EvidenceService

service = EvidenceService(
    workspace=Path("/path/to/learner"),
    oee=Path("/path/to/open-engineering-education"),
)

# Path is under the selected learner workspace; source revisions are
# taken from each attempt record, never from the current OEE HEAD.
result = service.check(Path("evidence/SEF/SEF1/SEF1-AS1/ATTEMPT-UUID.json"))
status = service.status()

# Optional explicitly pinned empty-course projection.
empty = service.status(
    "SEF1", "67416343f3eab17ada5d3c79ae6cc782524c29ff"
)

# Pure metadata operation. The caller must deliberately handle publication.
selected = service.export_selected([
    Path("evidence/SEF/SEF1/SEF1-AS1/ATTEMPT-UUID.json"),
])
```

`check` returns `valid`, `invalid`, or `incomplete` for **record integrity and structural references only**. Invalid local paths, mismatched artifact hashes, unsupported formats and unknown required assessments are rejected. Missing source commits or missing local artifacts are reported `incomplete`. Source failures never fall back to OEE `HEAD`. The `review` status is a description of a learner-supplied field, not a verified educational decision.

`status` scans local attempt records, flags duplicate IDs, displays the separate required assessments and their reported review decisions, and never rewrites `progress.md`. `export_selected` rejects missing/invalid/incomplete selections and returns only explicitly chosen record metadata, without copying artifact file content; it does **not** save a file or upload anywhere. The current CLI creates new attempts and exports only, using staged, exclusive file publication with no overwrite.

These filesystem checks are for a trusted learner-owned directory, **not a security sandbox against malicious concurrent filesystem mutation**. Check exports and any chosen optional external URL before sharing; the tool cannot promise that user-authored free-text fields contain no secrets.
