# RCDome — Classification Echo Register

**Purpose:** every change to the ontological classification (levels, counts, labels, or entity
assignments) must be echoed to EVERY artifact below. "Echo" means a **functional** update
(verified value-by-value), not a file copy. This register is the checklist for that echo.

**Canonical truth (V026):**

| Level | Label | Count |
|---|---|---|
| L1 | L1 Modalities | 16 |
| L2 | L2 Subtypes | 5 |
| L3 | L3 Triggers | 2 |
| L4 | L4 Functional/contextual | 12 |
| L5 | L5 Generic/umbrella/legacy/taxon/emerging | 18 |

Total 53 entities · 22,473 rows · 21,568 unique pairs · 9,265 genes · 20 databases · 3 analyses
· 469 executors · 9,489 regulators.

**Level ↔ category mapping (decoder → matrix):**
L1 ← Executioner, CORE_RCD_FORM, CORE_PENDING · L2 ← SUBTYPE, SYNONYM · L3 ← Trigger
· L4 ← Functional, CONTEXTUAL, CELL_TYPE, DIFFERENTIATION, MORPHOLOGY, CLEARANCE_PROCESS,
INTEGRATED_PROGRAM · L5 ← CELLULAR_PROCESS, UMBRELLA, LEGACY, TAXON, EMERGING, COMPOSITE.

---

## PRIMARY SOURCES

| # | Artifact | Path | Field(s) carrying the classification |
|---|---|---|---|
| 1 | Matrix (truth) | `output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv/.rds` | `rcdome_level`, `rcdome_level_name` |
| 2 | Decoder | `RCDome Decoder/RCDome_Decoder_53.csv/.xlsx` | `category` (→level), `hard_gate_status` |

## DERIVED ARTIFACTS (must echo #1/#2)

| # | Artifact | Path | Where the classification lives | Check |
|---|---|---|---|---|
| 3 | D1 adjudication | `RCDome Decoder/D1_adjudication_table.csv/.xlsx` + workbook Table S12 | `pre_adjudication_level`, `adjudicated_level` | 53 rows |
| 4 | Manuscript ¶31 | `manuscript_V026/RCDome_manuscript_governance_V026.docx` | "16 modalities … 5 subtypes … 2 triggers … 12 functional/contextual … 18 generic/umbrella/…" | grep "16 RCD modalities" |
| 5 | Manuscript ¶46 | idem | hard gates G0–G6 + 16/5/2/12/18 | grep "G0-G6" |
| 6 | Manuscript ¶240 | idem | "16 RCD modalities, 5 subtypes, 2 triggers, 12 functional/contextual…, 18 generic/…" | grep "16 RCD modalities" |
| 7 | Manuscript ¶334 | idem | "16 bona fide RCD modalities…" | grep "16 bona fide" |
| 8 | Manuscript ¶364 (Fig 3) | idem | "L4 Functional/contextual…, L5 Generic/umbrella/legacy/taxon/emerging" | grep "Functional/contextual" |
| 9 | Manuscript ¶367 (Fig 4) | idem | idem | idem |
| 10 | Figure 4 | `Figures/Figure_4_entity_coverage.pdf/.png/.tiff` | bar colors by `rcdome_level` | regenerate via `make_figure_entity_coverage.R` |
| 11 | Workbook Matrix Descriptor | `manuscript_V026/RCDome_manuscript_V026_supplementary_tables.xlsx` | L1–L5 level names (rows 7–8) | grep "Functional/contextual" |
| 12 | Workbook Table S4 | idem | 53-form vocabulary with category | 54 rows |
| 13 | Workbook Variable Descriptor | idem | descriptions of `rcdome_level`, `rcdome_level_name` | grep "L4 Functional/contextual" |
| 14 | App dome (live) | `Shiny app/RCDome_Atlas/APP/www/landing_page.html` | `LEVEL_COUNTS`, `LEVEL_NAMES`, `DATA.entities` | grep `"L1": 16` |
| 15 | App dome (prototype) | `.../www/dome_prototype.html` | idem | idem |
| 16 | App detail page | `.../www/detail_page_wireframe.html` | `LEVEL_NAMES`, `DATA` entity levels | grep Anoikis `"level": "L2"` |
| 17 | App explore | `.../www/explore.html` | stats (9,265/53/21,568/20/3/469), level text | grep "16 modalities" |
| 18 | App Gene Catalog | `.../modules/mod_omic.R` | `level_class()`, `rcdome_level_name`, tip text | grep "Functional/contextual" |
| 19 | App RCD grid | `.../modules/mod_rcd_grid.R` | entity list (53 from decoder), decoder description builder | 53 entities |
| 20 | App generators | `Shiny app/generate_dome.py`, `Shiny app/generate_detail_page.py` | matrix path (V026), `LEVEL_NAMES`, `short()` map | grep "V026" |
| 21 | App wireframe | `Shiny app/landing_page_wireframe.html` | legend counts | grep "(16)" |
| 22 | Parent HTML copies | `Shiny app/landing_page.html`, `dome_prototype.html`, `detail_page_wireframe.html` | (synced from `.../www/`) | identical to www |

