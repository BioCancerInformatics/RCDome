# PREAUDIT0_02 — MASTER OCCURRENCE TABLE
RCDome Pre-Audit 0 · Canonical terminology · Read-only

Legend — classification: VN = VOCABULARY_NORMALIZATION · BC = BIOLOGICAL_CANONICALITY · AMB = AMBIGUOUS · ACC = ACCEPTABLE_AS_WRITTEN.
Severity: CRITICAL / MAJOR / MODERATE / MINOR.
Columns (compact): id · source_file · location · original_text · classification · severity · proposed_text · rationale · author_review.

Bulk occurrences (not enumerated individually):
- Matrix CSVs + gene NCBI CSV (~78,000 lines): repeated schema column `rcd_form_canonical`. classification VN (schema). severity MINOR. proposed: keep column name (pipeline-internal); do not rename. author_review: no (schema).
- SigPolytope.html (~40): MapLibre third-party "CanonicalTileID"/"canonicalize*". ACC. out of scope (external library). author_review: no.
- detail_page_wireframe.html PMID-title dictionary (~60): verbatim published paper titles ("canonical apoptosis", "non-canonical autophagy", "canonical inflammasome"). BC/ACC. external citations. author_review: no.

---

### High-risk user-facing occurrences (VN → revise)

**A1** · Shiny app/RCDome_Atlas/APP/modules/mod_omic.R · stats line
orig: `53 canonical entities`
VN · MAJOR → `53 RCD-related entities`
rationale: vocabulary membership, not biological recognition. author_review: yes.

**A2** · modules/mod_omic.R · gene tooltip
orig: `The canonical regulated cell death entity (one of 53) that this gene is associated with.`
VN · MAJOR → `The RCD-related entity (one of 53) that this gene is associated with.` · author_review: yes.

**A3** · modules/mod_omic.R · tooltip
orig: `Canonical RCD entity (one of 53).`
VN · MAJOR → `RCD-related entity (one of 53).` · author_review: yes.

**A4** · modules/mod_board.R · lede
orig: `53 canonical entities with operational definitions, key molecules, …`
VN · MAJOR → `53 canonicalized RCD-related entities with operational definitions, …` · author_review: yes.

**A5** · modules/mod_board.R · payload label
orig: `Canonical RCD entity name (53 canonical entities)`
VN · MAJOR → `Canonicalized RCD-related entity name (53 entities)` · author_review: yes.

**A6** · modules/mod_board.R · payload label
orig: `Canonical RCD entity queried`
VN · MAJOR → `RCD-related entity queried` · author_review: yes.

**A7** · modules/mod_board.R · not-found notification
orig: `not in the RCDome database (53 canonical entities).`
VN · MAJOR → `not in the RCDome database (53 RCD-related entities).` · author_review: yes.

**A8** · modules/mod_rcd_grid.R · not-found notification
orig: `not in the RCDome database (53 canonical entities).`
VN · MAJOR → `not in the RCDome database (53 RCD-related entities).` · author_review: yes.

**A9** · modules/mod_od.R · lede
orig: `Browse the 53 canonical RCD entities and their curated operational definitions…`
VN · MAJOR → `Browse the 53 canonicalized RCD-related entities and their curated operational definitions…` · author_review: yes.

**A10** · modules/mod_network.R · edge tooltip
orig: `legacy form → canonical entity`
VN · MODERATE → `legacy form → normalized entity` · author_review: yes.

**A11** · server.R · validate message
orig: `No canonical pathway data available.`
VN · MAJOR → `No RCD entity data available.` (also "pathway"→"entity") · author_review: yes.

**A12** · www/landing_page.html · stats
orig: `53 canonical entities`
VN · MAJOR → `53 RCD-related entities` · author_review: yes.

**A13** · www/dome_prototype.html · stats
orig: `53 canonical entities`
VN · MAJOR → `53 RCD-related entities` · author_review: yes.

**A14** · www/detail_page_wireframe.html · table tooltip
orig: `Canonical RCD form name. Click to open the entity detail page.`
VN · MAJOR → `RCD-related entity name. Click to open the entity detail page.` · author_review: yes.

