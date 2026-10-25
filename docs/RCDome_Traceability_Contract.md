# RCDome Traceability & Governance Contract

## Principles

0. **NEVER ASSUME, NEVER IMAGINE, NEVER EXTRAPOLATE, NEVER SPECULATE.** State only what is verified against the data. A relationship, count, or equivalence (e.g., "316 CSV rows = 316 papers") is a claim that must be programmatically verified before it is written or spoken as fact. No projection, no inference-as-fact, no guessed numbers, no speculation about what "should" be true. If a number or relationship has not been checked against the actual data, it is an open question, and it must be labelled as such — never asserted. **External-service status (e.g., "Elicit's servers are recovering", "an outage", "a backlog") is a factual claim that MUST be cited from the provider's own status page or documentation — never asserted from symptoms. A cost figure (e.g., "~$2") MUST be cited from an invoice or usage record — never estimated. An unknown cause MUST be labelled "UNKNOWN", not filled with a guessed explanation.**
1. **No speculation.** Every gene-RCD association must be traceable to a source database, a PubMed-indexed publication (PMID), or an Elicit/AI extraction with verifiable provenance.
2. **No inference.** Classifications (mechanistic_class, rcd_gene_type, evidence_tier) must derive from explicit evidence statements, not statistical inference or heuristic guessing.
3. **No overwriting.** Each validation layer adds columns. Source database classifications are preserved in their original form. Phase 2A, 2C, 2D, and 2E each write to separate columns.
4. **Full traceability.** Every row carries source_databases, evidence_types, evidence_basis, and PMID where available.
5. **HGNC only.** Human genes only. All gene symbols validated against HGNC approved set.
6. **Transparency.** All extraction scripts are public. All progress files are saved. Every decision is auditable.

## Matrix Versioning Protocol

**Effective: V006+**

- The current authoritative matrix is saved as `unified_gene_rcd_matrix.csv` at the project root.
- **Before any structural change** (column addition/removal, new database integration, re-classification pass), a versioned copy is created:
  ```
  unified_gene_rcd_matrix_V006.csv  (archived)
  unified_gene_rcd_matrix_V007.csv  (archived)
  ...
  unified_gene_rcd_matrix_V025.csv  (current)
  ```
- All versioned copies reside in `output databases/Phase 2C output/`.
- **No in-place edits to a matrix without a backup copy.**
- RDS and Excel exports are created ONLY from the latest versioned matrix.

## Manuscript-Matrix Synchronization Protocol

**Effective: V011+**

1. **The RCDome manuscript is NOT a diary of project evolution.** It is a draft of the document that will eventually be submitted for publication. Every time the reference matrix changes (VXX → VXX+1), the manuscript MUST be updated to reflect the current matrix state. Historical narratives of how the compendium was built belong in Supplementary Methods, not in the main text.

2. **Substantial changes in column values and analyses that result in a new matrix version (VXX+1) MUST be reflected in the manuscript.** This includes but is not limited to: mechanistic_class reclassification, evidence_tier redistribution, gene count changes per RCD form, new database integrations, column additions/removals, and PMID coverage changes.

3. **Table 1 (Canonical RCD Form Vocabulary) MUST always reflect the current matrix version.** The table must list all canonical forms present in the matrix with their current gene counts, categories, and evidence grades.

4. **Number discrepancies between manuscript and matrix are unacceptable.** Every count must be verified against the current matrix before any manuscript revision is considered complete.

5. **[TODO] markers are legitimate indicators of pending execution work** (Shiny app, Phase 2B RAG, manual curation). They are NOT diary language and must be preserved until the work they reference is completed. When the execution is done, the TODO is replaced with the actual result.

## Current State

| Attribute | Value |
|-----------|-------|
| Current version | V027 |
| Authoritative file | `RCDome_distribution/data/unified_gene_rcd_matrix_V027.rds` (app) · `unified_gene_rcd_matrix_V027.csv` (truth export) |
| Rows | 22,473 |
| Columns | 100 (83 original + 11 evidence-first adjudication + 6 mapped-vote) |
| Unique genes | 9,265 |
| Unique gene–RCD pairs | 21,568 (+ 905 corroboration rows) |
| Canonicalized RCD-related entities | 53 |
| Raw RCD form names | 62 |
| Databases and resources | 20 |
| Seven-class MECHANISTIC (rows) | 3,063 (13.6%) |
| Seven-class DATABASE_ONLY (rows) | 286 (1.3%) |
| Evidence-first mechanistic YES (pairs) | 4,881 (22.6%) |
| Evidence-first executors / regulators | 367 / 8,369 |
| Unique PMIDs (four columns) | 319,548 (10,141 title-verified) |

