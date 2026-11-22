# OEE Workspace v0.1.0 release decision

The steward approved release preparation on November 21, 2026. OEE Toolkit `0.1.0` and the steward-signed curriculum `2026.11.1` were published on November 22. Workspace `v0.1.0` is the next planned release, separate from the OEE specification `v0.2.0`, Toolkit package and curriculum archive.

The [learner documentation PR #23](https://github.com/0xbuffdev/oee-workspace/pull/23) was DCO-signed and merged on November 22. It updated the README and directory guides to describe the supported release-locked CLI and removed obsolete generator commands.

## Accepted release scope

The release includes the Python 3.11+ learner CLI, OEE Toolkit export v2, exact signed curriculum lock, local course and project scaffolding, evidence attempt schema v2, read-only status, explicit JSON export and optional resource-map schema v3.

The default curriculum lock selects the official signed release `2026.11.1` by manifest SHA-256 `57441494eb69c2ff9cb3f6029c8adc3c6a56f8c6ecabc43196c9b686e5959a6c`. The separately approved steward Ed25519 public-key DER fingerprint is `0cbd8335bf39fab19b17a7bfaa33502d121d007fca4bddd5df0f43a9c814e2ef`.

Normal learner commands do not access the network, install updates, follow a Git branch, overwrite existing learner files or convert earlier evidence. The [resource catalogue](../resources/README.md) is public, but no SEF1 release-keyed resource map has received independent approval. Workspace does not grade assessments, authenticate reviewers or award certificates.

## Verified merged baseline

All four CI workflows passed on Workspace main commit `ed573e81051dd0e7c4bd6936fabc51ce60760304`, the merge of PR #23.

| Verification | Results on final documented baseline |
| --- | --- |
| [Official signed-release smoke](https://github.com/0xbuffdev/oee-workspace/actions/runs/45005257450) | Ubuntu, macOS and Windows passed |
| [Independent disposable-release smoke](https://github.com/0xbuffdev/oee-workspace/actions/runs/45005257433) | Ubuntu, macOS and Windows passed |
| [Workspace release contracts](https://github.com/0xbuffdev/oee-workspace/actions/runs/45005257422) | Passed |
| [Workspace quality](https://github.com/0xbuffdev/oee-workspace/actions/runs/45005257408) | Passed |

The official smoke uses the separately published OEE Toolkit wheel, signed curriculum archive, attestation and independently reviewed signing-key fingerprint. The disposable smoke uses an isolated test-only signing key. Successful tests establish the checked implementation behavior, not a learner grade or independent academic endorsement.

## Remaining publication steps

- [x] Publish the separate OEE Toolkit and signed curriculum releases.
- [x] Merge the student README and current-only documentation corrections with DCO sign-off.
- [x] Verify the official and disposable three-OS suites on the merged documentation baseline.
- [ ] Merge this publication-metadata update, including `CITATION.cff` and the public release notes, with DCO sign-off.
- [ ] Verify quality, resource/evidence contracts and both three-OS suites on the **new exact main SHA after this merge**.
- [ ] Check that the release date in `CITATION.cff` matches the actual publication date. If publication moves beyond November 22, update it before tagging and rerun the checks on the new final commit.
- [ ] Create `v0.1.0` on the final approved commit and publish a GitHub release with the [release notes](RELEASE-NOTES-v0.1.0.md).
- [ ] Confirm the tag resolves to the intended commit and the tag-triggered checks succeed.

Record the final commit and run URLs in [release tracking issue #18](https://github.com/0xbuffdev/oee-workspace/issues/18) after merging, so another documentation-only commit is not required solely to record its own SHA.

This release does not approve a new resource map, change existing learner locks or authorize a Content/0xNAND deployment. Those are separate subsequent reviews.
