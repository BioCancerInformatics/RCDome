# Terminology Fix Traceability Log

Date: 2026-09-15 10:49

Adjudication rule: canonicalized-vocabulary membership ≠ biological canonicality. “canonical” (vocabulary) → “canonicalized” / “RCD-related”. Stale numbers corrected to manuscript truth (22,473 rows; 71 columns; 21,568 pairs; 53 entities).

| # | File | Old | New | Category | Result |
|---|---|---|---|---|---|
| 1 | `code/figures/make_figure1_flowchart.py` | 53 canonical entities (62 name strings) | 53 canonicalized RCD-related entities (62 name strings) | TERM | OK x1 |
| 2 | `code/figures/make_figure_entity_coverage.R` | Gene coverage of the 53 canonical RCD entities | Gene coverage of the 53 canonicalized RCD-related entities | TERM | OK x1 |
| 3 | `code/make_figure_entity_coverage.R` | Gene coverage of the 53 canonical RCD entities | Gene coverage of the 53 canonicalized RCD-related entities | TERM | OK x1 |
| 4 | `code/insert_figure1_legend.py` | strings into 53 canonical RCD entities, producing 22,474 gene–RCD rows | strings into 53 canonicalized RCD-related entities, producing 22,473 gene–RCD rows | TERM+NUM | NOT FOUND |
| 5 | `code/insert_figure1_legend.py` | final consolidated matrix (22,474 rows | final consolidated matrix (22,473 rows | NUM | OK x1 |
| 6 | `code/decoder/insert_figure1_legend.py` | strings into 53 canonical RCD entities, producing 22,474 gene–RCD rows | strings into 53 canonicalized RCD-related entities, producing 22,473 gene–RCD rows | TERM+NUM | NOT FOUND |
| 7 | `code/decoder/insert_figure1_legend.py` | final consolidated matrix (22,474 rows | final consolidated matrix (22,473 rows | NUM | OK x1 |
| 8 | `code/insert_figure4_legend.py` | 53 canonical entities, 9,265 genes and 21,569 association pairs | 53 canonicalized RCD-related entities, 9,265 genes and 21,568 association pairs | TERM+NUM | OK x1 |
| 9 | `code/replace_figure_legends.py` | strings into 53 canonical RCD entities, yielding 22,474 gene–RCD association rows | strings into 53 canonicalized RCD-related entities, yielding 22,473 gene–RCD association rows | TERM+NUM | NOT FOUND |
| 10 | `code/replace_figure_legends.py` | (22,474 rows and 67 columns) | (22,473 rows and 71 columns) | NUM | OK x1 |
| 11 | `code/extraction/README.md` | Queries all 32 canonical RCD forms via E-utilities API | Queries all 32 RCD forms via E-utilities API | TERM | OK x1 |
| 12 | `code/extraction/channel_b_ncbi_gene.py` | Searches NCBI Gene for all 32 canonical RCD forms | Searches NCBI Gene for all 32 RCD forms | TERM | OK x1 |
| 13 | `code/extraction/channel_b_phase2_new_forms.py` | canonical RCD form name | canonicalized RCD form name | TERM | OK x1 |
| 14 | `code/extraction/channel_b_xdeathdb.py` | Map 12 RCD forms to RCDome canonical forms | Map 12 RCD forms to RCDome canonicalized RCD-related forms | TERM | OK x1 |
| 15 | `code/extraction/phase2b_rag/channel_c_deep_xml_rag.py` | RCD form vocabulary (54 canonical forms) | RCD form vocabulary (53 canonicalized forms) | TERM+NUM | OK x1 |
| 16 | `code/generate_detail_page.py` | (${entityNames.length} canonical entities) | (${entityNames.length} canonicalized RCD-related entities) | TERM | OK x1 |
| 17 | `code/make_variable_dictionary.py` | The normalized canonical RCD form name (one of 53 canonical forms). | The canonicalized RCD-related form name (one of 53 canonicalized forms). | TERM | OK x1 |
| 18 | `code/make_variable_dictionary.py` | "53 canonical forms" | "53 canonicalized forms" | TERM | OK x1 |
| 19 | `code/decoder/add_provenance.py` | per canonical entity | per canonicalized RCD-related entity | TERM | OK x1 |
| 20 | `app/modules/mod_network.R` | One edge per (gene, canonical entity) | One edge per (gene, canonicalized RCD-related entity) | TERM | OK x1 |
| 21 | `app/global.R` | exactly one canonical RCD pathway | exactly one RCD-related pathway | TERM | OK x1 |
| 22 | `app/modules/mod_board_qa.R` | canonical name or its stem | canonicalized name or its stem | TERM | OK x1 |
| 23 | `docs/dome.html` | 53 canonical entities | 53 canonicalized RCD-related entities | TERM | OK x1 |
| 24 | `docs/decoder/MandM_operational_definitions.md` | The RCDome canon comprises 53 canonical RCD entities | The RCDome canon comprises 53 canonicalized RCD-related entities | TERM | OK x1 |
| 25 | `docs/decoder/MandM_operational_definitions.md` | The canonical vocabulary is fixed at V026 | The canonicalized vocabulary is fixed at V026 | TERM | OK x1 |
| 26 | `docs/manuscript/MandM_operational_definitions.md` | The RCDome canon comprises 53 canonical RCD entities | The RCDome canon comprises 53 canonicalized RCD-related entities | TERM | OK x1 |
| 27 | `docs/decoder/RCD_Board_DeepSeek_Prompt.md` | one of the 53 canonical RCD entities | one of the 53 canonicalized RCD-related entities | TERM | OK x1 |
| 28 | `docs/decoder/Supplementary_Note_S4_Board_Benchmark.md` | by canonical name or its | by canonicalized name or its | TERM | OK x1 |

**Summary:** 28 fixes | 25 applied | 3 not-found | 0 errors

**Addendum (literal – escape):** 3 fixes re-applied with raw-string matching.

**Addendum 2:** 5 residual fixes (global.R comments, MandM line 5, Results_OD_census line 3).

**Addendum 3:** update_traceability.py + Example_RCDome_Board_BAX_Apoptosis.html.

**Addendum 4:** deep_audit.py + verbatim_audit.py (audit-script descriptive terms).