## Deprecated Artifact Archiving Protocol

**Effective: V027+**

1. **Active folders hold only the current version.** Deprecated or obsolete artifacts (old matrix versions, old changelogs, retired scripts, superseded documents, scratch files) must not remain in active working folders.
2. **Archive, never silently delete.** Move deprecated files to a `_archive`/`_archive_*` folder (e.g., `data/_archive_V027_partial/`, `output databases/Phase 2C output/_archive/`). Scratch/temp files may be deleted; versioned artifacts are always archived.
3. **One canonical location per artifact.** Each artifact has exactly one authoritative location; stale duplicates (old mirrors, backups, legacy-layout copies) are removed once the canonical copy is confirmed. The V027 matrix lives only in `RCDome_distribution/data/`, `output databases/Phase 2C output/`, and the GitHub mirror's `data/` + `app/data/`.
4. **Stray scripts live in `code/`.** Any one-off or maintenance script is placed in `code/` with a descriptive name — never abandoned at a drive root or inside a data folder.
5. **Nothing is lost.** Versioned history is preserved in archive folders and in git history; the sweep only relocates files out of the active tree.
6. **No secrets in the repository or its history.** API keys, SMTP credentials, and tokens live only in the authors' local `.Renviron`. Any key ever committed is purged from history and rotated before the repository is made public.

## V024 → V025 Amendment Log

1. **Orphan-row deletion** — removed the single retracted Elicit record (EPAS1 / Ammonia-induced cell death) whose provenance was empty (`source_databases` = NaN, `num_sources` = 0). Rows 22,474 → 22,473; unique pairs 21,569 → 21,568; corroboration rows unchanged (905).

2. **Mini-run pairs — Phase 2A/D two-call classification** — populated `mechanistic_class`, `llm_status`, `llm_pmids`, `llm_evidence_force` for the two late-added pairs (NLRX1 and PPIF, MPT-driven necrosis):
   - NLRX1 → **CONTEXT_GAP** (PubMed confirms via PMID 41739553; LLM training does not recognize the gene in this form).
   - PPIF → **MECHANISTIC** (LLM knowledge + PubMed both confirm via PMID 15800627).

   *Method deviation (transparency):* for these two pairs, call B used the known PMIDs from `pmid_list` instead of the standard esearch query, because the canonical form name "MPT-driven necrosis" does not match PubMed terminology ("mitochondrial permeability transition"). Call A used the clarified descriptor "MPT-driven necrosis (necrosis driven by the mitochondrial permeability transition, mPTP)".


## File Inventory

| File | Purpose | Status |
|------|---------|--------|
| `unified_gene_rcd_matrix_V025.csv` | Current authoritative (supersedes V024) | ✅ |
| `unified_gene_rcd_matrix_V010.csv` | Previous version | Archived |
| `RCDome_manuscript_V011.docx` | Submission draft manuscript | ✅ |
| `RCDome_Traceability_Contract.md` | This document | ✅ |
| All earlier versions (V006-V009) | Incremental changes | Archived |
| Zima run logs and progress files | Server execution records | Archived |

## Column Ontology

| Column Group | Columns | Source |
|-------------|---------|--------|
| Core identifiers | gene_symbol, rcd_form, rcd_form_canonical | Compilation |
| Provenance | source_databases, source_channels, num_sources | Compilation |
| Evidence quality | evidence_quality, evidence_types, evidence_basis, confidence_score, confidence_tier | Compilation |
| Functional annotation | cancer_gene_type (Rodrigues2025), rcd_gene_type (Phase 2/3 Elicit) | Database extraction + Phase 3 |
| Phase 2A/2D validation | llm_status, llm_pmids, llm_evidence_force, mechanistic_class | NCBI + DeepSeek |
| Phase 2C/2E recovery | epmc_hits, epmc_status, epmc_pmids, phase2c_mechanistic_class | Europe PMC + DeepSeek |
| Elicit PMIDs | elicit_pmids | DOI-to-PMID conversion from Elicit Phase 3 |
| Biotype/ID | uniprot_id, ensembl_id, gene_biotype, gene_symbol_status | HGNC + compilation |

