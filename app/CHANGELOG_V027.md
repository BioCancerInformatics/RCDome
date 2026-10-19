# CHANGELOG V027 — Matrix Upgrade: Semantic-Contradiction Repair + Full Consensus Merge

Date: 2026-09-27
Upgrade: V026 → V027
Status: propagation in progress

---

## 0. Additive adjudication columns (2026-10-16)

- Matrix dimension: 82 → **94 columns** (11 additive, original columns byte-identical).
- Added: `final_mechanistic`, `final_role`, `final_direction`, `final_verdict`, `gpt4o_verdict`, `higor_verdict`, `victor_verdict`, `deciding_evidence`, `evidence_source`, `decision_status`, `abstract_check`.
- `decision_status`: UNIFORM_PIPELINE (7,177) / AGREED_LABEL_ABSTRACT (14,284) / PENDING_DELTA (1,012).
- Policy + traceability: `REGRA_agreement_policy_fulltext_vs_abstract.md` + `docs/TRACEABILITY_optionB_execution_and_agreement_policy_2026-10-16.md`.

---

## 1. Why V026 became V027

1. **237 semantic-contradiction repairs** in the DeepSeek cot columns
   (Rule 2: REGULATOR with bad direction → UNCERTAIN/UNCLEAR; Rule 5: mechanistic YES
   with UNCERTAIN role → NO). Conservative downgrade-only.
2. **94 Consensus repairs** (75 downgraded; 19 umbrella cases kept and logged).
3. **11 Consensus variables merged** into the matrix (100% complete:
   21,568 / 21,568 pairs).

All repairs and the merge are logged:
- `TRACEABILITY_repair_237.csv`
- `TRACEABILITY_repair_consensus_100.csv`
- `TRACEABILITY_cot_rule4_repair.csv`
- `TRACEABILITY_V027_consensus_merge_full.csv`

---

## 2. Matrix V027

- `unified_gene_rcd_matrix_V027.csv` — 22,473 rows × **82 columns** (71 + 11 consensus).
- `unified_gene_rcd_matrix_V027.rds` — regenerated from the CSV (RDS policy).

---

## 3. Stat changes (V026 → V027, unique pairs)

| Stat | V026 | V027 |
|---|---|---|
| mechanistically involved | 10,016 (46.4%) | **9,785 (45.4%)** |
| not involved | 11,552 (53.6%) | **11,783 (54.6%)** |
| regulators | 9,489 | **9,311** |
| executors | 469 | 469 (unchanged) |
| markers | 5 | 5 (unchanged) |
| unresolved role | 11,605 | **11,783** |
| direction (PROMOTES/PROTECTS/UNCLEAR) | 5,070 / 4,755 / 11,743 | unchanged |
| matrix columns | 71 | **82** |

---

## 4. Artifacts updated and renamed

Done:
- `RCDome_manuscript_governance_V027.docx` (stats + 82 columns)
- `RCDome_manuscript_V027_supplementary_tables.xlsx` (INDEX + Matrix Descriptor)
- `RCDome_manuscript_V027_supplementary_information.docx` (renamed; S7 injection pending)
- Figure 1 (flowchart, 82 columns) and Figure 3 (death core, V027 numbers) regenerated

Archived (V026 "before" state):
- `manuscript_V027/_archive_V026_pre_V027/` (manuscript, Excel, SI + ARCHIVE_README.md)

---

## 5. Pending renames (V026 → V027)

Not yet renamed; to be done with the distribution + GitHub sync:

- `RCDome_V026_distribution.zip` → `RCDome_V027_distribution.zip`
- App folder `Shiny app/RCDome_Atlas/` (internal RDS reference → V027)
- GitHub mirror `D:/RCDome_github/` (manuscript + RDS copies)

---

## 6. Still pending (non-rename)

- SI: inject Supplementary Note S7 (Label-Error Benchmark) + its manuscript call-out.
- App modules: add the 11 consensus variables as filters (logged in
  `PENDING_app_consensus_variables.md`).
- Track A vote (`gpt4o_vote_disagreements.py`) and Track B fetch
  (`fetch_trackB_disagreements.py`) — ready, not yet run.
