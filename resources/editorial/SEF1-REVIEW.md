# SEF1 resource review

The [41-lesson resource alignment study](SEF1-LESSON-MAP.md) expands this module-level review with lesson-specific suggestions and coverage gaps. Both records are editorial research. This file is **not an active resource map** and cannot generate a learner reading plan.

These module findings were recorded on November 20, 2026, against OEE Git commit `67416343f3eab17ada5d3c79ae6cc782524c29ff`. The commit identifies the material reviewed; it is not a Workspace runtime selector. The official signed [curriculum `2026.11.1`](https://github.com/0xbuffdev/open-engineering-education/releases/tag/curriculum-2026.11.1) and [Toolkit `0.1.0`](https://github.com/0xbuffdev/open-engineering-education/releases/tag/toolkit-v0.1.0) are now published. The findings still need comparison with the exact released SEF1 Toolkit export, plus separate editorial approval of a release-keyed v3 resource map.

**Core distinction:** Nand to Tetris uses a 16-bit Hack computer; OEE SEF1's reference educational machine uses its own eight-bit architecture. Project and book sections are optional reference material, never substitutes for public assessment criteria. The independently identified chapter references and available free alternatives below must be reconfirmed before release activation.

| Module | Coverage on reviewed source | Optional references | Known gap requiring review |
| --- | --- | --- | --- |
| 1. Bits and Representation | partial | R91 (section-titles: Numbers, Text) | Confirmed sections introduce binary values and character encodings but do not independently cover OEE's address-versus-value distinction, historical switching devices or physical voltage/noise assumptions. Follow the canonical course for those topics. |
| 2. Logic Gates | mapped | R89 (projects: 1); B7 (chapters: 1) | No documented gap on that source |
| 3. Registers and Memory | partial | R89 (projects: 3); B7 (chapters: 3) | Official project uses Hack's 16-bit registers and large RAM hierarchy, not OEE's four-cell eight-bit store. Its sequential-logic work does not independently teach OEE's bus contention, clock-edge and reset convention checks. Adapt explicitly. |
| 4. Arithmetic and ALU | partial | R89 (projects: 2); B7 (chapters: 2) | Official materials implement the 16-bit Hack adders/ALU, not OEE's eight-bit carry chain, modulo-256 behavior and selected-result zero detector. These OEE-specific checks remain to be practiced independently. |
| 5. Processor Execution | partial | R89 (projects: 5); B7 (chapters: 5) | Project 5 uses a different Hack datapath and instruction encoding. It does not establish the OEE two-byte fetch, atomic state commit or fault-state semantics. Use the canonical OEE machine for those investigations. |
| 6. Instructions and Programs | partial | R89 (projects: 4); B7 (chapters: 4) | Project 4 uses Hack assembly and machine language, not OEE's two-byte aligned opcodes, ADDI/ANDI, conditional JZ or illegal-address behavior. Do not reuse Hack branch traces as OEE answers. |
| 7. Devices and Boot | partial | R89 (projects: 5); B7 (chapters: 5) | Computer Architecture project demonstrates memory-mapped screen/keyboard but does not explain OEE's firmware, bootloader, persistent storage/file-system boundary or polling-versus-interrupt distinctions. Those require additional independent sources. |
| 8. Computer System Integration | partial | R89 (projects: 5); B7 (chapters: 5) | Project 5 integrates Hack's 16-bit components, not the OEE eight-bit program-to-output trace or its required fault injection, assumptions and limitations defense. OEE's final integration evidence must use the canonical model. |

## Activation checklist

1. Verify the published signed curriculum `2026.11.1` against the [approved trust record](../../docs/OEE-RELEASE-TRUST.md) and installed Toolkit `0.1.0` using the committed `oee-curriculum.lock.json`. Never use a synthetic CI key for learner trust.
2. Compare the signed release's SEF1 `exportVersion: 2` module and lesson titles, outcome/assessment references and public briefs against the editorial research. Re-check each proposed book edition and chapter/section claim.
3. Document missing or partially covered requirements, accessibility and free alternatives before editorial approval.
4. Create `resources/mappings/SEF/SEF1.json` using only schemaVersion 3 with `releaseId`, `manifestSha256`, `courseSha256` and the exact course identifiers. Record the actual remaining gaps; only mark the new mapping reviewed after documented editorial approval.
5. Regenerate/check the guide using the locked, verified Toolkit export. Learner-owned files are never rewritten or re-pinned.

**Until these gates pass, the course generator must scaffold SEF1 without an attached reading plan.** The public resource catalogue remains available for independent browsing.
