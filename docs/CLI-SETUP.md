# Set up the OEE Workspace CLI

You can study with OEE Workspace without this setup. Follow the [getting-started guide](../README.md) to create a Workspace, choose a course and start working with Markdown files.

Use the CLI when you want course folders created automatically or want to keep local assessment records.

## 1. Check Python

Install [Python 3.11](https://www.python.org/downloads/) and open a terminal in your Workspace folder.

```sh
python --version
```

If your computer uses a different command to launch Python (such as `py` on Windows or `python3` on macOS/Linux), use that command throughout this guide.

Create a fresh [virtual environment](https://docs.python.org/3/library/venv.html) with CPython 3.11. The reviewed binary wheels support glibc Linux and macOS (x86-64/ARM64), and Windows x86-64:

```sh
python -m venv .venv
```

Activate it with `source .venv/bin/activate` on macOS/Linux or `.\.venv\Scripts\Activate.ps1` in Windows PowerShell. If PowerShell prevents activation, see the [Python venv documentation](https://docs.python.org/3/library/venv.html). The example commands below assume the environment is active .

## 2. Download the course files

The CLI uses a verified copy of OEE locally. Download the following files from the two published releases.

From the [OEE Toolkit release](https://github.com/0xbuffdev/open-engineering-education/releases/tag/toolkit-v0.2.0):

- `oee_toolkit-0.2.0-py3-none-any.whl`
- `oee_toolkit-0.2.0.tar.gz`

From the [OEE curriculum release](https://github.com/0xbuffdev/open-engineering-education/releases/tag/curriculum-2026.11.1):

- `oee-curriculum-2026.11.1.tar`
- `oee-curriculum-2026.11.1.attestation.json`
- `oee-curriculum-2026.11.1.sig`
- `oee-steward-ed25519-public.pem`

Create a folder named `oee-official-assets` **next to** your Workspace folder and place all six files there. Keep their original filenames. Do not extract the TAR archive or commit the downloaded files to your learning repository.

Your folders should look like this:

```text
learning/
  YOUR-WORKSPACE/
    README.md
    oee-curriculum.lock.json
    scripts/
  oee-official-assets/
    oee_toolkit-0.2.0-py3-none-any.whl
    oee_toolkit-0.2.0.tar.gz
    oee-curriculum-2026.11.1.tar
    oee-curriculum-2026.11.1.attestation.json
    oee-curriculum-2026.11.1.sig
    oee-steward-ed25519-public.pem
```

## 3. Check and install

From `YOUR-WORKSPACE/`, check the files before installing the Toolkit:

```sh
python -I scripts/install-official-curriculum.py --artifacts ../oee-official-assets --verify-only
```

If the check fails, confirm that you downloaded all six files from the release pages and kept their names. Do not bypass a verification failure.

Install the signature-verification dependency and the checked Toolkit wheel:

```sh
python -I -m pip download --only-binary=:all: --require-hashes -r oee-release-requirements.txt --dest ../oee-official-assets/wheels
python -I -m pip install --no-index --find-links ../oee-official-assets/wheels --only-binary=:all: --require-hashes -r oee-release-requirements.txt
python -I -m pip install --no-index --no-deps ../oee-official-assets/oee_toolkit-0.2.0-py3-none-any.whl
python -I -m pip check
```

Now install the verified curriculum:

```sh
python -I scripts/install-official-curriculum.py --artifacts ../oee-official-assets
```

The installer checks the official source and signature before installing the curriculum in a local store. Your Workspace already contains the matching release selection. You do not need to edit it or look up any identifiers.

## 4. Check that it works

Still in your Workspace folder, run:

```sh
python -m oee_workspace doctor
python -m oee_workspace course add SEF1 --dest .
```

If you are studying another course, replace `SEF1` with its OEE course code. The generator creates your course notes, exercise and lab folders. Project courses also get a project folder.

Existing course folders are never overwritten. If you already created the same folders manually, leave them intact and continue using them instead of rerunning the generator.

## 5. Start studying

Read your chosen course in the [OEE curriculum](https://github.com/0xbuffdev/open-engineering-education/tree/f2afed3e36f6ae0495e2b44a8d9337661defeda1/curriculum) and follow its lessons and assessments. For the original assessment wording and source locations, run:

```sh
python -m oee_workspace assessment-context SEF1
```

The JSON contains the complete verified course and required linked briefs. If applicability is `manual-resolution-required`, read those documents to resolve requirements yourself; the CLI has not classified them. Optional practice remains optional. This is not grading or approval.

Store your work in the new folders and update [`progress.md`](../progress.md).

For more help, use the [labs](../labs/README.md), [exercises](../exercises/README.md), [notes](../notes/README.md), [projects](../projects/README.md) and [assessment evidence](../evidence/README.md) guides.

## If setup fails

Run the commands from the Workspace root, confirm that you're using Python 3.11 and verify that all six downloads are present. If `doctor` reports a missing local curriculum, repeat step 3; the installer checks existing files and does not overwrite a valid installation.

If it still fails, [open a Workspace issue](https://github.com/0xbuffdev/oee-workspace/issues) with the error message, operating system and Python version. Never include personal work, credentials or private files. Contributors maintaining the release verification should use [CONTRIBUTING.md](../CONTRIBUTING.md) and the [release trust record](OEE-RELEASE-TRUST.md).
