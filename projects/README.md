# Portfolio Projects

Projects are where courses become evidence. The full briefs, gates, milestones, and acceptance criteria live in the curriculum:

- [Project ladder: P1–P11](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/projects/project-ladder.md)
- [Capstones: C1–C4](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/projects/capstones.md)
- [Portfolio guide](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/projects/portfolio-guide.md)

Do not start a project because the name sounds impressive. Start it when the stated gate is passed and the prerequisite labs are complete.

## Create a workspace

```bash
../open-engineering-education/scripts/new-project-workspace ledgerlab
../open-engineering-education/scripts/new-project-workspace workbenchd
../open-engineering-education/scripts/new-project-workspace c1-resilient-backend-platform
```

The script validates the project name and creates:

```text
projects/<slug>/
  README.md
  BRIEF.md
  docs/
    design.md
    evaluation.md
    retrospective.md
```

The brief stays canonical in `curriculum/projects/`; the workspace is your implementation and evidence. For security work, add an authorization/scope record before collecting any evidence.

## Rules

1. **Gate first.** A project begun before its prerequisites becomes tutorial copying.
2. **One project at a time.** Small increments are fine; parallel half-built systems are not.
3. **Evidence over demo.** Every claim needs a test, benchmark, trace, or reproducible command.
4. **Failure is part of the deliverable.** Include one broken case, one wrong assumption, and one correction.
5. **Security boundary.** Networked, AI, and security projects need a threat model and an authorization note. Test only systems you own or are explicitly authorized to test.
6. **No secrets, private data, weights, or copyrighted books in Git.** Use synthetic fixtures and documented downloads.
7. **Clean-checkout test.** A reviewer must be able to run the minimal demo and evaluation from a fresh clone.

## Definition of done

- [ ] README with problem, scope, setup, commands, and limitations.
- [ ] Tests for normal, boundary, invalid, and failure cases.
- [ ] Reproducible evaluation, benchmark, or threat-model verification.
- [ ] Design doc with decisions and trade-offs.
- [ ] Threat model and authorization note where relevant.
- [ ] One significant failure and the evidence that changed the design.
- [ ] Retrospective with next steps.
- [ ] Clean-checkout reproduction.

## Portfolio

Not every project belongs on a CV. Choose two or three deep artifacts and write case studies that explain the problem, the design, the measurement, the failure, and the limitation. See the [portfolio guide](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/projects/portfolio-guide.md).
