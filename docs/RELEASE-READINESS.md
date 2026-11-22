# REL-I04 Workspace immutable-release readiness

The signed OEE curriculum `2026.11.1` and Toolkit `0.1.0` are published. Workspace still needs passing disposable-fixture and public-release smoke tests on the exact merged `main` commit before its own release. These tests do not authorize grading, a commercial deployment, unreviewed resource maps or changes to learner records.

The implementation follows [OEE RFC 0005](https://github.com/0xbuffdev/open-engineering-education/blob/main/rfcs/0005-immutable-curriculum-releases.md) and the work recorded in [Stage 2 issue #257](https://github.com/0xbuffdev/open-engineering-education/issues/257). Toolkit provides the academic exports; Workspace does not read curriculum Markdown directly.

## Current-only supported interfaces

- Python 3.11+ and the published first-party OEE Toolkit `0.1.0`.
- Independently reviewed project lock with formatVersion 1, CalVer releaseId and full manifestSha256, selecting a previously installed and independently verified curriculum release.
- Toolkit exportVersion 2; resource-map schemaVersion 3; learner assessment-attempt schemaVersion 2.
- No learner-facing --oee / --revision, no moving Git source fallback, no v1 runtime export reader, no automatic map or learner-evidence conversion.
- Course IDs, outcomes, assessments, actual source status and lesson locators derive from the same verified Toolkit export. Structural passed does not certify learner achievement or source educational readiness.

## Independent disposable test

The [release-readiness workflow](../.github/workflows/release-readiness.yml) runs on Linux, macOS and Windows. It checks out OEE to build a disposable test archive at a pinned commit. Each platform signs that temporary archive with a test-only Ed25519 key, installs it in an isolated store and creates a temporary lock.

The [external smoke script](../scripts/verify-external-workspace.py) checks deterministic Toolkit v2 exports, Workspace `doctor`, SEF1 and SEF10 scaffolding, and evidence-v2 operations. It also checks that a duplicate course leaves files untouched, an unapproved SEF1 reading plan stays absent and a bad lock is rejected. CI retains JSON results without uploading the test archive, keys or learner data.

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

The `--oee-source` flag is accepted by the release-test fixture publisher only. Learner CLI commands do not use it.

## Separate stop gates

- [ ] Independent steward approval of official source closure, license notices, signed archive, its exact digest, steward public signing key and key revocation/trust policy.
- [ ] Authorized immutable curriculum release and separately approved Toolkit package publication.
- [ ] Re-review the full SEF1 resource/edition/assessment mapping against the **actual released** course and record a new approved v3 map before publishing any reading plan.
- [ ] Review Linux/macOS/Windows CI and negative tests at the DCO-signed PR head **and repeat release-readiness on the exact merged final main commit before tagging**. Record the three-platform workflow run URL and final main SHA in [RELEASE-DECISION.md](RELEASE-DECISION.md).
- [ ] Preserve non-disposable learner files and obtain separate approval before destructive data changes.
- [ ] Independent Workspace release and deployment approval. REL-I05 Content/0xNAND host replacement remains separately tracked.

A passing test confirms the behavior it exercises. It cannot grade a learner or authorize a production release.

## Release workflow triggering

The three-platform workflow runs when learner docs (`README.md` and `CONTRIBUTING.md`), maintainer docs, CLI, templates, resource code or tests change. It can also run manually or on `v*` tags. The tag run adds evidence after publication; the release decision still needs a passing run on the final `main` commit before tagging, even if the merge changed only documentation.

Read the run SHA and each Ubuntu/macOS/Windows conclusion. A successful
run based on a different source commit is insufficient for release
approval. The [release decision](RELEASE-DECISION.md) records the
remaining formal publishing steps; the CI signature is always test-only.

## Actual official OEE release acceptance

The [official-release smoke](../.github/workflows/official-release-smoke.yml) downloads all six published files for Toolkit `0.1.0` and curriculum `2026.11.1`. It checks their SHA-256 hashes before installing the wheel and checks the signing key against the independent fingerprint in the [release-trust record](OEE-RELEASE-TRUST.md).

The [offline installer](../scripts/install-official-curriculum.py) uses the committed [curriculum lock](../oee-curriculum.lock.json) to verify the signed attestation and install the archive in a temporary trusted store. The [consumer smoke](../scripts/verify-official-workspace.py) then runs Toolkit export v2, `doctor`, SEF1 and SEF10 generation, and evidence-v2 operations. It tests duplicate-course protection, missing reading-plan approval and invalid-lock rejection before any learner file is created.

The official smoke consumes downloaded release files without an OEE source checkout, test signing key or publishing permission. Wait for both workflows to pass on the final merged `main` commit before creating tag `v0.1.0`. Record the final SHA and run URLs in the [release tracker](https://github.com/0xbuffdev/oee-workspace/issues/18) after the merge, so the documentation does not need a new commit just to refer to itself.
