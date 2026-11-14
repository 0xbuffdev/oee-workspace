# ADR-0004: Local-first tooling, composable operations, and a minimal CLI

- **Status:** Proposed
- **Date:** 2026-11-14
- **Scope:** Workspace scripts, generated files, validation, and future command-line tooling
- **Decision owner:** OEE Workspace maintainers
- **Depends on:** Proposed OEE ADR-0001 and ADR-0002; workspace ADR-0003 and ADR-0005

## Context

OEE Workspace currently uses Bash generators for courses and projects and Python 3 standard-library programs to check and render public resource mappings. This is a useful low-cost baseline, but the behaviors are partly spread across shell scripts and parsers that assume older OEE course syntax. The project generator additionally expects canonical `curriculum/projects/` files not present on the currently inspected OEE `main` tree. Tool expansion before repairing these contracts would conceal existing failures.

The workspace should be usable by learners on Linux, macOS, and Windows, with ordinary editors and Git when desired. It should not attempt to become a bespoke IDE, full learning management system, or model execution environment.

## Decision

1. **Local-first and learner-owned.** All essential workspace creation, structure checks, evidence recording, and read-only inspection should work from local files without a login, hosted service, GitHub API, network connection, or paid product once the chosen curriculum snapshot is available.
2. **Keep existing scripts until a tested replacement exists.** Repair the current resource and project resolution workflows first. Preserve safe generator behavior while introducing reusable operations; do not rewrite all working scripts merely to choose a new programming language.
3. **Use a small Python 3 standard-library core for the first portable operations.** Python is already required for resource handling and is more portable than a Bash-only interface for the intended learners. The initial architecture does not require a Rust/Node monorepo, database, plugin framework, or mandatory package manager. Language selection can be revisited when actual distribution or performance requirements justify it.
4. **Keep a thin command interface over reusable domain operations.** Separate argument parsing, course/source resolution, mapping and schema validation, evidence operations, file generation, and filesystem adapters. Reuse one version resolver and contract parser; do not duplicate business rules in generators, commands, and template renderers.
5. **Treat OEE as read-only canonical input.** Prefer a pinned OEE manifest once its supported exporter exists. Until then, current source-specific compatibility adapters may be used only with explicit supported versions and clear errors. Never silently interpret an unsupported new course as legacy or rewrite OEE source files.
6. **File changes are safe and reviewable.** Validate all inputs and paths before modifying the learner directory; refuse overwrites, writes through unsafe symlinks, and writes into the OEE checkout. Stage multi-file operations and either commit the complete generated set or report a recoverable failure. Generated changes must be idempotent or explicitly non-overwriting.
7. **CLI surface stays small.** Candidate commands are course/project initialization, local source inspection, mapping validation, evidence validation, and status/export. Treat exact command names and flags as a separate interface review, not requirements of this ADR. Keep the existing script entry points working or provide explicit documented migration instructions.
8. **Extend via bounded adapters only when justified.** Editors, online synchronization, sandboxes, assessment tools, and AI providers are optional integrations behind interfaces; they are not dependencies for local course learning or evidence recording.

## Logical layers

| Layer | Responsibility |
| --- | --- |
| Commands | Parse arguments, show help, return consistent diagnostics and exit codes |
| Application operations | Coordinate a course initialization, validation, evidence capture, or export transaction |
| Domain contracts | Interpret source revision, course identity, assessment IDs, and mapping/evidence schemas |
| Adapters | Read local OEE snapshots, generate files, render guides, optionally run authorized tools |
| Learner-owned files | Retain source code, notes, artifacts, evidence, and a non-destructively updated progress view |

This is an implementation decomposition, not a requirement for separate packages or services. Keep modules together until a real maintenance boundary justifies splitting them.

## Alternatives considered

| Alternative | Reason not selected |
| --- | --- |
| Replace everything with a Rust CLI immediately | Adds build/distribution scope before the core compatibility contract is settled |
| Continue indefinitely with independent Bash and Python rules | Makes cross-platform use and SSOT validation increasingly difficult |
| Build a web app or hosted control plane | Violates local-first independence for the current primary learning workflow |
| Add a generic extension marketplace now | Broadens security surface and maintenance obligations without proven demand |
| Require live OEE `main` access for every operation | Destroys pinned historical interpretation and offline use |

## Consequences

The first command-line improvements are intentionally unambitious. A robust offline generator and evidence validator are more valuable than a sophisticated interface over inconsistent source data. Windows support needs tested filesystem and path behavior, not just a claim that Python can run there. Local development and learner execution dependencies should remain separate from optional repository CI tools such as Markdown lint.

Existing learners must not lose data when generated templates evolve. No command should infer course completion, mutate a historical reviewed assessment, or access network/AI providers without a separately authorized operation.

## Implementation and test gates

1. Reproduce and repair current SEF1 resource drift and missing project brief assumptions.
2. Extract stable source/revision resolution and mapping checks into reusable, unit-tested modules before adding commands.
3. Design a minimal CLI help/error contract and explicit supported OEE versions; publish migration guidance for existing scripts.
4. Test new workspace creation, duplicate invocation, interrupted writes, malformed paths, symlink traversal, permission denial, and missing source files.
5. Run platform checks on Linux, macOS, and Windows; prove a core workflow runs without network access after its dependencies are present.
6. Add integration tests using a fixed OEE commit and deliberate mismatches, plus an executable end-to-end learner setup example.
7. Defer richer agent orchestration and remote execution until a documented use case, threat model, and maintenance budget exist.

## Governance

The CLI may organize learning activities and evidence, but it cannot define new course completion requirements. Assessment policies remain in OEE; workspace UI and tooling must faithfully expose them without claiming certification or teaching readiness.
