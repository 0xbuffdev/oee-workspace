# Exercises

Exercises reinforce recall, reasoning, and implementation. They require you to produce an answer or artifact and explain the reasoning behind it, rather than follow a guided demonstration.

## Create a course workspace

From the root of your OEE Workspace checkout, run:

```bash
./scripts/new-course-workspace SEF F2
```

The example uses a course identifier from the current OEE curriculum. The generator creates the exercise directory alongside the matching lab and notes directories.

The course definition in OEE determines which exercises are required. This directory contains your own solutions, tests, traces, and explanations.

## Suggested layout

```text
exercises/<program>/<COURSE_CODE>/
  README.md
  01-<topic>.py
  01-<topic>.test.py
  02-<topic>.md
  03-<larger-exercise>/
    README.md
```

Choose extensions appropriate to the language or format. Use descriptive names and numbering to preserve the intended order.

## Exercise types

| Type | Evidence of completion |
| --- | --- |
| Implementation | Working code, relevant tests, and a complexity or design note where appropriate |
| Derivation | Assumptions, reasoning steps, units, a sanity check, and a limiting case where applicable |
| Trace | Input, intermediate state, output, and a check against observed behavior |
| Debugging | Failing case, minimal reproduction, identified cause, and regression test |
| Security | Authorized scope, minimal reproduction, root cause, fix, and retest |
| Written explanation | Reasoning in the learner's own words, supported by a concrete example |

## Programming exercise requirements

For an implementation exercise:

1. Restate the problem in your own words.
2. Produce a complete solution.
3. Test normal, boundary, invalid-input, and relevant failure cases.
4. Explain complexity and trade-offs where applicable.
5. Record a meaningful mistake, failed attempt, or correction.
6. Provide a clear command or procedure for reproducing the result.

A copied solution is not evidence unless you can reproduce it from memory later.

## Security exercise requirements

Security exercises must be conducted only against local training targets, systems you own, or systems you are explicitly authorized to test.

- Keep the target isolated and identify the permitted scope.
- Use minimal, non-destructive demonstrations.
- Do not publish credentials, personal data, or sensitive operational details.
- Record relevant authorization before testing.
- Test the correction and retain a regression test where applicable.

## Completion checklist

- The problem is understood and stated in my own words.
- The solution or implementation is complete.
- Tests or worked cases are recorded.
- Relevant complexity, assumptions, and trade-offs are explained.
- A meaningful failure or correction is documented.
- The work is reproducible.
- No secrets or private data are included.