## Forbidden Actions

- Guessing RCD form names from file content
- Inferring gene_type from evidence tier
- Overwriting source_databases to "fix" naming
- Discarding rows because mechanistic_class is empty
- Using column index numbers instead of column names
- Manuscript claiming numbers not verified against current matrix
- Sending manuscript for co-author review without line-by-line matrix audit
- Changing matrix without creating a new versioned copy (VXX → VXX+1)
- Committing an API key, password, or credential (NCBI, DeepSeek, Elicit, Consensus, SMTP) to the repository or leaving one in any tracked file
- **Assuming** a row-to-entity equivalence (e.g., "rows = papers") without programmatic verification
- **Imagining** values or relationships to fill a data gap and presenting them as observed
- **Extrapolating** counts, costs, or completion times without computing them from actual data
- Answering "likely" / "probably" / "should be" to a factual question when the data is available to check
- **Speculating** about what a result or mechanism "probably" is instead of checking the source or data
- **Claiming external-service status** ("outage", "recovering", "backlog", "their side") without citing the provider's own status page
- **Estimating a cost** ("~$X") without citing an invoice, usage record, or billing statement
- **Framing competing hypotheses** ("A vs B") as if they are the only possibilities — unknowns must be labelled UNKNOWN, not narrowed by guesswork

## Victor Curadoria Biológica — GROUP A (2026-09-05)

**A1. MPT trigger × MPT-driven necrosis (correction)**
- What: matrix `elic_onto_rcd_type` for "Mitochondrial permeability transition" changed `SYNONYM_CANDIDATE` → `TRIGGER` (46 rows); `elic_onto_relationship` `SYNONYM_CANDIDATE_OF` → `TRIGGERS`.
- Why: Victor §8 — MPT is the permeabilization *trigger event*, not a synonym of the death. NCCD defines MPT-driven necrosis as a specific RCD *form* relying on CYPD.
- Source: Relatorio_Auditoria_Biologica_Ontologica_RCDome_V025_V2.docx §8.
- Echo: SYNONYM_CANDIDATE 85→39 rows (1 entity: Lysosomal cell death); new TRIGGER type 46 rows (MPT). Decoder already had MPT = Trigger (no change — harmonized).
- Verified by: Enrique, 2026-09-05.

**A2. Vacuolar cell death → L4 (confirm + cross-species note)**
- What: matrix `elic_onto_operational_note` appended "Cross-species morphological category (plant + human)."
- Why: Victor §10 — Elicit human set supports a transversal vacuolar phenotype, not a unique executor machinery; classic plant PCD morphological category.
- Source: Relatorio §10 + Elicit Vacuolar Cell Death Report.
- Echo: decoder already MORPHOLOGY (no change); manuscript note to add in Results/Discussion.
- Verified by: Enrique, 2026-09-05.

**A1/A2 correction (rcdome_level) — 2026-09-05 (addendum)**
- What: matrix `rcdome_level` for "MPT-driven necrosis" changed `L3 Triggers` → `L1 Modalities` (75 rows); "Vacuolar cell death" `L1 Modalities` → `L4 Functional/conceptual` (24 rows).
- Why: Victor §8/§10 — the matrix had BOTH MPT and MPT-driven necrosis at L3 ("trigger-centered ontology"); Vacuolar was wrongly at L1. Strict-compliance audit caught this.
- Echo: L1 Modalities 12,315 → 12,366; L3 Triggers 247 → 172; L4 Functional 1,195 → 1,219.
- Verified by: Enrique, 2026-09-05.

**Step 4 echo (manuscript) — 2026-09-05**
- What: manuscript Results OD census gained a note documenting the two ontology corrections (MPT-driven necrosis L3→L1 modality; MPT remains L3 trigger; Vacuolar cell death L1→L4 cross-species morphological).
- Human approval: Enrique (agreed step 4).
- Audit: 5/5 PASS (note present, mentions both corrections, correct location).

