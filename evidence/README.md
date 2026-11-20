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

These are **runtime validation obligations for WS-I07**. WS-I06 supplies the schema, synthetic fixtures and independent tests of the source-reference contract. It intentionally does not ship a learner evidence validator, CLI, status engine or export tool yet. JSON Schema cannot verify a file exists, whether a hash matches, an outcome's assessed adequacy, or whether a reviewer is genuine.

## Example fixture and testing

The [synthetic fixtures](../tests/fixtures/evidence/) exercise SEF1 conceptual attempts and SEF10 project attempts at pinned OEE commit `67416343f3eab17ada5d3c79ae6cc782524c29ff`. They include unreviewed attempts, self-review, an **unverified claimed human review**, malformed structures and reference/integrity failures. They do not represent actual learner achievements.

```bash
python3 -m pip install "jsonschema==4.23.0"
OEE_REPO=/path/to/open-engineering-education \
  python3 -m unittest discover -s tests -p 'test_evidence_schema.py' -v
```

`jsonschema` is a **test-only dependency** to exercise the published Draft 2020-12 contract. It is not required to create or study in a Workspace; ordinary runtime tools remain offline and standard-library-based. CI independently checks the real fixed-commit OEE Toolkit exports for SEF1 and SEF10.

## Privacy and status boundaries

Records live locally and require no login, remote upload, model or paid book. Do not write credentials, private datasets, personal logs, raw agent transcripts or assessment secrets to public evidence directories. External URL entries are display references, not fetched content or trustworthy independent evidence.

The future WS-I07 status view may report *attempt recorded*, *self-assessed*, or *human-review reported* (reviewer unverified). It must consider every required assessment individually; two required assessments that cover one outcome cannot be collapsed into one success. Only explicitly selected attempts may enter a future portable export. No default telemetry, hidden upload, automatic execution or grading is authorized here.
