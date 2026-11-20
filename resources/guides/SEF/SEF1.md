# SEF1 — Resource study guide

> Reviewed resource guidance · [Canonical OEE course](https://github.com/0xbuffdev/open-engineering-education/blob/67416343f3eab17ada5d3c79ae6cc782524c29ff/curriculum/SEF/SEF1.md)

This is a non-normative study aid. OEE defines the required outcomes, assessments, and labs. No book purchase is required. Check verification labels before following chapter references.

**Curriculum revision:** 67416343f3eab17ada5d3c79ae6cc782524c29ff

**Map status:** Reviewed

## Module 1 — Bits and Representation

**Coverage:** Partial

**Outstanding:** Confirmed sections introduce binary values and character encodings but do not independently cover OEE's address-versus-value distinction, historical switching devices or physical voltage/noise assumptions. Follow the canonical course for those topics.

- **R91 — Computer Science Field Guide — Data Representation** — Sections “Numbers”, “Text”.
  - Role: Optional · Mapping verification: Verified
  - Study purpose: Use the free interactive explanations to compare bit patterns, binary/decimal/hexadecimal values and character encodings; distinguish a byte pattern from its interpretation.
  - Access: Free — [Official source](https://www.csfieldguide.org.nz/en/chapters/data-representation/)
  - [Catalogue record](https://github.com/0xbuffdev/oee-workspace/blob/main/resources/catalog/online/R91.json)

## Module 2 — Logic Gates

**Coverage:** Mapped

- **R89 — Nand to Tetris — Official Projects** — Project 1.
  - Role: Optional · Mapping verification: Verified
  - Study purpose: Official free Boolean Logic project supplies NAND-based gate building and truth-table checks; adapt the examples to OEE's own gate criteria instead of submitting this external project as evidence.
  - Access: Free — [Official source](https://www.nand2tetris.org/course)
  - [Catalogue record](https://github.com/0xbuffdev/oee-workspace/blob/main/resources/catalog/online/R89.json)

- **B7 — The Elements of Computing Systems** — Chapter 1.
  - Role: Optional · Mapping verification: Verified
  - Study purpose: Optional second-edition Boolean Logic chapter, if legally available; not necessary to complete the free project or OEE module.
  - Access: Mixed — [Official source](https://mitpress.mit.edu/9780262539807/the-elements-of-computing-systems/) · [Free companion materials](https://www.nand2tetris.org/)
  - [Catalogue record](https://github.com/0xbuffdev/oee-workspace/blob/main/resources/catalog/books/B7.json)

## Module 3 — Registers and Memory

**Coverage:** Partial

**Outstanding:** Official project uses Hack's 16-bit registers and large RAM hierarchy, not OEE's four-cell eight-bit store. Its sequential-logic work does not independently teach OEE's bus contention, clock-edge and reset convention checks. Adapt explicitly.

- **R89 — Nand to Tetris — Official Projects** — Project 3.
  - Role: Optional · Mapping verification: Verified
  - Study purpose: Free Memory project covers clocked state, enabled writes, registers and addressable RAM; compare its architecture against the OEE eight-bit model.
  - Access: Free — [Official source](https://www.nand2tetris.org/course)
  - [Catalogue record](https://github.com/0xbuffdev/oee-workspace/blob/main/resources/catalog/online/R89.json)

- **B7 — The Elements of Computing Systems** — Chapter 3.
  - Role: Optional · Mapping verification: Verified
  - Study purpose: Optional second-edition Memory chapter for register and address-selection theory; use OEE for the assessed four-cell semantics.
  - Access: Mixed — [Official source](https://mitpress.mit.edu/9780262539807/the-elements-of-computing-systems/) · [Free companion materials](https://www.nand2tetris.org/)
  - [Catalogue record](https://github.com/0xbuffdev/oee-workspace/blob/main/resources/catalog/books/B7.json)

## Module 4 — Arithmetic and ALU

**Coverage:** Partial

**Outstanding:** Official materials implement the 16-bit Hack adders/ALU, not OEE's eight-bit carry chain, modulo-256 behavior and selected-result zero detector. These OEE-specific checks remain to be practiced independently.

- **R89 — Nand to Tetris — Official Projects** — Project 2.
  - Role: Optional · Mapping verification: Verified
  - Study purpose: Free Boolean Arithmetic project supplies half/full adder and ALU construction examples; reason explicitly about width and zero detection differences.
  - Access: Free — [Official source](https://www.nand2tetris.org/course)
  - [Catalogue record](https://github.com/0xbuffdev/oee-workspace/blob/main/resources/catalog/online/R89.json)

- **B7 — The Elements of Computing Systems** — Chapter 2.
  - Role: Optional · Mapping verification: Verified
  - Study purpose: Optional second-edition Boolean Arithmetic chapter; derive the OEE eight-bit oracle independently rather than copying the Hack ALU.
  - Access: Mixed — [Official source](https://mitpress.mit.edu/9780262539807/the-elements-of-computing-systems/) · [Free companion materials](https://www.nand2tetris.org/)
  - [Catalogue record](https://github.com/0xbuffdev/oee-workspace/blob/main/resources/catalog/books/B7.json)

## Module 5 — Processor Execution

**Coverage:** Partial

**Outstanding:** Project 5 uses a different Hack datapath and instruction encoding. It does not establish the OEE two-byte fetch, atomic state commit or fault-state semantics. Use the canonical OEE machine for those investigations.

- **R89 — Nand to Tetris — Official Projects** — Project 5.
  - Role: Optional · Mapping verification: Verified
  - Study purpose: Free Computer Architecture project illustrates how CPU, ALU and memory connect; inspect differences from OEE's reference machine.
  - Access: Free — [Official source](https://www.nand2tetris.org/course)
  - [Catalogue record](https://github.com/0xbuffdev/oee-workspace/blob/main/resources/catalog/online/R89.json)

- **B7 — The Elements of Computing Systems** — Chapter 5.
  - Role: Optional · Mapping verification: Verified
  - Study purpose: Optional second-edition Computer Architecture chapter for broader processor and memory organization.
  - Access: Mixed — [Official source](https://mitpress.mit.edu/9780262539807/the-elements-of-computing-systems/) · [Free companion materials](https://www.nand2tetris.org/)
  - [Catalogue record](https://github.com/0xbuffdev/oee-workspace/blob/main/resources/catalog/books/B7.json)

## Module 6 — Instructions and Programs

**Coverage:** Partial

**Outstanding:** Project 4 uses Hack assembly and machine language, not OEE's two-byte aligned opcodes, ADDI/ANDI, conditional JZ or illegal-address behavior. Do not reuse Hack branch traces as OEE answers.

- **R89 — Nand to Tetris — Official Projects** — Project 4.
  - Role: Optional · Mapping verification: Verified
  - Study purpose: Free Machine Language project shows instruction encoding and low-level program tracing in a separate architecture.
  - Access: Free — [Official source](https://www.nand2tetris.org/course)
  - [Catalogue record](https://github.com/0xbuffdev/oee-workspace/blob/main/resources/catalog/online/R89.json)

- **B7 — The Elements of Computing Systems** — Chapter 4.
  - Role: Optional · Mapping verification: Verified
  - Study purpose: Optional second-edition Machine Language chapter for instruction/data distinctions and example machine programs.
  - Access: Mixed — [Official source](https://mitpress.mit.edu/9780262539807/the-elements-of-computing-systems/) · [Free companion materials](https://www.nand2tetris.org/)
  - [Catalogue record](https://github.com/0xbuffdev/oee-workspace/blob/main/resources/catalog/books/B7.json)

## Module 7 — Devices and Boot

**Coverage:** Partial

**Outstanding:** Computer Architecture project demonstrates memory-mapped screen/keyboard but does not explain OEE's firmware, bootloader, persistent storage/file-system boundary or polling-versus-interrupt distinctions. Those require additional independent sources.

- **R89 — Nand to Tetris — Official Projects** — Project 5.
  - Role: Optional · Mapping verification: Verified
  - Study purpose: Inspect the free project's memory-mapped I/O design as an alternative architecture; verify OEE's device-latch behavior from its own specification.
  - Access: Free — [Official source](https://www.nand2tetris.org/course)
  - [Catalogue record](https://github.com/0xbuffdev/oee-workspace/blob/main/resources/catalog/online/R89.json)

- **B7 — The Elements of Computing Systems** — Chapter 5.
  - Role: Optional · Mapping verification: Verified
  - Study purpose: Optional context for the Hack memory-mapped device interface; not an explanation of real boot or operating-system startup.
  - Access: Mixed — [Official source](https://mitpress.mit.edu/9780262539807/the-elements-of-computing-systems/) · [Free companion materials](https://www.nand2tetris.org/)
  - [Catalogue record](https://github.com/0xbuffdev/oee-workspace/blob/main/resources/catalog/books/B7.json)

## Module 8 — Computer System Integration

**Coverage:** Partial

**Outstanding:** Project 5 integrates Hack's 16-bit components, not the OEE eight-bit program-to-output trace or its required fault injection, assumptions and limitations defense. OEE's final integration evidence must use the canonical model.

- **R89 — Nand to Tetris — Official Projects** — Project 5.
  - Role: Optional · Mapping verification: Verified
  - Study purpose: Use the free complete Hack computer project as a comparative system-level integration exercise, not a substitute for the OEE program-to-output investigation.
  - Access: Free — [Official source](https://www.nand2tetris.org/course)
  - [Catalogue record](https://github.com/0xbuffdev/oee-workspace/blob/main/resources/catalog/online/R89.json)

- **B7 — The Elements of Computing Systems** — Chapter 5.
  - Role: Optional · Mapping verification: Verified
  - Study purpose: Optional second-edition architecture overview to compare with OEE's integrated reference machine.
  - Access: Mixed — [Official source](https://mitpress.mit.edu/9780262539807/the-elements-of-computing-systems/) · [Free companion materials](https://www.nand2tetris.org/)
  - [Catalogue record](https://github.com/0xbuffdev/oee-workspace/blob/main/resources/catalog/books/B7.json)

## How to use this guide

Read the canonical OEE module and lesson requirements first. Use these references as supporting explanations and practice, not substitutes for OEE labs or assessment evidence.

A **Partial** module still needs editorial research. A **Review needed** reference may have unconfirmed section titles or edition-specific numbering. Do not assume that a paid book is essential or that an optional project satisfies a required OEE lab.

When using this guide in a personal workspace, record your actual reading, editions and substitutions in the resources.md log. This guide is a versioned snapshot, not a progress log.