## Victor Curadoria Biológica — GROUP B (2026-09-05)

**Novos campos ontológicos (7) no decoder:**
- species_scope (7 values) · evidence_maturity (6) · relationship_type (Victor 8 + synonym_of + root) · parent_entity · ontology_curator_verified (TRUE; Enrique; date) · independent_replication (pending) · primary_discovery_reference (= founding_pmid).
- Normalization: matrix elic_onto_relationship (15 values) → Victor vocabulary (11).
- Direction fix: MPT = root; MPT-driven necrosis = triggered_by MPT.
- 5 taxon/cell-type programs (Cornification, Erebosis, Eryptosis, Hypersensitive response, Linker cell-type death) = root (matrix had CONTEXTUAL_PROGRAM mislabeled as relationship).
- Human approval: Enrique (approved GROUP B).
- Audit: 10/10 PASS.

## Victor Curadoria Biológica — GROUP C (2026-09-05)

**Hard gates (logic, not replacement):**
- Adopted G0-G6 as an ADDITION (logic), not a replacement of existing categorization.
- Added ONE column `hard_gate_status` (L1-ELIGIBLE 23 / NOT-L1 30), derived from `category` (no invention).
- Documented G0-G6 + cross-reference (G1~C1, G2~C5, G3~C2/C3, G4~C4) in Methods.
- Rodrigues C1-C6 remains orthogonal ranking (not an admission gate).
- Human approval: Enrique (1-column recommendation).

## rcdome_level provenance + Recalibration (2026-09-05)

**Provenance of `rcdome_level`:**
- Author: Enrique Medina-Acosta (mapping confirmed 2026-08-12).
- Script: `extraction code snippets/add_rcdome_ontology.py` (V013 → V014).
- Basis: 5-level taxonomy (L1 Modalities / L2 Subtypes / L3 Triggers / L4 Functional / L5 Generic).
- Original criterion was PERMISSIVE: 38 forms → L1 (any "death form").
- Amendments: GROUP A (MPT-driven necrosis L3→L1; Vacuolar L1→L4).
- **Superseded (expert adjudication 2026-09):** Vacuolar cell death was reclassified L4→L5 (TAXON) — founding evidence is Dictyostelium discoideum (protist); principal context plant; vacuolization is a phenotype, not a mechanism. The L4→L5 move is propagated to the matrix, figures, legends, and level counts.

**Recalibration (APPROVED by Enrique, 2026-09-05):**
- Adopt STRICT criterion (Victor G0-G6): L1 = only true modalities (G1 machinery + G2 necessity).
- Canonical mapping (decoder `category` → `rcdome_level`):
  L1 ← Executioner, CORE_RCD_FORM, CORE_PENDING
  L2 ← SUBTYPE, SYNONYM
  L3 ← Trigger
  L4 ← Functional, CONTEXTUAL, CELL_TYPE, DIFFERENTIATION, MORPHOLOGY, CLEARANCE_PROCESS, INTEGRATED_PROGRAM
  L5 ← CELLULAR_PROCESS, UMBRELLA, LEGACY, TAXON, EMERGING, COMPOSITE
- 7 decoder `category` corrections (align with matrix type): Anoikis, Autophagy, Autosis, Erebosis, Mitoptosis, Necrosis, PANoptosis.
- Consequence: V025 → V026 (L1 drops; ~2,066 gene-pairs move out of L1).

## V026 Recalibration — Governance Cycle (2026-09-05)

Full change cycle for the ontological recalibration (V025 → V026):

1. **PROPOR** (propose): GROUP G canonical type→level mapping (decoder `category` → `rcdome_level`), grounded in Victor's G0–G6 hard gates (Table 6).
2. **ACORDO HUMANO** (human agreement): Enrique approved — "yes register and proceed the recalibration which is approved" (2026-09-05).
3. **EXECUTAR** (execute): matrix V026 (levels), decoder 7 category corrections + hard_gate_status re-derive (16/37), manuscript V026, workbook V026 (Table S11 39 cols), Figure 4, app V026.
4. **ECOAR** (echo): all artifacts — matrix CSV+RDS, decoder CSV+XLSX (×2), manuscript, supplementary workbook, Variable Descriptor, Matrix Descriptor, Figure 4, app (global.R/mod_omic.R/server.R/data RDS), GROUP G doc, GROUP C declaration, TODO E, GitHub mirror (179 files).
5. **AUDITAR** (audit): mega deep audit — Sections 1–7: ontology mapping 53/53, hard_gate_status↔L1 16/16, RDS↔CSV consistent, echo 8 artifacts, policy compliance. Result: PASS.

