# RCDome — Extraction & Classification Code Catalog (V027)

Python scripts that build the RCDome compendium: gene–RCD associations from **20
databases and resources**, normalized into **53 canonicalized RCD-related
entities**, validated through independent LLM + literature channels, and merged
into the final truth matrix **`unified_gene_rcd_matrix_V027.csv/.rds`**
(**22,473 association rows × 100 columns**).

Scripts live here (`code/extraction/`) plus two subdirectories:
- `phase2b_rag/` — Phase 2B full-text RAG validation.
- `governance_extraction/` — governance theme-synthesis outputs.

> Note: the Consensus channel, GPT-4o arbitration, and the evidence-first
> adjudication scripts are maintained outside this folder (see
> `code/` and `external_data/` in the manuscript project).

---

## Phase 1 — Compilation (channels A, B, E)

| Script | Channel | Source | What it does |
|---|---|---|---|
| `channel_a_rodrigues2025.py` | A | Rodrigues et al. 2025 | Explodes Dataset S1B into one row per gene per RCD form |
| `channel_b_ferrdb_v3.py` | B | FerrDB v3 | 22 RCD modalities, 3,481 genes |
| `channel_b_rcddb.py` | B | RCDdb | Per-form CSVs (15 forms, PMIDs) |
| `channel_b_ipcd.py` | B | iPCD | Per-form ZIPs, *Homo sapiens* |
| `channel_b_lncrcd.py` | B | LncRCD | lncRNA gene sets |
| `channel_b_ilir.py` | B | iLIR | LC3-interacting proteins |
| `channel_b_hadb.py` | B | HADb | Human autophagy genes |
| `channel_b_hamdb.py` | B | HAMdb | Autophagy modulators |
| `channel_b_atd.py` | B | ATD | Autophagy-disease genes |
| `channel_b_kegg.py` | B | KEGG | RCD pathway KGML |
| `channel_b_reactome.py` | B | Reactome | Programmed Cell Death hierarchy |
| `channel_b_go.py` | B | GO (QuickGO) | RCD-specific GO terms |
| `channel_b_msigdb.py` | B | MSigDB/GSEA | RCD gene sets (GMT) |
| `channel_b_ncbi_gene.py` | B | NCBI Gene | E-utilities keyword records |
| `channel_b_xdeathdb.py` | B | XDeathDB | 12 RCD forms |
| `channel_b_phase2_new_forms.py` | B | NCBI Gene | New forms: NECSO, Eryptosis, Triaptosis, Mitoxyperilysis |
| `channel_e_elicit_extract.py` | E | Elicit Phase 3 | Systematic-review extraction |
| `master_extract.py` | — | Orchestrator | Runs the channel scripts in sequence |

## Phase 2A/D — Two-call validation (MSigDB extension)

| Script | What it does |
|---|---|
| `phase2ad_msigdb_1832.py` | Validates the 1,832 MSigDB-only pairs (mechanistic + role + direction) |
| `phase2ad_residual.py` | Residual pairs not covered by the main MSigDB pass |

## Phase 2B — Full-text RAG (deep evidence)

| Script | What it does |
|---|---|
| `phase2b_rag/channel_c_deep_pdf_rag.py` | Three-pass LLM-RAG over full-text PDFs |
| `phase2b_rag/channel_c_deep_xml_rag.py` | Full-text XML RAG |
| `phase2b_rag/utility_preflight_check.py` | Pre-flight prerequisites |
| `phase2b_rag/utility_check_open_access.py` | Open-access availability per PMID |
| `phase2b_rag/preflight_check.py` | Pre-flight verification |
| `download_phase2b_ris.py` | Downloads RIS for Phase 2B |

## Phase 2C / 2E — PMID recovery

| Script | What it does |
|---|---|
| `channel_c_recovery_europe_pmc.py` | Europe PMC full-text PMID recovery |
| `channel_2e_zero_pmid_recovery.py` | Zero-PMID pair recovery |

## Phase 2F — Chain-of-thought classification (full matrix)

| Script | What it does |
|---|---|
| `deepseek_cot_full.py` | Full-matrix CoT classification (role, direction, mechanistic, evidence) |
| `deepseek_cot_v11_full.py` | CoT v11 full run |
| `deepseek_cot_mini_2pairs.py` | CoT mini-run for late-added pairs |
| `cot_pilot.py` / `cot_pilot_rescue.py` | CoT pilots |

## Phase 3 — Elicit full-text

| Script | What it does |
|---|---|
| `elicit_fulltext_6.py` | Elicit full-text extraction |
| `elicit_semantic_search_8genes.py` | Elicit semantic search |
| `elicit_targeted_17.py` | Elicit targeted extraction |
| `channel_e_elicit_extract_benchmark_50.py` | Elicit 50-form benchmark |

## Phase 3B — Reintegration

| Script | What it does |
|---|---|
| `phase3b_p1.py` … `phase3b_p4_RegulatedNecrosis.py` | Reintegrate the Phase 3B output into the matrix |

## Evidence tier + merge

| Script | What it does |
|---|---|
| `channel_c_evidence_tier.py` | Two-call LLM validation → evidence tiers |
| `merge_engine.py` | Merge extraction outputs into the unified matrix |
| `merge_cot_into_matrix.py` | Merge CoT columns into the matrix |
| `merge_phase2d_results.py` | Merge Phase 2D results |
| `add_rcdome_ontology.py` | Add RCD ontology annotations |
| `complete_recovery.py` | Complete recovery pass |

## Governance theme synthesis

| Script | What it does |
|---|---|
| `extract_governance_literature.py` | Extract governance literature |
| `governance_theme_synthesis.py` | Synthesize governance themes (51 core themes) |
| `governance_finalize.py` / `governance_collapse.py` / `governance_final_collapse.py` / `governance_merge_v2.py` | Theme finalization/collapse/merge |

## Benchmarks & audits

| Script | What it does |
|---|---|
| `cot_benchmark.py` (+ `_v2` … `_v11`) | CoT model-selection benchmarks |
| `benchmark_phase2b.py` | Phase 2B benchmark |
| `benchmark_phase3.py` | Phase 3 benchmark |
| `audit_phase2b.py` / `audit_phase3.py` | Phase 2B/3 audits |

## Utilities

| Script | What it does |
|---|---|
| `utility_map_uniprot.py` | UniProt → HGNC symbol mapping |
| `utility_validate_hgnc.py` | Validate symbols against HGNC approved set |
| `utility_normalize_rcd_forms.py` | Normalize RCD form names → canonical |
| `utility_apply_qc.py` | Apply quality-control filters |
| `utility_convert_to_docx.py` | Convert manuscript markdown → .docx |
| `notify_email.py` | Email notifications |

## QA / debug / one-off (not part of the core pipeline)

`test_*`, `check_*`, `recheck_*`, `recover_*`, `compare_*`, `count_*_uncapped`,
`fill_*`, `fix_progress`, `debug_curl`, `download_extract`,
`inspect_session_structure`, `verify_rows_vs_papers`, `_llm_verify_temp`.

---

## Output

Final truth matrix: **`unified_gene_rcd_matrix_V027.csv/.rds`** — 22,473 rows ×
100 columns (83 original + 11 evidence-first adjudication + 6 mapped-vote
helpers), spanning 21,568 unique gene–RCD pairs, 9,265 HGNC genes, 53 entities.

## Traceability

Every script is self-contained with documented input paths and source URLs.
The master orchestrator produces timestamped logs; the matrix carries
`source_databases`, `source_channels`, PMID lists, and per-analysis columns so
provenance is never lost.
