# PREAUDIT0_03 — PROPOSED TEXT CHANGES
Grouped by artifact. Original → proposed. (Terminology-only; implementation deferred until review.)

## Shiny app — modules
- mod_omic.R: `53 canonical entities` → `53 RCD-related entities`
- mod_omic.R: `The canonical regulated cell death entity (one of 53)…` → `The RCD-related entity (one of 53)…`
- mod_omic.R: `Canonical RCD entity (one of 53).` → `RCD-related entity (one of 53).`
- mod_board.R: `53 canonical entities with operational definitions…` → `53 canonicalized RCD-related entities with operational definitions…`
- mod_board.R: `Canonical RCD entity name (53 canonical entities)` → `Canonicalized RCD-related entity name (53 entities)`
- mod_board.R: `Canonical RCD entity queried` → `RCD-related entity queried`
- mod_board.R: `not in the RCDome database (53 canonical entities).` → `not in the RCDome database (53 RCD-related entities).`
- mod_rcd_grid.R: `not in the RCDome database (53 canonical entities).` → `not in the RCDome database (53 RCD-related entities).`
- mod_od.R: `Browse the 53 canonical RCD entities and…` → `Browse the 53 canonicalized RCD-related entities and…`
- mod_network.R: `legacy form → canonical entity` → `legacy form → normalized entity`
- server.R: `No canonical pathway data available.` → `No RCD entity data available.`

## Shiny app — www pages
- landing_page.html: `53 canonical entities` → `53 RCD-related entities`
- dome_prototype.html: `53 canonical entities` → `53 RCD-related entities`
- detail_page_wireframe.html: `Canonical RCD form name.` → `RCD-related entity name.`
- detail_page_wireframe.html: `${entityNames.length} canonical entities` → `${entityNames.length} RCD-related entities`

## Board
- RCD_Board_DeepSeek_Prompt.md: `53 canonical RCD entities` → `53 canonicalized RCD-related entities`
- Example…BAX_Apoptosis.html: `canonical regulated cell death entity` → `RCD-related entity`
- Example…RIPK3_Pyroptosis_negative.html: `canonical regulated cell death modality` → `bona fide RCD modality` (AMB — confirm biologically)

## Decoder / governance
- MandM_operational_definitions.md: `The RCDome canon comprises 53 canonical RCD entities` → `The RCDome controlled vocabulary comprises 53 canonicalized RCD-related entities`
- Results_OD_census.md: `53 canonical RCD entities` → `53 canonicalized RCD-related entities`
- build_variable_descriptor.py: `Canonical RCD form name` / `Canonical RCD entity name (53 entities…)` → `Canonicalized RCD-related entity name (53 entities)` (regenerates supplementary Variable Descriptor)

## Docs
- RCDome_Traceability_Contract.md: `Canonical RCD forms | 53` → `Canonicalized RCD-related entities | 53`
- RCDome_Gene_Traceability_Spec.md: `CANONICAL RCD FORM NAMES` → `CANONICALIZED RCD-RELATED ENTITY NAMES`
- RCDome_Video_Layer/*.md: `canonical RCD form` → `RCD-related entity`

## Deliberately NOT changed
- `rcd_form_canonical` and all internal identifiers (schema/code).
- Biological "canonical apoptosis/autophagy/inflammasome/ferroptosis/gene set/signaling".
- Verbatim PMID titles.
- Third-party MapLibre "CanonicalTileID".
- `docs/reply_to_Higor_5level.md` (historical decision record).

## Version reconciliation (not a terminology patch)
- `docs/RCDome_manuscript.md` — obsolete draft ("54 canonical RCD forms", 9,252 genes). Mark superseded; align to V026 (53 entities, 9,265 genes, 21,568 pairs). Deferred.

## ADDENDUM — manuscript + supplementary (docx/xlsx) proposed changes

### Manuscript (governance docx)
- "establishment of a canonical RCD form vocabulary" → "establishment of a canonicalized RCD-related entity vocabulary"
- "Establishment of the Canonical RCD Form Vocabulary" → "Establishment of the Canonicalized RCD-Related Entity Vocabulary"
- "The RCDome canon comprises 53 canonical RCD entities" → "The RCDome controlled vocabulary comprises 53 canonicalized RCD-related entities"
- "The canonical vocabulary is fixed" → "The controlled vocabulary is fixed"
- "a non-canonical entity is marked retired" → "an entity outside the controlled vocabulary is marked retired"
- "searching each entity by its canonical name" → "searching each entity by its normalized name"
- "20 canonical database identifiers" → "20 controlled database identifiers"
- "53 canonical forms" (recurring) → "53 RCD-related entities"
- "the canonical name (rcd_form_canonical)" → "the normalized name (rcd_form_canonical)"
- "in their canonical form" → "in their normalized form"
- "(gene, canonical RCD form) pairs" → "(gene, RCD-related entity) pairs"
- "complete canonical list of 53 RCD-related entities" → "complete list of 53 RCD-related entities"
- "53-entity canonical vocabulary" → "53-entity controlled vocabulary"
- "53 canonical RCD-related entities" (recurring) → "53 RCD-related entities"
- "53 canonical entities" (recurring) → "53 RCD-related entities"
- "53 canonical RCD entities" (recurring) → "53 canonicalized RCD-related entities"
- "Figure 4 … 53 canonical RCD entities" → "… 53 RCD-related entities"
- KEEP: "canonical gene sets", "canonical RCD modalities" (or "bona fide RCD modalities"), "canonical executors".

### Supplementary information docx
- "by canonical name or its stem" → "by normalized name or its stem"

### Supplementary tables xlsx
- INDEX: "Canonical RCD Form Vocabulary (53 Forms)" → "Canonicalized RCD-Related Entity Vocabulary (53 Entities)"
- INDEX: "New Canonical Forms Added (Phase 2)" → "New Entities Added (Phase 2)"
- Variable Descriptor: "Canonical RCD form name" / "Canonical RCD entity name (53 canonical entities)" / "Canonical RCD entity name" → "Canonicalized RCD-related entity name"
- Variable Descriptor: "Canonical Name" → "Normalized Name"; "Q10: canonical name accuracy" → "Q10: normalized name accuracy"
- Table S5: "Canonical Name" → "Normalized Name"
- Table S9: "53 canonical (all forms)" → "53 normalized (all entities)"; "62 original -> 53 canonical" → "62 original -> 53 normalized"
- Matrix Descriptor: "The normalized canonical RCD form name (one of 53 canonical forms)" → "The normalized RCD-related entity name (one of 53 entities)"
- Matrix Descriptor: "The canonical RCDome operational definition" → "The RCDome operational definition"; "53 canonical forms" → "53 entities"
- KEEP: Table S4 "delta like canonical Notch ligand" (HGNC gene names); Matrix Descriptor "rcd_form_canonical" (schema).
- DEFER: Table S11 provenance "canonical concept name / label / mechanism" (ontological judgment).
