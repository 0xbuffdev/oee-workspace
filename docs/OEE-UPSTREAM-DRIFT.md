# Review changes between signed curriculum releases

Workspace uses a reviewed `releaseId` and `manifestSha256` from its project lock. The first-party OEE Toolkit verifies the locally installed curriculum before Workspace reads any course data. Normal learner commands do not select Git `main`, fetch a new archive or repin existing work.

Resource-map validation is blocking: an active reviewed map must match the exact signed release and course source. Missing, malformed or changed source data fails validation. A map approved for one release cannot be reused on another without review.

The advisory comparison checks a second, independently reviewed lock and installed release. Toolkit export v2 provides the course hashes, outcomes, assessments and module/lesson locators. The report identifies changes that may affect resource recommendations. Even when visible course structure is unchanged, a different `courseSha256` needs editorial review.

When **both** releases are installed and an active reviewed map exists, run:

```sh
python scripts/report-oee-drift.py --lock ./oee-curriculum.lock.json --target-lock ./reviewed-next-release.lock.json --course SEF1
```

Optional `--store` and `--target-store` select existing verified stores. The tool reports source identities, changed references, `reviewRequired` and `autoRemapped: false`. A missing target is incomplete rather than unchanged. It never writes a new map or edits learner evidence.

The signed curriculum `2026.11.1` is published, but **no active release-keyed resource map has been approved**. Until there is one, the example command reports that no active map was selected. The [SEF1 editorial review](../resources/editorial/SEF1-REVIEW.md) and [41-lesson matrix](../resources/editorial/SEF1-LESSON-MAP.md) are research for a future review, not learner-ready guides. Recheck chapter references, free alternatives and OEE-specific assessment behavior against the actual released course before activating a map.

Any new release selection or resource-guide publication requires explicit approval. Workspace does not fetch updates automatically or convert existing learner files.
