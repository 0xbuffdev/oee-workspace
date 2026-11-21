<!-- markdownlint-disable MD041 -->
<img width="1800" height="298" alt="oee-workspace-banner" src="https://github.com/user-attachments/assets/137ba418-0429-418e-8e71-917bd008577f" />

# OEE Workspace

OEE Workspace is a free, personal place to do the practical work in the [Open Engineering Education (OEE) curriculum](https://github.com/0xbuffdev/open-engineering-education). You can use it on your own or with a study group. It gives you a way to organize what you study, keep the programs and circuits you build, write down what you learn, and save evidence of the skills you have demonstrated.

OEE tells you which courses to take, what each lesson covers, and what you must be able to do. Workspace gives you folders and simple commands to manage the work. It does not teach the lessons for you, run your assignments, grade your answers, or award certificates. You choose how to study and which free or optional learning materials to use. You do not need a 0xNAND account or a paid book.

**You can start organizing and studying now.** Some commands below depend on an official, signed OEE curriculum release and a published OEE Toolkit. Those official releases are not available yet. Until they are published, follow the manual starting steps. The commands are documented so you know exactly what will become available.

## How to use it

The usual learning cycle is straightforward:

1. Choose a course from the public OEE curriculum.
2. Read the course's prerequisites, modules, lesson descriptions, learning outcomes and required assessments.
3. Find explanations and practical tools that help you learn those topics.
4. Do the exercises and experiments yourself. Keep the actual files and your reasoning in this workspace.
5. Check your work against the requirements in OEE and save reproducible evidence.
6. Review what you still need to learn before moving to another course.

For example, [SEF1: Demystifying the Computer System](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/SEF/SEF1.md) starts with bits and logic and proceeds through storage, computation and program execution. You can use Workspace to keep circuit designs, truth tables, state traces, experiment notes and your records for the three required SEF1 assessments.

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

The folders belong to you once you create your own copy of this repository. Workspace stores work locally, so you can study without a hosted learning account. You decide what to share and with whom.

## Start here

### Step 1. Make your own copy

Open [the OEE Workspace repository](https://github.com/0xbuffdev/oee-workspace) and select **Use this template**, then **Create a new repository**. Choose a repository name and select **Private** if your notes or work should not be public. Create the repository under your own GitHub account.

If you use Git on your computer, clone the repository you just created:

```sh
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

Replace both uppercase placeholders with the actual names shown on your new repository page. Run the rest of the commands from this directory unless a step says otherwise.

You can also choose **Code > Download ZIP** on the [original repository](https://github.com/0xbuffdev/oee-workspace), extract the files and open the folder on your computer. GitHub and Git are optional for studying. A downloaded ZIP has no Git commit history or remote backup.

If you prefer to fork instead, remember that **forks of public repositories are public by default**. Do not put private student records or credentials in a public fork. The template option is the better choice for a private personal workspace.

### Step 2. Choose what to learn

Open the [OEE curriculum](https://github.com/0xbuffdev/open-engineering-education/tree/main/curriculum) and select a program. If you are new to software engineering, start with the [Software Engineering Foundations (SEF) program](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/SEF/README.md), beginning with [SEF1](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/SEF/SEF1.md).

Before starting a course, read these parts of its OEE page:

- **Prerequisites:** what you must already know or have demonstrated.
- **Modules and lessons:** what to study, in the order given by the course.
- **Learning outcomes:** what you should be able to explain, build, test or defend.
- **Required assessments:** the work and evidence used to judge whether you met those outcomes.

Use the course codes exactly as OEE publishes them, for example `SEF1` and `SEF1-AS1`. Workspace uses those identifiers to keep your work connected to the right requirements.

### Step 3. Begin studying while official releases are pending

You can use the repository as a study notebook today. Read the OEE course, browse the [resource library](resources/README.md), save notes in [`progress.md`](progress.md), and create your own study folder such as `study/SEF1/` for your early exercises.

Keep this temporary folder separate from `labs/SEF/SEF1/`, `notes/SEF/SEF1/` and `exercises/SEF/SEF1/` for now. Once the official release is available, the `course add` command will create those course folders, but **it refuses to replace any folder that already exists**. You can then move your own files into the generated folders yourself, after reviewing where they belong.

At this stage, progress notes and files are your own study records. You cannot yet create release-verified assessment attempts with the CLI, because no official signed curriculum release has been installed.

### Step 4. Prepare for the automated tools

The automated course and evidence commands require:

- Python **3.11 or newer**, available through `python --version` (on some systems the command is `python3`).
- An **officially published OEE Toolkit** installed following its [Toolkit instructions](https://github.com/0xbuffdev/open-engineering-education/blob/main/tooling/README.md).
- An **official signed OEE curriculum release**, verified with an independently trusted steward public key and installed in the Toolkit's local release store.
- A reviewed `oee-curriculum.lock.json` file in the root of your learner workspace. This file selects the exact approved release you intend to use.

**Release availability:** OEE Toolkit's installable package is still a development candidate and no official steward-signed curriculum release has been published. There is no official package installation or release-lock value to copy yet. Do not use test keys, example hashes, an unapproved Git commit or an arbitrary download as a substitute.

When the official releases are available, follow their published installation and signature-verification instructions before continuing. The project lock must contain an approved release ID and the complete verified manifest SHA-256. A hash by itself does not prove who published an archive.

You will not need to clone the OEE curriculum repository to run the learner commands. Once installed, Toolkit reads the verified curriculum files locally. Workspace uses that same source to identify course outcomes, assessments and lesson positions.

### Step 5. Check that your curriculum is ready

With the official Toolkit, installed curriculum release and reviewed lock in place, open a terminal in the root of your personal Workspace and run:

```sh
python -m oee_workspace doctor
```

A successful check confirms that Workspace can read the trusted local Toolkit source. It does **not** mean the academic course has been graded or verified for educational quality.

The default lock file must be in the directory from which you run the command. If you were given approved release paths outside that directory, you can specify them:

```sh
python -m oee_workspace doctor --lock ./oee-curriculum.lock.json --store /path/to/verified-releases
```

The `--store` argument names an already verified local release store; it does not download an archive. On Windows, use the correct local path for your computer.

If `doctor` reports that the source is missing or incomplete, confirm your Toolkit installation, trusted release installation and lock file against the official release instructions. Workspace will not quietly fall back to GitHub or switch to a different curriculum version.

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

The folders hold your own work. No completed circuits, answers or course lessons are generated. The links in your new files point back to the exact OEE source that was included in the verified release.

When a course has a separately approved resource map for your selected release, the command also creates `notes/SEF/SEF1/reading-plan.md`. If the map is missing, unreviewed or belongs to another release, no reading plan is attached. You can still study the course and browse the resource catalogue.

If a course workspace already exists, `course add` stops rather than overwriting your files. Do not delete your work to rerun the generator.

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

An exercise can help you learn without being a required course assessment. Before you claim to have completed a course, open the **Required assessments** section in OEE and read the exact work, criteria and evidence expected.

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

An evidence record documents an attempt. Creating the file does not grade the attempt or prove that an outcome was met.

### Step 10. Check the evidence and inspect progress

Validate the attempt with the path printed during initialization:

```sh
python -m oee_workspace evidence check --path evidence/SEF/SEF1/SEF1-AS1/ATTEMPT-UUID.json --dest .
```

The validator checks the JSON format, the selected OEE release and assessment references, and the existence and integrity of any local artifacts you name. If an artifact is missing or a digest does not match, correct the reference or preserve the attempt as incomplete. The validator never runs your assignment or decides whether your solution is correct.

To see the recorded assessment attempts and outstanding decisions for the course:

```sh
python -m oee_workspace status --course SEF1 --dest .
```

`status` reads your local attempt records. A self-reported or human-reported evaluation is not authenticated by Workspace. This command cannot certify that you have completed a course.

Update `progress.md` yourself with the real work completed and links to supporting files. Only mark a course complete when its actual OEE completion conditions have been satisfied through appropriate assessment and review.

### Step 11. Export an attempt when you need to share it

To export a specific local attempt as JSON:

```sh
python -m oee_workspace export --dest . --attempt ATTEMPT-UUID --output exports/selected.json
```

Replace the UUID with an existing attempt ID. The command writes a new file at `exports/selected.json` and refuses to overwrite an existing file of that name. You can repeat `--attempt` to include more than one specific attempt.

The export contains the selected attempt records only. **It does not contain the actual circuit files, programs, reports or other artifact bytes.** If an assessor needs those files, share them separately through a method you choose. Review the JSON and any attached files before sharing; the built-in secret check is limited and cannot detect every type of private information.

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

OEE may publish a new signed curriculum release after academic changes. Workspace does **not** automatically switch your selected release, rewrite your notes, change previous evidence records or replace a reading plan. Keep the original release identity with work completed under that version. Review a new release and its resource mapping separately before choosing to change the lock for future study. See [release comparison](docs/OEE-UPSTREAM-DRIFT.md) for what the read-only comparison can show.

## Privacy, AI and your work

Your study notes, code, circuits and evidence belong in your own workspace. Review files before pushing them to a public GitHub repository, and never commit passwords, API keys, private records or material you are not allowed to redistribute.

Some external learning projects have their own licenses and rules about publishing solutions. Link to the original material and keep restricted solutions private. You can use a different free resource when a book or service is inaccessible.

OEE Workspace has no built-in AI tutor, agent, automatic grader or system for running your code. You can use independent tools when the specific OEE assessment rules permit them. Describe assistance accurately in your evidence; an AI-generated answer or a passing validator check cannot substitute for work you can explain and defend. See the [AI and agent safety guide](docs/AI-SAFETY.md).

## Need help or want to improve Workspace?

If a learner command fails, copy the exact error, note your operating system and Python version, and check whether your selected release and lock are available. Avoid posting private learner files or release signing keys in an issue. You can [report a problem](https://github.com/0xbuffdev/oee-workspace/issues) or open a discussion through the repository's existing community channels.

If you want to change the templates, CLI, validators, resource catalogue or documentation, read [CONTRIBUTING.md](CONTRIBUTING.md). It contains the maintainer workflow, developer tests and release-check procedures. For academic course changes, contribute directly to the [OEE curriculum repository](https://github.com/0xbuffdev/open-engineering-education).
