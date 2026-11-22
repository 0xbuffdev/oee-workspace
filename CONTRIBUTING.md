# Contributing to OEE Workspace

OEE Workspace is a free, learner-owned companion to the [Open Engineering Education curriculum](https://github.com/0xbuffdev/open-engineering-education). You can contribute to its Python CLI, templates, tests, documentation and optional resource catalogue.

For help studying with Workspace, start with the [learner README](README.md). This guide is for contributions to the repository.

## What belongs where

| Area | Authority |
| --- | --- |
| Curriculum, outcomes, prerequisites and assessments | [OEE specification and curriculum](https://github.com/0xbuffdev/open-engineering-education) |
| Trusted course data and source verification | [OEE Toolkit](https://github.com/0xbuffdev/open-engineering-education/blob/main/tooling/README.md) |
| Local course creation and CLI | [`oee_workspace/`](oee_workspace/) |
| Learner assessment records | [`evidence/`](evidence/) and assessment-attempt schema v2 |
| Optional resources and mappings | [`resources/`](resources/) and resource-map schema v3 |
| Starting files for new courses | [`templates/`](templates/) |

Workspace reads the Toolkit's exportVersion 2 against an exact, reviewed curriculum lock. It does not parse OEE curriculum Markdown itself. Normal learner commands run offline and do not fetch or switch source releases. A passing validation is evidence of structural correctness, not proof of academic readiness or learner achievement.

Keep changes to canonical course requirements in OEE. Do not change learner data, introduce a network service, execute a learner's code or add AI grading without a separate reviewed design and security assessment.

## Before opening a PR

1. Check existing issues and PRs. Describe the problem and keep the proposed fix focused.
2. For documentation, compare every command, path and version against the current CLI and published artifacts.
3. For a resource change, verify the edition, chapter or section, access conditions and any gap against the actual released course. An editorial matrix is not an approved reading plan.
4. For a template or CLI change, generate a fresh course, inspect the output and confirm that existing directories are not overwritten.
5. Keep learner records, secrets, paid material you cannot redistribute and unrelated generated files out of commits.

A PR should say what changed, which tests ran, whether existing learner files are affected and what remains outside its scope.

## Run checks locally

Use Python 3.11 or newer. The repository's schema tests require `jsonschema==4.23.0`, which CI installs separately.

```sh
python -m pip install "jsonschema==4.23.0"
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/check-resources.py
python scripts/render-resource-guides.py --check
python -m oee_workspace --help
npx --yes markdownlint-cli2@0.24.0
```

The learner CLI also requires the verified OEE Toolkit and signed curriculum; follow the [README installation instructions](README.md#install-the-official-oee-curriculum).

The [official OEE smoke workflow](.github/workflows/official-release-smoke.yml) downloads the published Toolkit `0.1.0` and signed curriculum `2026.11.1`, verifies their fixed hashes and signature and checks the learner path on Ubuntu, macOS and Windows.

The [independent readiness workflow](.github/workflows/release-readiness.yml) uses a disposable signed OEE test release. It covers normal behavior and failure handling without the steward's private signing key. To run that maintainer fixture test with an OEE source checkout and the source-built Toolkit available:

```sh
python scripts/verify-external-workspace.py --workspace-source . --oee-source ../open-engineering-education --report ./workspace-test.json
```

That `--oee-source` option belongs to the fixture script, not to the learner CLI. The [release-readiness guide](docs/RELEASE-READINESS.md) explains the separate test suites and final-commit checks.

## Templates and safe file creation

Course creation stages new directories and refuses destinations that already exist. Evidence records and exports also refuse to overwrite existing files. A template change affects new course workspaces only; previously generated learner files stay as they are.

Verify the course and project layouts against [`oee_workspace/__main__.py`](oee_workspace/__main__.py). Check placeholder substitutions, canonical source links, Markdown formatting and missing-map behavior. Test duplicate-course creation and failed publication when changing the file writer.

## Resources and release changes

The public resource catalogue remains available even without approved reading plans. Maps must use schema v3 and match the signed curriculum release, exact course hash and independently reviewed references. Before activating a map, verify optional books and free alternatives against the released OEE course, then check the generated guide.

Use the [immutable-release comparison](docs/OEE-UPSTREAM-DRIFT.md) to inspect possible course drift. It cannot approve a new map, repin learners or migrate old records. Changing the approved lock or stewardship key requires its own review.

## Safety and privacy

Read [AI and agent safety](docs/AI-SAFETY.md) before changes involving models, credentials, code execution or network calls. Repository text, external resources and model output are untrusted inputs. Keep assessment evaluation claims truthful: the CLI validates structure and references, but does not authenticate reviewers or grade learners.

Do not add telemetry, upload personal data or rewrite learner files as an incidental part of a change.

## Licenses and contribution sign-off

The documentation uses the license in [`LICENSE`](LICENSE), and scripts and templates use [`LICENSE-MIT`](LICENSE-MIT). Contributors retain their copyright and must have the right to submit work under those licenses.

Follow the [Developer Certificate of Origin](DCO.md) and sign commits with `git commit -s`. The [Code of Conduct](CODE_OF_CONDUCT.md) applies to all contributions.

## Release procedure

A published OEE curriculum release does not automatically publish Workspace. Before releasing a Workspace tag, merge the signed release-preparation PR, verify both three-OS release workflows and contract/quality checks on the **exact final merged main SHA**, then review the release notes and attribution. A passing PR-head run is not enough. See the [release decision](docs/RELEASE-DECISION.md) and [readiness guide](docs/RELEASE-READINESS.md).

Documentation should describe currently supported features and published versions. Keep historical changes in release notes rather than presenting obsolete commands as alternatives.
