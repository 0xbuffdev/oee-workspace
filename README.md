<!-- markdownlint-disable MD041 -->
<img width="1800" height="298" alt="OEE Workspace banner" src="https://github.com/user-attachments/assets/137ba418-0429-418e-8e71-917bd008577f" />

# OEE Workspace

OEE Workspace is a free place to work through the [Open Engineering Education (OEE) curriculum](https://github.com/0xbuffdev/open-engineering-education). Keep your experiments, code, notes, projects and assessment evidence in a repository you control.

OEE defines what you need to learn and demonstrate. Workspace gives that work a consistent structure. You can study independently or with others, without a 0xNAND account or paid books. Workspace does not grade assignments or issue certificates.

You can use the Markdown folders immediately. The Python CLI is available when you want course scaffolding and checks against the signed curriculum.

## Create your workspace

Select [**Use this template**](https://github.com/0xbuffdev/oee-workspace) on GitHub and make a repository under your account. Choose **Private** if you intend to keep personal work or assessment records.

Clone your new repository:

```sh
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

Replace the placeholders with your repository details. You can also download the [repository ZIP](https://github.com/0xbuffdev/oee-workspace) and work locally without Git. A ZIP has no commit history or remote backup. A public fork is not a private study space.

If you are new to software engineering, start with [SEF1: Demystifying the Computer System](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/SEF/SEF1.md). Otherwise choose a course from the [curriculum](https://github.com/0xbuffdev/open-engineering-education/tree/main/curriculum). The [SEF program guide](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/SEF/README.md) gives the course order and prerequisites. Read the lessons, outcomes and required assessments before beginning.

## What's in the repository

| Path | Purpose |
| --- | --- |
| [`progress.md`](progress.md) | Your course progress, evidence links and next steps |
| [`labs/`](labs/README.md) | Experiments, circuits, observations and results |
| [`exercises/`](exercises/README.md) | Solutions, tests, traces and reasoning |
| [`notes/`](notes/README.md) | Explanations and logs of materials used |
| [`projects/`](projects/README.md) | Project designs, implementations and evaluations |
| [`evidence/`](evidence/README.md) | Records linking required assessments to actual work |
| [`resources/`](resources/README.md) | Optional books and free learning material |

You can begin with a manual folder such as `study/SEF1/` and update `progress.md`. If you plan to run `course add` later, keep that work outside `labs/SEF/SEF1/`, `exercises/SEF/SEF1/` and `notes/SEF/SEF1/` until the CLI creates those directories. It will not overwrite existing work.

## Install the official OEE curriculum

The CLI requires Python 3.11 or newer, [OEE Toolkit 0.1.0](https://github.com/0xbuffdev/open-engineering-education/releases/tag/toolkit-v0.1.0) and the [signed OEE curriculum 2026.11.1](https://github.com/0xbuffdev/open-engineering-education/releases/tag/curriculum-2026.11.1). These are separate releases with separate versions.

This repository includes [`oee-curriculum.lock.json`](oee-curriculum.lock.json). It selects release `2026.11.1` with manifest SHA-256:

```text
57441494eb69c2ff9cb3f6029c8adc3c6a56f8c6ecabc43196c9b686e5959a6c
```

The approved steward Ed25519 public key has DER SHA-256 fingerprint:

```text
0cbd8335bf39fab19b17a7bfaa33502d121d007fca4bddd5df0f43a9c814e2ef
```

Check the signing-key identity against the independently reviewed [release-trust record](docs/OEE-RELEASE-TRUST.md). A public key downloaded alongside an archive cannot establish its own trust.

### Download six published files

Install the [GitHub CLI](https://cli.github.com/) if you want to use these commands. Run each command on one line from your Workspace root. This works in Bash and avoids shell-specific line continuation on Windows PowerShell.

```sh
mkdir oee-official-assets
gh release download toolkit-v0.1.0 --repo 0xbuffdev/open-engineering-education --dir oee-official-assets --pattern 'oee_toolkit-0.1.0-py3-none-any.whl' --pattern 'oee_toolkit-0.1.0.tar.gz'
gh release download curriculum-2026.11.1 --repo 0xbuffdev/open-engineering-education --dir oee-official-assets --pattern 'oee-curriculum-2026.11.1.tar' --pattern 'oee-curriculum-2026.11.1.attestation.json' --pattern 'oee-curriculum-2026.11.1.sig' --pattern 'oee-steward-ed25519-public.pem'
```

Alternatively, download the same six named files in a browser from the [Toolkit release](https://github.com/0xbuffdev/open-engineering-education/releases/tag/toolkit-v0.1.0) and [curriculum release](https://github.com/0xbuffdev/open-engineering-education/releases/tag/curriculum-2026.11.1). Put them in `oee-official-assets/` without extracting the archive.

### Verify, then install

Run the offline preflight before installing any downloaded wheel:

```sh
python scripts/install-official-curriculum.py --artifacts oee-official-assets --verify-only
```

This checks the size and SHA-256 of all six files and the exact project lock. Stop if it fails. In your chosen Python environment, install the signature verifier, the checked Toolkit wheel and finally the signed curriculum:

```sh
python -m pip install "cryptography>=44,<50"
python -m pip install --no-index --no-deps ./oee-official-assets/oee_toolkit-0.1.0-py3-none-any.whl
python scripts/install-official-curriculum.py --artifacts oee-official-assets
```

The installer verifies the approved public-key fingerprint, detached signature, attestation and archive before adding the curriculum to a trusted local store. It leaves existing installations untouched and does not fetch network data. Normal Workspace commands only read locally verified files.

| OS | Default local release store |
| --- | --- |
| Linux | `$XDG_CACHE_HOME/oee/curriculum-releases`, or `~/.cache/oee/curriculum-releases` if unset |
| macOS | `~/Library/Caches/oee/curriculum-releases` |
| Windows | `%LOCALAPPDATA%\oee\curriculum-releases` |

If you deliberately choose a different trusted location, pass `--store PATH` to the installer and subsequent commands. The steward's private signing key is never needed on your computer.

## Set up your first course

From the Workspace root:

```sh
python -m oee_workspace doctor
python -m oee_workspace course add SEF1 --dest .
```

`doctor` checks that the exact installed curriculum and Toolkit are readable. It does not evaluate the academic quality of a course.

`course add` creates:

```text
labs/SEF/SEF1/README.md
exercises/SEF/SEF1/README.md
notes/SEF/SEF1/summary.md
notes/SEF/SEF1/resources.md
```

Generated files point to the exact verified OEE source. A matching, separately approved resource map may also create `notes/SEF/SEF1/reading-plan.md`. **No SEF1 resource map is active yet**, so use the [public resource catalogue](resources/README.md) directly.

A repeated `course add` reports `WSC011 [conflict]` and does not replace your files. If `doctor` reports `store_missing` or `lock_digest_not_found`, check the installed store or repeat the explicit installer. Do not change the approved lock to bypass an error.

To select a reviewed lock and an existing trusted store explicitly:

```sh
python -m oee_workspace doctor --lock ./oee-curriculum.lock.json --store /path/to/verified-releases
```

Use the correct local path for your OS.

## Learn and keep the evidence

Read the selected OEE module, complete the work yourself and save the files under the appropriate folders. In `notes/SEF/SEF1/resources.md`, record the chapters, editions or URLs you used. Update `progress.md` with links to finished work and the gaps you still need to address.

For a logic circuit, save the circuit, its truth table, expected results and a note on errors you corrected. Someone else should be able to reproduce your results.

Suggested materials are optional. *Nand to Tetris* uses a 16-bit Hack computer; OEE SEF1's required teaching machine uses its own eight-bit design. Follow OEE's specified behavior when producing assessment evidence.

SEF1 has three required assessments: `SEF1-AS1` (representation and logic), `SEF1-AS2` (storage and ALU) and `SEF1-AS3` (program-to-output investigation). Check the [course](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/SEF/SEF1.md) and [OEE Evidence Rules](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/evidence-rules.md) for the actual criteria.

When work for an assessment is ready, create an evidence attempt:

```sh
python -m oee_workspace evidence init --course SEF1 --assessment SEF1-AS1 --dest .
```

The command prints a unique file such as `evidence/SEF/SEF1/SEF1-AS1/ATTEMPT-UUID.json`. Replace the placeholder in later commands with the actual UUID.

The record already contains the verified course, release, assessment and outcome identifiers; leave them unchanged. Fill in your observations and references to real files. For example, an entry inside the `artifacts` array might be:

```json
{
  "kind": "relative-path",
  "value": "labs/SEF/SEF1/01-logic/nand.circ"
}
```

The path is illustrative. Use an existing path inside your own Workspace. The [evidence guide](evidence/README.md) documents the supported format, optional hashes and privacy rules.

Check the attempt and see the local assessment summary:

```sh
python -m oee_workspace evidence check --path evidence/SEF/SEF1/SEF1-AS1/ATTEMPT-UUID.json --dest .
python -m oee_workspace status --course SEF1 --dest .
```

These commands validate record structure, release identity and local references. They do not run code, grade an assessment, authenticate a reviewer or certify completion.

To export selected attempt JSON for a reviewer:

```sh
python -m oee_workspace export --dest . --attempt ATTEMPT-UUID --output exports/selected.json
```

Export refuses to overwrite an existing file. It includes only the selected JSON records, not the circuits, code or other artifact bytes they refer to. Review the output for private information and share supporting files separately when needed.

## Continue to projects and other courses

Check prerequisites in the [OEE program guide](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/SEF/README.md) before moving on. For the Foundations capstone:

```sh
python -m oee_workspace course add SEF10 --dest .
```

OEE identifies SEF10 as a project course, so this also creates `projects/SEF10/` with its canonical brief link and templates for design, evaluation and retrospective. Generating a project folder does not verify that you have passed its prerequisite courses.

Your lock remains pinned when OEE publishes another curriculum release. The [release-comparison guide](docs/OEE-UPSTREAM-DRIFT.md) explains how maintainers review changes without altering your existing work.

## Privacy and support

Keep passwords, API keys, private records and restricted solutions out of public commits. Workspace has no built-in AI tutor, agent, automatic grader or student-code executor. Disclose outside assistance when an assessment requires it; a valid JSON record is not proof of mastery. See [AI and agent safety](docs/AI-SAFETY.md).

For a problem, [open a GitHub issue](https://github.com/0xbuffdev/oee-workspace/issues) with the command, error, OS and Python version. Do not post private learner files or credentials. See [CONTRIBUTING.md](CONTRIBUTING.md) to improve Workspace. Changes to learning outcomes and assessments belong in the [OEE curriculum repository](https://github.com/0xbuffdev/open-engineering-education).