**A15** · www/detail_page_wireframe.html · not-found
orig: `…is not in the RCDome database (${entityNames.length} canonical entities).`
VN · MAJOR → `…is not in the RCDome database (${entityNames.length} RCD-related entities).` · author_review: yes.

---

### Board / Decoder / governance occurrences

**B1** · board/RCD_Board_DeepSeek_Prompt.md
orig: `If the entity is not one of the 53 canonical RCD entities, reply ONLY with…`
VN · MAJOR → `…not one of the 53 canonicalized RCD-related entities…` · author_review: yes.

**B2** · board/RCD_Board_DeepSeek_Prompt.md
orig: `State the category using one of the canonical values, translated into plain prose`
VN · MINOR → ACC (refers to the closed category vocabulary). author_review: no.

**B3** · board/Example_RCDome_Board_BAX_Apoptosis.html
orig: `inclusion as a canonical regulated cell death entity`
VN · MAJOR → `inclusion as a RCD-related entity` · author_review: yes.

**B4** · board/Example_RCDome_Board_RIPK3_Pyroptosis_negative.html
orig: `inclusion as a canonical regulated cell death modality`
AMB · MAJOR → `inclusion as a bona fide RCD modality` (biological claim — confirm with adjudication) · author_review: yes.

**B5** · board/audit_canonical.py (multiple)
orig: `Canonical RCD entity queried` / `canonical count` / `canonical audit`
VN/ACC · MINOR → internal benchmark labels; no user-facing change required. author_review: no.

---

### Decoder / supplementary / docs

**C1** · RCDome Decoder/MandM_operational_definitions.md
orig: `The RCDome canon comprises 53 canonical RCD entities…`
VN · MAJOR → `The RCDome controlled vocabulary comprises 53 canonicalized RCD-related entities…` · author_review: yes.

**C2** · RCDome Decoder/Results_OD_census.md
orig: `The RCDome identified 53 canonical RCD entities…`
VN · MAJOR → `…53 canonicalized RCD-related entities…` · author_review: yes.

**C3** · RCDome Decoder/build_variable_descriptor.py
orig: `Canonical RCD form name` / `Canonical RCD entity name (53 entities, fixed at V025)`
VN · MAJOR → `Canonicalized RCD-related entity name (53 entities)` · author_review: yes (regenerates the supplementary Variable Descriptor).

**C4** · docs/RCDome_Traceability_Contract.md
orig: `Canonical RCD forms | 53` and `53 canonical entities`
VN · MAJOR → `Canonicalized RCD-related entities | 53` · author_review: yes.

**C5** · docs/RCDome_Gene_Traceability_Spec.md
orig: `CANONICAL RCD FORM NAMES — THE CLOSED VOCABULARY`
VN · MODERATE → `CANONICALIZED RCD-RELATED ENTITY NAMES — THE CLOSED VOCABULARY` · author_review: yes.

