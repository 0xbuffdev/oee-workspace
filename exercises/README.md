# Exercises

Exercises are short, closed-book drills. They force recall and implementation so that a lab does not become a guided tutorial.

## Create a workspace

```bash
../open-engineering-education/scripts/new-course-workspace foundations F2
```

This creates `exercises/foundations/F2/README.md`. The course file lists the required exercises; this directory holds your answers and tests.

## Layout

```text
exercises/<track>/<CODE>/
  README.md
  01-<topic>.py             implementation exercise
  01-<topic>.test.py        tests, or a `tests/` directory
  02-<topic>.md             written answer, derivation, or trace
  03-<topic>/               larger exercise with multiple files
```

Name files by topic, not by "homework". Use a number to preserve the course order.

## Types of exercise

| Type | What good evidence looks like |
| --- | --- |
| Implementation | Code, tests for normal/boundary/invalid cases, complexity note |
| Derivation | Assumptions, steps, units, a sanity check, and a limiting case |
| Trace | Input, state at each step, output, and a hand-check against the implementation |
| Debugging | Failing command, minimized reproduction, root cause, regression test |
| Security | Scope, harmless reproduction, root cause, fix, and retest |
| Written | Your reasoning in your own words, with one concrete example |

## Rules for programming exercises

For every implementation:

- restate the problem in your own words;
- include tests for normal, boundary, and invalid inputs;
- state time and space complexity where relevant;
- record one mistake or trade-off;
- make the code runnable with one command.

Do not copy a solution without reproducing it from memory later. A copied exercise is not evidence.

## Rules for security exercises

- Work only against a local, intentionally vulnerable target or an authorized training platform.
- Keep the target isolated and clearly marked.
- Use minimal, non-destructive proof.
- Do not retain or publish real credentials, personal data, or weaponized payloads.
- Record the authorization or lab boundary before you begin.
- Add a regression test for the fix.

## Completion checklist

- [ ] Problem restated in my own words.
- [ ] Solution complete and runnable.
- [ ] Tests or worked cases recorded.
- [ ] Complexity and trade-offs recorded where relevant.
- [ ] One mistake, failed attempt, or correction recorded.
- [ ] No secrets, private data, or copied copyrighted material.
