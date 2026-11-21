# OEE Workspace release decision

On 2026-11-21, the project steward delegated approval to prepare the
OEE and OEE Workspace releases, then explicitly requested these
preflight fixes and a written release-approval record.

**Decision:** approval in principle for the next OEE Workspace software
release. **Publication is held until the exact final commit has passed
the full cross-platform test and the official OEE Toolkit and signed
curriculum have been published and independently verified.** This file
records the delegated decision; it does not sign a Git tag, assert an
official signer key or publish a GitHub release.

The prior standalone Workspace release `v0.0.1` exists, but it does
not make the new Toolkit v2/offline consumer release available.
OEE's existing `v0.2.0` release is a specification/curriculum draft
release and has no official signed CalVer archive asset.

## Acceptance scope

The approved software release shall include:

- The student-focused README and the maintainer CONTRIBUTING guide.
- Exact-release Toolkit v2 integration and evidence schema v2.
- Optional resource-map schema v3, without an invented active SEF1 guide.
- No overwrite of existing learner files; fail closed for missing,
  mismatched or compromised release locks.
- Precise `store_missing` and `lock_digest_not_found` diagnostics, plus
  existing-course `WSC011 [conflict]`.
- CI that runs Linux/macOS/Windows release readiness for student docs
  changes and the exact merged final commit.
- No assumption of automatic grading, certification, curriculum
  course readiness or mandatory paid learning resources.

## Required final release evidence

- [ ] This preflight PR is signed (DCO) and merged, and the **final
      Workspace main SHA** is recorded below.
- [ ] The `Independent Workspace release readiness` workflow passes
      on that exact merged SHA on Linux, macOS and Windows. Paste
      its run URL and job conclusions below **before tagging**.
- [ ] Workspace quality, resource/evidence unit contracts and
      negative lock/file safety tests pass on the final commit.
- [ ] Coordinated OEE Toolkit portability PR is signed/merged and
      its final package/source test evidence is recorded.
- [ ] Official whole-curriculum CalVer archive, manifest digest,
      detached signature, trusted steward public key and Toolkit
      package distribution are approved and independently verified.
- [ ] Replace the README's pre-release installation wording with
      actual official installation and lock instructions, then
      retest the exact final documentation commit before tagging.
- [ ] Record the selected new Workspace version, GitHub tag and
      release assets only after the above evidence is complete.

## Release log

| Item | Value |
| --- | --- |
| Delegated preparation/approval date | 2026-11-21 |
| Documentation milestone | Student README and maintainer CONTRIBUTING merged previously |
| Prior tested Workspace SHA | `80050dd9b67c37f05ded8dbeaff7b024fae23a1d`, passed three platforms |
| Reviewed docs-only SHA | `2b245502c9c31af4016048f92aa55a89ca5f8079`, quality passed; no original release-smoke trigger |
| **Exact final Workspace SHA for release** | Pending signed preflight merge |
| **Exact-final-SHA cross-platform CI URL** | Pending post-merge run |
| Ubuntu/macOS/Windows job conclusions | Pending post-merge run |
| Coordinated OEE Toolkit PR | [OEE PR #261](https://github.com/0xbuffdev/open-engineering-education/pull/261) |
| Official signed curriculum and Toolkit install | Pending |
| Workspace release version/tag | Pending final decision |
| Published release status | **Not published by this PR** |

The planned order after approved software publication is:
complete the existing Content/0xNAND integration using its established
contract and release consumer; return to the optional SEF material
review and release-keyed resource mappings afterward. Neither activity
may alter already generated learner work without separate approval.

The final-release SHA and workflow URL **cannot be known at PR creation**.
Complete those fields from the actual GitHub main-branch run after
the final signed merge. A release decision cannot honestly claim
"all conditions satisfied" before those results exist.
