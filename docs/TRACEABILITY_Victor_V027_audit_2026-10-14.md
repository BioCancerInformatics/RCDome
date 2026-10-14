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


## H21 — "Elicit vs DeepSeek" mislabeled (ACTIONABLE, ALTA)

- Fact: the "Elicit" role column actually uses `rcd_gene_type`, which is a MULTI-SOURCE field
  (Traceability Contract: "Functional annotation ... Database extraction + Phase 3"), NOT Elicit-only.
  295 rows have rcd_gene_type filled with elicit_evidence_status=none (281 MSigDB + XDeathDB, FerrDB, ...).
- Decision: RENAME, not filter (filtering would discard legitimate multi-source provenance).
- Fix: relabel "Elicit" -> "Compiled gene role" + hover tooltip explaining the content, across:
  - mod_gene_catalog.R: header summary, source-selector label + data-tip, the "RCD Entities" table
    header, entity_compare labels, download data-tip.
  - mod_network.R: edge-source selector label.
  - server.R: Evidence Trail "Classifiers" row label.
- Kept as "Elicit" (genuine Elicit columns, not rcd_gene_type): the verbatim sentence, the ~14% Elicit
  coverage note, and the full-matrix download tip.


## H22 — 45 CoT contradictions (NO + UNCERTAIN + PROMOTES) (ACTIONABLE, ALTA)

- Fact: 45 unique pairs have cot_mechanistic=NO + cot_role=UNCERTAIN + cot_direction=PROMOTES
  (manuscript claims 5,025 PROMOTES = 5,070 - 45, i.e., assumes repair).
- Provenance: Rule 4 (log_rule4_repair.py) repaired "NO + confident ROLE -> UNCERTAIN/UNCLEAR" for 80
  pairs, but did NOT cover the "NO + UNCERTAIN role + confident DIRECTION" pattern — those 45 remained.
- Individual review split them:
  - Group A (35): consensus UNCLEAR -> clean Rule-4b (direction must be UNCLEAR). FIXED.
  - Group B (10): consensus confident (6 REGULATOR + 4 EXECUTOR; 8 PROMOTES + 2 PROTECTS) ->
    genuine DeepSeek-vs-Consensus disagreements -> routed to human curator verdicts (NOT mechanically flattened).
- Fix applied: Group A (35) cot_direction = UNCLEAR. PROMOTES 5,070 -> 5,035.
  Remaining contradictions: 10 (Group B, for human adjudication).
- Backups: unified_gene_rcd_matrix_V027_pre_H22_2026-10-14.csv/.rds.


## H26 — Discrepancy Radar 7,892 vs 7,895 (ACTIONABLE, MODERADA)

- Fact: card/module comment/changelog said "7,892"; the authoritative benchmark text says
  "7,895 arbitrated rows" (6,953 DeepSeek-vs-Consensus + 942 from the full Consensus run:
  866 new + 76 recovered).
- Curator context: these 7,895 rows are the arbitration universe that Victor and Higor are
  adjudicating (the human-resolution worksheets). The card count must equal the arbitration
  total, not a stale earlier figure, so their worksheets and the UI stay in sync.
- Fix: 7,892 -> 7,895 in explore.html, mod_discrepancy.R, CHANGELOG_V027.md.
- No arbitration rows were added/removed — this is a display-count synchronization only.
