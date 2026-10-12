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

## Issue #2 — Inclusão da opção de exportação em PDF no Operational Definition Comparator

- **Original comment:** the comparator only offers HTML download; suggests adding PDF export while keeping HTML.
- **Fact-check:** confirmed — `modules/mod_od_compare.R` line 155 has only "Download Comparison (HTML)"; no PDF option.
- **Assessment:** feature request, not a defect; legitimate need (print/archive/share); consistent with the existing PDF-export precedent in the Network module; low risk, no data/governance impact.
- **Classification:** ACTIONABLE.
- **Agreed solution:** add a single "Download Comparison (PDF)" button alongside the existing HTML button.
- **Solution detail (confirmed):** client-side jsPDF + html2canvas, reusing the Network module's PDF-export pattern; white-background canvas; standard watermark "© RCDome Group 2026. Cite us"; saved as `RCDome_Compare_<entities>.pdf`; HTML button unchanged; no new server dependency.
- **Action:** IMPLEMENTED (2026-10-12) — added `www/lib/{html2canvas.js, jspdf.debug.js, FileSaver.min.js}` (copied from the visNetwork htmlwidgets lib, self-contained); loaded them globally in `ui.R`; added the "Download Comparison (PDF)" button in `mod_od_compare.R` (client-side html2canvas → white canvas → watermark → jsPDF). ZIP rebuilt.

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

### 5a — Sobreposição dos pontos (glow/blur)

- **Original comment:** the glow around circles blurs dense regions, making individual entities hard to identify/count; suggests reducing or removing the glow.
- **Fact-check:** every node renders with `filter='url(#tlglow)'` → `feGaussianBlur stdDeviation='3'` (mod_timeline.R:142, 157–158). A vertical-offset mechanism (`yoff`) already separates same-year points.
- **Decision (user):** keep the glow — it is the original/intended design; do NOT reduce it. Overlap is handled by the existing vertical offset (`yoff`).
- **Classification:** NOT ACTIONABLE (no change to the glow; overlap already mitigated by the vertical offset).

### 5b — Distribuição temporal desproporcional (1859 stretches the scale)

- **Original comment:** including necrosis (1859) widens the scale and compresses post-2000 entities, especially near 2020.
- **Fact-check:** linear scale `X <- function(yr) 320 + (yr - min_yr)/(max_yr - min_yr) * 760`, min_yr = 1859, ~167 years over 760 px ≈ 4.5 px/year.
- **Preliminary classification:** ACTIONABLE (moderate) — but solution (axis break vs zoomed recent inset) must be designed explicitly.
- **Status:** pending user decision.

### 5c — Posicionamento de "Senescence and Autophagy in Cancer"

- **Original comment:** the entity appears outside expected temporal limits; verify its year and positioning.
- **Fact-check:** it is the composite (`year = "composite"` → NA), placed at x = 1120 (right edge) with an italic "composite" label (mod_timeline.R:131–132, 146). All 53 entities are represented (52 + 1 composite).
- **Preliminary classification:** NOT ACTIONABLE (by design — the composite has no single year).
- **Decision (user):** agreed — NOT ACTIONABLE.
- **Action:** none. Closed.
