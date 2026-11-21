<!-- markdownlint-disable MD041 -->
<img width="1800" height="298" alt="oee-workspace-banner" src="https://github.com/user-attachments/assets/137ba418-0429-418e-8e71-917bd008577f" />

# OEE Learner Workspace

A reusable workspace for individuals and groups studying the [Open Engineering Education (OEE)](https://github.com/0xbuffdev/open-engineering-education) curriculum.

OEE Workspace supports the practical side of studying OEE. It provides templates and a local Python CLI for organizing practical work, while giving learners a consistent structure for their actual implementations, labs, exercises, notes, projects, and evidence records.

The OEE repository remains the canonical source for the specification and curriculum. This workspace links to those definitions rather than maintaining independent copies of them.

## Repository responsibilities

| Repository | Responsibility |
| --- | --- |
| [Open Engineering Education](https://github.com/0xbuffdev/open-engineering-education) | Canonical specification, curriculum, course requirements, assessments, and project briefs |
| [OEE Workspace](https://github.com/0xbuffdev/oee-workspace) | Workspace structure, local CLI, templates, and conventions for learning and evidence |
| Personal or group workspace derived from OEE Workspace | Actual implementations, labs, exercises, notes, project work, and progress/evidence records |

Use OEE Workspace as the baseline for your own learning environment. You may adapt its structure to your workflow, provided you preserve the references needed to identify the relevant OEE course or project.

A personal or group workspace is where the learning work accumulates over time. It should contain the artifacts and records needed to demonstrate what was built, tested, understood, and improved.

## Getting started

### 1. Create your own workspace fork

Fork this repository and clone your fork. Your learner work is committed to your own repository and tracked on GitHub under your account; the upstream starter stays clean.

From the parent directory where you keep your projects:

```bash
mkdir -p ~/projects
cd ~/projects
```

If the GitHub CLI is installed, one command creates the fork and clones it, adding `upstream` so you can pull template updates from the starter later:

```bash
gh repo fork 0xbuffdev/oee-workspace --clone
cd oee-workspace
```

Without the GitHub CLI, fork the repository on github.com first, then:

```bash
git clone https://github.com/<your-username>/oee-workspace.git
cd oee-workspace
```

A fork of a public repository is public. For private work, create your repository from the template instead: use `Use this template` on the repository page, or run `gh repo create <name> --template 0xbuffdev/oee-workspace --private --clone`. A plain copy of the files also works when GitHub is not part of your workflow.

Do not commit personal work to the upstream starter repository. All content committed to a public repository is publicly visible.

### 2. Select an approved curriculum release

Workspace uses the first-party [OEE Toolkit](https://github.com/0xbuffdev/open-engineering-education/blob/main/tooling/README.md) and a verified, immutable, reviewed curriculum release. The learner CLI does not require an OEE Git checkout.

**Activation gate:** No official steward-signed CalVer curriculum release or published Toolkit package has yet been authorized. The commands below describe the implemented interface; they will return incomplete without an approved, safely installed release. CI uses disposable releases and temporary keys only. Never copy a test digest or key into a real learner project.

When available, independently verify/install the signed whole-curriculum archive using an explicitly trusted steward public key, and commit a reviewed oee-curriculum.lock.json to the learner project. A lock has formatVersion 1, releaseId in YYYY.MM.N format, and a full 64-character manifestSha256. The selected release's Git commit is provenance within its signed manifest, **not a learner input**.

By default, Workspace reads the lock **only from the current working directory**, and Toolkit looks for an already-installed release in its user-scoped cache. The optional --lock and --store arguments select explicit, independently approved paths. No implicit downloads, parent-directory lock search, moving HEAD or auto-repin are allowed.

### 3. Check the selected source

```sh
python -m oee_workspace doctor
# Or explicit reviewed inputs:
python -m oee_workspace doctor --lock ./oee-curriculum.lock.json --store /path/to/verified-releases
```

Missing or altered releases return an incomplete result, never a Git or network fallback.

### 4. Generate a course or project workspace

```sh
python -m oee_workspace course add SEF1 --dest .
python -m oee_workspace course add SEF10 --dest .
```

The CLI uses Toolkit exportVersion 2 to verify the exact selected source before creating learner files. The SEF10 project course also gets project-specific templates. Existing learner directories are never overwritten. Canonical source hyperlinks use the original Git commit from the verified release for attribution/audit, not source selection.

A reading-plan.md is included only if a reviewed resource-map v3 matches releaseId, manifestSha256, courseSha256 and the course's actual academic references. **No SEF1 map is currently active.** Its earlier [editorial review](resources/editorial/SEF1-REVIEW.md) is preserved but not approved for any unreleased source. SEF1 scaffolds without a reading plan until a separate release-specific editorial decision.

### 5. Record, inspect and export learner evidence

```sh
python -m oee_workspace evidence init --course SEF1 --assessment SEF1-AS1 --dest .
python -m oee_workspace evidence check --path evidence/SEF/SEF1/SEF1-AS1/ATTEMPT-UUID.json --dest .
python -m oee_workspace status --course SEF1 --dest .
python -m oee_workspace export --dest . --attempt ATTEMPT-UUID --output exports/selected.json
```

Replace ATTEMPT-UUID with the UUID shown by the init command. Each attempt follows [schema v2](evidence/schemas/attempt-v2.schema.json) and retains full release, manifest and course digests plus original OEE assessment/outcome IDs. A new attempt has no evaluation. A claimed self- or human-review is not an authenticated grade or completion.

The export writes only explicitly chosen local attempt JSON records and never copies artifact bytes, uploads learner data, or overwrites existing output. CLI commands work in Windows PowerShell as well as Linux and macOS, with Python 3.11+ and a separately installed Toolkit; Git is not required for consumer operations.

## Workspace structure

```text
oee-workspace/
├── README.md
├── progress.md
├── labs/
│   └── <program>/<COURSE_CODE>/
├── exercises/
│   └── <program>/<COURSE_CODE>/
├── notes/
│   └── <program>/<COURSE_CODE>/
├── projects/
│   └── <project-course-code>/
├── evidence/
│   └── <program>/<COURSE_CODE>/<ASSESSMENT_ID>/<UUID>.json
├── oee_workspace/
│   ├── __main__.py
│   ├── evidence.py
│   └── local.py
└── templates/
    ├── course-workspace/
    ├── project-workspace/
    └── progress.md
```

The generated directories hold your own work. The templates describe the expected structure; they do not contain completed assignments.

## What belongs in the workspace

Use the workspace to retain:

- Practical lab work and reproducible experiments.
- Exercise implementations, tests, and written reasoning.
- Course summaries and links to completion evidence.
- Project implementations, design decisions, and evaluations.
- Progress records that link to actual artifacts.

A completion claim should be supported by inspectable evidence, not by a checked box alone.

## Public study resources and immutable release updates

The [public resource catalogue](resources/README.md) remains available with optional books and free online material. No paid resource is required by OEE. Resource maps use strict release-keyed schema v3; the previous [SEF1 editorial source review](resources/editorial/SEF1-REVIEW.md) documents useful recommendations and gaps, including the OEE eight-bit versus Hack 16-bit distinction, but is **not an active reviewed release map**. Learners can still start any valid course without a guide.

[Read-only release comparison](docs/OEE-UPSTREAM-DRIFT.md) compares two separately installed approved source locks; it never changes a map or learner evidence. Any edited course source digest requires independent editorial approval before publishing a replacement guide.

## Independent release verification

The [readiness plan](docs/RELEASE-READINESS.md) describes the disposable signed-archive smoke and negative tests, exercised on Linux/macOS/Windows. Synthetic test keys and temporary locks do not approve or publish an official release. No learner, commercial or host data is affected by CI.

## Learner assessment evidence

The [evidence contract](evidence/README.md) is current-only schema v2. Previous Git-revision attempts are not silently upgraded, granted retrospective credit or destroyed. New attempts are tied to a full immutable course identity; local structural checks and reported evaluations cannot certify mastery or verify reviewer identity.

## Evidence and reproducibility

For work involving code or executable systems:

- Record the environment and relevant tool versions.
- Keep the commands required to build, run, and test the artifact.
- Test normal, boundary, invalid-input, and failure cases where relevant.
- Record important assumptions, trade-offs, and limitations.
- Explain at least one failed assumption, debugging result, or significant correction.
- Ensure another person can reproduce the documented result.

See the [OEE Evidence Rules](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/evidence-rules.md) for the canonical requirements.

## AI and agent boundaries

The supported Workspace CLI has **no embedded AI provider, agent runner,
shell executor, grading assistant or automatic network access**. A learner may
use an external assistant independently, but its suggestions and reported
assistance never change the pinned OEE assessment requirements or prove mastery.

Read the [AI and agent safety guide](docs/AI-SAFETY.md) for the enforced
local-file and command boundaries, untrusted prompt/repository text, optional
evidence assistance disclosures, private file handling and what the CLI
**does not** enforce. In particular, the guide is not a sandbox and does not
authorize a future model or execution adapter.

## Security and privacy

Never commit credentials, API keys, private learner data, or unrelated personal material.

For security work, use only systems you own or are explicitly authorized to test. Record the authorized scope and follow the applicable rules of engagement before testing.

Do not commit sensitive logs, private datasets, model weights, or other large generated artifacts unnecessarily. Prefer synthetic fixtures and documented steps for reproducing results.

## Updating templates and the CLI

Generated workspaces are snapshots. Updating a source template does not automatically rewrite files already generated in a learner's workspace.

When changing a template or generator:

1. Explain the intended behavior.
2. Preserve the canonical OEE curriculum as the source of course requirements.
3. Validate the generator against a clean test workspace.
4. Check that existing files are not overwritten.
5. Update the documentation and examples when command syntax changes.

## Curriculum status

OEE courses begin as `draft` and are promoted to `tested` or `verified` only against recorded evidence; see [spec/status-labels.md](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/status-labels.md).

## Project status

The OEE specification and curriculum are maintained in the [OEE repository](https://github.com/0xbuffdev/open-engineering-education). This workspace supports their use; it does not independently define or certify course completion.
