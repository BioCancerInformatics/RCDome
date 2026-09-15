# RCDome — Master Folder Restructure & Provenance Record

**Date:** 2026-09-06 · **Actor:** Enrique Medina-Acosta (with AI assistance, human-approved)
**Scope:** `D:\Pré-artigo 5-optosis model\Cellular_Spatial_RCD_manuscript\RCDome_manuscript`
**Rule:** RELOCATE ONLY (`mv`) — nothing deleted, nothing excluded. Strict provenance.

---

## 1. Rationale

The master folder accumulated scattered scripts, external reports, and versioned files at
the top level. This restructure separates the **current truth (V026)** from working/archived
material, so future validations or examinations can locate the canonical artifacts without
surprises. Every move is logged below; the source of truth is unchanged (V026).

## 2. Target structure

```
manuscript_V026/     latest manuscript (3 files)
Shiny app/           latest app (kept its name)
output databases/    V026 matrix (truth)
RCDome Decoder/      53x39 decoder + D1
Figures/             Figures 1-4 + S1-S2
docs/                governance + traceability + echo register
extraction code snippets/   (kept)
code/                all scripts (.py/.R)
comms/               emails + feedback
analysis/            Victor_analysis + Drafts + working
external_data/       Elicit/Cuproptosis/Emanuell/PDF/Ris/CSV/JSON
_archive/            all versioned/superseded (preV017/020/024/025, backups, old output)
_scratch/            temporary fragments + __pycache__
```

## 3. Full move log (source → destination)

### → manuscript_V026/ (3)
- RCDome_manuscript_governance_V026.docx
- RCDome_manuscript_V026_supplementary_tables.xlsx
- RCDome_manuscript_V026_supplementary_information.docx

### → code/ (31)
add_front_page.py · add_supplementary_legends.py · build_github_mirror.py ·
capture_gene_catalog.py · capture_raw_views.py · deepest_app_audit.py · final_review_77.py ·
fix_figure_references.py · fix_supplementary_tables.py · fix_v025_rds_2rows.R ·
full_manuscript_conformity_audit.py · global_conformity_audit.py · insert_figure1_legend.py ·
insert_figure2_legend.py · insert_figure4_legend.py · make_figure3_composite.py · make_figure4.py ·
make_figure4_pdf.py · make_figure4_v2.py · make_figure4_v3.py · make_figure_db_contribution.R ·
make_figure_entity_coverage.R · make_figure_source_classification.R · make_v025_zip.py ·
make_variable_dictionary.py · merge_supplementary_notes.py · phase2ad_mini_2pairs.py ·
reorder_phase23.py · replace_figure_legends.py · uniformize_supplementary.py · update_traceability.py

### → docs/ (2)
- Medinas_AI_Governance_Rules_in_Writing_Scientific_Manuscripts.docx
- RCDome_Traceability_Contract.docx

### → comms/ (2)
- emails_coautores/
- feedback/

### → analysis/ (3)
- Victor_analysis/
- Drafts/
- working/

### → external_data/ (26)
Folders: Cuproptosis Elicitfull report 77 genes · Cuproptosis pilot Elicit · Elicit P1 benchmark
results manual download · Elicit searches results · Emanuell crRNA · Emanuell proposal doutorate
UENF · PDF · Ris files · Consensus API · frustrating jason files.
Files: Literature_Search_Results_20260703_104320.csv · all_elicit_association_types.txt ·
unclassified_elicit_genes.txt · RCD_25_Forms_Reference_Table_FINAL.docx/.html ·
RCD_Biological_Context_Decoder.txt · Targeted_RCD_forms.xlsx · AI_Text_Purging_Prompt_General.docx ·
Elicit_Classification_Response.docx · Elicit_Conversation_Log.md · Elicit_Prompt_and_Summary.docx/.md ·
Elicit_RCDome_51_Term_Audit_and_Residual_Discovery_Prompt.docx · Elicit_Saturation_Sweep_Prompt.docx ·
phase2ad_mini_2pairs_result.json · phase2ad_mini_2pairs_result_corrected.json

