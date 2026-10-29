# Projects and portfolio

Projects integrate engineering concepts into systems that can be built, tested, evaluated, and reviewed. They should provide evidence of design judgment and implementation ability, and go beyond showing that something runs.

The canonical project briefs, prerequisite gates, milestones, and acceptance criteria are maintained in the [OEE curriculum](https://github.com/0xbuffdev/open-engineering-education/tree/main/curriculum/projects).

## Create a project workspace

From the root of your OEE Workspace checkout, run a project generator:

```bash
./scripts/new-project-workspace ledgerlab
```

You can specify a different destination:

```bash
./scripts/new-project-workspace ledgerlab /path/to/workspace
```

The generator validates the project slug against its supported list and creates a project directory containing a README and technical documents.

The example uses the currently published project catalogue. Project names and prerequisite gates must remain aligned with the canonical curriculum.

## Suggested structure

```text
projects/<project-slug>/
  README.md
  BRIEF.md
  docs/
    design.md
    evaluation.md
    retrospective.md
    authorization.md
```

The authorization record is required for projects that involve security testing or another activity requiring explicit permission. The generator creates it for the security projects it currently recognizes.

## Before implementation

1. Read the canonical project brief.
2. Confirm that the stated prerequisites have been met.
3. Define the problem, intended users, scope, and explicit non-goals.
4. Record important design decisions and constraints.
5. Identify relevant failure modes and evaluation criteria.
6. Establish data, access, and authorization boundaries where applicable.

Do not begin a gated project until its entry requirements have been met. A project begun before its prerequisites becomes tutorial copying.

## Engineering expectations

### Correctness

Test normal behavior, boundary conditions, invalid inputs, and relevant failure cases. Explain what each test establishes and what it does not.

### Reproducibility

Document setup, build, test, demo, evaluation, and teardown commands as applicable. A reviewer should be able to reproduce the minimum useful result from a clean checkout.

### Design

Record the architecture, component responsibilities, interfaces, important trade-offs, and rejected alternatives. Explain why the chosen approach fits the problem and where it may fail.

### Evaluation

State the claim being tested and the acceptance criteria before recording results. Include the baseline, method, relevant environment, observed results, and limitations.

### Security and privacy

Projects that process sensitive data, use networks, or invoke AI tools should document relevant trust boundaries and risks.

Security testing must remain within systems you own or are explicitly authorized to test. Record the authorized scope and stop conditions before testing. Keep sensitive authorization records outside public version control and commit only a suitable sanitized record.

## Definition of done

- Problem, scope, and non-goals are documented.
- Relevant prerequisites have been met.
- The minimal artifact runs from a clean checkout.
- Tests cover normal, boundary, invalid, and failure cases where relevant.
- Design decisions and trade-offs are documented.
- Evaluation results can be reproduced.
- Material limitations are clearly stated.
- A significant failure, correction, or rejected approach is documented.
- Required authorization and safety records are in place.
- The retrospective identifies lessons and next steps.

A project's completion claim must be supported by the evidence required in its canonical brief.

## Portfolio presentation

Choose projects that demonstrate meaningful engineering depth. A case study should explain the problem, design, implementation, evaluation, trade-offs, failure analysis, and limitations.

Avoid making claims that the included evidence cannot substantiate. See the [portfolio guide](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/projects/portfolio-guide.md) for what belongs in a portfolio.
