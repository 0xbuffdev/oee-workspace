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

For a future reviewed v2 map, validate against its **exact local OEE Git commit**:

~~~sh
python3 scripts/check-resources.py --course SEF1 --oee /path/to/open-engineering-education --json
python3 scripts/render-resource-guides.py --course SEF1 --oee /path/to/open-engineering-education --stdout
~~~

The resource validator now invokes the public OEE Toolkit directly on the map's recorded full Git commit and checks the derived export's exact source identity, modules, lessons, outcomes and assessments. When the commit is missing or unsupported, it returns **incomplete** (exit `3`) rather than using `HEAD`. The selected local checkout must be trusted; Git object IDs do not independently authenticate repository origin. Human bibliography/edition review remains separate (WS-I02), as does safe mapped-guide publishing (WS-I04). No current SEF1 map or reading guide has been accepted.