### → _archive/ (6)
- _archive_preV017/ · _archive_preV020/ · _archive_preV024/ · _archive_preV026/ · _backups/
- output databases_v002 → `_archive/output_databases_v002`

### → _scratch/ (5)
- _intro.txt · _para126.txt · _pending_para.txt · _table_refs.txt · __pycache__/

## 4. Exceptions

- `nul` (340 bytes) — Windows reserved device name; cannot be relocated with standard tools.
  Left in place at top level (garbage file created accidentally; not deleted per provenance rule).

## 5. Verification

- Total items relocated: ~76 (files + folders).
- Nothing deleted; every item has a logged destination.
- Current truth (V026) remains in: `manuscript_V026/`, `Shiny app/`, `output databases/`,
  `RCDome Decoder/`, `Figures/`.

**Prepared for future validations/examinations — no surprises.**

## 6. Addendum — output databases/ archiving (2026-09-06)

Relocated 12 old intermediates/duplicates into `output databases/_archive/` (mv only, nothing deleted):
- unified_gene_rcd_matrix.csv · _original · _validated_original · _via_qc
- normalized.csv · post_qc.csv · raw_merge.csv · step3_normalized.csv
- output databases_v001 · output databases_v002
- RCD_25_Forms_Reference_Table_FINAL.docx/.html (duplicate of external_data/ copy)

Kept in place (provenance): V026 matrix (Phase 2C output), 20 gene_rcd_*.csv per-database
extractions, Phase 2E/3B output, elicit_* folders, source_files_frozen, README.

## 7. Strict audit findings (2026-09-06)

Strict audit of the master folder (compliance/provenance/transparency/honesty/traceability):
- Structure: 13 target folders present, no scattered top-level files (except `nul`). PASS.
- V026 truth intact (manuscript, app, output, decoder, figures). PASS.
- Provenance record complete (rule, move log, nul exception, addendum). PASS.
- Honesty: no hidden files. PASS.
- **Transparency finding — 5 empty folders** (no data inside; kept in place per no-delete rule):
  1. `Shiny app/RCDome_Atlas/APP/data/papers/Overall/Regulated Necrosis/TP53`
  2. `Shiny app/RCDome_Atlas/APP/data/RCD modulo/figuras`
  3. `Shiny app/Emanuell versions/RCDome_V026_update_ERS/data/papers/Overall/Regulated Necrosis/TP53`
  4. `Shiny app/Emanuell versions/RCDome_V026_update_ERS/data/RCD modulo/figuras`
  5. `Shiny app/RCDome_Atlas/Artigo/3°-busca_RCDs`

## 8. Empty-folder resolution (2026-09-06)

The 5 empty folders (Section 7) were DELETED with explicit human approval (Enrique) —
they contained no data, so deleting them loses nothing and improves transparency.
Deletion used os.rmdir (removes only empty directories).

## 9. Narrative audit fixes (2026-09-06)

- Resolved residual TODO placeholder at the end (RCD entities module now presents 53/53 via the decoder, not 25/53).
- Normalized table references: "Supplementary Table S2" -> "Table S2"; "Supplementary Table S5" -> "Table S5" (2x).
- "L5 concepts" retained (correct abbreviation of L5 Generic/umbrella/legacy/taxon/emerging).

## 10. Submission-time checklist (deferred, not forgotten)

Reference/citation items to resolve ONLY at submission time (EndNote workflow):
1. Run EndNote "Format Bibliography" — convert in-text {Author, Year #Record} markers to final (Author, Year) or [n] citations.
2. Ensure the full bibliography includes the 4 references cited but currently missing:
   Cai 2014 (ferroptosis founder) · Sborgi 2016 (GSDMD/pyroptosis) · Tsvetkov 2022 (cuproptosis, Science) · Yang 2014 (GPX4/ferroptosis, Cell).
   (EndNote generates the complete bibliography from its library at format time.)
