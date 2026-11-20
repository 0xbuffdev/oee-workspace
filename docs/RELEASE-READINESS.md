# Independent Workspace release-readiness verification

**Milestone:** WS-I05 — independent external Workspace smoke and publishing checklist

**State:** Candidate for maintainer review; **not** a published release, learner grade, certification or permission to distribute a new package.

**Authority:** [Workspace interoperability acceptance matrix](https://github.com/0xbuffdev/context/blob/main/repos/oee-workspace/specs/0001-resource-interoperability.md), [CLI/agent safety contract](https://github.com/0xbuffdev/context/blob/main/repos/oee-workspace/specs/0003-cli-and-agent-safety.md) and canonical [Open Engineering Education](https://github.com/0xbuffdev/open-engineering-education).

## Current support and verification

The learner entry point is `python -m oee_workspace`, using Python 3.11+, Git and a trusted **local** first-party OEE Toolkit checkout. Only **OEE v0.2.0**, **Toolkit course exportVersion 1**, **Workspace resource-map v2** and **evidence schema v1** are supported. Old schema readers, project aliases, Bash wrappers, automatic source migrations and moving-HEAD fallbacks are absent.

The independent smoke makes new **standalone local Git clones** of both public repositories, then operates in a different, temporary learner directory. It never executes source code from an untrusted prompt, contacts a model provider, fetches remote resources or writes learner work into those source clones. CI obtains the two public repositories first, then the smoke runs using only those already available local checkouts. Private Content, 0xNAND, paid books, private accounts and network access are not required for the learner CLI.

### Reproduce on a fresh machine

Clone both public repositories, then from a Workspace checkout:

```sh
python -m oee_workspace doctor \
  --oee ../open-engineering-education \
  --revision 67416343f3eab17ada5d3c79ae6cc782524c29ff

python scripts/verify-external-workspace.py \
  --workspace-source . \
  --oee-source ../open-engineering-education \
  --report ../workspace-readiness.json
```

Inputs are existing **local Git checkout paths**, not URLs. The second command creates disposable independent clones, runs against separate temporary learner files and writes the JSON report only to the explicitly selected destination. Running it again does not reuse learner attempts from the previous run.

The [independent release workflow](../.github/workflows/release-readiness.yml) executes the exact PR commit on **Linux, macOS and Windows** and uploads a separate JSON report from each platform. It is a validation gate only: **no GitHub release, tag, package upload, source PR or learner-data upload occurs**.

## WS-T01–WS-T24 acceptance traceability

The case IDs and meanings come from the [existing Workspace acceptance specification](https://github.com/0xbuffdev/context/blob/main/repos/oee-workspace/specs/0001-resource-interoperability.md). Each seam below must be green for release readiness. This table is traceability, **not a claim that unrun tests passed**.

| Case | Acceptance | Executable verification |
| --- | --- | --- |
| WS-T01 | Independent public checkout | Clean-clone release smoke, public OEE and Workspace only |
| WS-T02 | Previous SEF1 map rejected | Smoke rejection; `test_resource_map_v2.py` |
| WS-T03 | No old-to-new SEF1 implicit mapping | Same negative map test and reviewed v2 positive source |
| WS-T04 | Pinned source while checkout HEAD moves | Smoke synthetic empty OEE commit; `test_pinned_resource_source.py` |
| WS-T05 | Missing pinned Git object | Smoke source-missing/incomplete; pinned-source tests |
| WS-T06 | Module title/meaning change | `test_toolkit_consumer.py` and `test_upstream_drift.py` |
| WS-T07 | Changed outcomes despite unchanged titles | `test_upstream_drift.py` outcome and coverage mutations |
| WS-T08 | Old OEE course specification | Smoke old-tag rejection; pinned-source tests |
| WS-T09 | Supported v0.2.0 course references | Smoke doctor and map check; pinned Toolkit contract |
| WS-T10 | Unknown outcomes/assessments | `test_toolkit_consumer.py` and pinned-resource tests |
| WS-T11 | Edition/section claims need actual review | Catalogue verification status and basis; **human bibliography check** |
| WS-T12 | Public free companion and optional paid book | Smoke catalogue and guide labels |
| WS-T13 | Reused catalogue ID is canonical | Smoke `R89` and `B7` reuse |
| WS-T14 | Review-needed cannot self-certify | Catalogue basis/status checks; **human source judgment** |
| WS-T15 | Partial map retains gaps | Smoke seven SEF1 gaps; `test_resource_map_v2.py` |
| WS-T16 | Unmapped material has no fabricated reference | Smoke unmapped SEF2; unmapped fixture |
| WS-T17 | Duplicate resource/locator | `test_resource_map_v2.py` duplicate tests |
| WS-T18 | Malformed URL/locator | Resource validation and shape/reference-negative tests |
| WS-T19 | Regenerating a public guide is deterministic | Smoke two identical outputs and committed-guide comparison |
| WS-T20 | Existing learner files never overwritten | Smoke repeat course/project/export; `test_safe_publication.py` |
| WS-T21 | V1 map unsupported | Smoke explicit rejection and v2-only schema test |
| WS-T22 | No invented universal final lab | Unmapped course output; OEE's actual assessment requirements |
| WS-T23 | No private consumer required | Entire clean-clone smoke has no private source or platform |
| WS-T24 | Guide never promotes OEE course status | Smoke pinned Toolkit export and `manualReviewRequired` |

Passing structural checks cannot prove a book's cited chapter is correct, certify editorial adequacy, authenticate an alleged human reviewer or assert learner mastery. WS-T11 and WS-T14 retain real **human editorial review** gates. A verified label or valid JSON shape alone is not sufficient.

## Additional release-readiness smoke

The independent run tests **SEF1** with its reviewed eight-module study map and **seven explicit partial-coverage gaps**, **SEF2** without a resource map, and **SEF10** whose actual pinned Toolkit export identifies `Type: project`. It rejects invented project aliases and repeated generation. The guide is regenerated twice byte-identically and compared to the published Markdown.

For learner evidence it creates two fresh UUID attempts, confirms both are initially unevaluated, validates local artifact references, rejects missing artifacts and mismatched hashes, checks read-only status, and exports **only explicitly selected JSON records**. Learner `progress.md`, unrelated attempts, artifact bytes and pre-existing export files remain untouched.

The script deliberately moves an **isolated OEE clone's HEAD** with an empty test commit, then verifies the previously recorded SEF1 pin still validates and the advisory upstream report never remaps sources. This does not modify the canonical OEE repository or the Workspace checkout.

The existing [blocking resource CI](../.github/workflows/resources.yml) runs broader pinned-export, schema, negative, safety, portability and upstream-drift regressions. The new smoke is a **separate consumer-path check**, not a second OEE parser or an alternative implementation.

## Maintainer publishing checklist

- [ ] Review and DCO-sign the WS-I05 PR, then run all checks against that exact signed commit.
- [ ] Independent clean-clone release CI succeeds on Linux, macOS and Windows, with a JSON artifact for **each** platform.
- [ ] Full pinned source, resource-map, evidence schema, file-safety, CLI, AI-safety and drift suites pass; no old-map runtime or compatibility shim is present.
- [ ] Run this smoke from a genuinely fresh public clone on a maintainer machine as an independent check of the CI environment.
- [ ] Reconfirm cited book editions/sections and free alternatives with human review; retain recorded incomplete/partial coverage rather than calling it complete.
- [ ] Check README commands, supported Python/Git requirements, security/privacy warnings, source provenance, LICENSE, NOTICE and any release notes.
- [ ] Decide the intended **Workspace** version, release tag and publishing method explicitly. OEE v0.2.0 is a curriculum specification, **not automatically the Workspace package version**.
- [ ] Obtain separate owner approval for any public release/tag. No automatic tag, package publishing or inference from an earlier repository release.

**CI success is engineering evidence, not a release authorization, accreditation decision or official assessment grade.** A source SHA pins bytes in a local checkout but is not proof that an untrusted checkout is authentic. Optional AI-provider research and private platform integrations remain deferred.
