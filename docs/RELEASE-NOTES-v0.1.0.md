# OEE Workspace v0.1.0

OEE Workspace is a free, learner-owned companion to the [Open Engineering Education curriculum](https://github.com/0xbuffdev/open-engineering-education). Use it to organize course notes, labs, programs, projects and evidence for required assessments in a repository you control.

This release makes the Python CLI available with the official, signed OEE curriculum. It creates study folders and keeps local assessment records tied to the exact curriculum release they came from. You can still study using the Markdown folders without installing the CLI.

## What's included

- Python 3.11+ CLI with `doctor`, `course add`, `resources check`, `evidence init`, `evidence check`, `status` and `export`.
- Immutable `oee-curriculum.lock.json` selecting the signed OEE curriculum `2026.11.1`, read through the published OEE Toolkit `0.1.0`.
- An offline verification and installation flow that checks the original release files, approved Ed25519 public-key fingerprint, detached signature and curriculum archive.
- Course folders for labs, exercises and notes, plus project templates for courses such as `SEF10`.
- Learner-owned assessment attempts using evidence schema v2, local status reports and explicitly selected JSON exports.
- A public catalogue of optional books and free resources. Reading plans require an independently approved resource map for the exact signed curriculum; none is active for SEF1 yet.
- Release checks on Ubuntu, macOS and Windows using both the official published archive and independent disposable test fixtures.

Workspace refuses to overwrite existing course folders or evidence records. Its normal CLI operates offline and does not download new curriculum releases or silently change the project lock.

## Getting started

Create your own repository using the [Workspace template](https://github.com/0xbuffdev/oee-workspace) or download the files as a ZIP. You can begin studying without a hosted account or paid books.

For CLI use, follow the [README's official OEE installation instructions](https://github.com/0xbuffdev/oee-workspace/blob/v0.1.0/README.md#install-the-official-oee-curriculum). After verifying and installing the exact published Toolkit and curriculum, run:

```sh
python -m oee_workspace doctor
python -m oee_workspace course add SEF1 --dest .
```

Study the course's actual lessons and assessments in [OEE](https://github.com/0xbuffdev/open-engineering-education). Workspace helps store the work and its evidence. It does not run student programs, grade assignments, verify prerequisite completion or award certificates.

## Release identity

The OEE specification `v0.2.0`, Toolkit `0.1.0`, curriculum `2026.11.1` and Workspace `v0.1.0` are independently versioned. See the [trusted-release reference](https://github.com/0xbuffdev/oee-workspace/blob/v0.1.0/docs/OEE-RELEASE-TRUST.md) for the exact source identity and signing-key fingerprint.

For problems or improvements, [open a Workspace issue](https://github.com/0xbuffdev/oee-workspace/issues). See the [release decision](https://github.com/0xbuffdev/oee-workspace/blob/v0.1.0/docs/RELEASE-DECISION.md) for the checks required before this tag is published.
