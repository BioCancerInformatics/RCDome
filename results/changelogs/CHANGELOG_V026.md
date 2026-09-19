# RCDome — CHANGELOG V026

## V026 → V026 — Victor's biological curation (7/7 groups)
- **GROUP A**: MPT-driven necrosis → L1 (modality); MPT → L3 (trigger, `triggered_by`); Vacuolar cell death → L4 (cross-species morphology).
- **GROUP B**: 7 ontological fields added to the decoder (species_scope, evidence_maturity, relationship_type, parent_entity, ontology_curator_verified, independent_replication, primary_discovery_reference) → decoder 31 → 39 columns.
- **GROUP C**: hard gates G0–G6 (addition, not replacement) + `hard_gate_status` column (L1-ELIGIBLE 16 / NOT-L1 37).
- **GROUP D**: D1 Ontology Adjudication Table (Table S12, 53 × 26, Q1–Q13 + C1–C5) + D2 two-validation separation in Methods.
- **GROUP E**: ontological recalibration — 23 level changes (L1 12,366 → 10,300 · L2 2,111 → 2,354 · L3 172 · L4 1,219 → 2,684 · L5 6,605 → 6,963); specific adjudications (Anoikis → L2 subtype_of Intrinsic apoptosis; Mitotic death → L4 driven_by Mitotic catastrophe; direction fix).
- **GROUP F**: Methods/Results/Discussion framing — 5 insertions (mechanistic fraction ≠ independent validation; subtype > parent; "RCD-related entities"; dynamic nomenclature via evidence_maturity; curator-governed adjudication).
- **GROUP G**: 9 ontological relationships registered (12-value relationship vocabulary + outcome_of).
- **Matrix**: V026 → V026 (22,473 × 67; levels recalibrated per G0–G6).
- **Decoder**: 39 columns; 7 category corrections; hard_gate_status 16/37.
- **Manuscript**: version-free content; matrix named **Database S1** (22,473 rows × 71 columns); 381 paragraphs.
- **Supplementary**: S1–S15 + Database S1; D1 registered as Table S12; Variable Descriptor 144 entries.
- **Figure 4**: regenerated with V026 level colors.
- **App**: loads V026 matrix.

## V024 → V026 (history)
- **Orphan row removed**: EPAS1 / Ammonia-induced cell death (retracted Elicit record, empty provenance). Matrix 22,474 → 22,473 rows; 21,569 → 21,568 unique pairs; corroboration rows unchanged (905).
- **Mini-run pairs classified (Phase 2A/D)**: NLRX1 → CONTEXT_GAP (PMID 41739553); PPIF → MECHANISTIC (PMID 15800627).
- **Numbers updated everywhere**: 22,473 · 21,568 · 11,605 · 11,743 · 8,863 · 3,063 · 6,170.
- **Figures regenerated**: Figure 1 (22,473), Figure 3 (21,568 pairs, 11,605 uncertain), Figure 4 (from V026).
- **Legends updated**: main FIGURE LEGENDS + Supplementary Information file.
- **Supplementary consolidated**: Notes S1–S3 + Supplementary Figures S1–S2 (front page in Calibri).
- **App updated**: loads V026 matrix; dome, Gene Catalog, and detail pages regenerated.
- **Traceability**: "V024 → V026 Amendment Log" added to the contract.

## Run
```
setwd(".../RCDome_Atlas/APP")
shiny::runApp(appDir = ".", port = 8890, launch.browser = TRUE)
```
