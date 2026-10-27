# Labs

Labs are where a course becomes evidence. Each lab answers one concrete question and leaves a runnable artifact, a measurement, or a diagnostic trace.

## Create a workspace

```bash
../open-engineering-education/scripts/new-course-workspace systems S1
```

This creates `labs/systems/S1/README.md`. The course file is the assignment; this directory is where you do it. Create a workspace only when you start the course.

## Layout

```text
labs/<track>/<CODE>/
  README.md                 lab log and links to the course
  01-<experiment>/
    README.md               question, setup, procedure, results, interpretation
    code/                   minimal runnable code
    data/                   small fixtures only; large data is regenerated
  02-<experiment>/
```

Use short, numbered subdirectories. Keep one experiment per directory. A lab that needs three unrelated questions is three labs.

## Experiment template

Every experiment README should answer:

```markdown
# <experiment name>

## Question

What mechanism or hypothesis is this experiment testing? State the prediction.

## Setup

Host/OS, kernel, CPU/GPU, memory, tool versions, compiler flags, dependency lockfile, and input data.

## Procedure

Exact commands and inputs needed to reproduce the work.

## Results

Measurements, plots, test output, and where the raw data lives.

## Interpretation

What happened, why, whether the prediction held, limitations, and the next experiment.
```

## Rules

- **Predict before you run.** A measurement without a hypothesis is a screenshot.
- **Record the environment.** OS, hardware, compiler/runtime, flags, seed, and versions.
- **Preserve the command.** A result that cannot be rerun is an anecdote.
- **Measure more than once.** Report warm-up, repetitions, variance, and outliers where relevant.
- **Test the failure case.** A lab that only demonstrates the happy path is incomplete.
- **Keep artifacts small.** Commit code, fixtures, and reports; regenerate large data, build outputs, and model weights.
- **No secrets or private data.** Use synthetic inputs and redact logs.
- **Security labs stay isolated.** Work only in a local VM/container or an authorized training platform.

## What to commit

- the experiment README;
- the minimal code and tests;
- a small fixture or a script that recreates the data;
- the results table or plot;
- the command used to reproduce the result.

Do not commit `.venv/`, `target/`, model weights, datasets, packet captures with real traffic, or credentials. The root [.gitignore](../.gitignore) covers the common cases; verify with `git status` before committing.
