# Notes and technical retrospectives

Notes should help you recover an idea, explain a mechanism, revisit a decision, or identify a gap in understanding. They are working documents, not transcripts of everything encountered during a course.

The course definition in OEE remains the authoritative source for course outcomes and completion requirements. Use your notes to record your own understanding and link to evidence in your workspace.

## Create a course workspace

From the root of your OEE Workspace checkout, run:

```bash
./scripts/new-course-workspace ai AI6
```

The example uses a course identifier from the currently published OEE curriculum. The generator creates the course's notes directory together with the corresponding lab and exercise directories.

## Suggested structure

```text
notes/<program>/<COURSE_CODE>/
  resources.md
  summary.md
  retrospective.md
  weekly.md
```

Use the files you need. Keep notes focused, and avoid duplicating material that is already maintained in the canonical course definition.

## Resource log

`resources.md` records the exact materials you used: book edition and section, URL and access date, paper or specification version, tool and runtime versions, and hardware where it affects a result. Record unavailable resources and the substitute you chose. Do not paste long copyrighted excerpts.

## Course summary

Write a summary when you have completed the course's required work. The summary should explain what you can now demonstrate and link to the artifacts supporting that claim.

A useful structure is:

````markdown
# <Course code> — Summary

## Mental model

Explain the central mechanism in your own words.

## Concepts I can explain

List the key concepts and give an example for each.

## Evidence

Link to relevant labs, exercises, project work, tests, and reports.

## Failure or misconception corrected

Describe one prediction, assumption, or implementation decision that
changed after you examined the evidence.

## Exit-check self-assessment

- [ ] I can demonstrate the required outcomes.
- [ ] The required artifacts can be reproduced.
- [ ] I can explain the design decisions and limitations.
- [ ] The evidence links are complete.

## Remaining gaps

Identify what is still unclear and the next action that will address it.
````

## Technical retrospective

A retrospective should capture what changed in your understanding or engineering approach. Explain:

- The assumption or approach you started with.
- The result you observed.
- The evidence that contradicted or refined your understanding.
- The correction you made.
- What you would do differently next time.

Use concrete examples from your work rather than general statements such as "the project was challenging" or "I learned a lot".

## Optional weekly log

For longer courses or projects, a short weekly entry can help identify blockers and maintain focus:

```markdown
### Week of YYYY-MM-DD

- Time spent:
- Work completed:
- Evidence produced:
- Current blocker:
- Key lesson:
- Next smallest deliverable:
```

## Review practices

- Write in your own words.
- Prefer diagrams, examples, traces, and failure analyses where they communicate the idea more clearly than long prose.
- Link to actual artifacts or commits.
- Separate observations from assumptions.
- Record uncertainty and limitations.
- Keep secrets, personal data, and sensitive logs out of public commits.
- Revisit a summary when you need to recover an idea rather than restarting the entire course.
