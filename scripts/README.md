# Workspace generation scripts

The scripts in this directory create workspace structures for OEE courses and projects. They use templates maintained in this repository and validate identifiers against a local checkout of the canonical OEE curriculum.

## Scripts

| Script | Purpose |
| --- | --- |
| `new-course-workspace` | Creates the lab, exercise, and notes directories for a course |
| `new-project-workspace` | Creates the documentation structure for a project |
| `check-resources.py` | Validates public catalogue records and canonical course mappings |
| `render-resource-guides.py` | Produces deterministic, portable Markdown guides |

## Pinned OEE Toolkit consumer contract (WS-I11 groundwork)

The independent `verify-oee-export.py` command checks an already
generated, source-pinned OEE **export format 1** against an explicitly
selected full OEE commit SHA. It accepts an optional **resource-map v2**
document, checking canonical source identity, module/lesson locators,
outcome IDs and assessment IDs without parsing the OEE Markdown again.

```sh
python3 scripts/verify-oee-export.py \
  --export /path/to/SEF1.json \
  --revision FULL_OEE_SOURCE_COMMIT_SHA \
  --json
```

Pass `--map /path/to/reviewed-v2-map.json` to inspect a resource map's
consumer references. An unsupported schema v1, incompatible export
version, wrong SHA, unknown assessment, missing outcome coverage or changed
module/lesson locator **fails explicitly**. There is no v1 reader,
conversion process or fallback to the checkout's moving HEAD.

This standalone export consumer is a narrow interface check, not proof of source provenance or an editorial review. WS-I01 now invokes the public OEE Toolkit on each v2 map's exact locally available Git commit, then checks the freshly derived export with this consumer. Old schema v1 is rejected. WS-I02 will author a reviewed map and WS-I04 will harden guide publishing. No active reviewed map has been published yet.

Do not use a standalone, externally provided export as proof of source provenance. The Workspace resource validator runs the public OEE Toolkit against the selected local Git commit, then checks the export. Its SHA identifies local bytes but does not authenticate the origin of an untrusted checkout. These checks establish structural consistency, **not** educational conformance, resource verification or learner achievement.

## Prerequisites

- Bash.
- Python 3 (for resource validation and mapped-course study guides).
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
OEE_REPO=/path/to/open-engineering-education ./scripts/new-course-workspace SEF SEF1
```

`OEE_REPO` must point to the local checkout containing the `curriculum/` directory.

## Destination directory

Both scripts accept an optional destination directory:

```bash
./scripts/new-course-workspace SEF SEF1 /path/to/workspace
./scripts/new-project-workspace ledgerlab /path/to/workspace
```

When the destination is omitted, the scripts use `OEE_WORKSPACE` if set, or the current directory otherwise.

The destination directory must already exist. The scripts refuse to overwrite existing generated destinations.

## Curriculum links

Generated files link to the canonical definitions in the public OEE repository. If you work from a fork or another published source, set `OEE_CURRICULUM_URL` to the appropriate base URL:

```bash
OEE_CURRICULUM_URL=https://github.com/example/oee-fork/blob/main ./scripts/new-course-workspace SEF SEF1
```

The expected format is a base URL that precedes paths such as `curriculum/SEF/<course-file>.md`.

## Current compatibility

The generators recognize the five canonical programs (`SEF`, `APP`, `SYS`, `AI`, `SEC`) but scaffold only course definitions that explicitly declare OEE `v0.2.0`; historical formats fail as `unsupported_format`. Each requested course is checked against the local OEE checkout. Course codes are the program code plus a number. The project generator reads each project's canonical brief from the local OEE checkout and fails until that brief exists. When OEE changes its course identifiers or project definitions, update the relevant script mappings and validate them against the new canonical files.

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

## Public reading plans

There is currently no reviewed active v2 course mapping. Unmapped course scaffolding
creates independent learner notes and resources logs without a reading plan.
The old SEF1 v1 map is a negative regression fixture, never current study advice.

For mapped courses, validation now invokes the **single OEE Toolkit parser** on
the map's full Git SHA from a local OEE checkout. Neither the worktree nor HEAD
is a fallback. No v1 reader, automatic remapping or arbitrary supplied export
is accepted by the full resource validator.

```sh
python3 scripts/check-resources.py --oee /path/to/open-engineering-education
python3 scripts/check-resources.py --oee /path/to/open-engineering-education --course SEF1 --json
python3 scripts/render-resource-guides.py --oee /path/to/open-engineering-education --course SEF1 --stdout
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The resource-check exit codes are `0` for structurally passed, `1` for
invalid references and `3` for missing or unsupported pinned sources.
With no active maps, the command checks the public catalogue only. This
does not imply a reviewed curriculum mapping or learner certification.

WS-I02 owns SEF1 human resource remapping, WS-I04 owns publication-safe
guide writes, and WS-I11 owns remaining upstream drift notifications.