**C6** · docs/RCDome_Video_Layer/*.md (3 files)
orig: `one per canonical RCD form (53 videos)` / `all 53 canonical RCD forms`
VN · MAJOR → `one per RCD-related entity (53 videos)` / `all 53 RCD-related entities` · author_review: yes.

**C7** · docs/reply_to_Higor_5level.md
orig: `54 canonical RCD-related entities` (documents the prior "forms"→"entities" decision)
ACC · — keep (historical decision record). author_review: no.

---

### OBSOLETE draft (version drift — CRITICAL, not terminology-only)

**D1** · docs/RCDome_manuscript.md (entire file, ~25 occurrences)
orig: `54 canonical RCD forms` / `9,252 genes` / `24,834 rows` / `21,371 pairs` / `38 canonical forms` / `51-term Elicit registry`
VN (obsolete) · CRITICAL
proposed: do NOT patch terminology in place; mark this draft superseded and align to V026 (53 entities, 9,265 genes, 22,473 rows, 21,568 pairs).
rationale: obsolete draft — not the current version. author_review: yes (version reconciliation, deferred to PREAUDIT0_06).

---

### Biological "canonical" — ACCEPTABLE, keep unchanged

- `canonical gene set` (manuscript) — BC.
- `canonical signaling pathway / diagram` (docs) — BC.
- `canonical apoptosis / autophagy / inflammasome / ferroptosis / BMP signaling / Nlrp1b inflammasome` (paper titles, Board examples) — BC.
- `canonical transcript` / `canonical symbol` (gene sequence/symbol) — BC/ACC.

### Schema/code identifiers — ACCEPTABLE (do not rename)

- `rcd_form_canonical`, `canonical_pathways`, `canonical_set`, `is_canonical`, `FERRDB_TO_CANONICAL`, `CANONICAL_RCD_FORMS`, `CANONICAL_DATABASES`, `audit_canonical.py`.

---

## SUPPLEMENT (added after docx/xlsx completion)

### Manuscript — V026 governance docx (39 occurrences)
VN (change): ¶33 "canonical RCD form vocabulary"; ¶36 heading "Canonical RCD Form Vocabulary"; ¶44 "canon comprises 53 canonical RCD entities" + "canonical vocabulary is fixed"; ¶53 "non-canonical entity"; ¶72 "canonical name"; ¶84 "20 canonical database identifiers" + "53 canonical forms"; ¶97 "53 canonical forms"; ¶108 "53 canonical forms" + "canonical name"; ¶110 "53 canonical forms"; ¶113 "53 canonical forms"; ¶116 "canonical names" + "canonical form"; ¶120 "(gene, canonical RCD form) pairs"; ¶168 "complete canonical list of 53 RCD-related entities"; ¶182 "53-entity canonical vocabulary"; ¶190 "(gene, canonical RCD form) pairs"; ¶219 "53 canonical entities"; ¶221 "53 canonical RCD-related entities" + "canonical vocabulary"; ¶233/¶235/¶237 "53 canonical RCD-related entities"; ¶240 "53 canonical RCD entities"; ¶329 "53 canonical entities"; ¶332 "canonical vocabulary"; ¶336 "53 canonical entities"; ¶340 "53 canonical forms"; ¶358 "53 canonical entities"; ¶365 "28 of the 53 canonical entities"; ¶373 "53 canonical RCD entities"; ¶379 Figure 4 "53 canonical RCD entities".
BC (keep): ¶81 "canonical gene sets"; ¶97 "canonical RCD modalities"; ¶237 "canonical executors".

### Supplementary information docx (3 occurrences)
VN: ¶84 "by canonical name or its stem" → "by normalized name or its stem".
Code (keep): ¶87 "audit_canonical.py".
BC (keep): ¶103 "canonical executors".

### Supplementary tables xlsx
VN (change): INDEX "Canonical RCD Form Vocabulary (53 Forms)" → "Canonicalized RCD-Related Entity Vocabulary (53 Entities)"; INDEX "New Canonical Forms Added" → "New Entities Added"; INDEX "canonical names"/"canonical RCD forms"/"canonical RCD entities" → "normalized names"/"RCD-related entities"; Variable Descriptor "Canonical RCD form name"/"Canonical RCD entity name (53 canonical entities)"/"Canonical Name"/"Q10: canonical name accuracy" → "Canonicalized RCD-related entity name"/"Normalized Name"/"Q10: normalized name accuracy"; Table S5 "Canonical Name" → "Normalized Name"; Table S9 "53 canonical (all forms)"/"62 original -> 53 canonical" → "53 normalized (all entities)"/"62 original -> 53 normalized"; Matrix Descriptor "The normalized canonical RCD form name (one of 53 canonical forms)" → "The normalized RCD-related entity name (one of 53 entities)"; "The canonical RCDome operational definition" → "The RCDome operational definition"; "53 canonical forms" → "53 entities".
BC (keep): Table S4 "delta like canonical Notch ligand" (HGNC gene names).
AMB (defer to ontological audit): Table S11 provenance_note "canonical concept name"/"canonical label"/"Canonical mechanism".
Schema (keep): Matrix Descriptor "rcd_form_canonical".
