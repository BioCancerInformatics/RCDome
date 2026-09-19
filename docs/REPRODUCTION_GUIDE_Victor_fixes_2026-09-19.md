# Manual reproduction guide — Victor's app fixes (V026_6, 2026-09-19)

**Launch the app**
1. Open RStudio.
2. Set the working directory to `RCDome_distribution`.
3. Run:
   ```r
   shiny::runApp(appDir = ".", port = 8890, launch.browser = TRUE)
   ```
4. The app opens on the **Home** tab (the interactive dome + module cards).

---

## Point 1 — "Back to the dome" navigation

**Victor reported:** clicking "Explore RCDome" showed the dome, but "back to the dome" landed on a
"home" layout and the dome only returned after a full reload.

**Reproduce (fixed):**
1. On the **Home** tab, click the **"Explore RCDome"** card (or the "Explore RCDome" tab).
2. Scroll to the bottom of the Explore page and click **"← Back to the dome"**.
3. **Expected now:** the app switches to the **Home tab**, and the dome (the cupola with the 53
   colored entity nodes) re-renders immediately — no page reload.

**Also fixed — gene/RCD detail pages (they live inside the Home iframe):**
1. Open the **Gene Catalog** tab, click any gene row → the gene detail opens (with the NCBI summary).
2. Click **"← Back to the dome"** at the top.
3. **Expected now:** the Home tab's iframe navigates back to the landing page (the dome), instead of
   doing nothing. The same applies to RCD detail pages opened from the dome.

---

## Point 2 — "dome" is intentional

The links read "Back to the **dome**" (not "home"). This is correct: the dome is RCDome's visual
signature (the cupola rim carries the 53 canonicalized RCD-related entities, colored by level).

---

## Point 3 — "PMID composite" no longer errors

**Victor reported:** "PMID composite" was unclear and clicking it gave an error.

**Reproduce (fixed):**
1. Open the **"Operational Definitions"** tab.
2. In the search box ("Search an RCD form…") type **"Senescence"** and select
   **"Senescence and Autophagy in Cancer"** from the list.
3. In the detail panel, under **References**:
   - **Founding PMID** now reads **"Composite — PMID 29362479 PMID 36864290"** (two real, clickable links).
   - **Reference PMID** shows **PMID 29362479** and **PMID 36864290** as two separate clickable links.
   - **Reference citation** links to the first PMID (29362479).

Before the fix, "Founding PMID" linked to `pubmed.ncbi.nlm.nih.gov/composite/` (dead page).

---

## Point 4 — NCCD_2018 × NOT_IN_NCCD_2018 contradiction

**Victor reported:** "Primary reference PMIDs", "Reference PMID", "Reference citation" showed
NCCD_2018 references contradicting "NOT_IN_NCCD_2018".

**Reproduce (fixed):**
1. Open **"Operational Definitions"**.
2. Select **"Apoptosis"** (or Autophagy, Methuosis, Mitochondrial permeability transition, Mitoptosis,
   Necrosis, Oxeiptosis, Paraptosis).
   - Under **References → Primary reference PMIDs**: now only the founding PMID (e.g. **PMID 17562483**).
     The NCCD_2018 PMID (29362479) is gone.
3. Select **"Senescence and Autophagy in Cancer"** again.
   - Under **NCCD 2018 → NCCD status**: now **COMPOSITE** (was NOT_IN_NCCD_2018).
   - Under **References → Reference citation**: "Composite of Cellular senescence (NCCD_2018; PMID
     29362479) + Autophagy (PMID 36864290) — composite pathway label, not a distinct NCCD entity".

---

## Point 5 — Vacuolar cell death reference (PMID 15358773)

**Victor reported:** PMID 15358773's title says "non-vacuolar cell death pathway", used to justify
Vacuolar cell death.

**Reproduce (fixed):**
1. Open **"Operational Definitions"**.
2. Select **"Vacuolar cell death"**.
   - **Reference citation** now reads:
     "Kosta et al. 2004 (Dictyostelium — name source; non-vacuolar pathway); plant context: Minina 2013
     (PMID 24344187), Feng 2022 (PMID 35390283)".
   - **Secondary reference PMIDs** shows the two plant PMIDs (24344187, 35390283) as links.
   - **Founding PMID** is 15358773 (Kosta 2004, Dictyostelium — the name source).

---

## Point 6 — "##" Markdown in the "Detailed" panel

**Victor reported:** "##" headers displayed literally in the "Detailed" panel, apparently in all entities.

**Reproduce (fixed):**
1. Open the **"RCD entities"** tab.
2. Click any entity card (e.g. **Apoptosis**).
3. Click the **"Detailed"** view toggle.
4. **Expected now:** the sections render as bold subheadings — **Operational definition**,
   **Core mechanism**, **Key molecules**, **Ontology**, **Scoring (Rodrigues C1–C6)**, **Provenance** —
   with no literal "##" text.
