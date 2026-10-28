# R4 EXHAUSTIVE DETECTOR — FINAL AUDIT (derivation map)
Date: 2026-10-28 · Method: read-only, exhaustive, "innocent until proven guilty".

## Scope
- T0 truth: FULLY DERIVED from `unified_gene_rcd_matrix_V027.csv` + `RCDome_Decoder_53.csv` + `adjudication/disc_df.rds` (zero hardcoded).
- T2 artifacts (6): manuscript `.docx` · supplementary information `.docx` · tables `.xlsx` (19 sheets) · figure code · figure legends · comms.
- Exhaustive derivation dive: `code/` + `analysis/` + `docs/` + `comms/` + `manuscript_V027/` (number→source index, byte-safe).

## Result (9,038 extracted values)
| Verdict | Count | Meaning |
|---|---|---|
| CONSISTENT | 385 | equals a matrix/decoder/disc_df-derived truth — **proven correct** |
| DERIVED | 8,581 | traced to a source file (figure scripts, benchmarks, pipeline logs) — **provenance established** |
| UNRESOLVED | 72 | external identifiers + usage figures (PMIDs, page numbers, HTML entities, API costs, GPT codes) — **not matrix values** |

## Phase 3 re-count (human-approved re-run, read-only)
`disc_df.rds` (7,905 rows) re-counted → SI sentence verified EXACTLY:
- 7,905 label-disagreements = role 320 + direction 935 + mechanistic 6,650 ✅
- 7,831 unique pairs ✅

## Detector evolution (this cycle)
1. Zero hardcoded truths (roles, directions, level %, raw vs unique-pairs vs genes, mechanistic YES, role-resolved).
2. 6-artifact coverage (added figure legends + SI + tables).
3. Auto-STALE flag **reverted** — it fabricated discordances (single-keyword → single-truth conflated denominators, e.g. "192 downgrades" vs "EXECUTOR pairs 225"). STALE is now **human-adjudicated** only.
4. Computed-aggregate tracing **added** — `disc_df.rds` disagreement counts derived, not hardcoded.

## CONCLUSION (locked)
> Every manuscript value is accounted for: the matrix-bound values (385) are proven consistent with the matrix/decoder/data; the derived values (8,581) are each traced to their derivation (figure scripts, benchmarks, pipeline logs); the remainder (72) are external identifiers or usage figures. **Nothing is unexplained.**

## Remaining (deferred, not a blocker)
Denominated **correctness** pass on the 8,581 DERIVED values (is each correct against its own denominator?) — to be done **human-adjudicated, detective-style** (never auto-flagged).
