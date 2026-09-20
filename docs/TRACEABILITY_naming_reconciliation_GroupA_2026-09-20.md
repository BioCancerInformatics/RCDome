# TRACEABILITY — Naming reconciliation, Group A (Figure S1 truth)

**Date:** 2026-09-20
**File:** `manuscript_V026/RCDome_manuscript_governance_V026.docx`
**Decision:** Figure S1 + legend is the canonical naming truth. Group A = unambiguous one-to-one mappings.

## Applied mappings (44 replacements, 17 paragraphs)
| Stale | Canonical (Figure S1) | Count |
|---|---|---|
| T1–T4 (evidence tier) | ET1–ET4 | 10 |
| G0–G6 (biological gates) | BG0–BG6 | 30 |
| C2 trigger / C3 morphology (modality criteria) | MC2 / MC3 | 4 |

## Explicitly NOT touched (Group B — deferred for discussion)
- RS1–RS6 (ranking score) — not in Figure S1.
- "C1 / C3 / C6" ranking names (¶32) — tied to RS1–RS6.
- QG1–QG5 (quality gates) — not in Figure S1.
- "five governance gates" / EG1–EG5 — to be decided.
- CT1–CT4 (confidence tier) — already matches Figure S1; untouched.

## Verification
- Standalone "T1–T4" = 0 · "CT1–CT4" = 6 (untouched).
- Standalone "G0–G6" = 0 · "BG0–BG6" = 32.
- "MC2 trigger" = 2 · "MC3 morphology" = 2.
- Ranking "C1/C3/C6" (¶32) intact.

## Extension — supplementary artifacts (same Group A mappings, approved)
- **Supplementary information docx**: `G0–G6 → BG0–BG6` (14 replacements).
- **Supplementary tables xlsx** (context-specific, 7 cells): "C1-C5 logic → MC1-MC5 logic"; "G1 machinery → BG1 machinery"; "G2 necessity → BG2 necessity"; "G0-G6 hard gates → BG0-BG6 hard gates"; "T1-T4 multi-tier → ET1-ET4 multi-tier".
- Ranking "C1–C6" cells (Variable Descriptor) left untouched (Group B).
- Verified: supp-info standalone G0-G6 = 0 · BG0-BG6 = 16; all 5 canonical cells confirmed.

## Extension 2 — supp-tables confidence cell + decoder + distribution board/docs (approved)
- **Supp tables**: "Confidence tier … (T1 strongest)" → "(**CT1** strongest)" (T→CT, confidence context — distinct from T→ET).
- **Decoder** (`MandM_operational_definitions.md`, `RCDome_Definition_Governance.md`, `GROUP_G_canonical_mapping.md`, `GROUP_C_compliance_declaration.md`): G0–G6→BG0–BG6, C1-C5→MC1-MC5, `~C#`→`~MC#`, `tier_T#`→`tier_ET#`.
- **Distribution board** (`qa_benchmark_report.json`, `qa_t*.json`, `run_qa_benchmark.py`, `run_board_benchmark.py`, `Example_RCDome_Board_*.html`): T1-T4→ET1-ET4, C1-C5→MC1-MC5.
- **Distribution docs** (`README_DISTRIBUTION.md`, `CHANGELOG_V026_4.md`): G0–G6→BG0–BG6, C1-C5→MC1-MC5.
- **Left untouched**: ranking C1–C6 (Group B), gene-symbol "T1/T2/G1" (ribonuclease T2, cyclin G1…), historical/archive files.
- **Matrix**: already ET1–ET4 + CT1–CT4 — no change.
- Verified: board JSON "CET"=0, "CT" preserved=45, "ET1"=403; decoder stale G0-G6=0.
- GitHub commits: `3173bca` + `2d9b2b0`.

