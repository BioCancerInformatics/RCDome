# RCDome — Figure code (single source of truth)

All figure-generation scripts live here. Each script emits the figure in **three formats at once** (PDF + PNG + TIFF) into `RCDome_manuscript/Figures_A4/` (the dedicated A4 output folder — originals stay in `Figures/`).

| # | Figure | Script | Output (in `Figures_A4/`) |
|---|---|---|---|
| 1 | Figure 1 (main) | `make_figure1_flowchart.R` | `Figure_1_pipeline_A4.{pdf,png,tiff}` |
| 2 | Figure 2 (main) | `make_figure2_benchmarks.R` | `Figure_2_benchmarks_A4.{pdf,png,tiff}` |
| 3 | Figure 3 (main) | `make_figure3_composite.py` | `Figure_3_A4.{pdf,png,tiff}` |
| 4 | Figure 4 (main) | `make_figure4_entity_coverage.R` | `Figure_4_entity_coverage_A4.{pdf,png,tiff}` |
| S1 | Figure S1 (suppl.) | `make_figureS1_infographic_EN.py` | `Figure_S1_evaluation_architecture_A4.{pdf,png,tiff}` |
| S2 | Figure S2 (suppl.) | `make_figureS2_db_contribution.R` | `Figure_S2_database_contribution_A4.{pdf,png,tiff}` |
| S3 | Figure S3 (suppl.) | `make_figureS3_stacked_by_level.py` | `Figure_S3_source_classification_A4.{pdf,png,tiff}` |

## Provenance note
- `make_figure2_benchmarks.R` was recovered from the *sibling* ML project folder (`Machine learning CancerRCDShiny_prediction/Enrique version/generate_rcdome_benchmark_figure.R`, dated 2026-10-06) and relocated here on 2026-10-24 to close the provenance gap.
- The older `code/make_figure_source_classification.R` is a pre-renumber duplicate of S3; the `.py` above is the current truth.

## Regenerate everything (A4 pass, when authorized)
Run the scripts in `#` order; each overwrites its three formats in `Figures_A4/`.
