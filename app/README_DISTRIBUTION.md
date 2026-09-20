# RCDome — Collaborator Distribution (copy-only, intentional files only)

This folder reproduces the **live** RCDome Shiny app (the 9 visible tabs), assembled by **copying** from the developer's reference app. The developer's original app was **not** modified. Vestigial signatures/omics/papers/bodymap leftovers are excluded.

## 1. What you received

- `ui.R`, `server.R`, `global.R`, `run.R` — Shiny entry points
- `R/` — helpers (utils, pathways, rcd_modal) + `R/validate_data_files.R` (pre-flight validation)
- `data/gene_info_lookup.json` — 9,264 NCBI Gene summaries for the gene-page "Gene information" block
- `modules/` — all 13 module files (only 6 are live; the rest are sourced but unrendered)
- `www/` — landing, explore, detail, logos, JS
- `board/` — Digital Molecular Board (DeepSeek) prompt, governance, benchmarks
- `data/` — matrix, decoder, HGNC set, RCD modulo (logos/figures/videos/descriptions/references), about (photos/data-sources/see-also), omic (3 lazy sub-tab tables)

## 1b. Included deliverables (V026_8)

- **Ontology**: 53 canonicalized RCD-related entities, final distribution **L1 = 19, L2 = 7, L3 = 2, L4 = 13, L5 = 12** (Victor V026 auditoria, evidence-based G0–G6 re-adjudications).
- **Nomenclature harmonized**: MC1–MC5 (modality criteria), RS1–RS6 (ranking score), QG1–QG5 (quality gates), ET1–ET4 (evidence tier), CT1–CT4 (confidence tier).
- **Supplementary Figure S1**: English infographic “Evaluation architecture of RCDome” (600 dpi) — the three evaluation objects (RCD entity, gene–RCD association, pipeline quality) with their gates, tiers, and levels.
- **Supplementary figures renumbered by first citation**: S1 = evaluation architecture (new) · S2 = database contribution (was S1) · S3 = mechanistic associations per source (was S2).
- **Manuscript package** in `manuscript/`: governance manuscript, supplementary information, supplementary tables (Excel) — version-free filenames — plus `manuscript/figures/` with the three supplementary figures (PNG/PDF/TIFF + data CSVs).

## 2. Already configured — just run

The DeepSeek API key is already present in `.Renviron`, and the email credentials in `data/email_creds.txt`, so the app runs immediately after unzipping. To use your own key instead, edit `.Renviron` (a template is kept at `.Renviron.example`).

## 3. R packages

```r
install.packages(c("shiny","readxl","dplyr","DT","httr","jsonlite","visNetwork",
                   "shinycssloaders","shinyjs","emayili","tidyr","plotly","magick"))
```

## 4. Run

```r
setwd(".../RCDome_distribution")
shiny::runApp(appDir = ".", port = 8890, launch.browser = TRUE)
```

## 5. What was excluded (vestigial files)

| Excluded | Why |
|---|---|
| `data/signatures.tsv/cache` | old signatures app (network only used it for an optional "nomenclature" search) |
| `data/papers/`, `data/disease_terms.tsv`, `www/bodymap/` | dead modules (paper manifest / body map — no UI) |
| `data/gene.xlsx`, `genes_simplificado…`, `data/logo.png`, `www/video_logo.mp4`, `pmid_title_lookup.*` | not referenced by the live app |
| `data/omic/` legacy (gene.xlsx, gene_with_ncbi_info.csv, genes_df_cache.rds) | not referenced; only the 3 lazy sub-tab xlsx are kept |
| old `*.zip`, `.Rhistory`, `_archive_preV024`, `CHANGELOG_*.docx` | non-runtime |

## 6. Pre-flight validation

The app runs `validate_data_files()` at startup — it verifies every bundled asset (matrix, decoder, HGNC, omic tables, NCBI summaries, board prompt, www pages) before serving anything. A broken asset stops the app with a precise message, so it is fixed by the developer before it reaches a user.

## 7. Traceability

- Reference: `Shiny app/RCDome_Atlas/APP` (untouched).
- Audit: `Shiny app/Emanuell versions/RCDome_App_LineByLine_INTENTIONAL_vs_VESTIGIAL.md`.
- ZIP: `RCDome_V026_distribution.zip`.