- Consensus full merge complete (21,568 pairs, 100%).

---

## 7. App artifact spread + GitHub sync — requires an end-to-end audit

Before the distribution ZIP and GitHub push, the V027 changes must spread to the app
artifacts and the GitHub mirror, each passing a **bigger, end-to-end consistency audit**
(horizontal + vertical propagation check):

- App: `data/…_V027.rds`, `mod_gene_catalog.R`, `mod_network.R`, the Board, the landing text.
- GitHub: V027 manuscript, RDS, benchmark folder, changelog.
- Audit: diff every artifact for stale V026 numbers, verify the app opens V027, verify the
  mirror matches the tree, verify the ZIP has no V026 leftovers, and log pass/fail.

Full detail in `analysis/benchmark_label_error_n800/PENDING_app_consensus_variables.md` §7.

---

## 8. Reader-experience modules + Evidence Trail fix (2026-10-04)

Status: DONE (reader-experience batch)

### New app modules

- **Discrepancy Radar** (`modules/mod_discrepancy.R`, tab after Gene Catalog) — the 7,895
  GPT-arbitrated classifier disagreements, faceted by axis (Direction 926 / Role 319 /
  Mechanistic 6,647), concordance dots (uniform CSS circles), GPT verdict + reason, PENDING
  human-adjudication slot. Click opens the extended Evidence Trail drawer. Data:
  `data/discrepancy/` (4 GPT-vote CSVs).
- **Discovery Timeline** (`modules/mod_timeline.R`) — five lanes (L1-L5), 1859-2026, dome
  palette + glow. Click opens a discovery card (founding year + paper title/authors/journal +
  PMID/DOI). The composite entity shows its two parent PMIDs, no fabricated PMID. Data:
  `data/discovery/founding_papers.csv` (53 founding papers).
- **Reader Mode** (`modules/mod_tour.R`) — first-visit 8-step modal tour with auto-navigation,
  a Home-only Start-tour button, and a Replay-tour control in About.
- **3D RCDome** (`www/dome_3d.html` + `generate_dome_3d.py`, tab after Network) — rotatable
  three.js sphere: 53 entities on the shell, network lines to top entities, level legend
  highlight, entity focus view (hoverable/clickable stars), gene click -> Evidence Trail, and
  a full/sampled toggle (default top 400 genes; full 9,265). three.js + OrbitControls bundled
  locally in `www/`.

### Fixes

- **Evidence Trail drawer** — direct HTML injection (`build_evidence_trail_html` +
  `observeEvent`), fixing the blank drawer from the Gene Catalog; one unified route for
  Network + Gene Catalog.
- **Gene Catalog** — Evidence column wired to the drawer; gene link and button separated.
- **Deep Dive** — Option 2: pure narrative + View associated genes; no drawer.
- **Timeline overlap** — plot shifted right (Necrosis no longer overlaps the L4 label).
- **DOI encoding** — `doi_href()` percent-encodes URL-hostile characters.

### Manuscript (`RCDome_manuscript_governance_V027.docx`)

- Module list (platform architecture + Web Application section) now includes Discrepancy
  Radar, Discovery Timeline, and 3D RCDome (ten data modules).
- Module cards updated on `explore.html` + `landing_page.html`.

### Verification

- Smoke test (`code/test_app_smoke_v027.py`) — ALL PASSED.
- Link audit — 52 PMID + 50 DOI founding links, 0 broken.
- 3D constellation mapping audit — 0 mismatches vs the matrix.

### Distribution

- `RCDome_V027_distribution.zip` rebuilt (797.1 MB, 397 files), including `.Renviron`.

## Victor V027 protocol — final review triage + fixes (2026-10-05 → 2026-10-07)

Victor's 49-item review (CRITICAL C01–C15, HIGH H01–H23, MODERATE M01–M10, EDITORIAL
E01–E02) was triaged one-by-one against the current artifacts. Result: **46 resolved
with evidence; 3 deferred** (C01 EndNote, C02 word count, C03 abstract — author precedent).

