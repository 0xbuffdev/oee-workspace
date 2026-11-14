# ADR-0005: Public resource ownership and curriculum revision synchronization

- **Status:** Proposed
- **Date:** 2026-11-14
- **Scope:** Workspace resource catalog, mappings, generated reading guides, and OEE integration
- **Decision owner:** OEE Workspace maintainers
- **Depends on:** Proposed OEE ADR-0001 and ADR-0002; workspace ADR-0004
- **Related:** [Current resource design](../../resources/README.md) and [mapping schema](../../resources/schemas/course-map.schema.json)

## Context

OEE owns canonical courses, required outcomes, assessment criteria, and completion requirements. OEE Workspace already owns the public reference catalog, optional course resource maps, JSON Schemas, and derived Markdown study guides. The old private `content` repository contains historical source mappings, but these are not a second current public authority.

The SEF1 mapping records a prior OEE source commit and ten old module titles. Current OEE SEF1 has eight modules. The existing resource checker compares the map against the local course file but treats a different checked-out commit primarily as a warning; the CI workflow checks out moving OEE `main`. This allows unrelated upstream merges to break a previously green workspace pipeline and leaves ambiguity about which version is actually being mapped.

## Decision

1. **Assign one owner to each artifact.** OEE defines normative educational requirements. OEE Workspace defines optional public resource records and maps. Generated study guides and learner-specific `reading-plan.md` files are derived outputs. Historical private `content` mappings are import candidates with provenance, not parallel authoritative public catalogs.
2. **Map against an exact curriculum revision.** The map's recorded full OEE commit SHA and canonical source path identify the course whose modules and lesson references it describes. Validation must resolve and inspect that revision, not silently substitute current `main`. If the required commit is missing, return a clear unsupported-source diagnostic.
3. **Separate reproducibility from migration readiness.** A pinned map can remain valid for a historical OEE revision while being stale for newer publication. A distinct compatibility/drift check compares the map with a proposed target commit and reports missing/reordered/renamed modules and lessons. It must not silently update references or claim semantic equivalence.
4. **Generate deterministic guides.** Resource catalog and map files are the only editable sources for public reading guides; guides and initial learner reading-plan snapshots are reproducible from those inputs. User-edited notes and reading logs are not overwritten by generation or synchronization.
5. **Keep optional resources optional.** A book, affiliate link, paid course, proprietary software, or external documentation must never become a hidden condition of OEE completion. Resource coverage status and reference-verification status are different facts; a module marked `mapped` does not mean its lessons or OEE assessments are fully taught or verified.
6. **Use stable resource identities once.** Catalog metadata is maintained once by resource ID, with mappings referring to IDs instead of duplicating book metadata. Required editorial claims such as edition, locator, access status, verification source, and date should remain reviewable.
7. **Do not invent course-side permanent module IDs.** Until OEE adopts such an identity contract, mapping references use exact source commit plus module/lesson locations. New mandatory OEE identifiers would require the OEE governance process. An optional source exporter may expose derived location references without pretending they are normative IDs.
8. **Make synchronization an explicit reviewed operation.** Produce a change report when updating resource maps to a new OEE revision; require human review for semantic mapping changes, edition-specific locators, and gaps. Revalidate before publishing regenerated guides.

## CI and generation behavior

- **Pinned validation:** Check schema, resource uniqueness, catalog references, links, mapped course structure, and deterministic guide output against the *recorded* OEE revision.
- **Upgrade compatibility:** Independently compare the pinned revision with a proposed newer OEE revision and report drift. This may warn or block according to the integration policy, but it must not mutate the mapping as a side effect.
- **Consumer generation:** A learner selecting a specific OEE revision should receive the matching map or a clear message that no compatible map exists. It may still create an unmapped course workspace without inventing a guide.
- **Cross-repository checks:** Exercise a known compatible pinned revision for reproducibility and monitor current OEE changes for migration work. Avoid treating any arbitrary latest commit as the source of a pinned map.

## Alternatives considered

| Alternative | Reason not selected |
| --- | --- |
| Move book mappings into OEE | Mixes optional educational resources with canonical course requirements |
| Maintain the same public resource catalog in workspace and private `content` | Creates divergent sources of truth |
| Only compare against current `main` | Breaks historical maps and causes non-reproducible CI |
| Auto-map renamed modules using similar titles or AI guesses | Risks misleading learners and fabricating verified references |
| Replace all maps whenever the curriculum changes | Loses historical provenance and reviewed mappings |

## Consequences

Maintainers must retain or resolve source revisions required by active maps and explicitly coordinate curriculum upgrades. The current SEF1 ten-to-eight-module transition needs a reviewed map migration, not just a rewritten SHA. Successful pinned validation does not imply the map is current, comprehensive, or pedagogically sufficient.

A map's `reviewed` status concerns the map. It cannot promote an OEE course from `draft` to `tested` or `verified`. Resource links may become stale independently of curriculum revisions and need separate maintenance checks.

## Implementation and test gates

1. Add a reproducible pinned OEE checkout fixture and source SHA resolution to validation.
2. Distinguish pinned-map validity from upgrade/drift status in CLI output, CI, and documentation.
3. Repair SEF1's resource mapping for its intended v0.2.0 source revision with manual review and truthful coverage labels.
4. Test a historical valid map, a newer incompatible curriculum, unavailable source SHA, edited lesson title, missing resource, and an unmapped course.
5. Ensure guide generation uses only validated map/catalog data and cannot overwrite learner-authored reading notes.
6. Define a maintainable opt-in upstream-change compatibility workflow across the two repositories.
7. Record a mapping migration checklist for contributions imported from historical private content.

## Governance

This ADR defines optional reading-resource implementation, not normative instruction or completion requirements. Changing OEE's educational contract or requiring a paid/free resource category across all implementations requires a separate OEE RFC.
