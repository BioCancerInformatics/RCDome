# Manuscript terminology-clarification — traceability report

Task: explicit distinction "canonical" vs "canonicalized" vs biological modality status (V026 governance manuscript).

## Modifications (4)

| # | Section | Original | Revised | Reason | Category | Downstream sync |
|---|---|---|---|---|---|---|
| 1 | Methods — "Establishment of the Canonicalized RCD-Related Entity Vocabulary" | *(no formal definition)* | "Throughout RCDome, 'canonicalized' refers exclusively to vocabulary normalization … Biological and ontological status is evaluated independently through the RCDome evidence and hard-gate framework." | establish the semantic firewall at first substantive use | vocabulary normalization | none (prose only) |
| 2 | Methods — "Operational definitions of RCD entities" | "…comprises 53 canonicalized RCD-related entities, derived from…" | "…comprises 53 canonicalized RCD-related entities, **where 'canonicalized' denotes normalization to a preferred RCDome vocabulary identifier rather than recognition as a canonical or established RCD modality**; it is derived from…" | self-contained reinforcement | vocabulary normalization | none |
| 3 | Results — "The RCDome Compendium Composition" | "The final vocabulary comprises 53 RCD-related entities organized into five ontological levels:" | "The final canonicalized vocabulary comprises 53 RCD-related entities spanning five ontological levels; **importantly, canonicalization denotes vocabulary normalization and does not confer modality status, and only 16 of the 53 entities satisfy the G0–G6 hard-gate criteria for classification as bona fide RCD modalities.** The 53 entities are organized into:" | biological consequence of the distinction | bona fide modality | none |
| 4 | Channel D (Methods) | "…extract **canonical gene sets**." | "…extract **reference gene sets**." | the gene sets are the discovery-paper reference collections, not a claim of biological canonicality | neutral/reference | none |

## Preserved (unchanged, as instructed)

- Discussion ¶358 — the existing heterogeneity clarification (hypersensitive response, linker cell-type death, eryptosis, cornification, necrosis, oncosis, metalloptosis, …).
- Phase 2A gene-association validation vs modality-status adjudication distinction.
- Figure 1 normalization logic; Figure 4 "53 canonicalized RCD-related entities".
- Legitimate biological "canonical": "canonical executors" (kept).

## Database field decision — `rcd_form_canonical`

**Decision: KEEP as legacy field name. Do NOT rename.**

- The field is frozen in the production schema (matrix 71 columns; CSV + RDS; `global.R`; all app modules; scripts; archived outputs).
- Renaming to `rcd_entity_normalized` would break reproducibility, code, the Shiny app, and archived matrices.
- **Documentation:** `rcd_form_canonical` is a legacy/informatics field name denoting the **normalized vocabulary identifier**, NOT biological canonicality. This note is to be carried in the Matrix Descriptor / Variable Descriptor.

## Residual "canonical" after this task

Pre-Audit 0 re-check: the only remaining bare "canonical" occurrences are the **intentional semantic-firewall uses** introduced by this task (the formal definition itself), plus the preserved biological/schema uses ("canonical executors", `rcd_form_canonical`). No unintended vocabulary-normalization "canonical" remains.

## Final consistency check (reader's view)

The manuscript now makes it explicit that RCDome consolidates heterogeneous source terminology into a controlled vocabulary of **53 canonicalized RCD-related entities**, that biological/ontological status is adjudicated independently, and that **only 16 of 53** satisfy G0–G6 for classification as **bona fide RCD modalities**.
