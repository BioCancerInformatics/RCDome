# PREAUDIT0_07 — CHANGELOG
Findings separated into four classes.

## A. Safe terminology-only changes (no scientific-meaning change)
- "53 canonical entities" → "53 RCD-related entities" (app stats, landing, dome).
- "Canonical RCD entity queried/name" → "RCD-related entity queried" / "canonicalized RCD-related entity name" (Board payload).
- "Canonical RCD form name" → "RCD-related entity name" (gene detail tooltip).
- "legacy form → canonical entity" → "legacy form → normalized entity" (Network edge tooltip).
- "No canonical pathway data available." → "No RCD entity data available." (server.R).
- Decoder/docs "53 canonical RCD entities" → "53 canonicalized RCD-related entities".

## B. Terminology changes requiring author confirmation
- Board example RIPK3–Pyroptosis: "canonical regulated cell death modality" → "bona fide RCD modality" (biological claim — confirm).
- mod_od.R L1 legend "canonical cell-death forms" — keep as biological, or replace with "bona fide modalities" (confirm).
- build_variable_descriptor.py regeneration (supplementary Variable Descriptor) — confirm before regenerating the shipped workbook.

## C. Potentially semantic changes (must NOT be applied blindly)
- `docs/RCDome_manuscript.md` "54 canonical RCD forms" — V025 draft ARCHIVED (preserved); truth = V026. Versioning, not a word swap.
- Any change that would alter the stated counts (53/54, 9,252/9,265, 24,834/22,473).

## D. Deferred biological/ontological issues (not touched)
- Vacuolar cell death adjudication.
- Modality count reconciliation (16 vs 39).
- Entity label vs biological status for ambiguous entities (Autophagy, Necrosis, Cellular senescence, …).
- 54→53 version history.

## Implementation gate
No authoritative file was modified during Pre-Audit 0.
Implementation begins only after author review of A and B, and after the 53-entity audit resolves D.
