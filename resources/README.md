# Public OEE resource library

This library supports independent study of [Open Engineering Education](https://github.com/0xbuffdev/open-engineering-education). OEE owns course requirements, outcomes and assessments. This free Workspace owns optional resource recommendations and learner-authored records.

## Current mapping status

**The SEF1 v2 mapping is reviewed.** Its [source-pinned map](mappings/SEF/SEF1.json) and [generated Markdown](guides/SEF/SEF1.md) make verified external references available alongside explicit gaps. The former SEF1 schema-v1 mapping describes a different curriculum. It remains a deliberately rejected [negative test fixture](../tests/fixtures/resource-map-v1-SEF1.json) and in Git history; its chapter assignments were not transferred by module number.

The public catalogue remains available: [books](catalog/books/) and [online resources](catalog/online/). The single [active mapping schema](schemas/course-map.schema.json) is **v2 only**, with an explicit OEE specification v0.2.0, exact 40-character lowercase source commit, canonical path, and optional outcome/assessment references. Module numbers, lesson locators and reading recommendations are scoped to the recorded revision.

The reviewed SEF1 map covers eight modules to independently checked public sources, including [Nand to Tetris](https://www.nand2tetris.org/course), the second-edition book table of contents and the [Computer Science Field Guide](https://www.csfieldguide.org.nz/en/chapters/data-representation/). Except for the logic-gates module, coverage is **partial**; the Hack architecture uses 16-bit components and is not OEE's eight-bit reference machine. Learners can use the reviewed guide as optional support while respecting the documented gaps; review does not imply OEE course readiness or assessment equivalence. Courses without a map still scaffold **without a reading plan**.

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

Validate the reviewed v2 map against its **exact local OEE Git commit**:

~~~sh
python3 scripts/check-resources.py --course SEF1 --oee /path/to/open-engineering-education --json
python3 scripts/render-resource-guides.py --course SEF1 --oee /path/to/open-engineering-education --stdout
~~~

The resource validator now invokes the public OEE Toolkit directly on the map's recorded full Git commit and checks the derived export's exact source identity, modules, lessons, outcomes and assessments. When the commit is missing or unsupported, it returns **incomplete** (exit `3`) rather than using `HEAD`. The selected local checkout must be trusted; Git object IDs do not independently authenticate repository origin. The maintainer reviewed the SEF1 source/edition references, mapping choices and explicitly declared gaps under WS-I02. This does not assert full resource coverage, promote the OEE course status, or certify learner achievement. Mapped guide publication safety is separately owned by WS-I04.
