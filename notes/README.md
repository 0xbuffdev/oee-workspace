# Notes and Retrospectives

Notes are for retrieval, not transcription. If a page only copies the book, it is not useful a month later.

## Create a workspace

```bash
../open-engineering-education/scripts/new-course-workspace ai AI6
```

This creates:

```text
notes/ai/AI6/
  resources.md     edition, URL, access, environment, blockers
  summary.md       mental model, evidence, exit-check self-assessment
```

The script creates a matching directory under `labs/` and `exercises/` at the same time.

## What to write

### `resources.md`

Record every resource you used:

- exact book edition and chapter/section;
- URL, access date, and whether it was free, purchased, or borrowed;
- paper/spec version;
- tool and runtime versions;
- hardware where it affects a result;
- any unavailable resource and the substitute you chose.

Do not paste long copyrighted excerpts. Record the section, your own summary, and the page range only in your private local copy if needed.

### `summary.md`

Write this at the end of a course, in one page:

```markdown
# <course> summary

## Mental model

Explain the central mechanism without looking at the book.

## Key terms I can explain

Five to ten terms, each with an example.

## Evidence

Links to labs, exercises, project increment, and benchmark/threat model.

## Failure or misconception corrected

What did I predict, what happened, and what changed in my model?

## Exit-check self-assessment

- [ ] I can demonstrate each item without notes.
- [ ] The artifact runs from a clean setup.
- [ ] I can explain the limitations and next experiment.

## References used

Exact editions/sections and the environment.
```

### Optional: weekly log

Keep `weekly.md` if you need to track hours, blockers, and the next action. One paragraph per week is enough:

```markdown
## 2026-W12

- Hours:
- Finished:
- Blocked by:
- Next:
- One thing I would do differently:
```

## Review schedule

Revisit the summary, not the whole chapter:

- **Day 1:** close the book and explain the mechanism.
- **Day 3:** redo one exercise or trace from memory.
- **Week 2:** answer the exit check again.
- **Month 1:** connect the idea to a later course or project.

If recall fails, reopen the smallest section that explains the gap. Do not restart the course.

## Rules

- Write in your own words.
- Prefer diagrams and failure tables over long prose.
- Link evidence by path or commit, not by "I did the lab".
- Redact secrets, tokens, personal data, and sensitive logs.
- Keep notes small enough to review. A 40-page summary is an archive, not a study aid.
