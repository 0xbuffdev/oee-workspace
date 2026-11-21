# Advisory comparison between immutable curriculum releases

Workspace never uses moving upstream Git main, HEAD or a guessed latest curriculum as a learner source. An approved releaseId and full manifestSha256 are selected in a local project lock, and all course bytes are verified by the first-party OEE Toolkit.

**Blocking validation** checks the current release-locked source against every active reviewed resource map. A missing/altered release or invalid source reference fails closed. It does not upgrade a release, migrate old maps or reinterpret learner evidence.

**Optional advisory comparison** validates a **second independently approved release lock**, then compares the first-party Toolkit exportVersion 2 for the same course. Differences include source digests, outcomes, assessment criteria, module/lesson locators and affected resource associations. A changed courseSha256 requires review even when derived structural fields remain identical. Neither report creates a reviewed guide nor updates source selection.

For two already reviewed and installed releases:

~~~sh
python scripts/report-oee-drift.py --lock ./oee-curriculum.lock.json --target-lock ./reviewed-next-release.lock.json --course SEF1
~~~

Optional --store and --target-store select explicit existing trusted stores. The script reports immutable source identities, changes, reference risks, reviewRequired and autoRemapped: false. An unavailable target is incomplete, not unchanged.

There are currently no active resource maps before the first official approved release. [SEF1 editorial findings](../resources/editorial/SEF1-REVIEW.md) remain historical source-specific context and may be reconsidered when a new release is actually approved. Review must explicitly approve any replacement mapping, not automatically transfer old chapter numbers or associate a book with newly changed assessments.

No auto-repin, network fetch, historical-format reader, official certification, learner-data conversion or source Markdown re-parser exists in this advisory path.