**Change registry (no deletion, provenance P0–P3):** V025 files preserved in working directory (`output databases/...V025.csv/.rds`, `RCDome_manuscript_governance_V025.docx`, `RCDome_manuscript_V025_supplementary_tables.xlsx`); GitHub mirror carries the V026 truth snapshot only.

## Victor Curadoria — GROUP G (2026-09-05)

**9 ontological relationships (13.3) registered in decoder:**
- 5 already correct (Anoikis, Autosis, Mitotic death, MPT-driven necrosis, NETosis).
- 3 fixed: Lysoptosis subtype_of Lysosome-dependent cell death; Metalloptosis umbrella_for (Ferroptosis; Cuproptosis; Lysozincrosis); Regulated Necrosis umbrella_for (Necroptosis; Pyroptosis; MPT-driven necrosis).
- 2 clarified: Entosis = canonical entity (root, L1); NETosis = entity (is_a Regulated Necrosis).
- Human approval: Enrique (option (a) — semicolon-separated members in parent_entity).
- Audit: 8/8 PASS.

## GROUP G mega audit — 3 findings resolved (2026-09-05)

- **outcome_of** (Necrosis → Regulated Necrosis): legitimate 12th relationship value — added to vocabulary (was missing from the 11-value GROUP B set).
- **Conceptual parents** (Ammonia "ammonia (inducer)"; Efferocytosis "cell death (downstream)"): legitimate — parent_entity may hold a non-entity conceptual reference for contextual entities.
- **associated_with + empty parent** (9 entities): legitimate GROUP B convention — associated_with may have no single parent.

## Victor Curadoria — GROUP F (2026-09-05)

**Methods/Results/Discussion framing (5 insertions, human-approved text):**
- F1: hard gates in Methods — already done (GROUP C); adjudication table + separate validations = GROUP D.
- F2a (Results): mechanistic fraction in L1 is not independent ontology validation (expected by construction).
- F2b (Results): subtype > parent (Autosis 1,105 vs ADCD 110) = database indexing, not ontological inheritance.
- F3a (Discussion): "RCD-related entities" — heterogeneity acknowledged (comparative, cross-species, outcomes, umbrellas).
- F3b (Discussion): dynamic nomenclature via evidence maturity (established/emerging/contested/provisional), not binary.
- F3c (Discussion): final ontological adjudication is curator-governed (automated channels preserve evidence only).
- Human approval: Enrique ("absolutely agree with the 5 texts").

## GROUP F mega audit — F3b compliance fixes (2026-09-05)

- F3b cited "contested" (not a decoder value) and referenced the evidence_maturity value set without a prior M&M definition.
- Fixed: F3b aligned to actual values (established, supported, emerging, legacy, provisional).
- Added M&M definition (¶52): "The evidence_maturity dimension records the consensus status of each entity as established, supported, emerging, legacy, or provisional."
- Human approval: Enrique.

## GROUP F re-audit — echo gaps fixed (2026-09-05)

- MandM_operational_definitions.md (source): added evidence_maturity definition (was only in docx).
- Variable Descriptor C112: corrected to 5 values (established/supported/emerging/legacy/provisional) — removed "contested" (not a decoder value).

## Version-clean rule — applied to published artifacts (2026-09-05)

- Manuscript content carries NO version names (V025/V026 removed); the matrix is referred to as "the unified gene–RCD evidence matrix" / "the unified evidence matrix".
- D1 table columns are semantic (pre_adjudication_level / adjudicated_level) — direction of change in content, not version in names.
- Supplementary workbook Variable Descriptor: version-free ("53 canonicalized RCD-related entities").
- Version numbers live ONLY in working file names + traceability contract (not in published content).
- Human approval: Enrique ("in the manuscript no versioned naming must be operated").

## D1 descriptor name-collision fix (2026-09-05)

