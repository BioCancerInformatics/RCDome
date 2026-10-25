# TRACEABILITY — Figure renumbering: promote S1 → main Figure 2 (Option B) (2026-10-24)

## Decision
Promote **Figure S1 (Evaluation Architecture)** into the main manuscript as **Figure 2** (inserted after the pipeline, before the results) — "framework early". Agreed by PI; justified as the paper's conceptual skeleton (no app equivalent).

## Renumbering map
| Old | New |
|---|---|
| Figure 2 (benchmarks) | Figure 3 |
| Figure 3 (death core) | Figure 4 |
| Figure 4 (gene coverage) | Figure 5 |
| Supplementary Figure S1 (architecture) | **Figure 2 (main)** |
| Supplementary Figure S2 (DB contribution) | Supplementary Figure S1 |
| Supplementary Figure S3 (source classification) | Supplementary Figure S2 |

## Implemented (direct XML — EndNote fields preserved)
1. **Manuscript** (`RCDome_manuscript_governance_V027.docx`):
   - In-text call-outs renumbered (placeholder-safe order).
   - New **Figure 2 legend** (Evaluation Architecture) inserted after Figure 1 legend.
   - Legends renumbered 2→3, 3→4, 4→5.
   - Word count line 17,268 → **17,267** (the S1→Figure 2 rename dropped one word).
   - **EN.CITE fields: 105 before → 105 after** (citations intact).
2. **Supplementary information**:
   - "Supplementary Figure S1" (architecture) legend **deleted**.
   - S2 → S1, S3 → S2; cross-ref "Figure 4" → "Figure 5".

## Figure files (submission folders only)
- `Submission FAI/Figures/` + `Submission FAI/Figures_A4/` renamed to the new numbering.
- Working folders (`Figures/`, `Figures_A4/`) **reverted to old names** so the `make_figure*` scripts stay in sync (regeneration clean).

## Verification
- First-occurrence order: Figure 1(55) < 2(64) < 3(231) < 4(278) < 5(411) — progressive ✅
- Supplementary: S1(276) < S2(357) ✅

## Propagation
- Manuscript + supplementary info synced to `manuscript_V027/` + `RCDome_distribution/manuscript/`.
- Distribution ZIP rebuilt (397.0 MB) + synced to `Submission FAI/`.
