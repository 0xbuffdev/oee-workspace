# Contributing

Use this guide when working on Workspace's Python CLI, templates, resource catalogue, tests or documentation. If you're studying OEE rather than contributing code, start with the [learner README](README.md) for setup, course work and evidence records.

The [OEE curriculum](https://github.com/0xbuffdev/open-engineering-education) defines learning outcomes, prerequisites, assessments and project briefs. Workspace organizes learner work and optional resources. Changes to course requirements belong in OEE, where they can be reviewed as part of the academic source.

## Documentation ownership

Use the root [README.md](README.md) for the learner's first steps: what Workspace does, prerequisites, installation of the published releases, exact commands, generated paths, privacy and limitations.

Keep development setup, template maintenance, resource review, contracts, test fixtures, the release procedure and DCO instructions in CONTRIBUTING or linked maintainer docs. Anything that changes what a learner must do also belongs in the README. Check documentation commands against the CLI before publishing.

Write plainly and describe the current behavior. Keep paths, flags, schema versions, license boundaries and links exact. A temporary test signature must never be described as an official release.

## Implementation boundaries

| Responsibility | Authority and implementation |
| --- | --- |
| Academic curriculum, required outcomes, evidence rules | [OEE](https://github.com/0xbuffdev/open-engineering-education) and its specification |
| Verified course exports | [OEE Toolkit](https://github.com/0xbuffdev/open-engineering-education/blob/main/tooling/README.md) reading a locally installed signed curriculum release |
| CLI and safe file creation | `oee_workspace/__main__.py` and `oee_workspace/local.py` |
| Evidence attempt records | `oee_workspace/evidence.py` and [schema v2](evidence/schemas/attempt-v2.schema.json) |
| Optional resource catalogue and mapping | `resources/catalog/` and [resource-map v3](resources/schemas/course-map.schema.json) |
| Generated learner starting points | `templates/`, with learner files stored in their own repository |

Workspace reads academic data from the Toolkit's version 2 export. It does not parse OEE Markdown on its own. CLI commands use the exact release selected by a reviewed project lock and work offline. A passing structural check validates the source format; it does not grade a learner or establish that a course is educationally ready.

The local file writer stages new directories and stops when a destination already exists. Changes to templates, evidence records or source checks must preserve that protection. Any feature that grades work, runs code, accesses a model or credentials, or uses the network requires a separate design and security review with tests.

## Developer and release verification

Tests require Python 3.11 or newer. The signed curriculum `2026.11.1` and Toolkit `0.1.0` are public. Two independent test suites cover different risks. Disposable fixtures test behavior under expected and invalid conditions; the official-release smoke downloads the actual signed files and checks their hashes, signing-key fingerprint and learner CLI operations. Neither suite grades student work.

The Toolkit package-verifier portability test is owned by the
[OEE repository](https://github.com/0xbuffdev/open-engineering-education).
On Debian/Ubuntu without `ensurepip`, install the matching `python3-venv`
package or select a Python with `--python` when running the OEE
`verify_package_install.py` script. OEE's source-only report and
independently executed wheel/sdist verifier have different scopes.

Documentation changes can affect learner installation, so `release-readiness.yml` runs when `README.md`, `CONTRIBUTING.md` or maintainer docs change. Before tagging a Workspace release, record passing Linux, macOS and Windows runs on the exact merged `main` commit. A green PR check for an earlier commit is insufficient.

From the source repository root:

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/check-resources.py
python scripts/render-resource-guides.py --check
python -m oee_workspace --help
npx --yes markdownlint-cli2@0.24.0
```

For an independent disposable curriculum-release smoke, start with separate local OEE and Workspace checkouts, then run the existing maintainer-only verification script from Workspace:

```sh
python scripts/verify-external-workspace.py --workspace-source . --oee-source ../open-engineering-education --report ./workspace-test.json
```

This maintainer command builds a temporary signed release from the OEE checkout, installs it locally and exercises Workspace without Git. It does not install the official learner release or approve a signing key. See the [release-readiness guide](docs/RELEASE-READINESS.md) for prerequisites and the Linux, macOS and Windows tests.

The Toolkit `0.1.0` and curriculum `2026.11.1` have separate public releases. Start with `python scripts/install-official-curriculum.py --artifacts DIR --verify-only` to check all six downloaded files before installing the wheel. Run the installer again without `--verify-only` to verify the signature and install the curriculum by its manifest digest. The approved source and signing-key identities are in `oee-curriculum.lock.json` and the [release trust record](docs/OEE-RELEASE-TRUST.md).

The [`official-release-smoke.yml`](.github/workflows/official-release-smoke.yml) workflow downloads those public assets on Linux, macOS and Windows. It exercises the published Toolkit and Workspace without an OEE source checkout or disposable signer. Record its run URL on the exact merged Workspace commit alongside the separate fixture workflow.

Review every cited chapter or section, access condition, coverage gap and assessment difference before approving a resource map. Use schema v3 and the existing guide renderer. Publishing the curriculum does not approve the SEF1 resource map or change anyone's release lock or study files.

## Documentation and resource change checklist

A README or resource edit should be checked against the current source before opening a PR:

1. Verify every student command against `python -m oee_workspace --help` and the current parser.
2. Verify the learner-facing folder layout against the templates and `course add` publication code.
3. Check every citation, book edition, chapter and optional resource against its publisher or official project page. Clearly record partial and unmapped curriculum coverage.
4. Keep the published Toolkit and signed curriculum release identities, independent public-key fingerprint and local verification instructions accurate. Disposable fixture signatures cannot become learner trust anchors.
5. Re-run tests and Markdown lint at the submitted commit. Keep existing generated learner paths and assessment records untouched.

## What you can contribute

- Improvements to the workspace README and directory guides.
- Better templates for labs, exercises, project documentation, or evidence.
- Bug fixes and validation improvements in the Python CLI and local publication operations.
- Improvements to privacy, reproducibility, and safe workspace practices.
- Documentation and configuration fixes.
- Reproducible examples that demonstrate a useful improvement.

## Before submitting

1. Check existing issues and pull requests.
2. Explain the problem the change is intended to solve.
3. Keep the proposed change focused.
4. Preserve the distinction between canonical OEE requirements and workspace-specific organization.
5. Avoid committing personal learner data, credentials, or unrelated generated artifacts.

Changes to a canonical course requirement should be proposed in the [OEE repository](https://github.com/0xbuffdev/open-engineering-education), not introduced solely through a workspace template.

## Template changes

Templates define the starting structure for future learner workspaces. A change to a template does not automatically rewrite files already generated by learners.

When changing a template:

- Explain the intended change.
- Preserve useful existing sections unless there is a reason to remove them.
- Check all links and placeholders.
- Generate a fresh workspace and inspect the output.
- Confirm that the generator does not overwrite an existing destination.
- Update the relevant documentation if the generated structure changes.

## CLI, templates and safety changes

Keep the OEE Toolkit as Workspace's sole source parser. CLI changes must validate the selected immutable release and leave learner files intact. Do not add compatibility wrappers or adapters for earlier export formats.

From the source repository root, run:

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python -m oee_workspace --help
npx --yes markdownlint-cli2@0.24.0
```

Disposable fixture tests use an exact local OEE checkout; learner commands use the installed verified release. CI runs on Linux, macOS and Windows.

Read the [AI and agent safety boundaries](docs/AI-SAFETY.md) before proposing a security-sensitive change. New model dependencies, code execution, network clients, credential readers or automatic assessment decisions require a reviewed threat model, permission design and tests. Treat repository text, imported prompts and model output as untrusted input; instructions in text do not enforce a security boundary.

## Contributions and licensing

Contributors must have the right to submit their work under the applicable repository license.

Documentation and workspace guidance use the license identified in [`LICENSE`](LICENSE). Scripts and templates use the license identified in [`LICENSE-MIT`](LICENSE-MIT).

Contributors retain their copyright. Submitting a contribution does not transfer ownership to 0xBUFF.

For contributions that use the Developer Certificate of Origin, follow the instructions in [`DCO.md`](DCO.md) and sign commits with `git commit -s`.

## Resource-map source changes

A changed OEE upstream `main` is not authorization to update a reviewed
resource map. Read the [upstream drift and pinned source guide](docs/OEE-UPSTREAM-DRIFT.md)
and inspect the reported canonical outcome, assessment and module changes
before proposing a new immutable curriculum release mapping. Keep partial-coverage gaps,
verify cited editions and accessible alternatives, regenerate guides
deterministically and seek maintainer approval. Do not add a version adapter
or use the moving OEE `HEAD` for any learner source check.

## Pull requests

A pull request should explain:

- The problem.
- What changed.
- How the change was validated.
- Whether existing generated workspaces are affected.
- Any limitations or follow-up work.

Do not describe a change as tested unless the relevant test or validation was actually performed.

## Community standards

All contributors must follow the repository's [`Code of Conduct`](CODE_OF_CONDUCT.md).
