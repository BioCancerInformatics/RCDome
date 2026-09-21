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

## Final deferred item RESOLVED — build_decoder_53.py output keys C→RS
- Output keys + `FIELDS` in `build_decoder_53.py` renamed "C1…C6" → "RS1…RS6" (3 edits). Source `d["C"]` + raw `c1..c6` values kept (Rodrigues invariance). NOT re-run.
- Backup: `RCDome Decoder/_archive/build_decoder_53_C_backup_20260920.py`.
- Reproducibility gap closed: the build code now emits RS1–RS6, matching the shipped decoder.

## Hallucination-risk cluster — fixes applied (approved)
- **U3/Channel E**: Figure 1 generator updated to "Five compilation channels … E: Elicit Phase 3 systematic review" + Figure 1 regenerated; ¶40 "four→five … Channel E".
- **S1**: ¶60 adds "Three further forms … (Floatptosis L4, Lysozincrosis L2, Metalloptosis umbrella)".
- **U1**: ¶113 XDeathDB rewording → "identified as an additional source by the external audit" (accurate + traceable).
- **H2**: ¶13 clarifies NCCD = 20 entities (15 + anoikis/autosis/efferocytosis/mitotic death/programmed cell death).
- **No-fix verdicts**: U2/H1 deepseek-v4-pro (real model), H2 20 (confirmed), H3 NCCD terms (in list).

## Logic cluster — fixes applied (approved)
- **L1**: ¶148/¶202 "16 bona fide modalities" → "19" (decoder = 19 L1-ELIGIBLE).
- **L2**: ¶190 "remaining 37" → "34" (53−19).
- **L6**: ¶88 "CT1 = 7–10 … CT4 = 1" → "CT1 = 7–9 … CT4 = 0–1" (matches `merge_engine.py`: max 9, T4 = score<2).
- **L7**: ¶173 percentages labelled "relative" (+33%/+113%/+310%).
- **L3/L4**: resolved (definition-source vs scoring-anchor are different dimensions).

## Horizontal/vertical spread of logic fixes
- Supplementary info: "16 bona fide RCD modalities" → "19" (matches decoder/matrix = 19 L1).
- Supplementary tables (Table S3) already lists Floatptosis/Lysozincrosis/Metalloptosis ✓; Table S6 (Phase-2 additions) correctly holds only the 4 ¶60 entities ✓; Table S2 already has XDeathDB ✓.
- Decoder = 19 L1-ELIGIBLE ✓ · Matrix = 19 L1 entities ✓ — no further spread needed.

## L5 (ground-truth ambiguity) — resolved
- ¶130 + ¶212 + Figure 2A/2C legend: "26-pair ground-truth set" → "26-pair benchmark set"; "17-pair ground truth" → "17-association accuracy ground truth". The 17-association accuracy set and the 26-pair benchmark set are now clearly distinct.

## S2 (Phase 2B/2C labelling) — resolved
- ¶111 clarifying sentence: "Phase 2C is distinct from Phase 2B (the deep RAG step): 2C recovers PMIDs, whereas 2B extracts deep evidence sentences."
- Supplementary tables (Table S9/S10, Matrix Descriptor) already use "Phase 2B deep evidence" / "Phase 2C recovery" consistently — no spread needed.

## Prose cluster (F1–F7) — applied
- F1 "recomputed bitwise"→"deterministically" · F2 closed FerrDB parenthesis · F3a/b missing spaces · F4 "the the … from." fixed · F5 "an entity" · F6 seven classes separated by "; " · F7 "47% to 100%".

## X1 + X3 + X10 — resolved
- X1: ¶132 Gene Catalog "Genes, Isoforms, miRNA, and Proteins views" → "a Genes view" (vestigial views removed from app).
- X3: ¶140 "protein-coding (20,643)" → "(20,642)" (matrix truth: 20,642 + 1,177 + 509 + 81 + 48 + 16 = 22,473).
- X10: "21 channel_*.py scripts" — verified exactly 21 in `extraction code snippets/` → no fix (false positive).

## X5 + X9 — resolved
- X5: ¶178 "…430 unknown, 70 context-dependent, and one row without a recorded direction" (matrix deep_best_direction = 1,382 vs 1,383 rows).
- X9: eryptosis founding_pmid 16910766 + od_author Rodrigues (RCDome) verified in decoder — consistent, no fix.

## X6 — corrected (verified)
- ¶180: "921→1,013 deep papers · 9,145→9,146 DOIs · 18,300→10,138 unique (deduplicated) · 19→21 overlap".
- ¶178 "167,868 processed" confirmed still present (correct).
- X4 resolved (roles in matrix rcd_gene_type match ¶177 exactly: 3,347/323/119/10/3 + 1 empty).

## X2 + X7/X8 + X12 — closed
- X2: ¶168 A–D grades defined inline ("rank support from A, strongest, to D, weakest").
- X7/X8: no fix (6,229/4,790 entries vs 5,897/4,634 unique genes — both correctly labelled).
- X12: DEFERRED with note — references are inserted via EndNote and will be completed at a later formatting stage; unformatted inline PMIDs will be resolved then. No manuscript change now.
