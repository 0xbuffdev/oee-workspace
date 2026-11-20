# AI and agent safety boundaries

OEE Workspace is a **local-first learning workspace**, not a coding agent,
hosted tutor, execution sandbox or automated examiner. The supported
`python -m oee_workspace` commands work with Python 3.11+, Git and a
**trusted local OEE Toolkit checkout** without an AI provider, account,
token, model, subscription, network connection or learner-code execution.

This guide records the present implementation boundaries for
[WS-I09](https://github.com/0xbuffdev/context/blob/main/repos/oee-workspace/tickets.md).
It follows the non-normative
[Workspace CLI and agent-safety contract](https://github.com/0xbuffdev/context/blob/main/repos/oee-workspace/specs/0003-cli-and-agent-safety.md).
It does **not** add normative educational requirements or interpret the
canonical [OEE Evidence Rules](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/evidence-rules.md)
on behalf of an OEE course reviewer.

## What the baseline actually does

| Operation | Current technical boundary |
| --- | --- |
| Explain course or resource references | Read the locally selected, pinned OEE Toolkit export; optional public resource URLs are displayed as references, not fetched |
| Generate course and project templates | Create new files only in an explicitly selected learner directory; validate local destinations, refuse symlink traversal and existing targets |
| Validate resource maps | Check local JSON and exact-commit Toolkit exports; a reviewed mapping can supply an optional reading plan |
| Create learner evidence | Generate a new UUID attempt with `evaluation: null`; no assessment decision is made |
| Validate evidence and show status | Read the selected learner directory; check local artifacts and hash references; do not execute learner code |
| Export selected attempts | Write a new local JSON file containing only explicitly selected attempt records, without artifact bytes or implicit upload |
| Invoke internal subprocesses | Run **known, first-party** Python Toolkit/export and resource-validation entry points against a trusted checkout; never run commands extracted from a learner file, prompt, assessment or resource page |

The baseline has **no** `ai`, `agent`, `run`, `execute`, `shell`,
`tutor`, `provider`, `connect` or `grade` command. It does not
provide a model API client, runtime memory service, agent plugin loader,
automatic network request, credential manager, system shell launcher,
container sandbox or autonomous assessment grader.

`--oee`, `--revision`, `--dest`, `--path`, `--map` and
`--output` are **explicit CLI inputs**, not authorizations for arbitrary
work. For course operations, the source SHA is a complete, immutable
Git commit. A Git SHA proves identity of local content, **not the
trustworthiness of the local checkout's origin**. Validate your OEE
checkout before relying on it.

## Threat model and trust boundaries

| Potentially untrusted input | Risk | Present handling / limitation |
| --- | --- | --- |
| Course or resource text, imported README, template, model output | Prompt injection instructing an assistant to disregard boundaries, read secrets or invoke a shell | Treated as local data or Markdown. **No assistant or agent is invoked.** Displayed instructions cannot grant a capability |
| JSON resource mapping, optional website address | Malicious URL, exfiltration or misleading recommendations | Validated as a map or displayed as a reference. The CLI does **not** fetch a resource URL, open a browser or infer academic approval from passing structural checks |
| Learner-supplied artifact paths and evidence | Directory traversal, symlink escape, reading or overwriting private files | Paths must remain under the learner-owned root; existing records are not overwritten. These checks **do not create a secure sandbox against hostile concurrent local processes** |
| Source repository or local executable | Modified OEE Toolkit or compromised source clone | Source must be explicitly selected and locally available, then checked against the exact commit; **caller must trust the checkout and Python runtime**. Pinned content is not code-signature verification |
| Learner-authored free text exported to a file | Unintentional exposure of tokens, private data, proprietary work | Only chosen attempts are exported. A limited common-credential pattern check rejects some obvious secrets; **this is not a complete secrets or PII scanner**. Review exports manually |
| Claimed human review, automated observation or AI-generated answer | False assertion that assessment criteria or learning outcomes were met | Observations do not become evaluations. Reviewer identity is not authenticated. The CLI never certifies mastery or changes OEE course status |
| External AI tools or an editor the learner starts independently | Arbitrary file access, network requests or commands by another program | **Out of Workspace's control.** This CLI does not sandbox, monitor, audit or constrain an unrelated external assistant |

Source files, tool results, prompts, embedded instructions and model
messages are **untrusted data**. They cannot turn on a missing
capability, override a pinned OEE assessment or change a student's
review history through this CLI. That is a property of **not
implementing an agent interface**, not proof of a universal prompt-
injection defense.

A normal CLI invocation does use the local Python interpreter and may
start first-party Toolkit processes. This is **not** equivalent to
running arbitrary learner build commands, but it still executes code
installed in the selected local checkout. Do not run the CLI against
source or Python installations you do not trust.

## Capability policy for future integrations

A future optional adapter is **not implemented or authorized** by this
document. If one is proposed, its API must enumerate narrowly scoped,
independently approved capabilities. The prospective defaults are:

| Capability | Default | Required before implementation |
| --- | --- | --- |
| Show offline explanations | Unavailable (no adapter installed) | User-selected provider, clear data-use/retention notice |
| Read learner files | Denied | Per-workspace/path consent, secret exclusions and tests |
| Create or edit learner files | Denied | Explicit target scope, collision handling, review of proposed diff |
| Run builds, tests, shell commands or scripts | Denied | Explicit user review and a credible platform-isolated execution environment |
| Access the network or call remote models | Denied | Separate opt-in, destination and data-exposure review, timeout and egress controls |
| Inspect credentials or private datasets | Denied | Necessity justification and enforceable secret protection; never implied by file access |
| Edit OEE source, change reviewed evidence or award completion | Denied | Separate source-review and assessment governance; not delegated merely by enabling an AI assistant |

Permissions cannot be inferred from the text of a repository file, a
`SKILL.md`, an imported prompt, a tool description, an agent's requested
action or the model's own statement of approval. Instruction text alone
is **not access control**.

Do not add a provider adapter, executable agent or tool interface as part
of WS-I09. This work is deferred to **WS-I10**, contingent on demonstrable
learner demand, a separate reviewed threat model, explicit permission
enforcement, cross-platform isolation evidence and security regression
tests. If an execution capability cannot be isolated credibly on a
target platform, **do not ship it on that platform**.

## Learning, assessment and assistance disclosure

Learners may choose external AI assistants independently. Their use for
learning does not by itself make an attempt valid or invalid. The **exact
OEE course revision and its assessment criteria** are the authority for
whether a particular level of assistance is permissible in an assessment.

Evidence schema v1 permits an optional **self-declared** `assistance`
object with `declaredMode` values `not-recorded`, `independent`,
`collaborative` and `delegated`. This field is descriptive and
**does not prove** a model was present or absent, that requested
restrictions were enforced, or that work was independently authored.
The existing `evaluation` remains a human- or self-declared review
with unverifiable reviewer identity.

Passing tests, a model's favorable comments, recorded agent steps and
locally valid JSON never automatically change an assessment to `met`.
Workspace does not add its own mandatory raw prompt transcript,
AI-provider name, blanket AI ban or universal assistance policy. Any
binding new summative restrictions must be adopted through OEE's
assessment governance and then implemented with evidence of what can
actually be enforced.

## Privacy and repository hygiene

The [`.gitignore`](../.gitignore) includes common private environment
files, credentials, model artifacts, captures and build outputs. This is
a **preventive convenience**, not data-loss prevention. A file already
tracked by Git is **not** removed when an ignore rule is added, and
secrets may still appear in source, JSON records, Markdown or diffs.

Keep real credentials, personal transcripts, raw assistant interactions,
private datasets, proprietary logs and other sensitive materials out of
public repositories. Store personal records in a private learner
workspace if they contain private data. Review staged changes before
each commit:

```sh
git status --short
git diff --cached
git check-ignore -v .env .env.local .secrets/token.txt
```

If credentials were committed, remove the exposure from the repository
and rotate or revoke the credentials; adding a `.gitignore` pattern
does not undo an earlier leak.

## Reproducible negative tests and boundaries

`tests/test_ai_safety.py` verifies that the documented command surface
is closed, unsupported `agent`/`run` commands and provider flags are
rejected, untrusted text is rendered only as data, optional external
artifact URLs do not initiate network requests, assistance disclosure
does not create grading authority, and secret-like filenames are
ignored. The suite also checks that the baseline contains no
AI-provider or network client imports.

These are **regression guards for this CLI**, not a penetration test or
proof that arbitrary models, hostile local processes, or a future
execution adapter are safe. The agent execution surface remains
unimplemented.

```sh
python -m unittest discover -s tests -p 'test_ai_safety.py' -v
python -m oee_workspace --help
```

The maintained platform CI exercises the CLI on Linux, macOS and
Windows and keeps its ordinary operations available without an
AI account, provider or token.