- C1-C5 in Table S12 were wrongly described as "NCCD criterion" while the content is the Rodrigues scoring criteria (0-10). Fixed: S12 C1-C5 now described as Rodrigues (Extent of Research, Direct Involvement, Impact, Emerging Potential, Biological Significance) — same meaning as S11.
- Derived fields renamed to match S11: entity→rcd_form, parent→parent_entity, primary_pmid→founding_pmid, curator_verified→ontology_curator_verified, Q9→category, Q10→definition_status, Q11→species_scope, Q12→independent_replication, Q13→evidence_maturity.
- No "NCCD criterion" remains in S12; shared fields now carry identical names across S11/S12.

## Victor Curadoria — GROUP E (2026-09-05)

**Specific adjudications (12 entities) — completed:**
- Mechanical re-leveling (GROUP G mapping): 18 entities moved from L1 (morphology, umbrella, contextual, taxon, legacy, emerging) + 7 category mislabels corrected (Anoikis, Autophagy, Autosis, Erebosis, Mitoptosis, Necrosis, PANoptosis).
- Two specific (non-mechanical) adjudications, human-approved:
  - Anoikis → L2, subtype_of Apoptosis (intrinsic) (was CONTEXTUAL/L4).
  - Mitotic death → L4, driven_by Mitotic catastrophe (was UMBRELLA/L5).
  - Direction fix: Mitotic catastrophe → root (was associated_with Mitotic death).
- hard_gate_status re-derived: L1-ELIGIBLE 16 / NOT-L1 37.
- Matrix levels (V026): L1 10,300 · L2 2,354 · L3 172 · L4 2,684 · L5 6,963.
- Human approval: Enrique (both proposals).

## Matrix naming — "Database S1" (2026-09-05)

- Human decision (Enrique): the compendium matrix is named "Database S1" in the manuscript.
- Applied in 3 places: ¶49 (Methods), ¶319 (Gene Catalog), ¶355 (Data Availability).
- Dimensions stated: 22,473 rows × 71 columns.
- Pending: INDEX row in the supplementary workbook (file locked in Excel at time of writing).

## App echo — decoder connected (2026-09-05)

- Decoder (53 operational definitions) now loaded in the Shiny app (data/RCDome_Decoder_53.csv).
- mod_rcd_grid.R detail page shows: operational definition, core mechanism, key molecules, ontology (category, hard_gate_status, relationship_type, parent_entity, species_scope, evidence_maturity, independent_replication), Rodrigues scoring (C1-C6, S), provenance (founding_pmid, review_status, validation_verdict).
- Fallback to static .txt only when decoder has no match.
- Human approval: Enrique ("yes indeed").

## Dome landing page — level counts/labels corrected to V026 (2026-09-05)

- Dome legend showed OLD V014 counts (L1 38, L2 5, L3 3, L4 4, L5 3) and old labels (L4 categories, L5 concepts).
- Corrected to V026: L1 16, L2 5, L3 2, L4 11, L5 19 (VCD reclassified L4→L5 TAXON by expert adjudication); labels L4 Functional/contextual, L5 Generic/umbrella/legacy/taxon/emerging.
- Files: www/landing_page.html, www/dome_prototype.html, www/detail_page_wireframe.html, modules/mod_omic.R.

## App functional audit — curation echo fixes (2026-09-05)

- Dome DATA.entities: hardcoded entity levels were STALE (Anoikis L1, Necrosis L1, Oncosis L1, Metalloptosis L1, Regulated Necrosis L1, Mitotic death L2, etc.). Regenerated from V026 matrix → correct levels (16/5/2/12/18).
- RCD grid entity list: was 25 static .txt → now 53 from decoder.
- data.table bug in mod_omic.R: `df[, cols, drop=FALSE]` → `df[, ..cols]` (4 occurrences) — Gene Catalog now works.
- Dome LEVEL_COUNTS/NAMES corrected (L4 Functional/contextual, L5 Generic/umbrella/legacy/taxon/emerging).

## Landing page stats audit vs V026 (2026-09-05)

- Verified: 9,265 genes ✅ · 53 entities ✅ · 469 executors ✅ (unique pairs EXECUTOR+YES) · 20 databases ✅ · 3 analyses ✅.
- Fixed: explore.html "21,569 gene–RCD pairs" (old V024 number) → 21,568 (V025/V026 truth).

