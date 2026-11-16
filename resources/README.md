# Public OEE resource library

This library supports independent study of [Open Engineering Education](https://github.com/0xbuffdev/open-engineering-education). OEE owns course requirements, outcomes and assessments. This free Workspace owns optional resource recommendations and learner-authored records.

## Current mapping status

**No active reviewed course map or generated study guide is published.** The former SEF1 schema-v1 mapping describes a different curriculum. It is now a deliberately rejected [negative test fixture](../tests/fixtures/resource-map-v1-SEF1.json) and remains in Git history; its chapter assignments must not be transferred by module number.

The public catalogue remains available: [books](catalog/books/) and [online resources](catalog/online/). The single [active mapping schema](schemas/course-map.schema.json) is **v2 only**, with an explicit OEE specification v0.2.0, exact 40-character lowercase source commit, canonical path, and optional outcome/assessment references. Module numbers, lesson locators and reading recommendations are scoped to the recorded revision.

The replacement SEF1 mapping requires independent editorial review under WS-I02. Until then, learner workspaces can be created **without a reading plan**; this is not an OEE completion gap.

## Editorial principles

- No legacy schema reader, converter, or automatic remapping. Historical data is not current guidance.
- Every map must reference one canonical OEE revision and carry a draft or reviewed mapping status. Valid JSON is not certification of educational meaning.
- Coverage is mapped, partial, or unmapped. Partial/unmapped require explicit gap explanations. Verified mapping claims need independent edition, section, or authoritative website checks.
- Catalogue IDs are stable and reusable, with optional resource-specific lesson, outcome and assessment references. References must exist in the exact selected OEE Toolkit export.
- Paid resources are always optional; no public OEE requirement depends on paid books, private 0xNAND content or proprietary services.

## Validation

Run catalogue checks and tests without a private service:

~~~sh
python3 scripts/check-resources.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/render-resource-guides.py --check
~~~

For a newly reviewed v2 map and an independently generated pinned OEE Toolkit export, use:

~~~sh
python3 scripts/check-resources.py --course SEF1 --export /path/to/pinned-SEF1-export.json
python3 scripts/render-resource-guides.py --course SEF1 --export /path/to/pinned-SEF1-export.json --stdout
~~~

The export consumer checks source identity, module/lesson locators and outcome/assessment references. The caller must independently prove that the export was derived from the named Git commit; a JSON claim alone is not cryptographic provenance. Source lookup and end-to-end binding remain WS-I01; editorial resource review is WS-I02; safe final publishing and regeneration are WS-I04. A map presented without its pinned export **fails closed as source_missing**. No new course guide has yet been accepted.
