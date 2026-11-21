# REL-I04 Workspace immutable-release readiness

**State:** engineering implementation for review. No official steward curriculum release, approved Toolkit package, commercial deployment or learner-data migration is authorized by this document.

The authoritative architecture is [OEE RFC 0005](https://github.com/0xbuffdev/open-engineering-education/blob/main/rfcs/0005-immutable-curriculum-releases.md), tracked in [Stage 2 issue #257](https://github.com/0xbuffdev/open-engineering-education/issues/257). The Toolkit's one parser is the academic export authority, not a Workspace Markdown reader.

## Current-only supported interfaces

- Python 3.11+ and installed first-party OEE Toolkit source-build candidate.
- Independently reviewed project lock with formatVersion 1, CalVer releaseId and full manifestSha256, selecting a previously installed and independently verified curriculum release.
- Toolkit exportVersion 2; resource-map schemaVersion 3; learner assessment-attempt schemaVersion 2.
- No learner-facing --oee / --revision, no moving Git source fallback, no v1 runtime export reader, no automatic map or learner-evidence conversion.
- Course IDs, outcomes, assessments, actual source status and lesson locators derive from the same verified Toolkit export. Structural passed does not certify learner achievement or source educational readiness.

## Independent disposable test

The [release-readiness CI](../.github/workflows/release-readiness.yml) runs on Linux, macOS and Windows. It checks out OEE **only for publisher-side fixture generation**, builds a complete temporary curriculum archive from one pinned Git commit, signs with an ephemeral Ed25519 key, independently verifies and installs into a temporary content-addressed store, and writes a temporary lock.

The [external smoke script](../scripts/verify-external-workspace.py) tests actual installed offline Toolkit v2 byte determinism, Workspace doctor, SEF1 course/SEF10 project scaffolding, learner file no-clobber, absence of unapproved SEF1 guide, evidence-v2 init/check/status/explicit export and bad-lock failure. CI stores JSON evidence only, not the archive, keys or real learner data.

To run unit and contract checks:

```sh
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/check-resources.py
python scripts/render-resource-guides.py --check
```

For disposable publisher-fixture smoke only, with source-built OEE Toolkit and optional cryptography installed:

```sh
python scripts/verify-external-workspace.py --workspace-source . --oee-source ../open-engineering-education --report ./workspace-test.json
```

The --oee-source switch belongs **only** to the release-test fixture publisher, not any learner CLI.

## Separate stop gates

- [ ] Independent steward approval of official source closure, license notices, signed archive, its exact digest, steward public signing key and key revocation/trust policy.
- [ ] Authorized immutable curriculum release and separately approved Toolkit package publication.
- [ ] Re-review the full SEF1 resource/edition/assessment mapping against the **actual released** course and record a new approved v3 map before publishing any reading plan.
- [ ] Review Linux/macOS/Windows CI and negative tests at a DCO-signed PR head.
- [ ] Preserve non-disposable learner files and obtain separate approval before destructive data changes.
- [ ] Independent Workspace release and deployment approval. REL-I05 Content/0xNAND host replacement remains separately tracked.

No successful test is equivalent to a learner grade, a released curriculum, or production authorization.