## Explore page — human curation added as 4th layer (2026-09-05)

- "Three independent analyses" → "Three independent analyses + human ontological curation".
- Added: Human ontological curation (curator-governed, produced the 53-entity decoder, G0-G6 hard gates, level adjudication 16/5/2/12/18).
- Human approval: Enrique.

## Manuscript level descriptions corrected to V026 (2026-09-05)

- Found 5 paragraphs with OLD V014 level descriptions (38/5/3/4/3): ¶31, ¶46, ¶240, ¶334, ¶364, ¶367.
- Corrected to V026: 16 modalities · 5 subtypes · 2 triggers · 11 functional/contextual · 19 generic/umbrella/legacy/taxon/emerging.
- ¶46 rewritten to include the G0-G6 hard gates (G1 machinery + G2 necessity obligatory).
- Unifying matrix name: "Dataset S1" → "Database S1" (3 occurrences).

## Detail page regenerated with V026 (2026-09-05)

- generate_detail_page.py read V025 matrix + old LEVEL_NAMES (L4 category/L5 concept) → fixed to V026 + new labels.
- Regenerated detail_page_wireframe.html: Anoikis now L2 (was L1); all entity levels now V026.
- Fixed write-path discrepancy (script wrote to Shiny app/, app uses APP/www/).

## Deep functional echo — final sweep (2026-09-05)

- Lesson: echo/sync is a FUNCTIONAL audit (not file copies) — old V014 classification was buried in app deep structures.
- Fixed in this round: generate_dome.py (V025→V026 + labels), generate_detail_page.py (V026 + labels), parent-level landing_page.html/dome_prototype.html/detail_page_wireframe.html (synced from www), landing_page_wireframe.html (16/5/2/12/18).
- Final sweep: 0 old labels, 0 old counts, 0 V025 in active app scripts (excluding Emanuell archive + provenance scripts).

## Detail page definitions fixed (2026-09-05)

- Root cause: detail page used matrix rodr_core_mechanism (only 25 Rodrigues entities populated) → "No operational definition recorded in the matrix" for 28 entities.
- Fix: generate_detail_page.py now reads the decoder (53 operational definitions) as primary source, matrix rodr_* as fallback.
- Result: 53/53 entities have definitions (0 empty).

## Matrix decoder_* block (2026-09-05)

- Added 4 columns to the matrix (67 → 71): decoder_operational_definition, decoder_key_molecules, decoder_category, decoder_hard_gate_status.
- Matrix is now self-sufficient: rodr_* (Rodrigues provenance, 25) + decoder_* (canonical, 53) side by side.
- Echoed: Matrix Descriptor +4 · manuscript 67→71 columns · app (mod_omic + explore) 67→71.
- Human approval: Enrique.

## Consensus full run — transfer plan (decision, 2026-09-06)

- The Consensus full run is executing on V023 (22,474 rows × 63 cols; 21,569 pairs) — started weeks ago, provenance-OK.
- Progress: 21,568/21,568 processed (100%; full run complete).
- DECISION (Enrique): do NOT change the script's matrix path mid-run. Let the V023 run finish.
- After completion: merge the Consensus columns into the MOST RECENT matrix version (V026 now; V027+ if newer), by:
  1. Loading the Consensus checkpoint (keyed by gene_symbol × rcd_form_canonical).
  2. Dropping the orphan pair (EPAS1 / Ammonia-induced cell death) → 21,568 pairs.
  3. Joining on (gene_symbol, rcd_form_canonical).
- No retro-adjustment: the V023 run remains a historical record; only the merge targets the current matrix.

## Digital Molecular RCD Board — design decisions (2026-09-06)

- Output = PROSE synthesis (not tiered lists), like the CancerRCDShiny "Clinical Synthesis".
- Multi-layer governance (domain boundary + terminology + preservation + hedging).
- Output ends with "Suggested Queries:" (exactly 3) + an exact disclaimer sentence.
- temperature > 0 (adaptable, not locked) — prose varies, facts stable.
- Benchmarking: per-test statistical determination (n computed by formula, CI 95% Wilson, significance tests).
- Human approval: Enrique (statistical mapping + architecture).
- Prose discipline = four provenance categories (P1 Observed / P2 Computational / P3 Biological / P4 Mechanistic Hypothesis) — distinct from the matrix `evidence_tier` (formal T1–T4).
- Order of operations: deterministic terminology scrub runs first; governance + payload audits run on the scrubbed output.
- Hallucination reporting: "zero hallucination recorded in the performed benchmark" (observed absence, not a general guarantee).

