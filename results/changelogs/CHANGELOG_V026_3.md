# RCDome — CHANGELOG V026_3

**Download (zip):** https://drive.google.com/file/d/1AuKXTfxGmfyDBowQ2Sy8VQnvSHxNwz9a/view?usp=sharing

## V026_3 — Operational Definitions + Comparator + landing-page menu
- **Operational Definitions module** (`modules/mod_od.R`): new navbar tab, list+detail browser over the 53-form decoder, source databases as wrapping pills, reference citations hyperlinked to PMIDs, didactic ontology-level legend.
- **Operational Definition Comparator** (`modules/mod_od_compare.R`): side-by-side comparison of 2-4 entities, difference highlighting, 3 display modes (all / differing / identical), top-aligned cells, NCCD badges, Download Comparison (HTML) with entity names in the filename.
- **Landing page lower panel**: now mirrors the full bar menu (Home, Explore RCDome, Operational Definitions, Compare Definitions, RCD entities, Gene Catalog, RCDome Board, Network, About, Contact), each linked to its tab.
- **Not-found pop-up**: universal on all scroll-downs via the verified create callback (returns false, value never added) + centered modal.
- **Gene Catalog**: click a gene opens the gene page in-app (navbar stays).
- **Detail page**: stable jump bar with type-ahead gene/entity search + not-found pop-ups.
- **Governance**: pre-run audit contract (`docs/RCDome_Code_Amendment_Contract.md`) + executable audit (`code/audit_before_run.sh`).

## V026 — Digital Molecular RCD Board + governed Q&A AI
- **Board module** (`modules/mod_board.R`): prose synthesis of any RCD entity (and optional gene) strictly from the matrix and decoder, with governance scrub, payload table, and HTML download.
- **Q&A submodule** (`modules/mod_board_qa.R`): retrieval-augmented (RAG) free-form Q&A across all 53 entities and all 9,265 genes; static full gene-entity index (22,473 associations) plus dynamic four-dimension records (class | role | direction | tier | PMID); no gene capping, no funneling; hyphenated gene-entity tokens split (XIAP-Apoptosis -> XIAP).
- **Governance**: zero hallucination (never invent gene/PMID/fact), exact refusal sentence, exact disclaimer, RCDome database/decoder terminology only, hedging, PMID discipline.
- **Benchmark**: board 9 tests (golden 26/26, census 53/53, fact-stability 73/73, governance 0.047% violation, anti-hallucination 4/4, articulation 98.7%); Q&A 2 tests (T10 positive + T11 negative, n=100 each, 100/100, Wilson 95% CI 96.3-100%, two-sided binomial p=0.010).
- **Logo**: `www/rcdome_logo.svg` (dome-only) and `www/rcdome_logo_full.svg` (full emblem with wordmark) - cupola dome + 53 ontology-colored entity nodes + rust gene constellation.
- **UI**: "Try an example query" relocated after the Q&A; footer processing-time darkened for visibility.
- **Supplementary Note S4** and manuscript paragraph 324 updated with the board and Q&A benchmarks.
- **Board benchmarks shipped**: `board/run_board_benchmark.py`, `board/run_qa_benchmark.py`, `board/qa_benchmark_report.json`.

## V026 -> V026 — Victor's biological curation (7/7 groups)
- **GROUP A**: MPT-driven necrosis -> L1 (modality); MPT -> L3 (trigger, `triggered_by`); Vacuolar cell death -> L4 (cross-species morphology).
- **GROUP B**: 7 ontological fields added to the decoder (species_scope, evidence_maturity, relationship_type, parent_entity, ontology_curator_verified, independent_replication, primary_discovery_reference) -> decoder 31 -> 39 columns.
- **GROUP C**: hard gates G0-G6 (addition, not replacement) + `hard_gate_status` column (L1-ELIGIBLE 16 / NOT-L1 37).
- **GROUP D**: D1 Ontology Adjudication Table (Table S12, 53 x 26, Q1-Q13 + C1-C5) + D2 two-validation separation in Methods.
- **GROUP E**: ontological recalibration - 23 level changes (L1 12,366 -> 10,300 · L2 2,111 -> 2,354 · L3 172 · L4 1,219 -> 2,684 · L5 6,605 -> 6,963); specific adjudications (Anoikis -> L2 subtype_of Intrinsic apoptosis; Mitotic death -> L4 driven_by Mitotic catastrophe; direction fix).
- **GROUP F**: Methods/Results/Discussion framing - 5 insertions.
- **GROUP G**: 9 ontological relationships registered (12-value relationship vocabulary + outcome_of).
- **Matrix**: V026 (22,473 x 71; levels recalibrated per G0-G6).
- **Decoder**: 39 columns; hard_gate_status 16/37.
- **Manuscript**: version-free content; matrix named **Database S1**; 381 paragraphs.
- **Supplementary**: S1-S15 + Database S1.
- **Figure 4**: regenerated with V026 level colors.
- **App**: loads V026 matrix.

## Run
```
setwd(".../RCDome_Atlas/APP")
shiny::runApp(appDir = ".", port = 8890, launch.browser = TRUE)
```
