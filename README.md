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

### 2. Clone the OEE repository

The Python CLI validates canonical course and project identifiers against a local OEE Toolkit checkout at an explicit immutable Git commit before creating any files. The checkout also lets you read the canonical course definitions and project briefs next to your work, and it keeps validation working offline.

Stay in the parent directory from step 1 and clone OEE as a sibling of your fork:

```bash
cd ~/projects

git clone https://github.com/0xbuffdev/open-engineering-education.git
```

Use the explicit `--oee` argument to select that trusted local checkout and `--revision` to select a full 40-character commit SHA. No command selects the moving `HEAD`, downloads a source or requires an account.

### 3. Check the local OEE source

From the root of your Workspace fork or template copy, run the offline CLI using Python 3.11 or later. This example uses one known immutable OEE v0.2.0 commit; choose the exact published source revision for the course you intend to study.

```bash
python -m oee_workspace doctor --oee ../open-engineering-education \
  --revision 67416343f3eab17ada5d3c79ae6cc782524c29ff
```

### 4. Generate a course workspace

The supported entry point is **`python -m oee_workspace`**. Both the source checkout and learner destination are explicit:

```bash
python -m oee_workspace course add SEF1 \
  --oee ../open-engineering-education \
  --revision 67416343f3eab17ada5d3c79ae6cc782524c29ff \
  --dest .
```

The CLI validates one Toolkit export from that commit, stages templates off-path, and creates `labs/`, `exercises/` and `notes/` only when no corresponding learner directories already exist. A `reading-plan.md` is included only when a **reviewed** public resource map matches the **same** source revision. An unmatched or unreviewed map is clearly omitted, not silently attached to newer course requirements. `resources.md` and `summary.md` remain learner-owned.

If the Toolkit identifies the course as `Type: project`, the same command also generates `projects/<COURSE_CODE>/` with its design and review templates. For example:

```bash
python -m oee_workspace course add SEF10 \
  --oee ../open-engineering-education \
  --revision 67416343f3eab17ada5d3c79ae6cc782524c29ff \
  --dest .
```

There is no project-alias table or second Bash generator. A project brief is a link to the exact canonical OEE commit. Course status and requirements are not invented by Workspace.

### 5. Record and check evidence

A new assessment attempt receives a fresh UUID, includes its real pinned assessment/outcome identifiers and starts with **no evaluation**:

```bash
python -m oee_workspace evidence init \
  --oee ../open-engineering-education \
  --revision 67416343f3eab17ada5d3c79ae6cc782524c29ff \
  --course SEF1 --assessment SEF1-AS1 --dest .
```

The command prints the resulting `evidence/SEF/SEF1/SEF1-AS1/<UUID>.json` path. Add your actual artifact links, observations and deliberately recorded evaluation as appropriate, then check the specific record:

```bash
python -m oee_workspace evidence check \
  --oee ../open-engineering-education \
  --path evidence/SEF/SEF1/SEF1-AS1/<UUID>.json --dest .

python -m oee_workspace status \
  --oee ../open-engineering-education --dest .
```

For a local, **explicitly selected** evidence-only export:

```bash
python -m oee_workspace export \
  --oee ../open-engineering-education --dest . \
  --attempt <UUID> --output exports/selected.json
```

The export command creates a new JSON file and refuses to overwrite an existing one. It includes neither unselected records nor artifact file bytes, and never uploads data. Review learner-authored text for private information before sharing. The tool cannot authenticate reviewer claims, certify mastery or change OEE course readiness.

On Windows, use the equivalent `python -m oee_workspace` command from PowerShell, with your own `--oee` and `--dest` paths. The CLI, Toolkit and Git must be available locally; no Bash runtime is required.

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

## Public study resources

The [public resource library](resources/README.md) contains optional book and online resources and a strict v2 mapping schema. A [reviewed SEF1 v2 resource map](resources/mappings/SEF/SEF1.json) and [generated guide](resources/guides/SEF/SEF1.md) are available for independent study. The review confirms the recorded references and explicit partial-coverage gaps; it does not certify OEE educational readiness or completion.

Mapped SEF1 workspaces generate a source-pinned reviewed reading-plan snapshot; other courses without a map still initialize **without a reading plan**. The resource validator resolves the exact OEE Git commit recorded in each map, not the checkout's moving HEAD. Learner-owned `resources.md` remains available, and existing learner directories are never overwritten. Generation stages complete directories before installation. Expected publication failures roll back only unchanged, newly created directories and preserve pre-existing files; a process crash or concurrent external modification can still leave partial new output requiring inspection. Evidence files and exports are published using exclusive, no-clobber filesystem operations. Public resources stay independent of private 0xNAND content.

## Learner assessment evidence

The [learner evidence record format](evidence/README.md) provides a strict, learner-owned JSON Schema v1 for OEE v0.2.0 assessment attempts. Records identify the exact OEE source commit, required assessment and outcome IDs, optional artifacts and observations, and explicitly declared evaluations.

The schema and [synthetic SEF1/SEF10 fixtures](tests/fixtures/evidence/) are published for interoperability. The supported Python CLI now exposes evidence initialization, pinned validation, read-only status and explicitly selected, local JSON export. A structurally valid record, automated test observation, self-assessment or claimed human-review label does **not** prove mastery or verify reviewer identity. No account, online service or paid resource is required.

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
