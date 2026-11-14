# ADR-0006: Optional AI integrations, permissions, and assessment integrity

- **Status:** Proposed
- **Date:** 2026-11-14
- **Scope:** OEE Workspace adapters for AI assistance, agent tools, and local execution
- **Decision owner:** OEE Workspace maintainers
- **Depends on:** Workspace ADR-0003 and ADR-0004; OEE's current assessment requirements and any subsequently accepted AI-assessment RFC

## Context

OEE currently teaches AI-assisted engineering and requires evidence proportionate to an assessed capability. The workspace should support learners who use coding assistants and supervised agents, but not assume that AI-generated code, passing tests, or a transcript proves understanding. External models and tools change rapidly; coupling OEE to one provider would undermine independent study.

AI assistance adds concrete risks: repository prompt injection, credential exposure, unsafe commands, uncontrolled network egress, unauthorized file changes, and fabricated completion claims. The appropriate response is a narrowly scoped optional integration, not a bespoke mandatory AI tutor or universal agent runtime.

## Decision

1. **AI is optional and provider-neutral.** The baseline workspace, course content access, source validation, and evidence capture work without AI, subscription, API key, internet access, or a specific IDE. Adapters may support user-selected assistants only where a maintainable and safe workflow is demonstrated.
2. **Canonical assessment conditions take precedence.** The workspace does not decide which AI assistance is educationally permitted. It reads the applicable OEE assessment rules for the selected revision, applies any explicit restrictions it can enforce, and identifies limitations it cannot enforce. Until OEE adopts more precise normative assistance profiles, no new universal pass/fail or mandatory transcript rule is inferred.
3. **Keep learner responsibility explicit.** AI may explain, suggest, draft, test, or execute permitted work, but a learner's completion claim requires the outcome-specific evidence and review defined by OEE. Generated artifacts and successful tools do not automatically establish reasoning, authorship, security, or mastery.
4. **Separate guidance from execution.** An optional AI conversation or tutoring adapter must not obtain filesystem, shell, network, or assessment-decision authority simply by being enabled. An execution adapter has explicit capabilities, independently configured permissions, and bounded operations.
5. **Least privilege by default.** Read-only repository access is distinct from modifying learner files; running commands, accessing networks, editing OEE source, touching secrets, and executing privileged operations require distinct authorization. Never silently execute untrusted repository text as instructions or grant tools new permissions because a model requested them.
6. **Prefer established isolation where execution is needed.** A proposed integration should use supported sandbox/container or equivalent constrained mechanisms where available. If safety cannot be credibly enforced on a target platform, disable the unsafe capability and document the limitation. Do not assert that a simple prompt or filesystem path check constitutes a secure sandbox.
7. **Explicit, proportional disclosure.** Where canonical assessment conditions require it, an evidence record may declare whether assistance was used, the relevant task/tool class, and material reviewer context. Avoid mandatory raw prompt archives, unnecessary personal information, proprietary model identifiers, or leaked credentials. Sensitive transcripts are opt-in and private by default.
8. **No automated credential authority.** AI feedback and tests remain observations. Only the published criteria and an appropriate evaluation process may establish assessed outcomes. Optional AI feedback must not modify course status, learner completion history, or independent-review claims.

## Permission and trust model

| Capability | Default interpretation |
| --- | --- |
| Explain or suggest changes | Guidance only, no implicit execution authority |
| Read learner-selected files | Scoped to selected workspace paths and privacy settings |
| Write or delete files | Explicitly authorized scope; prevent edits to canonical OEE checkout |
| Run build/test commands | Reviewable command and constrained environment; disclose effects |
| Access network or remote tools | Separate opt-in authorization and data-exposure explanation |
| Read credentials or private records | Not an implicit permission; avoid or block unless strictly necessary and explicitly controlled |
| Decide learner mastery | Not delegated to an assistant without the applicable OEE evaluation contract and defensible review |

Tool descriptions, resource pages, repository files, imported prompts, and model responses are **untrusted data**. They must never be allowed to override authorization or assessment policy. The user-facing confirmation and actual execution permissions must agree.

## Alternatives considered

| Alternative | Reason not selected |
| --- | --- |
| Require the same commercial AI API for every learner | Violates independence and excludes many users |
| Embed a comprehensive custom coding agent now | Large attack surface and maintenance cost without validated demand |
| Allow an agent to self-grade its own code as mastered | Confuses task completion with assessed competence |
| Prohibit all AI-assisted learning | Ignores legitimate modern engineering workflows and validated supervised uses |
| Require complete prompt logs for every assessment | Creates privacy burden and often adds irrelevant evidence |

## Consequences

Optional adapters require versioned capability descriptions, audit-friendly user choices, explicit error handling, and a documented threat model. A command runner may be harder to support across platforms than read-only AI guidance; support the safer subset first. Some AI-assisted activities may be valid formative practice but inadmissible for a particular published summative assessment.

The workspace must avoid advertising a provider or model as OEE-conforming merely because an adapter exists. Educational assistance, tool safety, and assessment validity are independently reviewable dimensions.

## Implementation and test gates

1. Define a minimal threat model and data-flow inventory for any proposed adapter before shipping it.
2. Specify explicit capability permissions and default-deny behavior for unsafe writes, network use, and access beyond the learner-selected workspace.
3. Add negative tests for prompt injection in repository files/resources, malicious tool arguments, accidental secret inclusion, path traversal, and attempts to bypass approved assessment conditions.
4. Verify that AI-generated changes cannot alter canonical course metadata, evidence decisions, or a learner's historical reviewed record without deliberate authorization.
5. Test operation without AI configuration and with a chosen provider unavailable; existing learner workflows must continue.
6. Validate assessment disclosures against the actual pinned OEE revision and record only necessary contextual evidence.
7. Pilot read-only or suggestion-only integrations before considering constrained command execution, and do not claim security properties untested on the platform.

## Governance and deferred work

This ADR is an implementation safety boundary, not an OEE-wide statement about what counts as mastery. Any binding categories of independent, collaborative, or delegated assessment; required disclosure; or AI-specific completion rule must be adopted through the OEE RFC process. Building a hosted tutor, agent marketplace, or full execution platform is expressly outside the current decision.
