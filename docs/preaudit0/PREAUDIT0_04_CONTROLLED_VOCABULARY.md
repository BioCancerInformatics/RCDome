# PREAUDIT0_04 — CONTROLLED VOCABULARY
RCDome terminology policy (governs the subsequent 53-entity adjudication and all future writing).

## 1. canonicalized RCD-related entity
- PREFERRED USE: an entity whose heterogeneous source terminology has been normalized/consolidated into the RCDome controlled vocabulary.
- ALLOWED CONTEXT: when the normalization history matters ("53 canonicalized RCD-related entities", "the decoder lists the canonicalized RCD-related entity names").
- AVOID WHEN: the sentence is purely about the set, not about how it was built — then use "RCD-related entity".
- EXAMPLE: "The 53 canonicalized RCD-related entities span five ontological levels."

## 2. RCD-related entity
- PREFERRED USE: the neutral default for any entity represented in the RCDome evidence atlas.
- ALLOWED CONTEXT: stats, UI labels, tooltips, module descriptions, not-found messages.
- AVOID WHEN: a biological modality claim is intended.
- EXAMPLE: "53 RCD-related entities · 9,265 genes · 21,568 associations."

## 3. RCDome entity
- PREFERRED USE: internal/UI shorthand when "RCDome" ownership is relevant.
- ALLOWED CONTEXT: app interface labels.
- AVOID WHEN: formal manuscript prose (prefer "RCD-related entity" or "canonicalized RCD-related entity").
- EXAMPLE: "Select an RCDome entity to explore."

## 4. RCD form
- PREFERRED USE: a named regulated-cell-death form in the source literature/databases; NOT a synonym for "entity" or "modality".
- ALLOWED CONTEXT: historical/source terminology, database extraction descriptions.
- AVOID WHEN: describing the current controlled-vocabulary members collectively ("53 forms") — use "RCD-related entities".
- EXAMPLE: "FerrDB names 22 RCD forms; these map onto the RCDome controlled vocabulary."

## 5. bona fide RCD modality
- PREFERRED USE: an entity that satisfies the RCDome mechanistic admission criteria/hard gates for modality status.
- ALLOWED CONTEXT: only where the L1/hard-gate adjudication supports it.
- AVOID WHEN: the entity has not passed the gates or is being referred to generically.
- EXAMPLE: "Apoptosis is a bona fide RCD modality with conserved executioner machinery."

## 6. canonical / established RCD modality
- PREFERRED USE: a biological claim that consensus and mechanistic evidence genuinely support.
- ALLOWED CONTEXT: discussion of consensus forms (e.g., the NCCD modalities).
- AVOID WHEN: merely meaning "in the RCDome controlled vocabulary".
- EXAMPLE: "The NCCD recognizes 12 canonical RCD modalities."

## 7. gene–RCD association
- PREFERRED USE: the raw evidence relationship recorded in the matrix (one gene × one RCD-related entity, with tier/role/direction/class).
- ALLOWED CONTEXT: counts, filters, exports, figures.
- AVOID WHEN: implying causality.
- EXAMPLE: "21,568 gene–RCD associations across 53 entities."

## 8. mechanistically validated gene–RCD relationship
- PREFERRED USE: only for relationships whose mechanistic class and evidence support a mechanistic link (e.g., MECHANISTIC with EXECUTOR role).
- ALLOWED CONTEXT: Board synthesis, results interpretation.
- AVOID WHEN: the relationship is CO_OCCURRENCE / DATABASE_ONLY / INSUFFICIENT_DATA.
- EXAMPLE: "BAX–Apoptosis is a mechanistically validated relationship (EXECUTOR · PROMOTES · T1)."

## Governing rule
**Canonicalized vocabulary membership ≠ biological canonicality.**
"In the RCDome controlled vocabulary" is a statement about provenance and normalization, never about biological endorsement.
