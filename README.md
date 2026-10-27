# Study Workspace

A study workspace for an individual or a group working through the [Open Engineering Education (OEE)](https://github.com/0xbuffdev/open-engineering-education) curriculum.

This is where learner state lives: labs, exercises, notes, project work, and the progress/evidence log. The standard itself (course files, book maps, templates, scripts) lives in the OEE repository. This workspace references it and does not duplicate it.

## Why a separate repository

OEE ships templates only. Experiments, answers, notes, projects, and the evidence log must not be committed to the standard's repository.

## Setup

Clone OEE next to this workspace. The examples below assume that:

```bash
cd ~/projects    # or wherever you keep your repositories
git clone git@github.com:0xbuffdev/open-engineering-education.git
```

## Start a course

Run from the root of this workspace:

```bash
../open-engineering-education/scripts/new-course-workspace foundations F0
```

The script validates the course against the OEE curriculum and writes into the current directory:

```text
labs/<track>/<CODE>/README.md
exercises/<track>/<CODE>/README.md
notes/<track>/<CODE>/resources.md
notes/<track>/<CODE>/summary.md
```

To write somewhere else, pass a target directory or set `OEE_WORKSPACE`:

```bash
../open-engineering-education/scripts/new-course-workspace foundations F0 /path/to/workspace
OEE_WORKSPACE=/path/to/workspace ../open-engineering-education/scripts/new-course-workspace foundations F0
```

Do not create a workspace for a course you have not reached; an empty directory is not progress.

## Start a project

```bash
../open-engineering-education/scripts/new-project-workspace ledgerlab
```

The briefs, gates, and acceptance criteria stay canonical in [curriculum/projects/](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/projects/README.md). This repository holds your implementation and evidence. Start a project only when its gate is recorded in [progress.md](progress.md).

## Layout

```text
labs/<track>/<CODE>/        experiments and implementation notes
exercises/<track>/<CODE>/   drills, written answers, tests
notes/<track>/<CODE>/       resource log, summary, retrospective
projects/<slug>/            portfolio and capstone work
progress.md                 completion and evidence log
books/                      legal local copies only; ignored by Git
```

## Rules

- A course is complete only when its exit check is demonstrable and the artifact runs from a clean checkout. A checked box without a link to evidence is not progress.
- Keep secrets, private data, model weights, and copyrighted books out of Git.
- Record versions, seeds, hardware, commands, and limitations for every measurement.
- Commit small, explain what changed, and keep a runnable artifact.

## Curriculum status

Every OEE course currently carries the `draft` status label. Labels are promoted to `tested` and `verified` only against committed evidence; see [spec/status-labels.md](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/status-labels.md).
