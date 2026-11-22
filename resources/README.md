# Optional learning resources

The Workspace catalogue collects books, free online explanations and tools you can use while studying the [OEE curriculum](https://github.com/0xbuffdev/open-engineering-education). OEE remains the source of the course order, learning outcomes and required assessments. You do not need a paid book or a 0xNAND account to study.

Browse the [books](catalog/books/) and [online resources](catalog/online/) directly. Check a resource's access conditions, edition and relevance to the lesson you are studying.

## Reading plans and review status

**No active, release-keyed SEF1 resource map or generated reading guide has been approved yet.** The [41-lesson SEF1 study](editorial/SEF1-LESSON-MAP.md) and [editorial findings](editorial/SEF1-REVIEW.md) are research for independent review, not a guide automatically attached to learner work.

Published curriculum `2026.11.1` uses a signed release selected by the project lock. A resource map must use [schema v3](schemas/course-map.schema.json), identify that exact release and the course's content hash, and receive separate editorial approval before a reading plan can be generated.

For SEF1, *Nand to Tetris* teaches a 16-bit Hack computer while the OEE reference machine is eight-bit. Course-specific instruction behavior, fault cases and assessment criteria must come from OEE itself. Supplementary materials cannot replace those requirements.

## Reviewing a resource map

A reviewer should confirm the cited edition and section against a publisher or the material itself, map recommendations to the released course's actual lessons and outcomes, and record gaps and access limits. Preserve free alternatives where possible. Mark recommendations as reviewed only after that work is complete.

Missing or stale maps cannot be silently attached. The course generator still creates study folders when no approved map exists.

Run repository checks from the root:

```sh
python scripts/check-resources.py
python scripts/render-resource-guides.py --check
python -m unittest discover -s tests -p 'test_*.py' -v
```

When a release-locked map exists, validate it against the installed and independently verified source:

```sh
python -m oee_workspace resources check --lock ./oee-curriculum.lock.json --map resources/mappings/SEF/SEF1.json
```

The map path above is an example of a future approved map; that file is not currently in the repository. `--store` can select another existing verified store.

The [release-comparison guide](../docs/OEE-UPSTREAM-DRIFT.md) explains how to review curriculum changes. Publishing a new signed curriculum cannot approve a resource map or change anyone's notes, reading plans or evidence automatically.
