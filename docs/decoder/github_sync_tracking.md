# GitHub Repository Sync — Tracking Document

**Repository:** `github.com/BioCancerInformatics/RCDome` (PRIVATE)
**Local mirror:** `D:/RCDome_github/`
**Last synced:** commits `af6cb5e … db13d38 … b945439` (pre-decoder work)
**This document:** tracks the **RCDome Decoder** deliverables to be pushed next.

---

## A. Truth deliverables (the decoder + review)

| File | Purpose | Sync |
|---|---|---|
| `RCDome_Decoder_53.csv` | 53-entity definition record (31 cols) | PENDING |
| `RCDome_Decoder_53.xlsx` | Excel view | PENDING |
| `RCDome_Decoder_53.csv` | locked truth (approved) | PENDING |
| `RCDome_Decoder_53.xlsx` | Excel view | PENDING |
| `definition_review_worksheet.csv` | two-call review (336 rows × 11 cols) | PENDING |
| `definition_review_worksheet.xlsx` | Excel view | PENDING |
| `merge_log.csv` | Call B traceability (308 decisions) | PENDING |
| `RCDome_Definition_Governance.md` | governance policy (invariance · P0–P3 · two-call) | PENDING |

## B. Manuscript subsections

| File | Purpose | Sync |
|---|---|---|
| `MandM_operational_definitions.md` | Methods — OD methodology | PENDING |
| `Results_OD_census.md` | Results — census + scores + validation | PENDING |

## C. Invariant source + reference data

| File | Purpose | Sync |
|---|---|---|
| `galluzzi2018_nccd_definitions.json` | verbatim NCCD 2018 Box 1 (22 terms) | PENDING |
| `Rodrigues 2025_Dataset S1.xlsx` | Rodrigues S1A anchors | PENDING |
| `entity_evidence_V026.csv` | per-entity matrix aggregates | PENDING |
| `founding_pmids_pending_FINAL.csv` | 28 founding PMIDs + status | PENDING |
| `gap_inventory_V026.csv` / `.md` | 53 = 25 defined + 28 pending | PENDING |

## D. Draft definitions (the 28 pending)

| File | Purpose | Sync |
|---|---|---|
| `definitions_SOLID_draft.md` / `.csv` | 15 SOLID drafts | PENDING |
| `definitions_CANDIDATE_draft.md` / `.csv` | 13 CANDIDATE/non-standard drafts | PENDING |

## E. Validation results

| File | Purpose | Sync |
|---|---|---|
| `od_validation_deepseek_fulltext.csv` | DeepSeek full-text RAG (40 entities) | PENDING |
| `od_crossref_consensus.csv` | Consensus API cross-reference (40) | PENDING |
| `consensus_crossvalidation_report.csv` | C1–C3 cross-validation | PENDING |
| `consensus_deep_search_report.csv` | coinage/mechanism/PubMed deep search | PENDING |
| `governance_audit_report.json` | V1–V6 governance audit | PENDING |
| `recovered_fulltexts.json` | Europe PMC recovery attempts | PENDING |

## F. Reproducible scripts

| File | Purpose | Sync |
|---|---|---|
| `build_decoder_53.py` | decoder builder (source of truth) | PENDING |
| `scoring_formulas.py` | S formula (verified 25/25) | PENDING |
| `governance_checker.py` | V1–V6 audit | PENDING |
| `final_readiness_audit.py` | 26-check readiness audit | PENDING |
| `deep_audit.py` | ocean-deep logic audit (27 checks) | PENDING |
| `verbatim_audit.py` | Galluzzi/Rodrigues byte-identity | PENDING |
| `pmid_topic_audit.py` | PMID topic correctness | PENDING |
| `consensus_crossvalidate.py` / `consensus_deep_search.py` | cross-validation | PENDING |
| `validate_od_deepseek.py` / `validate_od_fulltext.py` / `validate_od_consensus.py` | RAG validation | PENDING |
| `merge_approved.py` | merge Call B decisions | PENDING |
| `make_review_worksheet.py` | worksheet generator | PENDING |
| `founding_pmid_lookup.py` / `recover_fulltexts.py` | PubMed/Europe PMC | PENDING |
| `add_provenance.py` / `apply_galluzzi_format.py` / `add_rodrigues_complement.py` / `standardize_citations.py` / `fix_nccd_complements.py` | post-processing | PENDING |

## G. Working/intermediate (optional — exclude or archive)

| File | Note |
|---|---|
| `founding_pmids_pending.csv`, `pending_entity_founding_pmids.csv`, `od_validation_deepseek.csv` | superseded by `_FINAL`/`_fulltext` versions |
| `definition_review_worksheet_v2.xlsx` | deleted (obsolete) |
| `recover_fulltexts.py` / `recovered_fulltexts.json` | keep (documents the paywalled outcome) |

---

## Sync checklist

1. [ ] Add `RCDome Decoder/` (60 files) to the mirror `D:/RCDome_github/`
2. [ ] Update `mirror_manifest.txt` (sha256 of new files)
3. [ ] Add `tests/` for the decoder (optional: decoder integrity check)
4. [ ] Update `README.md` (link the decoder + governance + worksheet)
5. [ ] Commit + push (PRIVATE repo)
6. [ ] Note: M&M/Results `.md` will later become `.docx` inserts in the manuscript
