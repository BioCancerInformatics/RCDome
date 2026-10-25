# TRACEABILITY — Figure code centralization + A4 pass (2026-10-24)

## 1. Centralization — one folder: `code/figure_code/`
All 7 figure generators live in **`code/figure_code/`** (indexed in `README.md`).

| Figure | Canonical script | Origin |
|---|---|---|
| Figure 1 | `make_figure1_flowchart.R` | grViz/DiagrammeR — recovered from ML sibling project |
| Figure 2 | `make_figure2_benchmarks.R` | recovered from ML sibling project |
| Figure 3 | `make_figure3_composite.py` | `code/` |
| Figure 4 | `make_figure4_entity_coverage.R` | `code/` |
| Figure S1 | `make_figureS1_infographic_EN.py` | OCR-translation (see §4) |
| Figure S2 | `make_figureS2_db_contribution.R` | `code/` |
| Figure S3 | `make_figureS3_stacked_by_level.py` | `code/` |

Deprecated (kept for provenance, do NOT regenerate):
- `make_figure1_flowchart_DEPRECATED.py` (Python recreation — wrong boxes/arrows; grViz is canonical).
- `make_figure_source_classification.R` (pre-renumber duplicate of S3).

## 2. A4 pass — dedicated `Figure_A4/` folder
- Output goes to **`Figure_A4/`** (originals remain in `Figures/` as backup).
- All 7 → exact A4 (portrait 21.0×29.7 cm or landscape 29.7×21.0 cm), **600 DPI**, **3 formats** (PDF + PNG + TIFF).
- DPI compliance verified: **14/14 raster files @ 600 DPI** (fixed Figure_1 PNG which lacked DPI).

## 3. Figure-specific layout fixes (all via code, no pixels)

**Figure 1** — canonical grViz generator (uniform boxes + correct 45°/straight arrows).

**Figure 2** — panel labels → **(A)/(B)/(C)** pinned near the left margin (`grconvertX(0.02,'ndc','user')`, aligned vertically); titles stay centered.

**Figure 3** —
- fonts scaled up (ticks 8→11, bars 9→11, titles 11→13, bullseye 8→10);
- panel labels → **(A)/(B)/(C)/(D)** at x=-0.28 (aligned column);
- (D) title font 13→11 (no overlap with label);
- "REGULATOR" pushed down inside the blue ring (`y-0.06`);
- panel (A) x-axis widened 0→18,000 so the "Uncertain" bar (16,642) + label fit inside;
- bullseye enlarged (`R3=1.35`, inner rings ×1.35, axes ±1.4).

**Figure 4** — fonts scaled up (y-names 0.52→0.68, bar numbers 0.52→0.68, legend 0.65→0.85, base 0.9→1.1).

**Figure S1 (OCR)** —
- `Unsupported EXECUTOR rate` box-width constraint (non-COL uses box width);
- `LEFT_TXT` corrected/expanded so bullet texts render **left-aligned**:
  `{Allow-list compliance, Vocabulary compliance, Unsupported EXECUTOR rate, Traceability, evidence_maturity, species_scope, relationship_type, parent_entity}`;
- bullet-erase border fix **attempted and reverted** (border-gap left as source has it — no pixel patching).

**Figure S2** — panel labels → **(A)/(B)** moved to left margin + aligned; fonts scaled up (y-names 0.65→0.8, bar numbers 0.55→0.9, x-names 0.85→1.05, base 0.9→1.1).

**Figure S3** — fonts scaled up (bar numbers 6.5→8.5, y-ticks 7→9, x-ticks 8→10.5, x-label 9→11.5, title 10.5→13, legend 7→9 / title 7.5→9.5).

## 4. Figure S1 provenance note (honesty contract)
- The **true canonical generator** is `make_infographic_EN.py` (matplotlib, from-scratch) — recovered from `RCDome_GitHub/...backup.../code/figures/`.
- A from-scratch V027 reconstruction was attempted and **reverted** (layout unacceptable).
- Current S1 is therefore still the **OCR-translation** script with the §3 fixes. The OCR approach is a known derivative; a future from-scratch rebuild remains the correct end-state (not yet achieved).

## 5. Principle (binding)
1. No pixel-patching generated figures.
2. No re-rendering from raster derivatives.
3. Regenerate only from canonical source code.
