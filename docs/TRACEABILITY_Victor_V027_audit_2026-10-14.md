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


## H27 — Discussion rounds 5,826/9,265 to "64%" (ACTIONABLE, MODERADA)

- Fact: manuscript Discussion ¶398 said "64% of the 9,265 genes"; truth = 5,826/9,265 = 62.882%
  = 62.9% (verified in the matrix: 9,265 genes, 5,826 with >=1 YES).
- Fix: "64%" -> "62.9%" (one decimal, matching the manuscript's 45.4%/54.6%/4.8%/95.2% convention).
- Backup: RCDome_manuscript_governance_V027_pre_H27_2026-10-14.docx.


## H28 (Figure 3C) — citation + regeneration

- Figure 3C (Direction panel) was hard-coded to 5,025 PROMOTES (the "fully repaired" assumption),
  inconsistent with the matrix after H22 (5,035; 10 Group-B pending human verdicts).
- Fix: make_figure3_composite.py now reads the matrix dynamically (unique pairs) for the role and
  direction counts; the Direction panel shows the live truth and a footnote "10 pairs pending human
  curator verdicts (PROMOTES vs UNCLEAR)".
- Regenerated 2026-10-14: Figure_3.pdf/.png/.tiff. Will be regenerated again when the 10 verdicts return.
- (The ¶398 Figure 3C citation itself is addressed in H28's citation fix next.)


## H28 (cont.) — manuscript 5,025 -> 5,035 (stale "fully repaired" count)

- The Discussion + Figure 3 legend carried "5,025 promoters/promote" (the fully-repaired assumption),
  inconsistent with the matrix after H22 (5,035; 10 pending).
- Fix: all three "5,025" -> "5,035"; Discussion sentence annotated "(10 pairs pending human curator verdicts)".
- Backup: RCDome_manuscript_governance_V027_pre_5025_2026-10-14.docx.


## Dynamic-figure strategy (applied across figures, 2026-10-14)

Following the Figure 3C pattern (single source of truth = the matrix), the other figures now read
the matrix dynamically or were corrected for stale captions:

- Figure 3 (make_figure3_composite.py): role + direction counts read the matrix (unique pairs);
  Direction panel has the "10 pending human verdicts" footnote.
- Figure 1 (make_figure1_flowchart.py): consolidation box now reads the matrix (rows/genes/entities/columns).
- Figure 4 (make_figure4.py + make_figure4_v3.py): captions corrected "21,569 associations" ->
  "21,568 unique gene–RCD pairs", "Elicit" -> "Compiled gene role", "469 executors" -> "469 executor pairs".
- Figure S3 (make_figure_s3_stacked_by_level.py): already dynamic (reads the matrix).


## Figure 1 formatting fix (canonical generator restored)

- My first "dynamic" pass regenerated Figure 1 with the Python recreation
  (make_figure1_flowchart.py), which overflowed box text and misplaced arrows.
- Root cause: the canonical generator is generate_rcdome_flowchart.R (grViz + stri_wrap),
  which auto-wraps text and auto-spaces arrows. The Python script was a stopgap from when
  R/DiagrammeR were unavailable.
- Fix: updated the R script to read the matrix dynamically (rows/genes/entities/columns) and
  regenerated Figure 1 with it (4961x7016 @600 DPI). Python recreation marked DEPRECATED.


## H29 — Table S5 source-dependent mappings (fixed)

- Problem: S5 showed simple mappings but hid the source-dependent splits for "Lysosomal cell death"
  (iPCD -> Lysosome-dependent; XDeathDB -> Lysosomal) and "Mitotic death"
  (FerrDB -> Mitotic catastrophe; Elicit/XDeathDB -> Mitotic death).
- Fix: regenerated Table S5 from the frozen matrix; added a "Conditioning Source" column and made
  the two split mappings explicit (15 data rows). Non-split rows marked "—".
- Backup: RCDome_manuscript_V027_supplementary_tables_pre_H29_2026-10-14.xlsx.


## H30 — INDEX "Entosis" -> "Entotic cell death" (fixed)

- The INDEX described Table S5 with the example "both map to 'Entosis'", but the canonical
  rcd_form_canonical is "Entotic cell death" (Entosis is only an original source name).
- Fix: INDEX Table S5 entry now says "...both map to 'Entotic cell death'", title "15 mappings",
  dimensions "16 rows x 4 cols", and mentions the source-dependent splits added in H29.
- Backup: RCDome_manuscript_V027_supplementary_tables_pre_H30_2026-10-14.xlsx.


## H31 — Table S9 PMID count (fixed)

- S9 said "22,217 of 22,473 with PMIDs (98.8%)" — stale. The frozen matrix has
  22,187 rows (98.7%) with >=1 traceable PMID (7-8 digit, any of pmid_list/llm_pmids/epmc_pmids/elicit_pmids),
  and 21,283 of 21,568 unique pairs. This matches Victor's suggested 22,187/98.7%.
- Fix: S9 rows "Publications indexed" + "Per-gene PMID traceability" updated to 98.7% / 22,187.
- Manuscript Results ¶300 already carried the correct 22,187 / 21,283 / 98.7% (no manuscript change).


## H32 — Table S9 units mismatch (fixed)

- "Publications indexed" row conflated FerrDB ">20,000" (publications) with RCDome
  "21,568 unique gene-RCD pairs" (pairs) — methodologically invalid comparison.
- Fix: split into "Publications / literature records indexed" (FerrDB >20,000; RCDdb not specified;
  RCDome 319,548 distinct PMIDs referenced) and "Unique gene–RCD pairs" (RCDome 21,568, 100% validated).
  Added a header note defining per-row metrics. INDEX dims updated to 16 rows x 4 cols.
- Backup: RCDome_manuscript_V027_supplementary_tables_pre_H32_2026-10-14.xlsx.


## H32 (correction) — publications count not DeepSeek-inflated

- The first H32 fix used "319,548 distinct PMIDs", but that is 81% llm_pmids (258,568) —
  the DeepSeek abstract-level extraction, not a true "publications indexed" figure.
- Corrected to "123,188 distinct full-text PMIDs (Europe PMC, Phase 2B)" — the full-text papers
  RCDome actually retrieved and verified. Curated/verified columns only.


## H33 — Ferroptosis benchmark denominator (fixed)

- S13 said Ferroptosis allow-list = 1,715; Methods/Table S3 said 1,724. Root cause: the benchmark
  auto-populated its allow-list from the V013 matrix snapshot (1,715), while the current V027 matrix
  carries 1,724 (9 genes added after the freeze). Retroactively changing the denominator would be
  methodologically wrong.
- Fix: preserved 1,715 in S13 with a note (V013 snapshot); corrected Methods ¶237 + ¶336 to
  "1,715 ... at the V013 benchmark snapshot" and noted 1,724 as the current V027 count.
- Verified V013 Ferroptosis=1,715 / Cuproptosis=77 / Triaptosis=3; V027 Ferroptosis=1,724.
- Backups: _pre_H33_2026-10-14.docx/.xlsx.


## H33 (revision) — align to V027 truth (1,724), no snapshot framing

- Per curator decision, the "preserve the V013 snapshot" framing was rejected as a workaround.
- Truth = V027: Ferroptosis allow-list is 1,724. Since the benchmark's allow-list enforcement
  rejected 0 of the 393 raw records (raw = post-governance), widening 1,715 -> 1,724 does not
  change papers/records/governance — only the allow-list count.
- Fix: S13 Ferroptosis 1,715 -> 1,724 (Total 1,804), note removed; manuscript ¶237 + ¶336
  reverted to clean "1,724" (no snapshot note).
