# Internal validation and resource tools

The supported learner command is [`python -m oee_workspace`](../README.md). The
`scripts/` directory contains **repository-maintenance tools**, not a second
course or project generator. All CLI commands use Python 3.11+, Git and a
trusted local OEE Toolkit checkout. No Bash or remote service is required.

| Tool | Purpose |
| --- | --- |
| `check-resources.py` | Validate the resource catalogue and resource-map v2 against its exact OEE source |
| `render-resource-guides.py` | Render or check deterministic, repository-owned guides from reviewed v2 maps |
| `verify-oee-export.py` | Validate the canonical Toolkit export contract and optional consumer references without parsing OEE Markdown |
| `report-oee-drift.py` | Compare exact pinned maps with a separately selected upstream OEE commit; report review risks without remapping |

## Learner CLI

The current module provides the following operations without maintaining
deprecated Bash commands or project-name aliases:

```text
python -m oee_workspace doctor --oee OEE_REPO --revision FULL_SHA
python -m oee_workspace course add SEF1 --oee OEE_REPO --revision FULL_SHA --dest LEARNER_DIR
python -m oee_workspace resources check --oee OEE_REPO --map MAP_FILE
python -m oee_workspace evidence init --oee OEE_REPO --revision FULL_SHA --course SEF1 --assessment SEF1-AS1 --dest LEARNER_DIR
python -m oee_workspace evidence check --oee OEE_REPO --path RECORD_FILE --dest LEARNER_DIR
python -m oee_workspace status --oee OEE_REPO --dest LEARNER_DIR
python -m oee_workspace export --oee OEE_REPO --dest LEARNER_DIR --output FILE --attempt UUID
```

The `--oee` checkout and `--revision` are explicit where source selection
is needed. A moving `HEAD`, branch or abbreviated SHA cannot replace an exact
canonical course commit. The CLI refuses unsupported OEE formats: only
`v0.2.0` and Workspace resource-map v2 are current.

Course generation stages all new files under the learner destination before
publication. The validated Toolkit course type controls project scaffolding;
there is no separate arbitrary project generator. An existing course or
project destination is never merged or overwritten. Expected failed staged
publication rolls back only newly owned, unchanged directories. Power failure
or external concurrent mutations can require manual inspection.

Fresh evidence attempts and explicit local exports use a same-directory
temporary file and an exclusive hard-link installation to prevent
overwriting existing records. If hard links are unsupported by a selected
filesystem, publication fails rather than silently replacing a file.
`--output` for local exports must stay inside the selected learner workspace,
and exported files contain no artifact bytes. Workspace performs no hidden
upload, telemetry, automated grading or execution of learner code.

## Resource validation

The resource checker executes the **first-party OEE Toolkit** against the
map's recorded immutable local Git commit, then checks v2 source references.
No independent curriculum Markdown parser or schema converter is included.

```sh
python scripts/check-resources.py --oee /path/to/open-engineering-education
python scripts/render-resource-guides.py --oee /path/to/open-engineering-education --check
python -m oee_workspace resources check --oee /path/to/open-engineering-education --map resources/mappings/SEF/SEF1.json
```

SEF1 has a reviewed, source-pinned map with seven documented partial-coverage
gaps. Optional resources never replace OEE assessments or require a purchase.
A course without a matching **reviewed** map still scaffolds without a
reading plan and explicitly reports why guidance was omitted.

### Export-consumer interface

`verify-oee-export.py` is a narrow structural interface check for the
first-party Toolkit's `exportVersion: 1` JSON contract, not proof that
caller-supplied JSON is trustworthy. Normal Workspace operations obtain
exports directly from the first-party Toolkit.

```sh
python scripts/verify-oee-export.py \
  --export /path/to/pinned-course-export.json \
  --revision FULL_OEE_SOURCE_COMMIT_SHA \
  --json
```

A full, locally available source SHA and matching course, outcomes, assessments,
modules and lessons are mandatory. Missing revisions are incomplete;
unsupported formats and invalid source references fail explicitly.

## Advisory upstream OEE changes

Pinned maps and published guides are validated against the **recorded**
revision, not a moving branch. The separate
[upstream drift workflow](../docs/OEE-UPSTREAM-DRIFT.md) detects meaningful
changes in a chosen, explicit target revision. Its results never overwrite
resource maps or infer module/assessment equivalence.

```sh
# Supply a full OEE Git SHA for the target you wish to inspect.
python scripts/report-oee-drift.py \
  --oee /path/to/open-engineering-education \
  --target-revision TARGET_FULL_SHA \
  --course SEF1
```

Drift reports are deterministic JSON. Exit `0` means both revisions were
structurally comparable, **not** necessarily drift-free; consult
`results[].state`. Exit `3` means target revision data is incomplete, while
invalid recorded pins fail. The scheduled/manual workflow preserves a
separate advisory artifact and job summary. No automatically generated
resource remap or backward-compatibility reader is provided.

## Independent release smoke

Use the [release-readiness guide](../docs/RELEASE-READINESS.md) to verify an
entire learner flow from clean Git clones, without relying on private 0xNAND
content, paid resources or credentials:

```sh
python scripts/verify-external-workspace.py \
  --workspace-source . --oee-source /path/to/open-engineering-education \
  --report ../workspace-readiness.json
```

The script clones both selected source commits to a temporary directory,
runs their supported CLI with a separate local learner destination, and
records a JSON report. The CI release matrix runs it on Linux, macOS and
Windows, preserving platform artifacts. It does not release/tag software,
fetch remote sources, or rewrite either source checkout.

## Development checks

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python -m oee_workspace --help
npx --yes markdownlint-cli2@0.24.0
```

The repository contract CI additionally installs `jsonschema==4.23.0`
**for schema tests only** and exercises pinned SEF1/SEF10 OEE exports.
A separate CI matrix runs the public CLI smoke tests on Linux, macOS and
Windows. Only source repositories you trust should be selected with
`--oee`: a local Git object ID does not authenticate a repository origin.

For evidence record semantics, privacy boundaries and review claims, see
[the evidence record guide](../evidence/README.md).
