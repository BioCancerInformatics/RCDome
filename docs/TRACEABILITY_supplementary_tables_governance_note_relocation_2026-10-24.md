# TRACEABILITY — Supplementary Tables: MC-vs-RS governance note relocation (2026-10-24)

## Context
During the supplementary-tables format/content audit, a stray row was found in the **Variable Descriptor** sheet:

> `GOVERNANCE | MC vs RS vocabularies | MC1–MC5 (Galluzzi modality criteria…) and RS1–RS6 + S (Rodrigues ranking score) are distinct, non-interchangeable vocabularies. MC is never used for ranking scores; RS is never used for modality criteria.`

## Finding
- The Variable Descriptor sheet maps `Table → column → short descriptor` (S1–S15 columns only).
- `GOVERNANCE` is **not** a table — the row was a governance note, misplaced inside the **S12 descriptor block** (between `S` and `parent`).
- It was an **extra insertion, not a replacement**: all **28 S12 descriptors** were verified intact (`entity → … → rationale`).
- The note appeared **nowhere else** in the workbook (other "MC" hits were gene symbols like `MC1R`, or the word "governance" in script names).

## Decision
**Relocate** the note to a **footnote under Table S12** (where MC vs RS context is relevant), rather than deleting it (the note is accurate and useful).

## Action
1. Removed the `GOVERNANCE` row from **Variable Descriptor** (S12 block restored to `S → parent → relationship_type`).
2. Added the note as a footnote in **Table S12** (`A58`), prefixed `Note:`.
3. Propagated byte-for-byte (`cp`, no re-serialization) to:
   - `manuscript_V027/RCDome_manuscript_V027_supplementary_tables.xlsx`
   - `RCDome_distribution/manuscript/RCDome_manuscript_V027_supplementary_tables.xlsx`
   - `RCDome_GitHub/RCDome_github/RCDome_manuscript_V027_supplementary_tables.xlsx`
   - `RCDome_GitHub/RCDome_github/docs/supplementary/RCDome_manuscript_V027_supplementary_tables.xlsx`
4. Rebuilt `RCDome_V027_distribution.zip` (validation `ok: TRUE`) and synced to `Submission FAI/`.
5. GitHub: committed `078dd7f`, pushed to `main`.

## Final state
- Variable Descriptor: **0** `GOVERNANCE` rows; S12 block continuous.
- Table S12: footnote present under the 53 entities.
- All copies md5-identical: `7eb146061cfb73c0ad97fed3ba94dc0d`.
