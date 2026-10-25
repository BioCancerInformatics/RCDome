# TRACEABILITY — Table S10 completion + GitHub figure-code sync (2026-10-24)

## 1. Table S10 — Extraction Pipeline Scripts completed

**Reverse audit** (find scripts NOT listed, not just verify listed ones) found the sheet incomplete vs the INDEX's claim of "complete … full reproducibility".

- 13 extraction-pipeline scripts existed in `extraction code snippets/` but were missing from Table S10.
- Added them in pipeline order, with tier + role:

| Script | Tier | Role |
|---|---|---|
| channel_c_deep_pdf_rag.py | C | Phase 2B deep PDF RAG |
| channel_c_deep_xml_rag.py | C | Phase 2B deep XML RAG |
| extract_governance_literature.py | C | Governance literature deep RAG |
| recover_3_sessions.py | 2E | Session recovery (3 CSVs) |
| complete_recovery.py | 2E | Recovery completion (parse + govern) |
| elicit_fulltext_6.py | E | Elicit full-text (6 pairs) |
| elicit_semantic_search_8genes.py | E | Elicit semantic search (8 pairs) |
| elicit_targeted_17.py | E | Elicit targeted prove/disprove (17 rows) |
| download_extract.py | U | Download extract.csv |
| download_phase2b_ris.py | U | Phase 2B RIS/PDF batch download |
| preflight_check.py | U | Phase 2B preflight |
| utility_check_open_access.py | U | Open-access check |
| utility_preflight_check.py | U | Phase 2B preflight check |

- Table S10: **43 → 56 scripts**.
- INDEX updated: `43 rows × 3 cols` → `56 rows × 3 cols`.
- Propagated: `Submission FAI/`, `manuscript_V027/`, `RCDome_distribution/manuscript/` (md5 `aefdffbe…`); distribution ZIP rebuilt (397.0 MB).

## 2. GitHub — figure code centralized + synced

- Public repo `code/figures/` (stale, old names) → replaced by **`code/figure_code/`** (8 canonical scripts + README).
- Renames tracked by git (e.g., `translate_infographic_EN.py` → `make_figureS1_infographic_EN.py`).
- Commit `7f02668`, pushed to `main`.
- **Manuscript files remain purged** from the public repo (a re-added xlsx during sync was removed).

## 3. State
- Figure code: unified + public (GitHub) + working (`code/figure_code/`).
- Manuscript + supplementary tables: private (Submission FAI / local), purged from GitHub.
- ZIP + A4 figures: synced to Submission FAI.
