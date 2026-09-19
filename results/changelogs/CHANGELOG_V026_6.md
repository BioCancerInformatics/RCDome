# RCDome — CHANGELOG V026_6

## V026_6 — Victor app-verification fixes (2026-09-19)

Fixes approved from Victor's *RELATÓRIO DE VERIFICAÇÃO DO APP* (5 findings, all validated).

- **Navigation**: "Back to the dome" now clicks the parent **Home** tab (same pattern as the landing-page cards) instead of navigating the iframe to `landing_page.html` — the dome (d3.js) now re-renders correctly on return. "dome" is intentional (RCDome's visual signature), not a typo.
- **Composite entity**: "Senescence and Autophagy in Cancer" (`founding_pmid = "composite"`) no longer linkifies to `pubmed…/composite/`; it renders the two real PMIDs (29362479 + 36864290) with a "Composite —" label. `reference_pmid` and `primary_discovery_reference` now render multi-PMID lists as separate clickable links; `reference_citation` links to the first PMID only.
- **Reference discipline (data)**: dropped NCCD_2018 (29362479) from `primary_refs_pmids` for the 8 `NOT_IN_NCCD_2018` entities (Apoptosis, Autophagy, Methuosis, Mitochondrial permeability transition, Mitoptosis, Necrosis, Oxeiptosis, Paraptosis) — an entity declared "not in NCCD_2018" no longer lists NCCD_2018 among its primary references. Composite entity (Senescence and Autophagy in Cancer) unchanged (its two PMIDs are its components, not an NCCD contradiction).
- **Vacuolar cell death citation**: clarified to "Kosta et al. 2004 (Dictyostelium — name source; non-vacuolar pathway); plant context: Minina 2013 (PMID 24344187), Feng 2022 (PMID 35390283)" — the two-reference structure (one Dictyostelium founding PMID + plant secondary PMIDs) is preserved.
- **Composite entity citation**: clarified to "Composite of Cellular senescence (NCCD_2018; PMID 29362479) + Autophagy (PMID 36864290) — composite pathway label, not a distinct NCCD entity" — 29362479 is the NCCD_2018 reference of the *Cellular senescence component* (which is NCCD_2018_INVARIANT), not of the composite (correctly NOT_IN_NCCD_2018).
- **Markdown rendering**: "##" headers in the entity detail no longer display literally — `build_decoder_desc` now joins sections with `\n\n` so `desc_to_html` converts each "##" into a subheading.

Files touched: `www/explore.html`, `www/detail_page_wireframe.html`, `www/module_placeholder.html`, `modules/mod_od.R`, `modules/mod_rcd_grid.R`, `RCDome_Decoder_53.csv/.xlsx` (decoder + app + GitHub copies).

Traceability: `docs/TRACEABILITY_Victor_app_fixes_2026-09-19.md`.