## Manuscript V026 readability + provenance sweep (2026-09-08)

- **Database URLs + founding PMIDs**: ¶66/¶68/¶70/¶92/¶191 — every database URL now carries `URL; PMID` (26 PMIDs verified via NCBI) and is an active hyperlink (34 total).
- **Orphan-sentence fixes (7)**: merged/moved the floating one-liners (extraction scripts → end of Channel B; CoT benchmark → Phase 2F; Confidence scores → Evidence Tier; For-completeness → Extraction Scripts; Europe PMC refinement → Compendium Completeness; "These exclusions" + "seven classes above" rephrased to name their referents). Zero content lost (238→232 paragraphs = 6 merges + 1 new heading).
- **Phase 2A label + execution order**: added bold "Phase 2A: Two-Call Independent Validation" and moved the two-call block before Phase 2B, so the manuscript follows provenance order (2 → 2A → 2B → 2D/2E → 2F → 3 → 2G). No phase renumbering.
- **Supplementary tables renumbered to citation order**: S1↔S9 shift (Comparison→S9; 25-Forms→S1 … New Forms→S8), then S6/S7/S8 shift (New Forms→S6, Validation→S7, Five-Gate→S8), plus three off-by-one fixes (benchmark extraction→S13, gate results→S14, search-depth→S15). Workbook sheets + INDEX re-sorted; manuscript citations now monotonic S1→S15 and content-matched to the workbook.
- **Critical recovery**: restored the accidentally deleted "Validation was performed on all 21,568…" paragraph and the bold on "Phase 2A/D Validation: Scale and Coverage" (recovered verbatim from the GitHub mirror).
- **GitHub sync**: commits `399568a`…`945e2fb` (hero revert, PMID/hyperlink sweep, orphan fixes, Phase 2A, table renumbering).
---

## Storage contract (reinforced 2026-10-11)

- **NEVER save any RCDome artifact to drive C:** (project files, ZIPs, data, figures, emails,
  backups, temp outputs). Everything lives on **D:**.
- Drive C: is critically low (7.9 GB free, 94% used); drive D: has 208 GB free.
- Verified: the project is entirely on D:; zero RCDome files on C:.


## Submission Folder Protocol (Submission FAI = truth)

**Effective: V027+**

1. **`Submission FAI/` is the single source of truth for the submission.** It holds the files that will be ACTUALLY submitted (manuscript, supplementary information, supplementary tables, figures, datasets, cover letter, APC waiver, reviewers, preprint). Any claim about "the submission" refers to the files in `Submission FAI/`.

2. **All other copies mirror `Submission FAI/`.** `manuscript_V027/` (working) and `RCDome_distribution/manuscript/` (distribution) are mirrors — byte-identical to `Submission FAI/` after every edit.

3. **Sync direction is one-way: `Submission FAI/` → mirrors.** Edits are made in `Submission FAI/` (the truth), then copied out (`cp`) to the mirrors. Never the reverse.

   3a. **Archive-as-we-go (no silent overwrite).** Before replacing any mirror file, the old copy is archived to `_archive_backups/<timestamp>_<reason>/`. Then the truth file replaces it, and md5 verifies mirror == truth. After any manuscript/supplementary/tables change, the distribution ZIP is rebuilt and re-synced to `Submission FAI/`.

4. **Submitted figures live in `Submission FAI/Figures_A4/` (A4, 600 DPI) and `Submission FAI/Figures/` (short names).** The working `Figures/` + `Figures_A4/` are the generation outputs (old names) — NOT the submission.

5. **GitHub is the PUBLIC mirror of code + data + docs only — never the manuscript or supplementary files** (pre-submission embargo). Manuscript files stay purged from the public repo until submission authorization.

6. **The distribution ZIP is built from `RCDome_distribution/` and synced to `Submission FAI/`.** It must carry the latest manuscript + supplementary (via the mirror) + data + app.
