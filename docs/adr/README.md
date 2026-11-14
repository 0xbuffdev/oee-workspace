# OEE Workspace Architecture Decision Records

These are **proposed** implementation decisions for the free, learner-owned workspace. They do not alter Open Engineering Education (OEE) outcomes, assessment requirements, readiness labels, or conformance rules. Those definitions remain in the [canonical OEE repository](https://github.com/0xbuffdev/open-engineering-education) and follow OEE governance.

| ADR | Status | Purpose |
| --- | --- | --- |
| [ADR-0003 — Learner-owned assessment evidence](0003-learner-owned-assessment-evidence.md) | Proposed | Evidence data, review provenance, and truthful status |
| [ADR-0004 — Local-first tooling and minimal CLI](0004-local-first-tooling-and-minimal-cli.md) | Proposed | Cross-platform, maintainable workspace operations |
| [ADR-0005 — Public resource mapping and revision synchronization](0005-public-resource-mapping-and-revision-synchronization.md) | Proposed | Single mapping owner and deterministic course guides |
| [ADR-0006 — Optional AI integrations and execution safety](0006-optional-ai-integrations-and-execution-safety.md) | Proposed | Provider independence, permissions, and assessment integrity |

These decisions complement OEE's proposed ADR-0001 (canonical Markdown and deterministic curriculum exports) and ADR-0002 (course revision identities and non-destructive migrations). The canonical normative references are OEE's [Course Format](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/course-format.md), [Evidence Rules](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/evidence-rules.md), [Conformance](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/conformance.md), and [Implementation Boundary](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/implementation-boundary.md).

## Lifecycle and authority

- **Proposed:** a recommended design, pending explicit maintainer review.
- **Accepted:** an explicitly approved implementation decision, subject to OEE normative limits.
- **Superseded:** replaced by a later recorded decision, with history retained.
- **Rejected:** documented but not adopted.

Do not treat a proposed ADR as implemented functionality. An accepted workspace ADR cannot override the OEE specification. If a decision requires a new normative learner or assessment obligation, propose that change in OEE through its RFC process first.

## Guiding boundaries

- OEE defines the required curriculum and educational contract.
- Workspace contains optional tooling, templates, resources, and learner-controlled artifacts.
- Actual learner evidence belongs in the learner's own copy, not upstream.
- 0xNAND and other learning providers may add instruction and services without silently changing the canonical public completion standard.
- Prefer shared parsers, schemas, adapters, and derived views over divergent manually maintained copies.
