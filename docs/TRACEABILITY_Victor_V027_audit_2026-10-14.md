# TRACEABILITY — Victor V027 audit (H21–H55) applied (2026-10-14)

Source: analysis/Victor_analysis/Victor assesment app manusicritp and supplementary material/RCDome_V027_relatorio_auditoria_APP_MANUSCRITO_SUPLEMENTAR.docx
Protocol: one finding at a time; deep audit of the truth artifacts; classification; apply with provenance.

## H23 + H24 + H25 + H48 — hard-coded counters (ACTIONABLE, HIGH)

- H23: Gene Catalog header had hard-coded "10,016 mechanistic · 469 executors · 9,489 regulators"
  (truth: 9,785 YES / 469 EXECUTOR / 9,311 REGULATOR).
- H24: Explore RCDome showed "21,569" (truth: 21,568 unique pairs).
- H25: "469 EXECUTORS" mixed pairs vs genes (truth: 469 executor PAIRS).
- H48: "21,568 associations" was ambiguous (truth: 21,568 unique gene–RCD pairs).

Fix:
- global.R: added `rcd_counts` (derived from the matrix unique pairs: n_genes, n_pairs,
  mech_yes, role_exec, role_reg) — single source of truth.
- mod_gene_catalog.R: header now renders from `rcd_counts` (formatted), and labels:
  "21,568 unique gene–RCD pairs", "9,785 mechanistic", "469 executor pairs", "9,311 regulator pairs".
- www/explore.html: "21,569" -> "21,568"; "executors" -> "executor pairs".

Verified: rcd_counts = 9,265 genes / 21,568 pairs / 9,785 YES / 469 exec / 9,311 reg.