### Data / ontology
- C04 "53 unresolved" removed · C05 DATABASE_ONLY 286 / INSUFFICIENT_DATA 9,019 ·
  C06 71 MSigDB PMIDs filled (MECHANISTIC 3,063, 0 without PMID) · C10 keyword reclassify
  (14 mixed + 15 NECSO documented).
- C08 rows vs pairs defined · C09/C09.2 per-row tier + confidence universe (1,874 documented) ·
  C13 unsupported EXECUTOR rate 53→0 (traceability 24% PMID → 98.3% DOI) ·
  C14 Table S12 L1-ELIGIBLE (NECSO/Mitoxyperilysis/Triaptosis) · C15 XDeathDB 216.
- H08 enrichment 4.3×/4.5× · H09 definition denominators (27/53; 33 non-NCCD) ·
  H06 Elicit evidence_type (250 unassigned documented) · H13 mitotic death vs catastrophe
  (driven_by) · H01 Consensus 100% · H18 freeze date 2026-10-15.

### Nomenclature / text
- "20 source databases and resources" · "systematically evaluates" · gene-RCD single hyphen
  spelling (87) · impactful→high-impact · version tags removed from manuscript + artifacts
  (internal-only) · EG1–EG5 (was QG1–QG5) · unsupported EXECUTOR rate (was EXECUTOR precision).

### Figures (regenerated + legends aligned)
- Figure 1 (M05: app modules + 82 columns) · Figure 2 (H23: S5/S14 + unsupported EXECUTOR
  rate + traceability) · Figure 3 (C11: 5,025 promoters + 63.5/22.9/30.2%) ·
  Figure S1 (M06: parallel ET/CT arrows) · Figure S3 (C12: V027 matrix, 21.6–86.5%).

### Distribution
- `RCDome_V027_distribution.zip` rebuilt (797.2 MB, 363 files): `_archive` excluded, real
  secrets (`.Renviron` + `email_creds.txt`), no placeholders.
- GitHub mirror sync (this commit); secrets remain gitignored.
## RCD entities module redesign + author distribution (2026-10-08)

Status: DONE

### RCD entities module (rewritten: `modules/mod_rcd_entities.R`)

- Name-first navigation: searchable list of the 53 entity names (no unlabeled honeycomb).
- Selecting an entity shows the enlarged transparent logo, the ontological-level pill, the
  human-curated description with clickable [n] -> DOI/PMID citations, the reference list,
  and a "View associated genes" handoff to the Gene Catalog.
- Three controls: View cartoon, Read legend, Download PNG.

### Cartoon experience

- Full-screen modal (96vw x 94vh) so the whole figure is visible at once.
- Click-to-zoom at 1.5x the displayed size (zoom-out on second click).
- Download PNG action; Read legend opens a second modal (legend citation-free as delivered).
- Startup batch preload of all 53 cartoons (staggered, non-blocking) plus a per-entity
  off-screen preload, so the modal opens instantly after selection.
- Case-insensitive filename lookup fixes 9 Title-Case cartoon names (HTTP is case-sensitive).

### Deep Dive fused into RCD entities

- The standalone "RCD Entity Deep Dive" tab/card was removed; its narrative now lives inside
  RCD entities. Propagated to the manuscript (module list + Figure 1 legend), Figure 1
  (regenerated), `explore.html` / `landing_page.html`, and the GitHub README.

### Figures re-exported at 300 DPI

- Emanuell delivered the 53 cartoons at 96 DPI (1536 x 1024 px), too low for full-screen zoom
  and print. All 53 were re-exported at 300 x 300 DPI in place (pixels unchanged); the 96-DPI
  originals are archived byte-for-byte in `figuras RCDs/_archive_96dpi_originals/` (53 files).

### Author distribution (no secrets, no password)

- The app now runs without the bundled API key: `global.R` warns (does not stop) when
  `DEEPSEEK_API_KEY` is absent; the AI modules already degrade with a notice.
- The build script never ships real secrets: `.Renviron` and `data/email_creds.txt` are
  excluded; the `.example` templates remain for coauthors who add their own key.
- `RCDome_V027_distribution.zip` rebuilt (unzip + run; no password, no secret files).
### Emanuell 300 DPI delivery integrated (2026-10-08, follow-up)

