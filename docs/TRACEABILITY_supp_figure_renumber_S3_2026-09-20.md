# TRACEABILITY — Supplementary Figure Renumbering (infographic → S1)

**Date:** 2026-09-20
**Driver:** New infographic "Evaluation Architecture of RCDome V026" (English, 600 dpi) added as a supplementary figure.
**Rule:** Figures numbered by order of first citation. The infographic's natural call-out (Methods, evaluation framework) precedes the existing S1/S2 call-outs, so the infographic became **S1** and the existing figures shifted down.

## Renumbering map

| New | Content | Old | File (base) |
|-----|---------|-----|-------------|
| Figure S1 | Evaluation architecture of RCDome (infographic) | *(new)* | `Figure_S1_evaluation_architecture` |
| Figure S2 | Database contribution and multi-database corroboration | was S1 | `Figure_S2_database_contribution` |
| Figure S3 | Mechanistic associations per source, stacked by ontological level | was S2 | `Figure_S3_source_classification` |

## Artifacts updated

1. **Figure files** (`Figures/` + `D:/RCDome_github/docs/figures/`): renamed + new S1 copied (PNG/PDF/TIFF, 600 dpi) + data CSVs.
2. **Main manuscript** `manuscript_V026/RCDome_manuscript_governance.docx`:
   - New S1 call-out added at the evaluation-framework sentence ("…documented in Supplementary Note S1; the complete evaluation architecture … is summarized in Supplementary Figure S1").
   - "(Supplementary Figure S1)" → "(Supplementary Figure S2)"; "(Supplementary Figure S2)" → "(Supplementary Figure S3)".
3. **Supplementary information** `manuscript_V026/RCDome_manuscript_supplementary_information.docx`:
   - New S1 legend inserted; existing S1 legend → S2; existing S2 legend → S3.
4. **Code** (main + GitHub mirror): `add_supplementary_legends.py`, `merge_supplementary_notes.py`, `make_figure_db_contribution.R`, `make_figure_s2_stacked_by_level.py` → renamed `make_figure_s3_stacked_by_level.py`, `make_figure_source_classification.R`, `final_review_77.py`, `manuscript_v026_deep_audit.py`, `build_github_mirror.py`, `full_manuscript_conformity_audit.py`.
5. **Docs/changelogs**: `RCDome_distribution/CHANGELOG_V026_6.md`, `docs/TRACEABILITY_V026_auditoria_2026-09-19.md`, `HIGOR_CORRECTIONS_APPLIED.md` (2 copies).
6. **Source folder** `analysis/Victor_analysis/…/Versões do infográfico nomeclatura/`: English deliverables renamed to `Figure_S1_evaluation_architecture.{png,pdf,tiff}`; Portuguese source kept as `Nomeclatura_4K_PT_source.png`.

## Scripts (re-runnable, in `code/`)
- `translate_infographic_EN.py` — generates the English infographic (600 dpi PNG/PDF/TIFF).
- `renumber_supp_figures.py` — docx renumbering (with backups).
- `renumber_supp_figures_universal.py` — code/docs/GitHub propagation.

## Verification
- Governance + supplementary docx both resolve to: S1, S2, S3 (in order).
- No stale `Figure_S1_database_contribution` / `Figure_S2_source_classification` filenames remain (only inside the migration script's own mapping table).
- Main `Figures/` and `D:/RCDome_github/docs/figures/` are identical for the three S-figures.
