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
