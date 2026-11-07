# Public OEE resource library (SEF1 pilot)

This is the **public resource index** for [Open Engineering Education](https://github.com/0xbuffdev/open-engineering-education) independent study.

## Ownership

- **OEE** owns curriculum, outcomes, lesson order, assessments and completion requirements.
- **OEE Workspace** owns public resource metadata and optional course/module/lesson mappings.
- **Private 0xNAND Content** may import these mappings but adds its own instructional implementation. No private authored lessons are published here.

## Browse

- [SEF1 draft resource mapping](mappings/SEF/SEF1.json)
- [Book catalog](catalog/books/) and [online resources](catalog/online/)
- [Resource schema](schemas/resource.schema.json) and [mapping schema](schemas/course-map.schema.json)

Resource identifiers **B1, B7, B46, R89 and R90** are preserved from the private legacy catalogue. Define each resource once and reference its ID from any number of course maps. A course mapping follows the *current OEE module order*, not a textbook's chapter order.

This pilot uses JSON rather than YAML so that Python 3's standard library can validate and consume resources offline without additional dependencies.

## Editorial status

Each module has a `coverage` value:

- `mapped`: reviewed anchor material exists, but not necessarily every lesson is independently covered.
- `partial`: known gaps or important references remain unverified.
- `unmapped`: no usable material has yet been identified.

Every mapping entry has a separate `verification` value of `verified` or `review-needed`. A title or range inherited from private Content is **not verified** merely because it was previously mapped. Never invent chapter/page numbers or source URLs, and record edition differences.

`reference`, `practice`, and `optional` are resource recommendation roles; none imposes a paid-book requirement. The goal is adequate, freely accessible study and hands-on material for independent learners.

## Validate

With a sibling OEE checkout:

```bash
python3 scripts/check-resources.py --oee ../open-engineering-education
```

The validator will check catalogue identities, all resource pointers and mapping correspondence to the actual OEE module and lesson titles. The OEE source revision is recorded for provenance, not used to reject unrelated curriculum changes; structural drift fails validation.

## Generated course guides

- [Browse the SEF1 study guide](guides/SEF/SEF1.md).
- Regenerate public guides with `python3 scripts/render-resource-guides.py --write`.
- Check committed guides with `python3 scripts/render-resource-guides.py --check`.
- Print a course with `python3 scripts/render-resource-guides.py --course SEF1 --stdout`.

These public guides are deterministic snapshots derived from the catalogue and mappings. Do not edit generated guides directly; change the source records and regenerate. The course generator creates a `notes/SEF/SEF1/reading-plan.md` snapshot when a map exists, while the personal `resources.md` reading log remains separate. Existing learner directories are never overwritten. Courses without mappings can still be created, but receive no reading plan yet.
