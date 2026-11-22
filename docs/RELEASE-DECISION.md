# OEE Workspace release decision

The steward approved preparation of the OEE and Workspace releases on 2026-11-21, with an explicit review of release checks and documentation before publication.

The Toolkit `0.1.0` and signed curriculum `2026.11.1` are published. Workspace release preparation is approved, but its own release must wait for both independent test suites to pass on the exact final merged `main` commit across Linux, macOS and Windows. This record tracks that decision and the remaining work.

The existing Workspace release is `v0.0.1`. The next release will include the offline Toolkit v2 consumer path. OEE's specification `v0.2.0` has its own version number, while the signed curriculum is distributed as [`2026.11.1`](https://github.com/0xbuffdev/open-engineering-education/releases/tag/curriculum-2026.11.1).

## Acceptance scope

The next Workspace release must include:

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

- [x] Preflight PR #21 DCO-signed and merged at Workspace main
      `c3176d5de5a1b69decd6cdb63158bad94ad23a8f`.
- [ ] This official-release integration PR DCO-signed and merged at
      a new exact final Workspace main SHA; record post-merge evidence.
- [x] Preflight `Independent Workspace release readiness` workflow
      [passed on the previous exact main SHA](https://github.com/0xbuffdev/oee-workspace/actions/runs/44957330776).
- [ ] The disposable and official signed-release workflows both pass on the
      **new** exact final merged main SHA on Ubuntu, macOS and Windows.
      Record both run URLs and all six job conclusions before tagging.
- [ ] Workspace quality, resource/evidence unit contracts and
      negative lock/file safety tests pass on the final commit.
- [x] Coordinated OEE Toolkit portability and 0.1.0 package PRs merged;
      [published Toolkit](https://github.com/0xbuffdev/open-engineering-education/releases/tag/toolkit-v0.1.0)
      has independently checked wheel/sdist SHA-256 and three-OS CI.
- [x] Official whole-curriculum archive, signed attestation, public key
      and independently packaged Toolkit `0.1.0` are published.
      Actual manifest SHA-256 and public-key fingerprint are locked.
- [ ] The **real published release** passes cross-platform offline
      signature+consumer acceptance on this final Workspace source.
- [ ] Merge final learner README and official installation/lock instructions
      and retest their exact merged main SHA before tagging.
- [ ] Record the selected new Workspace version, GitHub tag and
      release assets only after the above evidence is complete.

## Release log

| Item | Value |
| --- | --- |
| Delegated preparation/approval date | 2026-11-21 |
| Documentation milestone | Student README and maintainer CONTRIBUTING merged previously |
| Prior tested Workspace SHA | `80050dd9b67c37f05ded8dbeaff7b024fae23a1d`, passed three platforms |
| Reviewed docs-only SHA | `2b245502c9c31af4016048f92aa55a89ca5f8079`, quality passed; no original release-smoke trigger |
| Previous confirmed Workspace main SHA | `c3176d5de5a1b69decd6cdb63158bad94ad23a8f` |
| Previous exact-main disposable smoke | [Passed three OS](https://github.com/0xbuffdev/oee-workspace/actions/runs/44957330776) |
| **New exact final Workspace SHA for release** | Pending official-installation PR merge |
| **Exact-final-SHA cross-platform official CI URL** | Pending post-merge run |
| Official Ubuntu/macOS/Windows job conclusions | Pending post-merge run |
| Coordinated OEE Toolkit PR | [OEE PR #261](https://github.com/0xbuffdev/open-engineering-education/pull/261) |
| Official signed curriculum and Toolkit | [`2026.11.1` published](https://github.com/0xbuffdev/open-engineering-education/releases/tag/curriculum-2026.11.1); [Toolkit `0.1.0` published](https://github.com/0xbuffdev/open-engineering-education/releases/tag/toolkit-v0.1.0) |
| Committed manifest SHA-256 | `57441494eb69c2ff9cb3f6029c8adc3c6a56f8c6ecabc43196c9b686e5959a6c` |
| Independently pinned public-key DER fingerprint | `0cbd8335bf39fab19b17a7bfaa33502d121d007fca4bddd5df0f43a9c814e2ef` |
| Proposed Workspace version/tag | `v0.1.0` (not created until final CI passes) |
| Published release status | **Not published by this PR** |

After Workspace is released, finish Content/0xNAND integration against the same reviewed OEE consumer contract. Return to the optional SEF resource mappings afterward. Existing learner work must remain untouched unless a separate reviewed change explicitly authorizes a migration.

Record the final Workspace SHA and workflow URLs from GitHub after the signed PR merges. Until those results exist, the release cannot be marked ready.
