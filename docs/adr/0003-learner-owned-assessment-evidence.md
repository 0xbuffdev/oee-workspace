# ADR-0003: Learner-owned assessment evidence and review provenance

- **Status:** Proposed
- **Date:** 2026-11-14
- **Scope:** Learner workspace evidence records and derived progress displays
- **Decision owner:** OEE Workspace maintainers
- **Depends on:** OEE [Evidence Rules](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/evidence-rules.md), [Course Format](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/course-format.md), and proposed OEE ADR-0002
- **Related:** ADR-0004 and ADR-0006

## Context

The current `progress.md` and templates let learners describe accomplishments and link artifacts. They do not provide an interoperable, machine-checkable record of the precise course revision, assessment criteria, outcome IDs, attempts, reviewer identity, or evaluation decision. Markdown checkmarks and passing software tests do not independently prove mastery.

The learner must retain ownership of their work. The workspace is free and usable offline, without assuming a hosted 0xNAND account, a GitHub repository, an automated grader, or a specific AI model. OEE v0.2.0 already requires proportional, inspectable evidence and warns against unsupported completion claims, but it does not prescribe this workspace's storage format.

## Decision

1. **Store evidence in the learner's own workspace.** The upstream repository contains schemas, templates, and tools, never actual learner assessments or secrets. No service subscription, public GitHub account, or external credential issuer is necessary.
2. **Add an optional, versioned JSON evidence-record format** as a *workspace interoperability format*, not as a new OEE completion condition. Keep a single schema and validator for storage and export; Markdown reports are derived views or manually maintained notes rather than competing authoritative assessment databases.
3. **Identify exact assessed requirements.** A record includes its own schema version, course code, applicable OEE specification version, canonical course path and source revision (full commit SHA when available), assessment ID, evaluated outcome IDs, and assessment attempt identity. No implicit latest-branch resolution is permitted for a reviewed decision.
4. **Link evidence; do not copy everything.** Reference actual artifacts, reproducibility instructions, test results, explanations, and optional trace metadata. Store links or relative paths appropriate to portability and privacy. Do not require exporting source code, confidential datasets, private prompts, or test answers into a public record.
5. **Separate claims and evaluations.** A learner may record a self-claim or an unreviewed attempt; a review decision identifies the criteria evaluated, decision, evaluator type (self, human reviewer, or automated checker), relevant identity and timestamp when appropriate, and explicit limitations. A successful structural check is not a mastery decision.
6. **Preserve attempts and historical context.** Revising course requirements, regenerating templates, or rerunning checks must not rewrite prior reviewed records or silently upgrade their status. A new attempt or explicit revisioned decision references the previous result when relevant.
7. **Proportional detail.** Small conceptual evaluations may link a short explanation; executable projects need sufficient instructions and verification context for the claims made. Avoid imposing a universal build log, full retrospective, or detailed environment inventory on every exercise.
8. **Use minimal and truthful progress projections.** Existing `progress.md` remains usable. Tool-generated summaries should derive completion from the relevant reviewed outcomes and explicit assessment decisions, not from checked lessons, elapsed time, mere file existence, or the learner's assertion alone. Do not silently modify a learner-edited `progress.md`.

## Proposed record lifecycle

1. Select and pin the actual OEE course revision and required assessment.
2. Create an attempt record in the learner copy, initially `pending-review` or otherwise clearly unevaluated.
3. Add artifact references and, where needed, reproducibility context.
4. Run supported structural or executable checks and record their narrow observations separately from any educational decision.
5. Obtain the appropriate review for the published outcome and criteria; a reviewer may mark that evidence meets, fails, or cannot establish the claimed criteria.
6. Derive an outcome-level progress view from evaluated evidence. If outcomes require several assessments, do not infer completion from only one.
7. Export only an authorized, privacy-appropriate view, preserving its source revision and reviewer limitations.

The precise JSON fields, filenames, admissible decision values, and evaluation method semantics belong in a reviewed schema specification and fixtures. For multiple attempts, use unique stable record identifiers rather than relying only on a course or assessment filename. An example path convention is `evidence/<program>/<course>/<assessment>/<attempt>.json`; this is a proposed workspace convention, not an OEE requirement.

## Alternatives considered

| Alternative | Reason not selected |
| --- | --- |
| Continue with only a manually edited progress table | Insufficient traceability and difficult to compare against changing outcome requirements |
| Make all evidence public on GitHub | Unsafe for private learner data and excludes offline or private learning |
| Use a mandatory hosted evidence API | Couples the open workspace to a product, network, and account |
| Treat automated tests as a completion authority | Tests cannot establish every reasoning, authorship, or design outcome |
| Introduce a credential blockchain or signing network | Adds cost and claims of verification before assessment reliability exists |

## Consequences and trust boundaries

A JSON record can be edited by its owner; it is not cryptographically authenticated or proof that the stated reviewer actually participated. External attestation and credential issuance are distinct future features requiring explicit trust rules. Self-review can help learning but cannot be misrepresented as independent assessment. A `verified` course readiness label is not a learner outcome status.

Historical evidence referencing older OEE versions must remain readable even if a newer schema is introduced. Validators must explain unsupported schema versions and avoid destructive conversions. Private evidence may use redaction or controlled access where the intended reviewer can still assess the claim.

## Implementation and test gates

1. Specify a minimal JSON Schema, version policy, and durable attempt identity with normative-like precision *for the workspace format only*.
2. Add examples for conceptual, executable, AI-assisted, self-reviewed, independently reviewed, partially assessed, and private evidence.
3. Test missing/unknown outcome IDs, unresolved course SHA, absent artifact, conflicting criteria, duplicate attempt identity, and mismatched revisions.
4. Test that a successful software test cannot promote an outcome whose criteria require engineering explanation or a reviewer.
5. Test multiple assessments contributing to one outcome and a course with not-yet-assessed outcomes.
6. Demonstrate an offline workflow and a read-only summary/export; never overwrite user-owned notes or prior decisions.
7. Validate a complete pilot against the current SEF1 and SEF10 public requirements before generalizing.

## Governance

No change to OEE's public completion rules is made by this ADR. Any mandatory OEE-wide record requirement, new normative AI disclosure requirement, or portable credential claim must be proposed in the OEE specification process. This ADR remains proposed until design and privacy review are complete.
