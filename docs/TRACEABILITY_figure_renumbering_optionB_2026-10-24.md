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


## Correction (2026-10-25) — benchmark figure panel order fixed
The benchmark figure's panel order was re-aligned to the EXECUTION order:
- **A = DeepSeek**, **B = Consensus**, **C = Elicit** (Consensus is Phase 2G, Elicit is Phase 3 — so Consensus precedes Elicit).
- `make_figure2_benchmarks.R` panels B/C swapped (Elicit↔Consensus), figure regenerated + copied to `Submission FAI/Figures_A4/Figure_3_benchmarks_A4.*` and short-name `Submission FAI/Figures/Figure_3.*`.
- Manuscript legend updated: (A) DeepSeek, (B) Consensus, (C) Elicit + color legend (green = A+B, salmon = A+B; post/pre-governance = C).
- In-text call-outs re-lettered (3B = Consensus, 3C = Elicit) and text order restored to DeepSeek → Consensus → Elicit.
- First mentions now ascending: 3A(230) < 3B(234) < 3C(239). EndNote fields 105 preserved.


## Figure 4 panel-order fix (2026-10-25)
- Figure 4 (death core) first-mention order corrected from A-C-B-D to **A-B-C-D**.
- Removed the early '(Figure 4C)' from the Results paragraph (direction is now first cited in the Discussion after 4B).
- Verified: 4A(281) < 4B(409) < 4C(411) < 4D(411). EndNote fields 105 preserved.


## Figure S1 panel call-outs added (2026-10-25)
- Added a real S1A mention (per-source contribution, 2 Elicit Alert to 10,131 Rodrigues) at the compendium-composition sentence; corrected the corroboration call-out to S1B. Order now S1A(253) < S1B(279). EndNote 105 preserved.


## Figure S1 call-out finalized (2026-10-25)
- S1A = per-source associations (legend-coherent wording), numbers extracted from Dataset S1 (source_databases): 2 (Elicit Alert) to 10,131 (Rodrigues et al. 2025).
- S1B = corroboration (10,009 single-source...).
- Order S1A(253) < S1B(279). EndNote 105 preserved.


## Final triple audit + sync (2026-10-25)
- All figures + supplementary figures + panels audited across BOTH the main manuscript and supplementary information.
- Verified: every panel called out, ascending order (A→B→C→D), legend-coherent content, supplementary renumbering fully propagated, no stray Figure 2/3/4.
- Figures 3 (A=DeepSeek, B=Consensus, C=Elicit), 4 (A=Role, B=Mechanistic, C=Direction, D=Core), S1 (A=per-source, B=corroboration) all correct.
- Manuscript + supplementary synced (md5 3a0d72ba...); ZIP rebuilt (397.0 MB) + synced.

## Archival-sync (Submission FAI = truth) — 2026-10-25 02:38
- Codified "Submission Folder Protocol" in the Traceability & Governance Contract: `Submission FAI/` = single source of truth; mirrors (`manuscript_V027/`, `RCDome_distribution/manuscript/`) are one-way mirrors.
- Executed archival-sync: old mirror copies archived to `_archive_backups/20261025_023829_submission_fai_truth_sync/`, then replaced with truth files, md5-verified == truth.
- Manuscript re-saved at 02:34 (Word) — content verified intact (EN.CITE=105, all figure call-outs present); ZIP rebuilt (md5 2109ef6f…) + synced.
- Files verified identical: manuscript abe9809a…, supplementary cbd38f9c…, tables aefdffbe…, ZIP 2109ef6f….

## Figure 4 panel-label alignment fix — 2026-10-25
- Issue: labels (B) and (D) misaligned vertically (panel D's `set_aspect('equal')` shrinks its axes, shifting the `transAxes` label).
- Fix: removed per-panel `ax.text(-0.28,1.02,transAxes)` labels; placed all four labels in figure coordinates after `tight_layout()`, using `_posB.x0` for BOTH (B) and (D) and `_posC.x0` for (C).
- Verified via PDF text extraction: (B)x0=(D)x0=466.4, (A)x0=(C)x0=58.6 pts.
- Regenerated from canonical script `code/figure_code/make_figure3_composite.py`; propagated to `Submission FAI/Figures_A4/Figure_4_A4.*` + `Submission FAI/Figures/Figure_4.*` (md5 969cd44d…).

## Figure 4 non-A4 render restored (design: Figures/ = non-A4, Figures_A4/ = A4) — 2026-10-25
- Design clarification: `Submission FAI/Figures/` holds ORIGINAL non-A4 renders (short names); `Submission FAI/Figures_A4/` holds A4 resizes. My earlier A4 overwrite of `Figures/Figure_4` was reverted.
- Added canonical non-A4 variant `code/figure_code/make_figure3_composite_nonA4.py` (figsize 10.5×8, bbox_inches tight, V027 final_role/final_direction) with the SAME figure-coordinate label fix.
- Regenerated: `Figures/Figure_4.*` non-A4 6240×4778, (B)x0=(D)x0=450.9 pts; `Figures_A4/Figure_4_A4.*` A4 7014×4962, (B)x0=(D)x0=466.4 pts. Both aligned.

## Figure 3 narrative refinement (Results integration) — 2026-10-25
- Goal: integrate 3A/3B/3C callouts into the scientific argument; contextualize DeepSeek, Consensus, Elicit roles.
- Edits (direct XML, EN.CITE preserved = 105):
  1. 3A (¶ model-selection): added framing "Figure 3 evaluates the three independent analyses that underpin RCDome's evidence integration — the DeepSeek classifier, the Consensus evidence channel, and the Elicit systematic-review governance." + "three models" → "three DeepSeek model configurations".
  2. 3B (¶ Consensus): added form-biased vs neutral comparison (92%/12% FP vs 100%/0% FP) + interpretation "form-name priming rather than the retrieval channel itself was the source of false positives" (legend-consistent).
  3. 3C (¶ Elicit Benchmark Design): added "This benchmark quantifies the extraction risks described above and tests whether post-export governance neutralizes them."
- No redesign, no data changes; all numbers from the legend. Archived pre-patch to `_archive_backups/20261025_025955_fig3_narrative_refinement/`; mirrors + ZIP synced.

## Figure 3A callout separation — 2026-10-25
- Moved "(Supplementary Note S5; Figure 3A)" out of the section lead-in "Model-selection benchmark" and placed it at the end of the "Figure 3 evaluates the three independent analyses …" sentence, so the header is clean and the callout follows the explanation. EN.CITE preserved = 105. Mirrors + ZIP synced.

## Figure 3A — DeepSeek-only contextualization — 2026-10-25
- Removed the whole-figure "three independent analyses" introduction from the 3A paragraph (it misused the 3A callout).
- 3A callout now contextualized to the DeepSeek model-selection benchmark: "…three DeepSeek model configurations were benchmarked on 26 well-established gene-RCD pairs (10 executors, 8 regulators, and 8 negative controls) (Supplementary Note S5; Figure 3A): …". Header clean: "Model-selection benchmark." EN.CITE = 105. Mirrors + ZIP synced.
