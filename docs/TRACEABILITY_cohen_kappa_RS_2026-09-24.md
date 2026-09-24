# Traceability — Cohen's κ (RS1–RS6 drafted vs human-reviewed)

**Date:** 2026-09-24
**Status:** VERIFIED (computable + reported in manuscript ¶70)

## Purpose
Estimate the inter-rater agreement between the AI-drafted RS1–RS6 scores and the
human-reviewed (approved) RS1–RS6 scores for the 28 RCDome-drafted entities.

## Data sources (both preserved — traceable comparison)
| Source | Where | Contents |
|---|---|---|
| Draft RS1–RS6 | `RCDome Decoder/build_decoder_53.py` | inline DRAFT records (28 entities) |
| Final RS1–RS6 | `RCDome_Decoder_53.csv` | human-approved scores |

## Method
1. Parse each of the 28 drafted entities' 6 draft scores (RS1–RS6) from the build script.
2. Read the same 6 final scores from the decoder CSV.
3. Pair every score (draft vs final): 28 entities × 6 criteria = 168 score-pairs.
4. Count identical vs edited pairs; compute Cohen's κ.

## Result
| Metric | Value |
|---|---|
| Score-pairs compared | 168 |
| Identical (draft = final) | 164 |
| Edited | 4 |
| Observed agreement (p0) | 164/168 = 0.976 |
| Chance agreement (pe) | 0.237 |
| **Cohen's κ** | **(0.976 − 0.237) / (1 − 0.237) = 0.968 ≈ 0.97** |

## The single edited entity
"Senescence and Autophagy in Cancer" (composite WikiPathways label):
- draft `(4,4,4,3,5,3)` → final `(4,3,4,4,4,4)`

All 27 other drafted entities were approved unchanged.

## Verdict
κ = 0.97, above the ≥ 0.80 target. Human review largely confirmed the AI drafts;
the only substantive change was the composite entity's scores.

## Manuscript effect
¶70 now reads:
"Inter-rater agreement between the drafted and human-reviewed RS1–RS6 values was
assessed with Cohen's κ = 0.97 (164 of 168 score-pairs identical across the 28
drafted entities)."

## Note on a second, unrelated κ
`extraction code snippets/channel_c_evidence_tier.py` contains a `compute_kappa()`
used in the `--validate` Phase 2A benchmark, comparing LLM Call A (internal
knowledge) vs Call B (evidence force) on a 14-pair ground-truth set. That κ is an
internal diagnostic, never reported in the manuscript, and is distinct from the
RS1–RS6 agreement above.
