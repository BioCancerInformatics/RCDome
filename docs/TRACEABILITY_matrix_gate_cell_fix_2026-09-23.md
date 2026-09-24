# Traceability — Single-Cell Gate-Status Fix (TP53 | MPT-driven necrosis)

**Date:** 2026-09-23
**Status:** ADJUDICATED → PROPAGATED → VERIFIED

## Finding (final integrity audit)
One matrix row carried a stale `decoder_hard_gate_status` value:

| gene_symbol | rcd_form_canonical | rcd_form (original) | rcdome_level | decoder_hard_gate_status (before) |
|---|---|---|---|---|
| TP53 | MPT-driven necrosis | MPT-driven-necrosis (hyphenated) | L1 | NOT-L1 ❌ |

The decoder truth (`RCDome_Decoder_53.csv`) states **MPT-driven necrosis = L1-ELIGIBLE**.
All 75 other MPT-driven necrosis rows were correctly L1-ELIGIBLE; only the hyphenated-name
row was stale. (1 of 22,473 rows = 0.004%.)

## Adjudication
Rule: `decoder_hard_gate_status` must equal `L1-ELIGIBLE` iff `rcdome_level == L1`.
This rule already held for all other 22,472 rows; the one TP53 cell violated it.

## Propagation (single source of truth = the matrix CSV)
Per the RDS policy — *the matrix CSV is the source of truth; the .rds is a faithful
serialization of it and must never be edited separately* — the fix was applied to the CSV,
then the .rds was regenerated from the CSV.

1. `unified_gene_rcd_matrix_V026.csv` — 1 cell corrected (NOT-L1 → L1-ELIGIBLE).
2. `output databases/Phase 2C output/unified_gene_rcd_matrix_V026.rds` — regenerated from CSV (xz).
3. `RCDome_distribution/data/unified_gene_rcd_matrix_V026.rds` — regenerated from CSV (xz).
4. `RCDome_V026_distribution.zip` — rebuilt (pre-flight `ok: TRUE`).
5. GitHub mirror `data/` + `app/data/` — synced.

## Independent verification (post-propagation)
- CSV: 22,473 rows × 71 cols; L1-ELIGIBLE = 10,344; L1/eligibility mismatches = **0**.
- Master RDS: 22,473 × 71; L1-ELIGIBLE = 10,344; mismatches = **0**.
- Distribution RDS: 22,473 × 71; L1-ELIGIBLE = 10,344; mismatches = **0**.
- 53 canonicalized entities; 62 original name strings; 9,265 genes (all unchanged).
- Column types preserved (62 character, 2 integer, 7 numeric).

## Impact
None on any manuscript claim. Entity-level truth (19 L1 modalities, L1-ELIGIBLE 19/53)
was never affected; only one provenance cell in the gene-level matrix was stale.
