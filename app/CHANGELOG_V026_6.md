# RCDome — CHANGELOG V026_6

## V026_6 — Victor app-verification fixes (2026-09-19)

Fixes approved from Victor's *RELATÓRIO DE VERIFICAÇÃO DO APP* (5 findings, all validated).

- **Navigation**: "Back to the dome" now clicks the parent **Home** tab (same pattern as the landing-page cards) instead of navigating the iframe to `landing_page.html` — the dome (d3.js) now re-renders correctly on return. "dome" is intentional (RCDome's visual signature), not a typo.
- **Composite entity**: "Senescence and Autophagy in Cancer" (`founding_pmid = "composite"`) no longer linkifies to `pubmed…/composite/`; it renders the two real PMIDs (29362479 + 36864290) with a "Composite —" label. `reference_pmid` and `primary_discovery_reference` now render multi-PMID lists as separate clickable links; `reference_citation` links to the first PMID only.
- **Reference discipline (data)**: dropped NCCD_2018 (29362479) from `primary_refs_pmids` for the 8 `NOT_IN_NCCD_2018` entities (Apoptosis, Autophagy, Methuosis, Mitochondrial permeability transition, Mitoptosis, Necrosis, Oxeiptosis, Paraptosis) — an entity declared "not in NCCD_2018" no longer lists NCCD_2018 among its primary references. Composite entity (Senescence and Autophagy in Cancer) kept its component PMIDs (29362479;36864290) but its `galluzzi_nccd_status` was changed `NOT_IN_NCCD_2018` → `COMPOSITE` (matching `category` and `definition_status`), so the data is self-consistent.
- **Vacuolar cell death citation**: clarified to "Kosta et al. 2004 (Dictyostelium — name source; non-vacuolar pathway); plant context: Minina 2013 (PMID 24344187), Feng 2022 (PMID 35390283)" — the two-reference structure (one Dictyostelium founding PMID + plant secondary PMIDs) is preserved.
- **Composite entity citation**: clarified to "Composite of Cellular senescence (NCCD_2018; PMID 29362479) + Autophagy (PMID 36864290) — composite pathway label, not a distinct NCCD entity" — 29362479 is the NCCD_2018 reference of the *Cellular senescence component* (which is NCCD_2018_INVARIANT), not of the composite (correctly NOT_IN_NCCD_2018).
- **Markdown rendering**: "##" headers in the entity detail no longer display literally — `build_decoder_desc` now joins sections with `\n\n` so `desc_to_html` converts each "##" into a subheading.

Files touched: `www/explore.html`, `www/detail_page_wireframe.html`, `www/module_placeholder.html`, `modules/mod_od.R`, `modules/mod_rcd_grid.R`, `RCDome_Decoder_53.csv/.xlsx` (decoder + app + GitHub copies).

Traceability: `docs/TRACEABILITY_Victor_app_fixes_2026-09-19.md`.

---

# RCDome — CHANGELOG V026_7

## V026_7 — Victor V026 auditoria: ontology re-adjudication + nomenclature harmonization (2026-09-19)

Full assessment of Victor's *Relatório Crítico-Didático* (42 sections), executed evidence-first under the change-spread policy.

### Ontology re-adjudications (G0–G6 worksheets, full-text evidence)
- **Lysoptosis** → SUBTYPE / L2 (serpin/SERPINB3-moderated subtype of lysosome-dependent cell death; Luke et al. 2022).
- **Lysozincrosis** → SUBTYPE / L2 (zinc-specific LMP).
- **Floatptosis** + **Spectosis** → CELL_TYPE / L4 (macrophage vacuolization; RBC complement/caspase-8 hemolysis).
- **Mitoptosis** → CELLULAR_PROCESS / L5 (organelle turnover, not cell death).
- **Aponecrosis** → UMBRELLA / L5 · **Pyronecrosis** → SYNONYM / L5.
- **NECSO** (TRPM4 Na+ overload), **Mitoxyperilysis** (BAX/BAK1/BID), **Triaptosis** (VPS34) → **CORE_PENDING / L1-ELIGIBLE (emerging)** — G1+G2 passed with explicit KO/rescue evidence (PMID 39915626, 41317732, 39446948).
- `EMERGING` + `LEGACY` categories removed; L5 renamed to **"Generic/umbrella/taxon"** (maturity words removed).
- Final distribution: **L1 = 19, L2 = 7, L3 = 2, L4 = 13, L5 = 12**.

### Renames (NCCD-consistent)
- **Entosis** → **Entotic cell death** · **NETosis** → **NETotic cell death** (process names retained as source terms).

### Nomenclature harmonization (with crosswalk)
- C1–C5 → **MC1–MC5** (Modality Criteria) · C1–C6 → **RS1–RS6** (Ranking Score)
- Q1–Q5 → **QG1–QG5** (Quality Gates, Q = Quality) · T1–T4 → **ET1–ET4** (Evidence) / **CT1–CT4** (Confidence)
- G0–G6, Q1–Q13, `confidence_score`, `S` unchanged.

### Governance
- **Held-out benchmark** (n=100, seed 20260919, excluding dev) — reference discipline + context fidelity 100/100 (95% CI 96.4–100%).
- **Human review** documented: primary curator EM-A (per-entity) + independent curators VdSL + HACN; disagreements jointly adjudicated.
- §12/§13 cautions recorded in Note S1; reference discipline fixes (NCCD_2018 × NOT_IN_NCCD_2018; composite entity) in V026_6.

### Figures
- Figure 3 (panel B percentages), Figure 4 (L5 name), Figure S3 (level counts) regenerated with the corrected distribution.

Traceability: `docs/TRACEABILITY_V026_auditoria_2026-09-19.md` · crosswalk · `docs/AUDIT_ultimate_granular_2026-09-19.md` (115/115 PASS).
