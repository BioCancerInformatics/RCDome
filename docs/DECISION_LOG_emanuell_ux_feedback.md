# Decision Log — Emanuell UX Feedback (RCDome v27)

Source: `Relatório de experiencia do usuário RCDome v27.docx`
Assessor: Enrique Medina-Acosta
Protocol: independent critical assessment; one issue at a time; classification = ACTIONABLE / NOT ACTIONABLE / REQUIRES FURTHER INVESTIGATION. No change is implemented without explicit agreement.

---

## Issue #1 — Inconsistência na nomenclatura das análises

- **Original comment:** the top indicators panel shows "3 ANALYSES" while the explanatory section uses "Three independent analyses"; suggests changing the badge to "3 INDEPENDENT ANALYSES" for terminological consistency.
- **Fact-check:** the badge is in `www/explore.html` (the "Explore RCDome" tab, embedded via `ui.R` iframe), line 91. The label is lowercase "analyses" and is rendered uppercase only by a global CSS rule (`.counter .l { text-transform: uppercase; }`, line 36) applied to all six counters. The phrase "Three independent analyses" is the adjacent accordion header (line 110). The badge is NOT on the Home/dome landing page (`landing_page.html` has no such counters) — the report called it "página inicial", a minor location imprecision.
- **Assessment:** no genuine contradiction — "3 analyses" is a count and "three independent analyses" is a descriptive heading; they are compatible. The qualifier "independent" is already present immediately beside the badge (header + body). All six badges omit qualifiers by design ("20 DATABASES", not "20 INDEPENDENT DATABASES"). Adding "INDEPENDENT" would make one badge longer and visually inconsistent with the other five, adding no scientific value that is not already stated.
- **Classification:** NOT ACTIONABLE.
- **Rationale:** stylistic preference, not a defect; current design is intentional (compact counters + qualifiers in prose).
- **Action:** none. Closed.

---

## Issue #2 — Export options in the Operational Definition Comparator (revised)

- **Original comment:** the comparator only offers HTML download; suggests adding PDF export while keeping HTML.
- **Fact-check:** confirmed — `modules/mod_od_compare.R` originally had only "Download Comparison (HTML)"; no PDF option.
- **Assessment:** a genuine export need exists, but a PDF would only capture a snapshot of the visible table, not the complete comparison data — of limited practical value for a scientific application. Users need the full dataset (all fields × all selected entities) in a form they can inspect, filter, sort, and analyze.
- **Revised decision (replaces the initial PDF idea):** provide a genuine complete-data export.
  - **Preferred:** Excel (.xlsx) — preserves the comparison table structure, column headings (entity names), and field labels.
  - **Alternative:** CSV — straightforward, machine-readable.
  - **Removed:** the snapshot-based PDF button.
- **Classification:** ACTIONABLE.
- **Action:** IMPLEMENTED (2026-10-12) — in `mod_od_compare.R`: added `build_cmp_df()` (exports ALL fields × selected entities from the decoder, independent of the on-screen diff/same filter); added "Download Comparison (XLSX)" (writexl) and "Download Comparison (CSV)" buttons; kept the HTML button; removed the PDF button and its JS handler; removed the `www/lib/` html2canvas/jsPDF/FileSaver files and the global script tags in `ui.R`. ZIP rebuilt.

---

## Issue #3 — Problema de navegação e perda do contexto no Gene Catalog

- **Original comment:** after opening a gene's detail page from the Gene Catalog, "Back to the dome" returns to Home instead of the previous catalog position, forcing the user to redo the search; suggests returning to the catalog with preserved state, or two buttons ("Back to Gene Catalog" / "Back to Home").
- **Fact-check:** confirmed — `www/detail_page_wireframe.html` line 78 "← Back to the dome" activates the Home tab and reloads `landing_page.html`. The detail page is rendered inside the Home tab iframe and is shared by all entry points (dome, Gene Catalog via `mod_gene_catalog.R` navigate_to_gene_page, entity module, jump bars). The Gene Catalog is a Shiny tab, so its filters/search/sort are preserved when switching tabs — not destroyed.
- **Assessment:** the reported behavior is real but the severity is overstated (state is preserved, not lost; the button label is accurate). Genuine moderate friction: no one-click return to the catalog. The two-button proposal is flawed because the detail page is shared across entry points, so "Back to Gene Catalog" would be wrong for dome/entity origins.
- **Classification:** ACTIONABLE (moderate, low priority).
- **Agreed solution direction:** any fix must be origin-aware (track the entry point and adapt the back target), not a fixed two-button layout.
- **Action:** implement after the review cycle (pending).

---

## Issue #4 — Ausência de opções de exportação na tabela RCD Entities — Elicit vs DeepSeek

