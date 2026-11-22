# Projects and portfolio work

An OEE project is where you apply what you have learned, make engineering decisions and show how you tested them. The requirements come from the [OEE curriculum](https://github.com/0xbuffdev/open-engineering-education/tree/main/curriculum), including its project brief, prerequisites, assessment criteria and evidence rules.

## Create a project workspace

After [installing the official OEE release](../docs/CLI-SETUP.md), choose a course that OEE identifies as a project. For the Software Engineering Foundations capstone, run from the Workspace root:

```sh
python -m oee_workspace course add SEF10 --dest .
```

The command uses the verified course export and creates the normal course folders plus:

```text
projects/SEF10/
  README.md
  BRIEF.md
  docs/
    design.md
    evaluation.md
    retrospective.md
```

`BRIEF.md` links to the exact OEE source and identifies the pinned release. The other documents are starting points for your work. Add source code, tests and supporting files as needed. The CLI refuses to overwrite an existing course or project directory.

Creating folders does not prove that you met the prerequisites. Read OEE's entry conditions before beginning. You can organize a personal project manually, but `course add` only accepts canonical OEE course codes, not arbitrary project names.

## Before implementation

Record the problem, intended users, expected behavior, constraints and acceptance criteria. Decide what evidence a reviewer will need. For authorized testing, document the permitted systems, scope and stop conditions first.

The project README should give the setup, build, test, demonstration, evaluation and teardown instructions needed to reproduce your work.

## What to document

| Area | What a reviewer should find |
| --- | --- |
| Correctness | Normal, boundary, invalid-input and failure tests with results |
| Design | Component responsibilities, interfaces, decisions and trade-offs |
| Reproducibility | Versions, fixtures and commands needed to repeat the work |
| Evaluation | Claim, criteria, method, results and limitations |
| Security and privacy | Trust boundaries, permissions, data handling and residual risks |
| Retrospective | Important mistakes and decisions revised after testing |

Use only systems you own or are explicitly authorized to assess when performing security testing. Keep sensitive authorization records, credentials, private data and exploit material out of public version control.

## Completion and portfolio

Complete the required OEE assessments and retain supporting artifacts. A project is not complete merely because it runs or has a generated folder. The CLI does not grade work, verify prerequisite completion or grant certification.

A portfolio case study can explain the problem, design, implementation, tests, evaluation, failures and remaining limits. Link to the evidence for each claim.
