# PROCEDURE — Evidence-First Sweep Runbook (post-delta round)

## Purpose

When the ~938 delta rows (PENDING_DELTA) are adjudicated and the matrix is re-merged,
repeat this exact sequence to propagate the evidence-first values to every artifact.

## 0. The evidence-first reference table (unique pairs, 21,568)

| Vocabulary | Value | Count |
|---|---|---|
| mechanistic | NO · YES · OUT_OF_CONTEXT | 15,589 · 4,881 · 160 |
| role | UNCERTAIN · REGULATOR · EXECUTOR · MARKER | 11,800 · 8,369 · 367 · 94 |
| direction | UNCLEAR · PROTECTS · PROMOTES | 12,270 · 4,181 · 4,179 |
| decision_status | AGREED_LABEL_ABSTRACT · UNIFORM_PIPELINE · PENDING_DELTA | 13,737 · 6,893 · 938 |
| abstract_check | INSUFFICIENT · CONFIRMED · DIFFERENT_VIEW | 13,019 · 481 · 237 |

Matrix rows: 22,473 × 100 columns (83 original + 11 adjudication + 6 mapped-vote helpers).

## 1. Matrix re-merge

1. `python3 code/build_matrix_additive_columns.py` (restore 83-col first from GitHub HEAD, then merge).
2. `Rscript code/add_mapped_vote_columns.R` (adds `gpt/curator_1/curator_2_mapped_role/dir`).
3. `Rscript code/precompute_disc_df.R` (rebuild `data/adjudication/disc_df.rds`, 7,905+ rows).
4. Sync CSV + RDS to `output databases/Phase 2C output/`, `D:/RCDome_github/app/data/`, `D:/RCDome_github/data/`.

## 2. App RCDome

- `global.R` — `rcd_counts` (ef_exec/ef_reg/ef_mech) + the curator-renamed columns.
- `mod_gene_catalog.R` — 7-source selector (evidence default), Adjudication filter, Evidence-first column, death-core 367, landing Evidence-first line, detail-card Evidence-first block.
- `mod_network.R` — 7-source selector.
- `mod_discrepancy.R` — 7-layer table, 6-dot concordance, All axis, Gene+Entity filters, heading, PENDING badge.
- `server.R` — Evidence Trail card (7 decisions, mapped votes, NO_SOURCE_ANNOTATION, ellipsis).
- `mod_board.R` + `mod_board_qa.R` — add `final_*` + `decision_status` to the payload/lines.
- `www/explore.html` — Evidence-first line + death-core 367/8,369.

## 3. Manuscript + supplementary + figures

- `RCDome_manuscript_governance_V027.docx` — abstract/results/discussion/legends → evidence-first.
- `..._supplementary_information.docx` — disagreement 7,905, third-opinion 7,892, Figure S3 legend.
- `..._supplementary_tables.xlsx` — Matrix Descriptor (100 columns, curator_* helpers).
- `generate_rcdome_flowchart.R` (Figure 1, 100 cols) · `make_figure3_composite.py` (death core + mechanistic-by-level) · `make_figure_entity_coverage.R` (Figure 4) · `make_figure_s3_stacked_by_level.py` (final_mechanistic) · `make_figure_db_contribution.R` (Figure S2, V027).

## 4. README + changelog

- `D:/RCDome_github/README.md` — 100 columns, 367/8,369/94/11,800, direction 4,179/4,181.
- `CHANGELOG_V027.md` — append a new delta-round entry (do NOT rewrite history).

## 5. Verification

Run the 21-check audit (unique pairs + all vocabulary sums + abstract_check = agreement pool)
against the truth matrix. Every number in the table must reconcile.

## 6. Rebuild + ship

1. `python3 code/build_distribution.py` (pre-flight `ok: TRUE`).
2. `git add -A && git commit && git push origin main`.
