<!-- markdownlint-disable MD041 -->
<img width="1800" height="298" alt="oee-workspace-banner" src="https://github.com/user-attachments/assets/137ba418-0429-418e-8e71-917bd008577f" />

# OEE Workspace

OEE Workspace is a free place to organize your work as you follow the [Open Engineering Education (OEE) curriculum](https://github.com/0xbuffdev/open-engineering-education). Study independently or with a group. Keep your programs, circuits, notes and assessment evidence together in a workspace you control.

OEE defines the courses, lessons and assessment requirements. Workspace helps you turn those requirements into organized work. You still choose your study materials and complete the exercises yourself. Workspace does not run assignments, grade submissions or award certificates, and you do not need a 0xNAND account or paid books.

The [OEE Toolkit 0.1.0](https://github.com/0xbuffdev/open-engineering-education/releases/tag/toolkit-v0.1.0) and [signed OEE curriculum 2026.11.1](https://github.com/0xbuffdev/open-engineering-education/releases/tag/curriculum-2026.11.1) are published. Step 4 explains how to check the signing key and install the verified curriculum for Workspace commands. You can start using the Markdown folders without installing either package.

## How to use it

For each course, follow this routine:

1. Choose a course from the public OEE curriculum.
2. Read the course's prerequisites, modules, lesson descriptions, learning outcomes and required assessments.
3. Find explanations and practical tools that help you learn those topics.
4. Do the exercises and experiments yourself. Keep the actual files and your reasoning in this workspace.
5. Check your work against the requirements in OEE and save reproducible evidence.
6. Review what you still need to learn before moving to another course.

In [SEF1: Demystifying the Computer System](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/SEF/SEF1.md), you start with bits and logic, then work through storage, computation and program execution. Workspace is where you can save the circuits you build, truth tables, state traces, experiment notes and evidence for SEF1's three required assessments.

The public [SEF program guide](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/SEF/README.md) gives the study order and prerequisites. Follow that order, especially where one course depends on work you should already have demonstrated in another.

## What you will find here

| Place | What you use it for |
| --- | --- |
| [`progress.md`](progress.md) | Record the courses you are studying, what you have done and what remains |
| [`exercises/`](exercises/README.md) | Keep solutions, practice problems, tests and written reasoning |
| [`labs/`](labs/README.md) | Save experiments, circuits, measurements, procedures and results |
| [`notes/`](notes/README.md) | Explain concepts in your own words and keep resource notes |
| [`projects/`](projects/README.md) | Build larger projects and document their design, tests and evaluation |
| [`resources/`](resources/README.md) | Browse optional books, free websites, tools and reviewed study suggestions |
| [`evidence/`](evidence/README.md) | Keep records that point to work for required OEE assessments |

Your copy of the repository is yours to manage. It stores your work locally, and you decide whether to share it. You do not need an account on a hosted learning platform.

## Start here

### Step 1. Make your own copy

Open [the OEE Workspace repository](https://github.com/0xbuffdev/oee-workspace) and select **Use this template**, then **Create a new repository**. Choose a repository name and select **Private** if your notes or work should not be public. Create the repository under your own GitHub account.

If you use Git on your computer, clone the repository you just created:

```sh
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

Replace the uppercase placeholders with your repository's owner and name. Run subsequent commands from that directory unless noted otherwise.

You can also choose **Code > Download ZIP** on the [original repository](https://github.com/0xbuffdev/oee-workspace), extract the files and open the folder on your computer. GitHub and Git are optional for studying. A downloaded ZIP has no Git commit history or remote backup.

A fork of a public repository is public by default. For private study records or credentials, create a private repository from the template instead of keeping them in a public fork.

### Step 2. Choose what to learn

Open the [OEE curriculum](https://github.com/0xbuffdev/open-engineering-education/tree/main/curriculum) and select a program. If you are new to software engineering, start with the [Software Engineering Foundations (SEF) program](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/SEF/README.md), beginning with [SEF1](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/SEF/SEF1.md).

Before starting a course, read these parts of its OEE page:

- **Prerequisites:** what you must already know or have demonstrated.
- **Modules and lessons:** what to study, in the order given by the course.
- **Learning outcomes:** what you should be able to explain, build, test or defend.
- **Required assessments:** the work and evidence used to judge whether you met those outcomes.

Use the course codes exactly as OEE publishes them, for example `SEF1` and `SEF1-AS1`. Workspace uses those identifiers to keep your work connected to the right requirements.

### Step 3. Begin studying, with or without the CLI

You can start with the files already here. Read the [published curriculum](https://github.com/0xbuffdev/open-engineering-education/tree/f2afed3e36f6ae0495e2b44a8d9337661defeda1/curriculum), browse the [resource library](resources/README.md), update [`progress.md`](progress.md), and make a study folder such as `study/SEF1/`. Python and Toolkit installation can come later.

Before running `course add`, keep your manually created work in a separate folder from `labs/SEF/SEF1/`, `notes/SEF/SEF1/` and `exercises/SEF/SEF1/`. The command will stop if those destinations already exist. Afterward, move your earlier work into the generated folders where it belongs.

Step 4 sets up verified course files, source checks and evidence records. Workspace organizes these files; you complete the learning and assessments.

### Step 4. Install and verify the published OEE release

Install Python **3.11 or newer** with `pip`, the Toolkit `0.1.0` wheel and signed curriculum `2026.11.1`. Once the release is installed, ordinary Workspace commands run offline against the pinned files. They do not fetch GitHub or follow a moving `main` branch.

The project already includes an immutable [`oee-curriculum.lock.json`](oee-curriculum.lock.json).
It selects exactly:

- `releaseId: 2026.11.1`
- `manifestSha256: 57441494eb69c2ff9cb3f6029c8adc3c6a56f8c6ecabc43196c9b686e5959a6c`

The approved public-key DER SHA-256 fingerprint is `0cbd8335bf39fab19b17a7bfaa33502d121d007fca4bddd5df0f43a9c814e2ef`. Check it against the steward's separate record in [release trust and verification](docs/OEE-RELEASE-TRUST.md). A key file downloaded alongside an archive needs this independent check before it can establish who signed the release.

From the root of your personal Workspace, use [GitHub CLI](https://cli.github.com/) to download the release files into a new `oee-official-assets` folder. The same commands work in a Windows terminal with `gh` and Python:

```sh
mkdir oee-official-assets
gh release download toolkit-v0.1.0 --repo 0xbuffdev/open-engineering-education \
  --dir oee-official-assets \
  --pattern 'oee_toolkit-0.1.0-py3-none-any.whl' \
  --pattern 'oee_toolkit-0.1.0.tar.gz'
gh release download curriculum-2026.11.1 --repo 0xbuffdev/open-engineering-education \
  --dir oee-official-assets \
  --pattern 'oee-curriculum-2026.11.1.tar' \
  --pattern 'oee-curriculum-2026.11.1.attestation.json' \
  --pattern 'oee-curriculum-2026.11.1.sig' \
  --pattern 'oee-steward-ed25519-public.pem'
```

You can alternatively download the **same six named files** directly from
the [Toolkit release](https://github.com/0xbuffdev/open-engineering-education/releases/tag/toolkit-v0.1.0)
and [curriculum release](https://github.com/0xbuffdev/open-engineering-education/releases/tag/curriculum-2026.11.1)
using your browser and put them in `oee-official-assets`. Do not extract
the curriculum TAR yourself or use a private signing key.

Before installing the Toolkit wheel, check the size and SHA-256 of each downloaded file against the values committed to this repository. The offline preflight also checks the release lock:

```sh
python scripts/install-official-curriculum.py \
  --artifacts oee-official-assets --verify-only
```

If it passes, install the **exact checked** Toolkit wheel and the verifier
dependency into your chosen Python virtual environment:

```sh
python -m pip install "cryptography>=44,<50"
python -m pip install --no-index --no-deps \
  ./oee-official-assets/oee_toolkit-0.1.0-py3-none-any.whl
python scripts/install-official-curriculum.py --artifacts oee-official-assets
```

The installer checks the Ed25519 public-key fingerprint and detached attestation, validates the archive, then adds the curriculum to your local trusted cache. It refuses to overwrite a previously installed snapshot. Finally, Toolkit reads the committed release lock to select the correct source. The installer and Toolkit do not make network requests. Use Windows path separators where your terminal requires them.

Keep notes and assessment records in your private learner repository. The downloaded public key is safe to share; the steward's private signing key is never needed or created on your computer. After a successful installation, you can delete the download folder and keep the verified local release and lock.

By default, Toolkit looks for an already verified release in the following
user-local folder:

| Operating system | Default installed-release store |
| --- | --- |
| Linux | `$XDG_CACHE_HOME/oee/curriculum-releases` when `XDG_CACHE_HOME` is set; otherwise `~/.cache/oee/curriculum-releases` |
| macOS | `~/Library/Caches/oee/curriculum-releases` |
| Windows | `%LOCALAPPDATA%\oee\curriculum-releases` |

If you deliberately installed the approved archive in a different store,
pass `--store /path/to/verified-releases` to the installer and CLI commands.
The separate explicit installer is allowed to populate the chosen trusted
directory; Workspace's normal `doctor`, course and evidence commands never
download or install releases automatically.

### Step 5. Check that your curriculum is ready

After the verified installation above, open a terminal in the root of your personal Workspace and run:

```sh
python -m oee_workspace doctor
```

A successful check confirms that Workspace can read the trusted local Toolkit source. It does **not** mean the academic course has been graded or verified for educational quality.

The default lock file must be in the directory from which you run the command. If you were given approved release paths outside that directory, you can specify them:

```sh
python -m oee_workspace doctor --lock ./oee-curriculum.lock.json --store /path/to/verified-releases
```

The `--store` argument names an already verified local release store; it does not download an archive. On Windows, use the correct local path for your computer.

If `doctor` reports `store_missing` or `lock_digest_not_found`, check the installed-release directory and run the explicit installer again. Do not change the committed lock just to suppress an error. Workspace will not select another release or download one from GitHub.

### Step 6. Create your course workspace

From the same directory:

```sh
python -m oee_workspace course add SEF1 --dest .
```

The final `.` means "this directory": your personal Workspace root. The command checks the selected SEF1 curriculum and creates space for labs, exercises and notes. For a regular course, the new structure looks like this:

```text
YOUR-REPOSITORY/
├── progress.md
├── labs/
│   └── SEF/
│       └── SEF1/
│           └── README.md
├── exercises/
│   └── SEF/
│       └── SEF1/
│           └── README.md
├── notes/
│   └── SEF/
│       └── SEF1/
│           ├── summary.md
│           └── resources.md
└── evidence/
```

The generated folders are starting points for your own circuits, answers and notes. Their links point to the exact OEE source commit in your verified release.

When a course has a separately approved resource map for your selected release, the command also creates `notes/SEF/SEF1/reading-plan.md`. If the map is missing, unreviewed or belongs to another release, no reading plan is attached. You can still study the course and browse the resource catalogue.

Running `course add` again for the same course reports a conflict and leaves your existing files in place.

### Step 7. Study each module and keep the work

Return to your [OEE course](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/SEF/SEF1.md), read its first module and work through the listed lessons. Your daily routine can be as simple as:

1. Read the lesson description and related outcome in OEE.
2. Choose an explanation or tool from the [resource catalogue](resources/README.md), an approved reading plan if one exists, or another legitimate source.
3. Do the actual practice. Save circuit files and experiments in `labs/SEF/SEF1/`, exercise solutions and tests in `exercises/SEF/SEF1/`, and your explanations in `notes/SEF/SEF1/`.
4. Record which sections or chapters you used in `notes/SEF/SEF1/resources.md`. Include the edition, section title or URL when possible.
5. Update `progress.md` with the work you finished, a link to the files and any questions you still need to answer.

For example, when studying Boolean gates in SEF1, save the simulator circuit, its input/output table, the expected results you calculated independently and a note explaining an error you found. Give files descriptive names so another person can inspect and repeat your work.

You may study with free online material, borrowed books, paid books you already own or other resources. A suggested book chapter is a reading aid, **not** a replacement for the requirements in OEE. For SEF1, Nand to Tetris's Hack computer uses a 16-bit design while the OEE reference machine uses an eight-bit design; you must follow OEE's own required behaviors when preparing OEE assessment evidence.

### Step 8. Prepare for the required assessments

Practice exercises may help you prepare, but course completion depends on the assessments specified in OEE. Read the course's **Required assessments** section for the work, criteria and evidence required.

SEF1 has three required assessment IDs:

| Assessment | Area of work |
| --- | --- |
| `SEF1-AS1` | Representation and logic |
| `SEF1-AS2` | Storage and ALU |
| `SEF1-AS3` | Program-to-output investigation |

Do the work, keep the artifacts and record how to reproduce the results. Your files should allow another person to check what you did and how it addresses the OEE criteria. The [OEE Evidence Rules](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/evidence-rules.md) explain what counts as appropriate evidence.

### Step 9. Create an evidence attempt

When your assessment work is ready and the official release has been installed, create a new local attempt record:

```sh
python -m oee_workspace evidence init --course SEF1 --assessment SEF1-AS1 --dest .
```

The command prints a file path that looks like:

```text
evidence/SEF/SEF1/SEF1-AS1/ATTEMPT-UUID.json
```

`ATTEMPT-UUID` is a placeholder. Use the actual UUID printed by your command. Each attempt has its own file, so you can retain multiple attempts without replacing earlier work.

Open the generated JSON in a text editor. Its OEE course identity, release digest, assessment ID and outcome IDs are taken from the verified curriculum. Leave those identifiers unchanged. The new record contains empty `artifacts` and `observations` arrays, and `evaluation` is initially `null`.

Add references to files that actually exist in your workspace. For example, after saving a circuit you can use an artifact entry of this form inside the generated `artifacts` array:

```json
{
  "kind": "relative-path",
  "value": "labs/SEF/SEF1/01-logic/nand.circ"
}
```

The path is an example. Use your real file path, relative to the Workspace root, with forward slashes. Never point a local artifact entry outside your workspace. You can also add an observation describing what you tested, what happened and how you fixed a mistake. The [evidence guide](evidence/README.md) explains the supported format and optional file hashes.

An evidence record documents what you submitted for an assessment attempt. A reviewer still needs to evaluate whether you met the outcome.

### Step 10. Check the evidence and inspect progress

Validate the attempt with the path printed during initialization:

```sh
python -m oee_workspace evidence check --path evidence/SEF/SEF1/SEF1-AS1/ATTEMPT-UUID.json --dest .
```

The validator checks the JSON record, its release and assessment references, and the local files you cite. It also checks file digests when present. Missing or changed artifacts leave the attempt incomplete until you correct the reference. The validator does not execute or grade your assignment.

To see the recorded assessment attempts and outstanding decisions for the course:

```sh
python -m oee_workspace status --course SEF1 --dest .
```

`status` summarizes local attempts and recorded evaluations. Workspace does not authenticate the evaluator's identity or certify course completion.

Update `progress.md` yourself with the real work completed and links to supporting files. Only mark a course complete when its actual OEE completion conditions have been satisfied through appropriate assessment and review.

### Step 11. Export an attempt when you need to share it

To export a specific local attempt as JSON:

```sh
python -m oee_workspace export --dest . --attempt ATTEMPT-UUID --output exports/selected.json
```

Replace the UUID with an existing attempt ID. The command writes a new file at `exports/selected.json` and refuses to overwrite an existing file of that name. You can repeat `--attempt` to include more than one specific attempt.

The export contains only the attempt records you selected. Circuit files, programs, reports and other artifact bytes must be shared separately if an assessor needs them. Review the JSON and any supporting files before sending them; the built-in secret check does not detect every type of private information.

### Step 12. Continue with other courses and projects

When you are ready for another course, consult the [OEE program guide](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/SEF/README.md) for the prerequisite-valid order. Then run `course add` with the next official course code.

Project courses also use the same command. For example, `SEF10` is the Foundations capstone:

```sh
python -m oee_workspace course add SEF10 --dest .
```

For a project course, Workspace additionally creates `projects/SEF10/` with a project brief link and templates for design, evaluation and retrospective. These are blank starting points for your own project.

**Check prerequisites before starting a project.** Workspace validates the selected course and creates files, but it does not authenticate that you have already passed prerequisite courses. For SEF10, OEE requires verified prerequisite completion before the capstone begins.

## Resources and curriculum updates

The [resource library](resources/README.md) contains optional reading and free tools. Some courses may eventually have a reviewed reading plan linked to individual modules and lessons. The learner remains responsible for checking the exact edition, chapter, access conditions and course outcomes. A missing reading plan never removes OEE's public requirements.

When OEE publishes a new signed curriculum release, your Workspace stays pinned to the current version. Your notes, earlier evidence and reading plans are left alone. Keep each completed attempt tied to the release you used. Review a new release and its resource mapping before updating the lock for future work. The [release comparison](docs/OEE-UPSTREAM-DRIFT.md) explains what changed without editing your files.

## Privacy, AI and your work

Your study notes, code, circuits and evidence belong in your own workspace. Review files before pushing them to a public GitHub repository, and never commit passwords, API keys, private records or material you are not allowed to redistribute.

Some external learning projects have their own licenses and rules about publishing solutions. Link to the original material and keep restricted solutions private. You can use a different free resource when a book or service is inaccessible.

OEE Workspace has no built-in AI tutor, agent, automatic grader or system for running your code. You can use independent tools when the specific OEE assessment rules permit them. Describe assistance accurately in your evidence; an AI-generated answer or a passing validator check cannot substitute for work you can explain and defend. See the [AI and agent safety guide](docs/AI-SAFETY.md).

## Need help or want to improve Workspace?

If a learner command fails, copy the exact error, note your operating system and Python version, and check whether your selected release and lock are available. Avoid posting private learner files or release signing keys in an issue. You can [report a problem in GitHub Issues](https://github.com/0xbuffdev/oee-workspace/issues). The repository does not currently have GitHub Discussions enabled.

If you want to change the templates, CLI, validators, resource catalogue or documentation, read [CONTRIBUTING.md](CONTRIBUTING.md). It contains the maintainer workflow, developer tests and release-check procedures. For academic course changes, contribute directly to the [OEE curriculum repository](https://github.com/0xbuffdev/open-engineering-education).
