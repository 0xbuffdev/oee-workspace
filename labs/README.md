# Labs

Labs turn course concepts into practical evidence. Each lab answers one concrete engineering question and produces an artifact, measurement, or diagnostic trace that another person can inspect.

## Create a course workspace

From the root of your OEE Workspace checkout, run the generator for the course you are starting:

```bash
./scripts/new-course-workspace systems S1
```

The example uses the currently published OEE course identifiers. The generator creates a directory under `labs/`, along with matching directories under `exercises/` and `notes/`.

The canonical assignment stays in the [OEE curriculum](https://github.com/0xbuffdev/open-engineering-education). This directory is where you perform the lab and retain the evidence.

Create a course workspace when you are ready to begin the course. An empty directory is not evidence of progress.

## Suggested layout

```text
labs/<program>/<COURSE_CODE>/
  README.md
  01-<experiment>/
    README.md
    code/
    data/
  02-<experiment>/
    README.md
    code/
    data/
```

Use numbered directories to preserve the order of experiments. Keep one main question per experiment; split unrelated questions into separate experiments.

Keep data fixtures small. Where large datasets are needed, provide a documented method to obtain or generate them rather than committing large generated files.

## Experiment record

Each experiment should document the following:

````markdown
# <Experiment title>

## Question and prediction

What mechanism or hypothesis is being tested? State the expected result
before running the experiment.

## Setup

Record the operating system, relevant hardware, tool versions, dependency
versions, configuration, and input data.

## Procedure

List the commands, inputs, and steps needed to reproduce the result.

## Results

Record measurements, test output, relevant plots, and the location of
the supporting artifacts.

## Interpretation

Explain what happened, whether the prediction held, what the evidence
establishes, and what remains uncertain.

## Next step

Identify the next experiment or engineering change justified by the result.
````

## Lab practices

- Predict before measuring. A measurement without a hypothesis is a screenshot.
- Record the environment. Capture the details that materially affect the result.
- Preserve commands. A result that cannot be rerun is an anecdote.
- Repeat measurements where appropriate. Record repetitions, warm-up, variability, and outliers when they affect interpretation.
- Test failure cases. A lab that only demonstrates the happy path is incomplete.
- Interpret the evidence. Distinguish observation from explanation.
- Protect data. Use synthetic inputs where practical and redact secrets or private information.
- Isolate security work. Test only systems you own or are explicitly authorized to assess, within the agreed scope.

## What to retain

A useful lab record usually contains:

- An experiment description and prediction.
- The minimal code or commands required to reproduce the result.
- Tests and small fixtures, where applicable.
- Measurements, results, and interpretation.
- Known limitations and the next step.

Before committing, review `git status` and confirm that credentials, sensitive captures, private data, large generated outputs, and unnecessary build artifacts are excluded.
