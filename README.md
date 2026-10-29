# OEE Learner Workspace

A reusable workspace for individuals and groups studying the [Open Engineering Education (OEE)](https://github.com/0xbuffdev/open-engineering-education) curriculum.

OEE Workspace supports the practical side of studying OEE. It provides templates and generation scripts for organizing practical work, while giving learners a consistent structure for their actual implementations, labs, exercises, notes, projects, and evidence records.

The OEE repository remains the canonical source for the specification and curriculum. This workspace links to those definitions rather than maintaining independent copies of them.

## Repository responsibilities

| Repository | Responsibility |
| --- | --- |
| [Open Engineering Education](https://github.com/0xbuffdev/open-engineering-education) | Canonical specification, curriculum, course requirements, assessments, and project briefs |
| [OEE Workspace](https://github.com/0xbuffdev/oee-workspace) | Workspace structure, templates, generation scripts, and conventions for learning and evidence |
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

The generation scripts validate course and project identifiers against a local OEE checkout before creating any files. The checkout also lets you read the canonical course definitions and project briefs next to your work, and it keeps validation working offline.

Stay in the parent directory from step 1 and clone OEE as a sibling of your fork:

```bash
cd ~/projects

git clone https://github.com/0xbuffdev/open-engineering-education.git
```

If you use a fork or a different local location for OEE, set `OEE_REPO` to the path of that checkout. The default is a sibling directory named `open-engineering-education`.

### 3. Generate a course workspace

Run the course generator from the root of your workspace copy:

```bash
./scripts/new-course-workspace SEF SEF0
```

To write into another directory:

```bash
./scripts/new-course-workspace SEF SEF0 /path/to/workspace
```

You can also set a default destination:

```bash
OEE_WORKSPACE=/path/to/workspace ./scripts/new-course-workspace SEF SEF0
```

The generator validates the requested course against the local OEE curriculum and creates the corresponding directories under `labs/`, `exercises/`, and `notes/`.

Course codes are the program code plus a number, such as `SEF0` or `SYS1`. The generator validates the code against the local OEE checkout and fails until the matching course file exists.

### 4. Generate a project workspace

Use the project generator for a project defined by the OEE curriculum:

```bash
./scripts/new-project-workspace ledgerlab
```

To choose a destination:

```bash
./scripts/new-project-workspace ledgerlab /path/to/workspace
```

The generator creates the project's documentation structure and links back to its canonical OEE brief. It does not copy the canonical brief into the workspace as an independent source of truth. The generator validates the project brief against the local OEE checkout and fails until that brief exists in the checkout.

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
│   └── <project-slug>/
├── scripts/
│   ├── new-course-workspace
│   └── new-project-workspace
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

## Evidence and reproducibility

For work involving code or executable systems:

- Record the environment and relevant tool versions.
- Keep the commands required to build, run, and test the artifact.
- Test normal, boundary, invalid-input, and failure cases where relevant.
- Record important assumptions, trade-offs, and limitations.
- Explain at least one failed assumption, debugging result, or significant correction.
- Ensure another person can reproduce the documented result.

See the [OEE Evidence Rules](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/evidence-rules.md) for the canonical requirements.

## Security and privacy

Never commit credentials, API keys, private learner data, or unrelated personal material.

For security work, use only systems you own or are explicitly authorized to test. Record the authorized scope and follow the applicable rules of engagement before testing.

Do not commit sensitive logs, private datasets, model weights, or other large generated artifacts unnecessarily. Prefer synthetic fixtures and documented steps for reproducing results.

## Updating templates and scripts

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
