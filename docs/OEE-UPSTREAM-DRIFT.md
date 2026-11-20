# OEE upstream drift and pinned Workspace resource maps

OEE Workspace consumes the canonical
[Open Engineering Education specification and curriculum](https://github.com/0xbuffdev/open-engineering-education)
through the first-party OEE Toolkit. A reviewed Workspace resource-map v2
identifies **one exact full OEE v0.2.0 Git commit**, and every generated
reading plan is derived from that commit and the reviewed mapping.

**An upstream OEE update does not update a learner's source revision,
rewrite a resource map, move lesson associations or invalidate existing
pinned guide generation merely because `main` changed.**

This is the WS-I11 contract for
[Workspace resource-map v2](https://github.com/0xbuffdev/context/blob/main/repos/oee-workspace/specs/0004-resource-map-v2.md).
It remains non-normative: structural export differences are not judgments
about curriculum quality, mastery, suitability or resource accuracy.

## Two separate checks

| Check | Source selection | What happens on failure |
| --- | --- | --- |
| **Blocking pinned contract validation** | Every map's own `curriculum.revision` | Required CI fails if the referenced Git commit is missing, unsupported, or disagrees with map module/lesson/outcome/assessment references |
| **Advisory upstream drift report** | A separately chosen full Git commit, usually the explicit checked-out OEE `main` commit | Reports differences and marks them for review. OEE changes do **not** silently replace the pinned course. An unavailable/unsupported target is **incomplete**, not "no drift" |

The blocking job in
[`resources.yml`](../.github/workflows/resources.yml) checks all active v2
maps, deterministic published guides, evidence and CLI contracts. It also
checks SEF1 against its *recorded pin* independently of OEE's working
`HEAD`, using the canonical Toolkit export. A required pinned-validation
failure cannot be ignored or reclassified as drift.

The separate
[`oee-upstream-drift.yml`](../.github/workflows/oee-upstream-drift.yml)
workflow runs weekly on Monday and supports manual
**Run workflow** execution. Its checkout explicitly selects OEE `main`,
resolves its full Git SHA, compares it to all reviewed recorded pins and
writes a JSON report artifact (30-day retention) and a human-readable
Actions job summary. It **never** pushes, opens or merges a PR, fetches
a new remote inside the reporter, publishes a guide or contacts a
learner service. The scheduled workflow uses GitHub Actions minutes;
the maintainer can disable the schedule when desired.

Drift itself is **nonblocking**; the advisory job records changed or
unavailable targets without failing the immutable pinned guide gate.
A broken pinned map or an internal reporter crash **fails that job** and
must be investigated. A missing target returns `incomplete`; no
silent substitute from HEAD or a previous format is provided.

## Run an explicit comparison locally

From the root of this repository, with Python 3.11+, Git and a
**trusted, full-history local OEE checkout**:

```sh
# Choose the current checked-out OEE commit explicitly, outside the reporter.
git -C ../open-engineering-education rev-parse --verify 'HEAD^{commit}'

# Replace TARGET_FULL_SHA with exactly the value from the command above.
python scripts/report-oee-drift.py \
  --oee ../open-engineering-education \
  --target-revision TARGET_FULL_SHA \
  --course SEF1
```

Omit `--course SEF1` to compare all active resource maps.
Use shell output redirection if a persistent JSON report is wanted.
The reporter itself has **no `--latest`, `--head`, `--write` or
`--migrate` option**. It accepts only exact lower-case 40-character
Git SHAs and locally available, supported OEE v0.2.0 Toolkit exports.

The report is deterministic for the same source objects and resource
maps. It carries no run-time timestamp and discloses:

- The course, recorded pin, explicit target commit and independent
  pinned/target validation states.
- Added or removed outcome/assessment IDs; changed outcome descriptions,
  assessment requirements, evidence criteria, and required outcome-to-
  assessment coverage.
- Module/lesson title and ordinal differences, module-outcome links and
  title-only movement *hints* that require review, never automatic matching.
- Mapping resource associations at risk because of module, lesson,
  assessment, outcome or coverage changes.
- `reviewRequired`, `autoRemapped: false`, and
  `assessmentCompletionDetermined: false`. No educational completion
  decision is made.

Changes to only source line-number locations are not treated as
structural identity drift. These locations should still be inspected
by a reviewer when copying citations between commits.

## What to do when drift is detected

1. **Keep the existing pinned map and published guide unchanged.**
   Confirm required pinned CI is green before interpreting advisory drift.
2. Review the target OEE course's intended competencies and assessment
   changes against the canonical OEE design guide and revision.
3. Check every affected module/lesson locator, outcome/assessment reference,
   resource URL, book edition and accessible free alternative **by a person**.
   Structural matching is not evidence of bibliography correctness.
4. If an updated mapping is warranted, make an explicit resource-map v2
   edit on a separate reviewed branch. Set its target full commit, remap
   resources with individually justified associations and preserve any
   remaining `partial` or `unmapped` gaps. Do not mechanically reassign
   module numbers or mistake shared titles for semantic equivalence.
5. Run the full resource validator, regenerate the guide deterministically,
   check the learner CLI smoke suite and obtain the maintainer's review
   and DCO sign-off **before merging**. OEE release status and learner
   assessment decisions are governed separately.

If the target source is missing or uses an unsupported format, the
report is **incomplete**, not a success or an invitation to use old
source formats. There is **no backward compatibility** for resource
schema v1, pre-v0.2.0 OEE courses, or previous CLI commands.

## Verification and safety limitations

```sh
python -m unittest discover -s tests -p 'test_upstream_drift.py' -v
python scripts/check-resources.py --oee ../open-engineering-education
python scripts/render-resource-guides.py --oee ../open-engineering-education --check
```

Regression tests prove the pinned SEF1 map resolves at
`67416343f3eab17ada5d3c79ae6cc782524c29ff`, missing target
objects remain incomplete, and synthetic outcome/assessment/module
changes are reported without editing source files. The report uses
the public Toolkit for both revisions and the same strict consumer
as runtime map validation, **not** a second curriculum Markdown parser.

A Git SHA identifies local bytes; it does not prove the authenticity
of an untrusted checkout. The drift report cannot assert whether two
educational approaches are semantically equivalent or establish
learner achievement. Those decisions require independent review.
