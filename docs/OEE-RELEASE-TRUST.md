# Approved OEE software and curriculum selection

Workspace selects the Toolkit software and the signed curriculum independently. The values below identify the approved distributions, source release and steward public key. Changes require maintainer review. The software lock is the machine-readable owner of the Toolkit version, rule set, distribution sizes and hashes, and independently reviewed steward fingerprint. The table records their human-readable provenance. The installer separately pins the signed curriculum assets; those pins do not change with a software upgrade.

| Property | Approved value |
| --- | --- |
| Curriculum CalVer | `2026.11.1` |
| Specification | OEE `v0.2.0` |
| Toolkit Python distribution | `oee-toolkit 0.2.0` |
| Publisher-source commit | `f2afed3e36f6ae0495e2b44a8d9337661defeda1` |
| Signed manifest SHA-256 | `57441494eb69c2ff9cb3f6029c8adc3c6a56f8c6ecabc43196c9b686e5959a6c` |
| Curriculum archive SHA-256 | `931b30209a2727717af331f4fd46bfc8e637c94c4d1d95d08d6ffeee753c78d2` |
| Approved steward Ed25519 public-key fingerprint (DER SHA-256) | `0cbd8335bf39fab19b17a7bfaa33502d121d007fca4bddd5df0f43a9c814e2ef` |
| Official release assets | [Curriculum 2026.11.1](https://github.com/0xbuffdev/open-engineering-education/releases/tag/curriculum-2026.11.1) and [Toolkit 0.2.0](https://github.com/0xbuffdev/open-engineering-education/releases/tag/toolkit-v0.2.0) |
| Three-platform archive source validation | [Four successful jobs](https://github.com/0xbuffdev/open-engineering-education/actions/runs/44997272152) |
| Toolkit 0.2.0 wheel SHA-256 | `933d82a09f8ca01930a9a4e76b1bb399f2d10a940783a3bc6a39e7b5e9dc46f3` |
| Software selection | [Toolkit lock](../oee-toolkit.lock.json), export v2, context v1 |
| Verification dependency wheels | [Hash-locked requirements](../oee-release-requirements.txt) |

The steward's local release-script output reported the fingerprint recorded above. Check the downloaded public PEM against that independently approved value. Then verify its Ed25519 signature over the canonical attestation, which includes the archive and manifest digests. A matching tag name alone cannot establish authenticity.

The [offline installer](../scripts/install-official-curriculum.py) checks the hashes of all six published files, the trusted public-key fingerprint and the detached signature. It rejects altered files, missing locks and unexpected version changes. The installer leaves existing releases intact. Only the public key belongs in the download set; never commit or upload the steward's private key.

Normal source commands invoke the Toolkit through `run-pinned-toolkit.py` with isolated Python. The runner checks the installed distribution and module identity against the reviewed software selection. Course exports must declare the approved software and rule set. Assessment context must also match the course export and the verified manifest, including document and range hashes. Use the pinned dependency requirements for both download and offline installation.

If the signing key is compromised or revoked, stop using it for new installations. The OEE steward must publish an advisory, review affected releases and approve a replacement key. Do not silently update learner locks or replace existing files. A verified signature authenticates the source; it does not establish a course's academic readiness or a learner's achievement.
