# Extraction Code Snippets

Python scripts used to extract gene-RCD associations from 15 independent databases and build the unified gene-RCD matrix.

## Scripts

| Script | Tier | Source Database | What It Does |
|--------|------|-----------------|--------------|
| `channel_a_rodrigues2025.py` | A | Rodrigues et al. 2025 | Explodes Dataset S1B into one row per gene per RCD form |
| `channel_b_ferrdb_v3.py` | 1 | FerrDB v3 | Parses `ferrdb_genes_only.md` (22 RCD modalities, 3,481 genes) |
| `channel_b_rcddb.py` | 1 | RCDdb | Downloads per-form CSV files (15 forms, 1,846 genes, all with PMIDs) |
| `channel_b_ipcd.py` | 1 | iPCD | Downloads per-form ZIP files, filters *Homo sapiens* (15 forms) |
| `channel_b_lncrcd.py` | 1 | LncRCD | Parses `lnRCD_geneset_12_RCD.csv` (12 forms, 1,595 genes) |
| `channel_b_ilir.py` | 1 | iLIR | Downloads TSV export of LC3-interacting proteins (6,087 entries) |
| `channel_b_hadb.py` | 1 | HADb | Scrapes 371 human autophagy genes from HTML |
| `channel_b_hamdb.py` | 1 | HAMdb | Parses protein-role ZIP (551 human autophagy modulators) |
| `channel_b_atd.py` | 1 | ATD | Downloads XLSX of autophagy-disease genes (87 genes) |
| `channel_b_kegg.py` | 2 | KEGG | Downloads KGML for 5 RCD pathways (Apoptosis, Ferroptosis, Necroptosis, Autophagy, Senescence) |
| `channel_b_reactome.py` | 2 | Reactome | Queries ContentService API for Programmed Cell Death hierarchy (R-HSA-5357801) |
| `channel_b_go.py` | 2 | GO (QuickGO) | Queries 7 RCD-specific GO terms via QuickGO REST API |
| `channel_b_msigdb.py` | 2 | MSigDB/GSEA | Downloads 12 RCD-relevant gene sets in GMT format |
| `channel_b_ncbi_gene.py` | 3 | NCBI Gene | Queries all 32 RCD forms via E-utilities API |
| `master_extract.py` | — | Orchestrator | Runs all channel scripts in sequence |
| `merge_engine.py` | — | Integration | Merges outputs into unified matrix with evidence quality and confidence tiers |
| `utility_map_uniprot.py` | — | Utility | Converts UniProt accession IDs to HGNC gene symbols via UniProt REST API |
| `utility_validate_hgnc.py` | — | Utility | Validates all gene symbols against the complete HGNC approved set (45,030 symbols) |
| `utility_check_open_access.py` | -- | Check PMIDs for PubMed Central open access availability |
| `utility_preflight_check.py` | -- | Pre-flight verification for Phase 2B prerequisites |
| `channel_b_phase2_new_forms.py` | 2/3 | NCBI Gene (Phase 2 new forms: NECSO, Eryptosis, Triaptosis, Mitoxyperilysis) |
| `channel_c_evidence_tier.py` | C | Two-call independent LLM validation (Phase 2 evidence tiers) |
| `channel_c_deep_pdf_rag.py` | C | Phase 2B: Full-text PDF RAG validation (3-pass) |
| `utility_convert_to_docx.py` | — | Utility | Converts the manuscript markdown to formatted .docx |

## Requirements

- Python 3.8+
- openpyxl (for XLSX parsing)
- Standard library: csv, json, urllib, subprocess, xml.etree, zipfile, re

## Output

All scripts write to `output databases/`. The final unified matrix is `unified_gene_rcd_matrix.csv`.

## Traceability

Every extraction is auditable. Each channel script is self-contained with documented input paths and source URLs. The master orchestrator produces timestamped logs.

## Governance

- **No normalizations were applied during extraction.** RCD form names and gene symbols are preserved exactly as provided by each source database.
- Normalization (RCD form names → canonical, gene type consolidation) is applied at the merge stage by `merge_engine.py` and is fully reversible.
- Two exclusion filters are applied: NCBI Gene keyword-only noise (10,857 rows) and HGNC-invalid gene symbols (696 rows). Both are documented in the Methods.

## Phase 2B: Full-Text RAG Validation

Scripts in `phase2b_rag/` subdirectory:

| Script | Purpose |
|--------|---------|
| `channel_c_deep_pdf_rag.py` | Three-pass LLM-RAG per PDF (--validate for ground truth audit) |
| `utility_preflight_check.py` | Pre-flight verification of all Phase 2B prerequisites |
| `utility_check_open_access.py` | Check PMIDs for PubMed Central open access availability |
| `Phase2B_RAG_Design_Contract.md` | Complete design contract with governance rules |
| `Phase2B_RAG_PDF_Plan.md` | Implementation plan |

**Note:** 3 Phase 2B scripts are in the `phase2b_rag/` subdirectory.
