# Public OEE resource library

OEE Workspace provides optional resources for independent study. The [OEE specification and curriculum](https://github.com/0xbuffdev/open-engineering-education) remain authoritative for courses, outcomes, assessments and completion evidence. Neither paid books nor a private teaching platform are required.

## Current map status

The [resource catalogue](catalog/) remains browsable: [books](catalog/books/) and [online material](catalog/online/). However, **no active resource-map or generated SEF1 reading guide has yet been approved for an immutable curriculum release**. The previous reviewed Git-source SEF1 map cannot be transferred automatically to a new release. The [current 41-lesson SEF1 resource-alignment study](editorial/SEF1-LESSON-MAP.md) is a non-active editorial artifact, not an approved reading-plan feed. Its references, eight module descriptions and explicit learning gaps survive in the [SEF1 editorial review](editorial/SEF1-REVIEW.md). It documents the 16-bit Hack versus OEE eight-bit teaching-machine differences.

New public maps follow only [resource-map schema v3](schemas/course-map.schema.json). Each map identifies the exact releaseId, manifestSha256, courseSha256, OEE specification, course code/path and repository. Its draft/reviewed status describes independent resource editorial review, not source academic readiness.

## Editorial requirements

- Confirm each recommendation against the actual released course, authored outcome/assessment IDs, module titles and optional lesson navigation.
- Identify edition and source section accurately. Mark module coverage mapped, partial or unmapped, recording clear gaps for partial/unmapped cases.
- Never treat external projects, books or fees as substitutes for public OEE assessments. Preserve free alternatives.
- Only an explicitly reviewed map with a matching verified Toolkit exportVersion 2 may generate a guide. Missing or stale maps are not silently attached.
- Learner resources.md, personal notes, previous projects and assessment evidence are never overwritten or automatically re-pinned.

## Validate

```sh
python scripts/check-resources.py
python scripts/render-resource-guides.py --check
python -m unittest discover -s tests -p "test_*.py" -v
```

Those commands can validate the public catalogue and the currently empty active map set without an official release. After approval and independent installation of an official signed curriculum release, use an explicitly reviewed lock:

```sh
python -m oee_workspace resources check --lock ./oee-curriculum.lock.json --map resources/mappings/SEF/SEF1.json
python scripts/render-resource-guides.py --lock ./oee-curriculum.lock.json --check
```

The SEF1 map path above is **illustrative for future activation**, not a currently published map. Optional --store chooses an already verified local release store. A test-only signed archive is not steward authorization. [Release-drift review](../docs/OEE-UPSTREAM-DRIFT.md) is an independent read-only process.
