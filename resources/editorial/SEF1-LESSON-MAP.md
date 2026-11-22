# SEF1 — lesson-by-lesson resource alignment (editorial only)

**State:** research and mapping for review, **not** a published or approved resource map. This file cannot be consumed as schema v3 by the learner CLI.

**Source reviewed:** [OEE SEF1 at editorial commit `216553f10d20ed5fcb40dda46a147c68d7895555`](https://github.com/0xbuffdev/open-engineering-education/blob/216553f10d20ed5fcb40dda46a147c68d7895555/curriculum/SEF/SEF1.md), OEE specification v0.2.0, course status `draft` at that commit. The [signed curriculum `2026.11.1`](https://github.com/0xbuffdev/open-engineering-education/releases/tag/curriculum-2026.11.1) is published and selected by Workspace's release lock. This editorial mapping has **not** yet been verified against the signed release's Toolkit export. The older Git commit is research provenance, not a runtime source selector or approved learner lock.

**Scope:** all 8 OEE modules, all 41 OEE lessons, the course's 7 outcomes and required assessments `SEF1-AS1` (O1/O2), `SEF1-AS2` (O3/O4), `SEF1-AS3` (O5/O6/O7). Every recommendation is **optional**. Book chapters/project descriptions support concepts; the public OEE course defines actual assessment obligations.

## Findings from the Content resource comparison

- The private Content `docs/resource/books.md` records **B1**, **B7**, **B46**, but `docs/curriculum/SEF/SEF1.md` describes a **previous eight-module academic arrangement** that is *not* positionally identical to the current public OEE eight modules. Do **not** migrate module indexes or force the old structure onto current OEE.
- The Content recommendation to read B1 in its own order is a helpful narrative option, but cannot replace exact OEE representation/logic/clock/bus/instruction requirements. The book's 2009 section titles, including “Addresses”, “The Arithmetic and Logic Unit”, “Firmware” and “Boots”, are independently listed at [Open Library](https://openlibrary.org/works/OL18200842W/But_How_Do_It_Know?edition=buthowdoitknowba0000scot); their **full technical adequacy remains unverified**.
- B7's second-edition chapters 1–5 are accurate from the [publisher contents](https://penguinrandomhousehighereducation.com/book/?isbn=9780262539807) and [official project sequence](https://www.nand2tetris.org/course). Important: **Nand to Tetris uses a 16-bit Hack computer**, while SEF1's assessment machine is **eight-bit**, with *two-byte instructions*, `PC`, `A`, `Z`, custom RAM and `0xF0`/`0xF1` latches, OEE-defined faults and atomic transitions. Comparing concepts is legitimate; substituting Hack results as OEE traces is not.
- B46's “only chapters 1–2” mapping is **under-specific**. The [publisher's 2nd-edition table of contents](https://www.pearson.com/en-us/subject-catalog/p/code-the-hidden-language-of-computer-hardware-and-software/P200000007298?view=educator) confirms relevant chapters 9–13 for bases and encodings, 14/20–21 for arithmetic/ALU, 17–19/22 for state and memory, and 23–26 for control and peripherals. The previous “SEF1 Module 2 codes” label is not a correct reference to *current OEE* Module 2 (Logic Gates). These are **TOC-derived topical matches**, not verified chapter-text equivalence.
- The old private Content `B3` (Harris & Harris) does **not** specify an edition, so its chapter/section numbers cannot safely be promoted into a public map. A second-edition table of contents exists, but the learner's edition must first be confirmed.
- B7 and R89 are not required purchases. R89 supplies free official project materials; R92, R93, B4, R94, R95, R96 and existing R91 add free independent alternatives and context.
- [Nand to Tetris license](https://www.nand2tetris.org/license): CC BY-NC-SA 3.0; link to original material, never mirror project assets in Workspace. The authors ask learners not to publish project **solutions** publicly. Recommend a private learner repository for original Nand to Tetris project work; this is separate from OEE's own public and free assessment requirements.

## Confidence and coverage conventions

- **Topical:** a publisher/official-source chapter or section explicitly addresses the lesson's main concept; **not** a claim of full OEE outcome or assessment coverage.
- **Partial:** useful conceptual material exists, but the named OEE-specific behavior, width or verification still needs independent work.
- **Source-only:** no sufficiently verified external section is identified; the public OEE requirement itself is the binding reference. A paid book is never required to eliminate a gap.
- The “OEE adaptation / gap” column is essential even when the topic matches. All chapter numbers for B7 and B46 refer to the cited **second editions**. For B1 use literal **section titles**; no invented chapter numbering. No table cell contains a private answer key, graded solution or new learner obligation.

## Lesson-level traceability

### Module 1 — Bits and Representation

Outcome coverage: SEF1-O1.

| OEE lesson | Verified-section / optional resource suggestions | Support | OEE-specific adaptation / gap |
| --- | --- | --- | --- |
| 1.1 From Bits to Computers | R95 (Computer History Museum: 1947 transistor, 1949 EDSAC); B46 ch. 6–8 (switches and relays); B1 sections “Just the Facts Ma'am” and “The First Great Invention” | partial | History and broad mechanism only; OEE distinguishes real switching and the eight-bit teaching model; no external text substitutes for its reference specification. |
| 1.2 Physical Signals and Logical States | R92 (Digital Circuits, ch. 3: “Digital Signals and Gates”, “Logic Signal Voltage Levels”); B46 ch. 6–8 | topical | Check actual high/low thresholds, noise and switching delay without treating a simulator's abstract bits as measured voltages. |
| 1.3 Bits and Bytes | R91 (“Numbers”); B46 ch. 11–12; B1 “Just a Little Bit”, “Eight Is Enough” | topical | Explicitly derive 2^8=256 patterns and 0–255 values using OEE's own examples. |
| 1.4 Number Representations | R91 (“Numbers”); R92 (ch. 1: decimal/binary/hexadecimal); B46 ch. 9–12 | topical | Keep unsigned eight-bit width and signed/unsigned interpretations separate; no implicit 16-bit Hack interpretation. |
| 1.5 Codes and Meaning | R91 (“Text”); B46 ch. 13 (“From ASCII to Unicode”); B1 “Codes” | topical | Connect 0x2D to unsigned 45 versus ASCII hyphen and distinguish UTF-8 bytes from characters. |
| 1.6 Addresses and Values | B1 “Numbers”, “Addresses”; R89 project 3 (addressed RAM); B7 ch. 3 | partial | Distinguish address 0x80 from the byte stored there; external RAM often has different address/word widths. |

### Module 2 — Logic Gates

Outcome coverage: SEF1-O2, SEF1-O1. Relevant summative requirement: SEF1-AS1 (with Module 1).

| OEE lesson | Verified-section / optional resource suggestions | Support | OEE-specific adaptation / gap |
| --- | --- | --- | --- |
| 2.1 Boolean Logic | R92 (ch. 7: Boolean Algebra; ch. 3: Logic Gates); R89 project 1; B7 ch. 1 | topical | Independently derive every truth table instead of treating a tool's expected output as the explanation. |
| 2.2 NAND Construction | R89 project 1; R90 (early gate levels); B7 ch. 1; R93 (logic simulator) | topical | Construct OEE's NAND-derived NOT and AND with inspectable gate connections. |
| 2.3 Combining Gates | R89 project 1; R90 (gate levels); B7 ch. 1; B46 ch. 8 | topical | Build NAND-based OR and XOR; document intermediate wires and all input combinations. |
| 2.4 Combinational Circuits | R92 (ch. 7: Boolean expressions and multigate circuits); R89 project 1; R93 | partial | Explain present-input-only behavior and label intermediate signals; this is not a sequential storage circuit. |
| 2.5 Circuit Verification | R89 project 1 (hardware simulator and test files); R93 (probes); R92 (ch. 7: truth tables) | partial | Derive an independent oracle for 2-input truth tables, record a miswire and correction; supplied Hack tests do not establish independent OEE evidence. |

### Module 3 — Registers and Memory

Outcome coverage: SEF1-O3, SEF1-O1.

| OEE lesson | Verified-section / optional resource suggestions | Support | OEE-specific adaptation / gap |
| --- | --- | --- | --- |
| 3.1 Clocked Storage | R89 project 3; R92 (ch. 10: edge-triggered latches and flip-flops); B46 ch. 17–18 | partial | OEE requires an explicit clock edge, controlled write and hold rule; distinguish real timing from ideal model. |
| 3.2 Registers and Enables | R89 project 3 (Bit, Register); B7 ch. 3; B46 ch. 22; R93 | partial | Hack project register is 16-bit; adapt to OEE's eight-bit enabled register and inspect each clock edge. |
| 3.3 Bus Selection | B46 ch. 22 (“Registers and Busses”); R92 (ch. 3: special-output gates); R93 | partial | Demonstrate single active bus source, disabled drivers and contention; source TOCs do not prove the exact OEE wiring. |
| 3.4 Addressable Memory | R89 project 3 (RAM8 and address selection); B7 ch. 3; B1 “Addresses” | partial | Use four independently addressable 8-bit cells with defined reset, write enable, distinct values, nondestructive reads. |

### Module 4 — Arithmetic and ALU

Outcome coverage: SEF1-O4, SEF1-O2. Relevant summative requirement: SEF1-AS2 (with Module 3).

| OEE lesson | Verified-section / optional resource suggestions | Support | OEE-specific adaptation / gap |
| --- | --- | --- | --- |
| 4.1 Bitwise Operations | R92 (ch. 2: binary arithmetic; ch. 7: Boolean algebra); B46 ch. 20; R93 | partial | Apply AND/OR/XOR/NOT and shifts to explicit eight-bit patterns; do not assume infinite-width values. |
| 4.2 Single-Bit Adders and Carry | R89 project 2 (HalfAdder, FullAdder); B7 ch. 2; B46 ch. 14 | topical | Independently derive sum/carry truth tables for carry-in and carry-out. |
| 4.3 Eight-Bit Addition | R89 project 2 (Add16 concept); R92 (ch. 2: binary overflow); B7 ch. 2 | partial | Adapt sixteen-bit addition to eight-bit carry chain and modulo 256; test 250+10 and 255+1. |
| 4.4 ALU Selection | R89 project 2 (ALU); B7 ch. 2; B46 ch. 21 | partial | Hack ALU operations/selectors differ; implement OEE's arithmetic and AND/OR/XOR selection only. |
| 4.5 Zero Detection | R89 project 2 (ALU status outputs); B46 ch. 21; R93 | partial | Zero must reflect the selected eight-bit result, not an unselected ALU path or earlier result. |
| 4.6 ALU Debugging | R89 project 2 (simulator test files); R93 (probes and saved circuits) | partial | Supply independent truth/arithmetic expectations and deliberately diagnose a carry, enable, selector or zero fault. |

### Module 5 — Processor Execution

Outcome coverage: SEF1-O5, SEF1-O3, SEF1-O4.

| OEE lesson | Verified-section / optional resource suggestions | Support | OEE-specific adaptation / gap |
| --- | --- | --- | --- |
| 5.1 Processor Datapath | R89 project 5; B7 ch. 5; B46 ch. 23 | partial | Label OEE's PC, accumulator, instruction decoder, ALU, Z flag, RAM and device interfaces; Hack is not this machine. |
| 5.2 Clock and Control | B46 ch. 18, 23; R89 project 5; R93 | partial | Explicitly distinguish OEE's atomic instruction transition from real clock and propagation behavior. |
| 5.3 Fetch and Decode | R89 project 5; B7 ch. 5; B46 ch. 23 | partial | OEE's instructions are two bytes and require even PC; do not transplant Hack's instruction encoding. |
| 5.4 Execute and Commit | R89 project 5; B7 ch. 5; B46 ch. 23 | partial | OEE computes full next state and commits atomically; faults must preserve PC/register/RAM/device state. |

### Module 6 — Instructions and Programs

Outcome coverage: SEF1-O5.

| OEE lesson | Verified-section / optional resource suggestions | Support | OEE-specific adaptation / gap |
| --- | --- | --- | --- |
| 6.1 Instruction Encoding | R89 project 4; B7 ch. 4; B1 “Instructions” | partial | Use OEE's exact 2-byte opcodes, operand rules and even-aligned addresses, not Hack assembler syntax. |
| 6.2 Data Movement | R89 project 4; B7 ch. 4; B1 “The Load and Store Instructions” | partial | Respect OEE's LOAD/STORE permitted RAM and device addresses, device direction, and errors. |
| 6.3 Arithmetic Instructions | R89 project 4; B1 “The Arithmetic or Logic Instruction”; B46 ch. 24 | partial | Translate only the concept: OEE's LDI, ADDI, ANDI and Z-flag semantics are separate. |
| 6.4 Branches and Flags | R89 project 4; B46 ch. 24; B1 “Another Way to Jump” | partial | OEE's taken JZ validates target; untaken JZ ignores operand and advances PC by two. |
| 6.5 Program Tracing | R89 projects 4–5; B7 ch. 4–5; B46 ch. 24 | partial | Hand-encode and trace the exact eight-bit OEE program, with PC/A/Z and memory/device effects. |
| 6.6 Invalid Instructions | OEE SEF1 reference-machine and AS3 requirements (canonical source); R93 is only an optional diagramming aid | source-only | No checked external source implements OEE's illegal address, unsupported opcode, uninitialized fetch and atomic fault rules. |

### Module 7 — Devices and Boot

Outcome coverage: SEF1-O6, SEF1-O5.

| OEE lesson | Verified-section / optional resource suggestions | Support | OEE-specific adaptation / gap |
| --- | --- | --- | --- |
| 7.1 Memory-Mapped I/O | R89 project 5 (Screen/Keyboard); B7 ch. 5; B46 ch. 25 | partial | OEE uses display latch 0xF0 and keyboard latch 0xF1, not Hack's screen RAM model. |
| 7.2 Input and Output | R89 project 5; B46 ch. 25; B1 “The Keyboard”, “The Display Screen” | partial | Show read-only initialized input and write-only display-latch behavior and device faults. |
| 7.3 Polling and Interrupts | R96 ch. 20 §§20.5–20.7 (“Modes of Data Transfer”, “Programmed I/O”, “Interrupt-initiated I/O”); B46 ch. 25 | partial | A free chapter directly contrasts busy-wait polling and device interrupts. The OEE eight-bit machine implements no interrupts: explain conceptual differences, not an invented instruction or interrupt controller. |
| 7.4 Storage and Files | B4 (OSTEP ch. 36, 39–40); B1 “The Disk”, “The File System”; B46 ch. 26 | partial | Keep persistent bytes and filesystem abstractions distinct from RAM and the OEE simulator; OSTEP is deeper than required. |
| 7.5 Firmware and Boot | R94 (Microsoft Learn “PreBoot”, “Boot Manager”, “OS Loader”); B1 “Firmware”, “Boots” | partial | Microsoft's PC/Windows boot chain is one real example, not OEE's educational image initialization or a universal platform. |
| 7.6 Hardware and Software | B4 (OSTEP introduction/ch. 2); B46 ch. 25–26; B1 “Hardware and Software” | partial | Distinguish physical CPU/device, driver, OS and application boundaries; do not imply the OEE emulator runs an OS. |

### Module 8 — Computer System Integration

Outcome coverage: SEF1-O5, SEF1-O6, SEF1-O7. Relevant summative requirement: SEF1-AS3 (with Modules 5–7).

| OEE lesson | Verified-section / optional resource suggestions | Support | OEE-specific adaptation / gap |
| --- | --- | --- | --- |
| 8.1 System Connections | R89 project 5 (Computer, CPU, Memory); B7 ch. 5; R93 | partial | Integrate the earlier verified eight-bit gates/ALU/registers with OEE's PC/decode/RAM/device model, not Hack chip sizes. |
| 8.2 Program-to-Output Trace | R89 projects 4–5 (concept); B1 “Step by Step”, “The Outside World” | partial | Only OEE defines the required exact byte sequence, reset values, taken/untaken JZ and display effects. |
| 8.3 Fault Diagnosis | R93 (inspectable simulations); R89 project 5 (test comparisons); OEE SEF1 AS3 | partial | Generate OEE-specific independent expected traces and fault reproduction; a passing Hack comparison is insufficient. |
| 8.4 Model Boundaries | B46 ch. 25–26; B4 (OSTEP ch. 2, 36); OEE SEF1 model exclusions | partial | Explain missing interrupts, pipelines, OS, MMU, caches, real voltage/timing and boot behavior, rather than equating the model with hardware. |

## Resource identity and access review

- B1 = *But How Do It Know?* (2009), historical private Content per-section reference; Open Library 2009 contents verified; **book text not independently read** (review-needed).
- B7 = *The Elements of Computing Systems*, 2nd edition (MIT Press, 2021); publisher chapters 1–5 and official Nand to Tetris projects (verified section/project identities).
- B46 = *Code*, 2nd edition (Pearson/Microsoft Press, 2022); publisher confirms chapters 1–28; **only contents/topical fit verified, not full prose** (review-needed).
- R89 = Nand to Tetris original Project 1–5 guidelines and simulator; Chapter 1 logic, 2 arithmetic, 3 memory, 4 machine language, 5 architecture.
- R90 = NandGame (free optional introductory puzzle, not an OEE evaluator).
- R91 = Canterbury CS Field Guide, “Numbers” and “Text” (free educational content).
- R92 = All About Circuits Digital Circuits textbook (free; chapter/section titles checked).
- R93 = Logisim-evolution (free open-source simulator; teaching aid, not a textbook or OEE grader).
- B4 = OSTEP, free online ch. 2, 36, 39–40; deeper context, not an introductory device simulator.
- R94 = Microsoft Learn Windows boot phases; Windows-specific illustration, not universal firmware specification.
- R95 = Computer History Museum timeline; dated evidence for switching/transistor/stored-program history.

### Additional free resource descriptions

- [R92 All About Circuits digital circuits](https://www.allaboutcircuits.com/textbook/digital/): chapters 1 (Numeration Systems), 2 (Binary Arithmetic), 3 (Logic Gates), 7 (Boolean Algebra), 10 (Multivibrators) and 15 (Digital Storage). The chapter indexes name the actual public navigation headings; never prescribe an unexplained paid component.
- [R93 Logisim-evolution](https://github.com/logisim-evolution/logisim-evolution): inspectable gates, registers, memory and signals on Windows/macOS/Linux. Official README states Java 21+ for JAR use; choose an appropriately packaged version. There is no OEE circuit auto-conversion or grader.
- [B4 OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/): free introduction and selected I/O / files / directories chapter material. It is **not** the OEE teaching machine or a beginner's gate-construction manual.
- [R94 Microsoft Learn boot phases](https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/windows-boot-issues-troubleshooting): “PreBoot”, “Boot Manager”, “OS Loader” and “Kernel”; a specific Windows PC case study only.
- [R95 Computer History Museum timeline](https://www.computerhistory.org/timeline/): historical anchor for EDSAC, stored programs and switching technologies; additional [silicon-engine timeline](https://www.computerhistory.org/siliconengine/timeline/) supports 1947 transistor history.
- [R96 The Open Book Project, Input-Output Interface and Modes of Transfer](https://open-book-project.github.io/courses/csa_course/io-interface-and-modes-of-transfer.html): free Chapter 20, especially §§20.5–20.7, compares programmed/polled I/O with interrupt-driven I/O. It is a conceptual supplement only; no OEE interrupt emulator is supplied.
- [Code's free companion animations](https://www.codehiddenlanguage.com/Chapter00/) supplement B46's diagrams. The site explicitly says it is **not** a replacement for the book's written explanations; do not count it as a complete free textbook. Catalogue publication is not required to access this optional link.

## Assessment-boundary review

| OEE summative | Relevant mapping | Why external activity is not equivalent |
| --- | --- | --- |
| `SEF1-AS1` | Modules 1–2, O1/O2; encoding and NAND-derived gates | A book's solutions or supplied Hack truth-table tests do not establish the required independently justified eight-bit analysis and inspectable gates. |
| `SEF1-AS2` | Modules 3–4, O3/O4; enabled registers, four 8-bit RAM cells, adders, ALU and faults | Hack's 16-bit RAM/ALU cannot substitute for the defined eight-bit, clock/write-enable, modulo-256 and zero-selected-result checks. |
| `SEF1-AS3` | Modules 5–8, O5/O6/O7; exact bytes and device trace | No identified outside project implements the OEE two-byte ISA, initialized program boundaries, atomic faults, `Z` and `0xF0`/`0xF1` semantics. OEE's source contract is required. |

## Before approving an active resource map

1. Review the research links and the actual text of optional books (B1/B46) before claiming independent section **content** validation. Verify B3's physical/local edition separately if used. Preserve OEE's explicit no-interrupt-model boundary when using the free R96 polling-vs-interrupt comparison; retain the separate OEE-specific invalid-instruction gap as source-only.
2. Verify the published [Toolkit `0.1.0`](https://github.com/0xbuffdev/open-engineering-education/releases/tag/toolkit-v0.1.0) and signed [curriculum `2026.11.1`](https://github.com/0xbuffdev/open-engineering-education/releases/tag/curriculum-2026.11.1) against the [approved lock and signing-key trust reference](../../docs/OEE-RELEASE-TRUST.md). Use the independent fingerprint and published digest. A disposable CI signature cannot authorize a learner release.
3. Obtain the signed release's actual SEF1 Toolkit exportVersion 2 and its `releaseId`, `manifestSha256` and `courseSha256`. Compare all **41 lesson positions/titles and source scopes**, including the three assessments, against this research. Any changed course digest needs an explicit editorial review even if the headings look identical.
4. Only then add an active `resources/mappings/SEF/SEF1.json` using **existing schemaVersion 3** (no parallel schema), per-module/optional per-lesson entries, supported part selectors (`chapters`, `projects`, `section-titles`, `topics`, `section-range`) and documented `gap` for partial/unmapped sections. Mark `reviewed` only after approval. Generate a learner reading plan with the existing renderer; ensure all optional paid readings have free alternatives. Never overwrite user-created files or repin existing evidence.
5. Continue SEF in [OEE's authoritative prerequisite-valid study order](https://github.com/0xbuffdev/open-engineering-education/blob/main/curriculum/SEF/README.md), with independent editorial source reviews and specific release-bound resource maps. Do not derive order from numeric codes alone.

**References:** [source OEE SEF1](https://github.com/0xbuffdev/open-engineering-education/blob/216553f10d20ed5fcb40dda46a147c68d7895555/curriculum/SEF/SEF1.md), [Workspace v3 resource schema](../schemas/course-map.schema.json), [earlier SEF1 source review](SEF1-REVIEW.md), [tracking issue #18](https://github.com/0xbuffdev/oee-workspace/issues/18).
