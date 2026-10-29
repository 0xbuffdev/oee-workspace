# Workspace generation scripts

The scripts in this directory create workspace structures for OEE courses and projects. They use templates maintained in this repository and validate identifiers against a local checkout of the canonical OEE curriculum.

## Scripts

| Script | Purpose |
| --- | --- |
| `new-course-workspace` | Creates the lab, exercise, and notes directories for a course |
| `new-project-workspace` | Creates the documentation structure for a project |

## Prerequisites

- Bash.
- A local clone of [Open Engineering Education](https://github.com/0xbuffdev/open-engineering-education).
- A workspace directory that already exists.
- The templates included in this repository.

The scripts do not download or rewrite the curriculum. They read the local OEE checkout to validate the requested course or project.

## Repository discovery

By default, the scripts look for an OEE checkout in a sibling directory named `open-engineering-education`:

```text
projects/
  open-engineering-education/
  oee-workspace/
```

If your directories differ, set `OEE_REPO` to the OEE repository's root:

```bash
OEE_REPO=/path/to/open-engineering-education ./scripts/new-course-workspace SEF SEF0
```

`OEE_REPO` must point to the local checkout containing the `curriculum/` directory.

## Destination directory

Both scripts accept an optional destination directory:

```bash
./scripts/new-course-workspace SEF SEF0 /path/to/workspace
./scripts/new-project-workspace ledgerlab /path/to/workspace
```

When the destination is omitted, the scripts use `OEE_WORKSPACE` if set, or the current directory otherwise.

The destination directory must already exist. The scripts refuse to overwrite existing generated destinations.

## Curriculum links

Generated files link to the canonical definitions in the public OEE repository. If you work from a fork or another published source, set `OEE_CURRICULUM_URL` to the appropriate base URL:

```bash
OEE_CURRICULUM_URL=https://github.com/example/oee-fork/blob/main ./scripts/new-course-workspace SEF SEF0
```

The expected format is a base URL that precedes paths such as `curriculum/SEF/<course-file>.md`.

## Current compatibility

The generators support the five canonical programs (`SEF`, `APP`, `SYS`, `AI`, `SEC`) and validate the requested course against the local OEE checkout. Course codes are the program code plus a number. The project generator reads each project's canonical brief from the local OEE checkout and fails until that brief exists. When OEE changes its course identifiers or project definitions, update the relevant script mappings and validate them against the new canonical files.

Do not invent new identifiers in a generator just to make a command pass.

## Safe operation

The generators:

- Validate the requested course or project.
- Confirm that the required templates exist.
- Require an existing destination.
- Refuse to overwrite an existing generated destination.
- Avoid generating learner files inside the canonical OEE repository.

Generated files are starting points. Review and customize them to reflect your actual implementation, experiments, and evidence.

## Validation

From the workspace repository root, run:

```bash
bash -n scripts/new-course-workspace
bash -n scripts/new-project-workspace
npx --yes markdownlint-cli2@0.24.0
```

Test generation in a disposable directory before relying on a changed script in a real workspace.