- **Original comment:** the "RCD Entities — Elicit vs DeepSeek (executors / regulators)" table has no download/export options, unlike the gene table above.
- **Fact-check:** the claim is incorrect — `modules/mod_gene_catalog.R` lines 90–91 already has "Download comparison table (CSV)" in the section header, wired (lines 474–477) to `RCDome_entities_elicit_vs_deepseek.csv`. The only real difference vs the gene table is the gene table's TSV/XLSX/CSV format selector; the entities table is CSV-only.
- **Assessment:** the core need (download) is already met; the observation misreads the UI as having no download option. The remaining gap (format selector) is cosmetic for a 53-row comparison table and does not justify modification.
- **Classification:** NOT ACTIONABLE.
- **Rationale:** misunderstanding of existing functionality; no genuine defect.
- **Action:** none. Closed.

---

## Issue #5 — Problemas de visualização e distribuição temporal na Discovery Timeline

### 5a — Sobreposição dos pontos (coinciding dots)

- **Original comment:** the glow around circles blurs dense regions, making individual entities hard to identify/count; suggests reducing or removing the glow.
- **Fact-check:** every node renders with `filter='url(#tlglow)'` → `feGaussianBlur stdDeviation='3'`. Same-year + same-level collisions = 7 pairs (14 entities), max group size 2. The vertical-offset (`yoff`) already spreads coinciding dots, but at ±6 px the two dots (radius 6–8 + glow) still overlapped.
- **Decision (user):** keep the glow (original design); ensure all 53 dots are individually distinguishable by spreading coinciding dots clearly above and below the lane line.
- **Classification:** ACTIONABLE (minor).
- **Action:** IMPLEMENTED (2026-10-12) — increased the `yoff` spread from ±6 to ±12 px (24 px center-to-center), so each of the 7 coinciding pairs is clearly separated above/below the lane line; all 53 dots distinguishable. ZIP rebuilt.

### 5b — Distribuição temporal desproporcional (1859 stretches the scale)

- **Original comment:** including necrosis (1859) widens the scale and compresses post-2000 entities, especially near 2020.
- **Fact-check:** linear scale `X <- function(yr) 320 + (yr - min_yr)/(max_yr - min_yr) * 760`, min_yr = 1859, ~167 years over 760 px ≈ 4.5 px/year; 43 of 52 entities sit in 2000–2024 (~110 px).
- **Classification:** ACTIONABLE (moderate).
- **Agreed solution (Option 3, zoomed inset):** keep the full overview (all 53, 1859–2025, unchanged) and add a clearly-labeled second panel below titled "Recent discoveries (2000–2024) — zoomed", same 5 lanes, the recent window stretched to full width (~31.7 px/year). Duplication allowed (recent dots appear in both panels). Window = 2000–2024.
- **Action:** implement after the review cycle (pending).

### 5c — Posicionamento de "Senescence and Autophagy in Cancer"

- **Original comment:** the entity appears outside expected temporal limits; verify its year and positioning.
- **Fact-check:** it is the composite (`year = "composite"` → NA), placed at x = 1120 (right edge) with an italic "composite" label (mod_timeline.R:131–132, 146). All 53 entities are represented (52 + 1 composite).
- **Preliminary classification:** NOT ACTIONABLE (by design — the composite has no single year).
- **Decision (user):** agreed — NOT ACTIONABLE.
- **Action:** none. Closed.

---

## Issue #6 — Falha na geração de sínteses no Digital Molecular Board

- **Original comment:** "Generate Synthesis" shows "Error: DeepSeek HTTP 402"; suggests regularizing the API balance, showing a clearer message, and disabling download when no synthesis is generated.
- **Fact-check:** the code reports the real HTTP status (mod_board.R line 604); the app already shows "⚠ Generation failed — no synthesis produced (DeepSeek API error)" on failure. The DeepSeek key is shipped inside the distribution ZIP via `.Renviron` (real key, no placeholder).
- **Decision (user):** REJECTED — NOT ACTIONABLE (by design). The 402 occurs when the running copy lacks a valid DeepSeek key (e.g., an older distribution without the key, or no credits). No app change is warranted.
- **Classification:** NOT ACTIONABLE.
- **Action:** none. Closed.

---

## Issue #7 — Presença de informações residuais de versões anteriores no módulo Network

- **Original comment:** the Network "Search gene" field still shows "e.g. TP53, UVM-99..."; UVM-99 is a signature from a previous article, no longer in the current scope.
- **Fact-check:** confirmed — `modules/mod_network.R` line 109 placeholder is "e.g. TP53, UVM-99...". "UVM-99" is not a gene symbol; its origin is the legacy signature table (`_archive/Shiny app_legacy/*/data/signatures.tsv`, "UVM-99.2.1.P.0.0.0.4.4.2" — a uveal-melanoma signature from the earlier signature-based analysis). No other residual "e.g." placeholder exists in the live modules.
- **Classification:** ACTIONABLE (minor).
- **Action:** IMPLEMENTED (2026-10-12) — replaced the placeholder with "e.g. TP53, BCL2, BAX, GPX4...". ZIP rebuilt.
