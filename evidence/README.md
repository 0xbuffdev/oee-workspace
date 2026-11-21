# Learner-owned evidence records

OEE Workspace records assessment **attempts**, not academic grades or automatic certification. The [OEE Evidence Rules](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/evidence-rules.md) remain authoritative.

## Active format

The only active record is [assessment-attempt schema v2](schemas/attempt-v2.schema.json). It contains a UTC timestamp and UUIDv4, an exact source repository and OEE specification, canonical course code/path and the independently selected releaseId, full manifestSha256 and courseSha256. It records one required authored assessment ID, its outcome IDs, optional artifact references, observations, assistance disclosure and an evaluation (initially null).

Artifact paths stay inside the selected learner workspace; optional SHA-256 values verify bytes. Display-only external HTTP(S) references are never fetched. No automatic student-code execution, model access or grading occurs. Evaluations are explicitly self- or human-reported and reviewer identity is **not authenticated**. A passing structural validation does not prove the learner satisfied academic criteria or upgrade the OEE course status.

The earlier Git-revision-based evidence contract is **not** an active runtime reader. There is no automatic conversion, retroactive grading, re-pinning or deletion of existing learner files. Non-disposable learner work must be preserved pending a separately approved disposition process.

## Commands

After an official curriculum release is reviewed, independently verified/installed and locked for your project:

~~~sh
python -m oee_workspace evidence init --course SEF1 --assessment SEF1-AS1 --dest .
python -m oee_workspace evidence check --path evidence/SEF/SEF1/SEF1-AS1/ATTEMPT-UUID.json --dest .
python -m oee_workspace status --course SEF1 --dest .
python -m oee_workspace export --dest . --attempt ATTEMPT-UUID --output exports/selected.json
~~~

Use the actual UUID returned by the first command. The current working directory supplies only its own oee-curriculum.lock.json by default; --lock and --store optionally select reviewed explicit inputs. Missing or altered sources return an incomplete result, never a Git/network fallback.

New attempt paths follow evidence/PROGRAM/COURSE/ASSESSMENT/UUID.json. Evidence check validates the record format and source identity against the verified Toolkit export, confirms required assessment references, checks local artifacts, and rejects unsafe traversal and mismatched digests. Read-only status reports separate assessment decisions and never infers completion. Export includes only selected JSON records, no artifact bytes, and refuses overwriting existing output or unrelated learner data.

Unit tests use synthetic records and CI uses disposable signed curriculum releases. Neither constitutes steward authorization or a learner grade.
