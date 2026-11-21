# SEF1 — Editorial resource review before release activation

**New source-by-source follow-up:** the [41-lesson SEF1 editorial alignment matrix](SEF1-LESSON-MAP.md) compares current OEE SEF1 with existing Content B1/B7/B46 and independently verified free supplementary resources. It is not a release-keyed resource map or grading contract. The historical review below is preserved for source-specific comparison.

This preserves the independently reviewed **resource recommendations and known gaps** from the November 20, 2026 SEF1 editorial assessment. It is **not an active resource map**, approved curriculum release, learner guide or transferable source approval.

The reviewed comparison was against the immutable OEE course at Git commit `67416343f3eab17ada5d3c79ae6cc782524c29ff`. That commit is historical editorial context, **not a supported Workspace runtime selector**. An official signed curriculum release, an approved release lock, a re-review of its actual SEF1 export and new release-keyed resource-map v3 are required before publishing a reading plan.

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

1. Record steward approval of the exact signed, immutable **whole-curriculum** release, license notices, trusted signing key and `manifestSha256`.
2. Independently install and verify it with the first-party Toolkit. Commit the separately reviewed project `oee-curriculum.lock.json`; never use a synthetic/CI key or checksum as official trust.
3. Review the new SEF1 `exportVersion: 2` module titles, outcome/assessment references, evidence and public assessment briefs against each proposed resource. Re-check page/chapter/section claims.
4. Create `resources/mappings/SEF/SEF1.json` using only schemaVersion 3 with `releaseId`, `manifestSha256`, `courseSha256` and the exact course identifiers. Record the actual remaining gaps; only mark the new mapping reviewed after documented editorial approval.
5. Regenerate/check the guide using the locked, verified Toolkit export. Learner-owned files are never rewritten or re-pinned.

**Until these gates pass, the course generator must scaffold SEF1 without an attached reading plan.** The public resource catalogue remains available for independent browsing.
