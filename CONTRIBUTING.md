# Contributing

This guide is for people improving OEE Workspace's Python CLI, templates, resource catalogue, tests and documentation. If you are learning with the OEE curriculum, start with the [learner README](README.md). It explains how to create your own workspace, study a course, keep artifacts and record evidence.

OEE's [public curriculum](https://github.com/0xbuffdev/open-engineering-education) remains the authority for learning outcomes, prerequisites, assessments and project briefs. Workspace supplies local organization and optional study resources. Do not create course requirements here or change the academic source to fit a resource.

## Documentation ownership

The root [README.md](README.md) is the student's first guide. Explain the purpose, what they get, prerequisites, precise learner commands and output paths, limitations, privacy, and what can be used before official releases.

Put contributor onboarding, source code and template maintenance, CLI development, resource review, contract validation, release process, test fixtures and DCO instructions here in CONTRIBUTING or the linked maintenance documents. Student-facing notices still belong in the README when they affect a student's actions. Documentation examples must match the supported CLI exactly.

Apply plain factual language. Avoid inflated claims, unnecessary status chatter, historical implementation notes and unsupported statements that a temporary signed test fixture is an approved release. Keep paths, flags, schema versions, licensing statements and URLs accurate.

## Implementation boundaries

| Responsibility | Authority and implementation |
| --- | --- |
| Academic curriculum, required outcomes, evidence rules | [OEE](https://github.com/0xbuffdev/open-engineering-education) and its specification |
| Verified course exports | [OEE Toolkit](https://github.com/0xbuffdev/open-engineering-education/blob/main/tooling/README.md) reading a locally installed signed curriculum release |
| CLI and safe file creation | `oee_workspace/__main__.py` and `oee_workspace/local.py` |
| Evidence attempt records | `oee_workspace/evidence.py` and [schema v2](evidence/schemas/attempt-v2.schema.json) |
| Optional resource catalogue and mapping | `resources/catalog/` and [resource-map v3](resources/schemas/course-map.schema.json) |
| Generated learner starting points | `templates/`, with learner files stored in their own repository |

The Toolkit's course-export version 2 is the only supported academic consumer source. Workspace does not parse curriculum Markdown independently. CLI commands operate offline against a release selected by an independently approved project lock. A passing structural check does not establish academic readiness or grade a learner.

The local publication layer stages new directories and refuses to replace existing learner work. Preserve these boundaries when making changes to paths, templates, evidence, source checks or project generation. New grading, model access, execution, credentials or network capabilities require separate design, security review and tests.

## Developer and release verification

The repository tests run with Python 3.11 or newer. The basic CLI and resource checks do not make an official curriculum release available. Release integration tests create separate, short-lived fixtures; the signed artifacts they generate are not for learner use.

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

This command builds publisher-side fixtures using the local OEE checkout, verifies a temporary signed archive, and checks the Git-free Workspace CLI against the installed test release. It is **not** a normal student command and cannot supply official package installation, signing-key trust or publication approval. The [release-readiness guide](docs/RELEASE-READINESS.md) documents its prerequisites, Windows/macOS/Linux CI runs and failure checks.

Official curriculum distribution and Toolkit package publication are separate steward decisions. Before activating an official resource map, verify the exact approved release ID, complete manifest SHA-256, installed release and actual Toolkit course export. Then independently review every source chapter/section, access condition, coverage gap and OEE-specific assessment difference. Use the existing map schema v3 and guide renderer. Never fill in fictional signed release digests, alter existing learner locks or rewrite learner files automatically.

## Documentation and resource change checklist

A README or resource edit should be checked against the current source before opening a PR:

1. Verify every student command against `python -m oee_workspace --help` and the current parser.
2. Verify the learner-facing folder layout against the templates and `course add` publication code.
3. Check every citation, book edition, chapter and optional resource against its publisher or official project page. Clearly record partial and unmapped curriculum coverage.
4. Keep the official-release availability statement accurate. Temporary signatures, repository tags and the Toolkit source-build candidate do not make a public learner release.
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

Changes to the Workspace Python CLI must keep the canonical OEE Toolkit as
the only source parser, validate independently reviewed immutable release locks and preserve
existing learner files. No compatibility shell wrappers or prior-format
adapters are accepted.

From the source repository root, run:

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python -m oee_workspace --help
npx --yes markdownlint-cli2@0.24.0
```

The disposable publisher-side acceptance fixtures additionally require an exact local OEE
checkout. Learner CLI operations use only a verified offline release. CI runs tests on Linux,
macOS and Windows.

For security changes, consult the
[AI and agent safety boundaries](docs/AI-SAFETY.md). No pull request may add
a model-provider dependency, execution entry point, network client, credential
reader or automatic assessment decision without a **separate reviewed threat
model, permission design and tests**. Repository content, imported prompts
and model output are always untrusted data. A text instruction is not a
technical sandbox or authorization.

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