---

## ECHO PROCEDURE (for any future change)

1. **Propor** the classification change (one discussion).
2. **Acordo humano** (Enrique).
3. **Executar**: update #1 (matrix) + #2 (decoder) — the primary sources.
4. **ECOAR (functional)**: propagate to #3–#22 above, then run the verification sweep:
   - `grep -rn "38 modalities|L4 categor|L5 concept|functional/conceptual|generic/composite"` → **0 hits**.
   - `grep -rn "V026"` in active scripts → **0 hits**.
   - Matrix form-counts == decoder-derived counts == app counts == **16/5/2/12/18**.
5. **Auditar**: value-by-value comparison (matrix vs decoder vs D1 vs app DATA), no stale copies.
6. **Registrar** in `docs/RCDome_Traceability_Contract.md`.

**Rule:** if an artifact is not in this register and it displays levels/counts/labels, it is an
echo GAP — add it here.

---

## RIGOROUS ECHO & SYNC CONTRACT (mandatory, every change)

**Principle:** "Echo" and "sync" are FUNCTIONAL — value-by-value verification across every
derived artifact, never a mere file copy. A superficial echo is an INCOMPLETE echo.

### The 5 obligations (no skipping)

1. **PROPOR** — one change at a time, stated explicitly.
2. **ACORDO HUMANO** — Enrique approves before execution (recorded).
3. **EXECUTAR** — update the PRIMARY sources first (matrix, decoder).
4. **ECOAR (functional)** — propagate to ALL artifacts in this register (#3–#22), then run
   the verification sweep below until it is clean.
5. **AUDITAR + REGISTRAR** — deepest-audit script (`deepest_app_audit.py`) + traceability entry.

### Verification sweep (must return 0 hits)

```bash
grep -rn "38 modalities|L4 categor|L5 concept|functional/conceptual|generic/composite"  → 0
grep -rn "V026" (active files only)                                                    → 0
matrix counts == decoder-derived == app counts == 16/5/2/12/18                          → TRUE
```

### Anti-patterns (what a superficial echo looks like — DO NOT)

- Updating the matrix but NOT the app DATA arrays / LEVEL_COUNTS / LEVEL_NAMES.
- Updating the decoder but NOT the detail-page generator scripts.
- Updating the manuscript but NOT the figure legends (¶364/¶367).
- Leaving old counts/labels buried in parent-level copies, wireframes, or generate scripts.
- Checking one page and declaring the whole app "echoed".

### Definition of DONE

A change is **echoed** only when: (a) every artifact in this register returns PASS in the
deepest audit; (b) the sweep returns 0 old values; (c) the traceability entry is written;
(d) GitHub is pushed. Nothing less.

**Status 2026-09-05:** all inconsistencies from the earlier superficial echo were found and
fixed (8 app structures + 6 manuscript paragraphs + 2 generator scripts). Register v1 complete.