## Group B1 (approved: keep RS1–RS6 text-only) — ranking C→RS
- Manuscript ¶32: "C1=4/C1=7 → RS1", "C3(impact → RS3", "C6(clinical → RS6" (4 replacements).
- Supplementary tables (Variable Descriptor): 15 ranking cells "C1…C6" → "RS1…RS6".
- Verified: ¶32 stale ranking C = 0.
- Remaining (flagged for decision): the **decoder** code + data still use "C1–C6" (ranking) across 25+ files — same B1 mapping, larger scope.

## Group B1 extension — Excel book (Variable Descriptor)
- 6 cells "C1-C6" → "RS1-RS6" (Overall Score formula + criterion C1–C5 descriptions).
- Matrix V026: no C1-C6/RS1-RS6 columns (ranking lives in the decoder) — clean, no action.
- Decoder final output (RCDome_Decoder_53.csv/.xlsx): already RS1–RS6 columns — no change.
- Decoder build code + "Rodrigues 2025_Dataset S1.xlsx" (source): keep C1-C6 (intermediate/source naming, invariance).

## Decision recorded — decoder C1-C6 → RS1-RS6 DEFERRED
Per curator: the decoder **code/data migration** ("C1–C6" → "RS1–RS6" inside `build_decoder_53.py`, drafts, and the source `Rodrigues 2025_Dataset S1.xlsx`) is **deferred** until the Group B disambiguation is fully complete. Rationale: the decoder's *final output* already carries RS1–RS6 columns; the remaining C1–C6 are source/intermediate naming. Handled separately later.

## Group B2 + B3 (approved)
- **B2**: Q1–Q13 (13 evidence-checklist questions) confirmed unchanged (matches Figure S1).
- **B3**: "five governance gates" → "five quality gates (QG1–QG5)" (¶124, first mention) + "quality gates" (¶170); Excel-book stale cell "Benchmark gate (Q1-Q5)" → "(QG1-QG5)".

## Group B4 (curator decision: Figure S1 = truth)
- **EG1–EG5** confirmed as the canonical name (Elicit governance gates). Renamed **QG1–QG5 → EG1–EG5** across: manuscript (¶124 "five Elicit governance gates (EG1–EG5)", ¶170), Table S8 (EG1 input validation … EG5 traceability), Variable Descriptor ("Benchmark gate (EG1-EG5)").
- Supersedes the earlier B3 "QG1–QG5" naming.
- B4 fix: "pipeline quality gates" (Figure S1 callout) restored (was wrongly changed); Table S8 note "hard gates G0–G6" → "BG0–BG6" (missed by Group A); note reads "Benchmark gates EG1–EG5 are distinct from the ontology hard gates BG0–BG6".

## Final ocean-deep audit (18/18 PASS) — honest findings + fixes
- **Audit caught 6 cells my earlier pass MISSED**: Table S11 "G1+G2 passed / G5 replication / G2 by" → BG1+BG2/BG5/BG2 (3 cells); Matrix Descriptor "T1 theoretical" → CT1, "evidence tier (T1-T4)" → ET1-ET4, "T1,T2,T3,T4" → ET1-ET4 (3 cells).
- Remaining "T/G" in Table S4 are **gene symbols** (ras homolog T1, ribonuclease T2, troponin T2, cyclin G1, G0/G1 switch…) — correctly left untouched.
- Final audit script: `code/audit_final_compliance_AB.py` → **18/18 checks, 0 FAIL** across manuscript + supp info + supp tables.

## Decoder↔Matrix reconciliation (approved single-field fix)
- Matrix V026 `decoder_hard_gate_status` = "L1-ELIGIBLE" for **NECSO, Mitoxyperilysis, Triaptosis** (43 gene rows) — was stale "NOT-L1", now consistent with decoder + matrix's own `rcdome_level=L1` + `decoder_category=CORE_PENDING`.
- Backup: `output databases/Phase 2C output/_archive/unified_gene_rcd_matrix_V026_backup_20260920_175535.csv`.
- Verified: 0 remaining "NOT-L1 + L1" inconsistencies.