- Emanuell delivered the native 300-DPI figures (53, `versao final 300 dpi`), the 300-DPI logos
  (53, `versao 2 300 dpi`), and the logo audit (58 files) in `RCD modulo new 5`.
- Figures verified byte-identical to the local 300-DPI re-export (0 mismatches).
- Logos transparentized (flood-fill white background -> transparent) at 300 DPI and deployed to
  `logo RCDs/` + `logo RCDs/thumbs/`; the 96-DPI transparent originals archived in
  `logo RCDs/_archive_96dpi_transparent/` (53 files).
- Logo audit synced to `data/RCD modulo/auditoria_logo/` (58 files).
- `RCDome_V027_distribution.zip` rebuilt (581.4 MB).
### Download watermark — © RCDome Group 2026. Cite us (2026-10-08)

- The downloadable cartoon PNG is watermarked in the bottom-right corner with
  "© RCDome Group 2026. Cite us" (white text on a semi-transparent dark box, ~2.8% of width).
- The on-screen full-screen cartoon and zoom stay clean (no stamp on display).
- Download is now a Shiny downloadHandler (`magick::image_annotate`), filename
  `<entity>_cartoon_RCDome_Group_2026.png`.
- Refined (discreet version): box opacity 50% -> 35%, size 2.8% -> 1.5% of width.
### Elicit over-indexing correction (2026-10-08)

- Re-indexed the Elicit Phase 3B evidence by the raw `gene_symbol` column only (removed the
  free-text regex over-indexing), keeping all genes.
- Added column `elicit_multi_gene` (TRUE/FALSE; TRUE = paper's gene_symbol lists >1 gene).
- Matrix stays V027 (no version bump); the pre-reindex original is archived at
  `data/_archive_V027_pre_reindex_2026-10-08/` (SHA-256 stamped).
- Delta: 4,509 rows with Elicit verbatim -> 1,523 LOSE + 1,955 SWAP + 2,479 multi-gene flag.
- Propagated: matrix CSV + RDS (22,473 x 83), app, ZIP (584.7 MB). Decoder unaffected.
- Traceability: `docs/TRACEABILITY_elicit_reindex_2026-10-08.md` + `TRACEABILITY_elicit_reindex_delta.csv`.
### Evidence Trail drawer — multi-gene flag + verbatim footnote (2026-10-08)

- Added the `elicit_multi_gene` flag to the drawer: a small "multi-gene" pill before the
  Elicit verbatim when TRUE, with an amber CSS tooltip (same flag color) explaining that the
  supporting paper is indexed under multiple genes.
- Added an italic footnote (flag color) clarifying: verbatim claims appear only when an exact
  source sentence was retrieved (~6% DeepSeek, ~14% Elicit); the classification fields are
  always populated, and a classification must not be read as confirming verbatim evidence.
- Fixed a sprintf "too few arguments" error (the footnote's literal % signs are now escaped).
### Network export upgrade + Board entity logo (2026-10-10)

- Network module: replaced the low-res visExport with genuine 3x high-resolution PNG/PDF
  export (the vis.js canvas is re-rendered at 3x, white background, selection header
  caption drawn top-left, discreet "© RCDome Group 2026. Cite us" watermark bottom-right).
- Board module: the selected entity's logo (240px, 2x the entity-module logo) now appears
  below the "Download Synthesis (HTML)" button.
### Entity logos extended across modules (2026-10-10)

- Evidence Trail drawer: the entity logo now appears in the drawer header (gene × entity).
- Synthesis HTML report: the entity logo (top-left, embedded base64) added to the downloaded report.
- Gene Catalog: the gene detail modal shows each RCD entity with its 22px logo.
- Discovery Timeline: the discovery card shows the 56px entity logo in the header.
### Landing-page entity logo + cache-busting (2026-10-10)

- The dome node click now lands on the entity subpage with the 56px entity logo next to
  the title (showEntity renders the logo via the rcd_mod resource).
- Fixed the missing logo: the browser was caching the old detail_page_wireframe.html;
  added a ?v=4 cache-buster to the dome node click and the Gene Catalog navigation.
