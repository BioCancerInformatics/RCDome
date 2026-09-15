# RCDome — Operational Definitions (SOLID group, DRAFT)

**Version-stamp:** V026 · **Status:** DRAFT for two-call human review
**Grounding:** founding-paper abstracts (`founding_abstracts_SOLID.txt`) + V026 matrix evidence (`entity_evidence_V026.csv`)
**S formula:** S = 0.25·C1 + 0.25·C2 + 0.20·C3 + 0.15·C4 + 0.10·C5 + 0.05·C6 (verified 25/25)
**Rule:** every field traces to a source; unsourced fields are marked *"not specified"* — never invented.

---

## 1. Programmed cell death
- **Category:** Umbrella (parent term)
- **Year of Discovery:** 1965
- **Operational Definition:** Umbrella term for genetically encoded, developmentally scheduled cell death, first defined by Lockshin & Williams (1965) from the cytological degeneration of intersegmental muscles during insect metamorphosis. It is the **parent** of the specific RCD programs, not a single mechanism.
- **Key Molecules:** not specified (umbrella — member forms carry their own machinery)
- **Inflammatory?:** member-dependent
- **Biological Relevance:** developmental tissue remodeling, homeostasis, and removal of superfluous cells.
- **Overlaps:** parent of all programmed RCD forms (apoptosis, necroptosis, pyroptosis, ferroptosis, …).
- **C1–C6 (DRAFT):** 10 / 3 / 9 / 5 / 10 / 8 → **S = 7.20**
- **References:** Lockshin & Williams 1965, PMID 14287218 (primary).

## 2. Mitotic death
- **Category:** Umbrella (overlapping mitotic catastrophe)
- **Year of Discovery:** 1967
- **Operational Definition:** Delayed cell death that follows aberrant mitosis after radiation or drug exposure, defined by Jacobson & Lee (1967) in Chlamydomonas and Chlorella; an umbrella overlapping mitotic catastrophe rather than a distinct executioner.
- **Key Molecules:** not specified in founding abstract
- **Inflammatory?:** not specified
- **Biological Relevance:** elimination of cells that fail chromosome segregation.
- **Overlaps:** mitotic catastrophe; downstream execution via apoptosis or necrosis.
- **C1–C6 (DRAFT):** 5 / 3 / 5 / 4 / 5 / 4 → **S = 4.30**
- **References:** Jacobson & Lee 1967, PMID 6027879 (primary).

## 3. Aponecrosis
- **Category:** Legacy / unresolved (provisional)
- **Year of Discovery:** 2000
- **Operational Definition:** A syncretic cell death sharing dynamic, molecular, and morphological features of both apoptosis and necrosis, induced by high-dose mitochondrial insult (Antimycin A); Formigli et al. (2000) showed it represents an incomplete execution of the apoptotic program that degenerates into necrosis, with intracellular ATP as a primary determinant of the outcome.
- **Key Molecules:** caspase-3; mitochondrial respiratory chain complex III.
- **Inflammatory?:** Yes (via the necrotic component)
- **Biological Relevance:** a continuum intermediate between apoptosis and necrosis under metabolic stress.
- **Overlaps:** shares apoptosis (caspase-3) and necrosis.
- **C1–C6 (DRAFT):** 4 / 4 / 4 / 4 / 5 / 3 → **S = 4.05**
- **References:** Formigli et al. 2000, PMID 10567915 (primary). *Committee decision required for promotion from legacy status.*

## 4. Phagoptosis
- **Category:** Contextual program (clearance)
- **Year of Discovery:** 2012
- **Operational Definition:** Cell death caused by phagocytosis of **viable** cells (primary phagocytosis), provoked by exposure of "eat-me" signals and/or loss of "don't-eat-me" signals, defined by Brown & Neher (2012).
- **Key Molecules:** eat-me signals (e.g., phosphatidylserine exposure); don't-eat-me signals (e.g., CD47).
- **Inflammatory?:** No (anti-inflammatory clearance); context-dependent regulation of inflammation.
- **Biological Relevance:** quantitatively a main turnover route for erythrocytes, neutrophils and other cells; defense against pathogens and regulation of immunity.
- **Overlaps:** distinct from efferocytosis (which clears already-dead cells); shares phagocyte machinery.
- **C1–C6 (DRAFT):** 5 / 5 / 5 / 5 / 6 / 5 → **S = 5.10**
- **References:** Brown & Neher 2012, PMID 22682109 (primary).

## 5. PANoptosis
- **Category:** Integrated program
- **Year of Discovery:** 2019
- **Operational Definition:** An integrated inflammatory cell death that simultaneously engages Pyroptosis, Apoptosis, and Necroptosis through the RIPK1/RIPK3–FADD–caspase-8 complex, orchestrated by master regulators ZBP1 and TAK1 (Malireddi et al., 2019).
- **Key Molecules:** ZBP1, TAK1, RIPK1, RIPK3, FADD, caspase-8, NLRP3.
- **Inflammatory?:** Yes
- **Biological Relevance:** innate immune defense and host-pathogen response; a hub where death programs co-regulate.
- **Overlaps:** integrates pyroptosis + apoptosis + necroptosis.
- **C1–C6 (DRAFT):** 5 / 6 / 5 / 7 / 6 / 6 → **S = 5.70**
- **References:** Malireddi et al. 2019, PMID 31850239 (primary).

## 6. Lysoptosis
- **Category:** Legacy / unresolved (provisional)
- **Year of Discovery:** 2022
- **Operational Definition:** An evolutionarily conserved lysosome-dependent cell death defined by lysosomal membrane permeabilization (LMP) and cathepsin-dependent cytoplasmic proteolysis, predominating when neutralizing serpin inhibitors (SERPINB3 / srp-6) are absent (Luke et al., 2022).
- **Key Molecules:** cathepsins (predominantly cathepsin L); serpins (SERPINB3, mSerpinb3a, srp-6).
- **Inflammatory?:** Yes (LMP + cathepsin release)
- **Biological Relevance:** lysosomal quality control and a fallback death routine when lysosomal proteolysis is unopposed.
- **Overlaps:** subtype of lysosome-dependent cell death (LDCD); conscripted LMP in other RCD programs.
- **C1–C6 (DRAFT):** 4 / 5 / 4 / 5 / 5 / 4 → **S = 4.50**
- **References:** Luke et al. 2022, PMID 35022507 (primary). *Committee decision required for promotion from legacy status.*

## 7. Floatptosis
- **Category:** Emerging RCD form (provisional)
- **Year of Discovery:** 2025
- **Operational Definition:** A cytoplasmic vacuolization cell death induced by Bergeyella cardium variant in macrophages, characterized by **F**used **L**ys**O**some-**A**ssociated **T**ermination and inhibited by the sodium-channel inhibitor amiloride (Mao et al., 2025).
- **Key Molecules:** SLC9A9 (endosomal Na⁺/H⁺ exchanger), sodium channels; barrel-like membrane proteins (lipocalin, β-barrel, PorV).
- **Inflammatory?:** not specified
- **Biological Relevance:** host defense against bacterial infection via vacuole-fusion-driven death.
- **Overlaps:** lysosome-associated vacuolar death (distinct from apoptosis).
- **C1–C6 (DRAFT):** 3 / 4 / 3 / 7 / 5 / 3 → **S = 4.05**
- **References:** Mao et al. 2025, PMID 41115953 (primary).

## 8. Ammonia-induced cell death
- **Category:** Contextual program
- **Year of Discovery:** 2002
- **Operational Definition:** Dose-dependent cell death with vacuolation induced by ammonia (ammonium chloride) in epithelial cells, detoxified via arginase-mediated conversion to urea and protected by L-glutamine (Nakamura & Hagen, 2002).
- **Key Molecules:** arginase; L-glutamine.
- **Inflammatory?:** not specified (vacuolating)
- **Biological Relevance:** epithelial response to ammonia cytotoxicity (e.g., H. pylori infection).
- **Overlaps:** vacuolar/necrotic death features.
- **C1–C6 (DRAFT):** 4 / 3 / 3 / 4 / 4 / 4 → **S = 3.55**
- **References:** Nakamura & Hagen 2002, PMID 12388179 (primary).

## 9. Oncosis
- **Category:** Morphology / outcome (umbrella)
- **Year of Discovery:** 1995
- **Operational Definition:** Accidental cell death with cell swelling caused by failure of the plasma-membrane ionic pumps (e.g., ischemic cell death); the term (from Greek *ónkos*, swelling) was reintroduced by Majno & Joris (1995) to denote cell death with swelling, which leads to necrosis with karyolysis.
- **Key Molecules:** plasma-membrane ionic pumps (Na⁺/K⁺-ATPase).
- **Inflammatory?:** Yes (leads to necrosis)
- **Biological Relevance:** the morphological endpoint of non-apoptotic, energy-failure cell death (ischemia).
- **Overlaps:** leads to necrosis; contrasts with apoptosis (shrinkage).
- **C1–C6 (DRAFT):** 4 / 4 / 4 / 3 / 4 / 4 → **S = 3.85**
- **References:** Majno & Joris 1995, PMID 7856735 (primary).

## 10. Mitoxyperilysis
- **Category:** Emerging RCD form (provisional)
- **Year of Discovery:** 2025
- **Operational Definition:** A distinct lytic cell death induced by the synergism of innate immune signaling and metabolic disruption, in which mitochondria undergoing BAX/BAK1/BID-dependent oxidative stress maintain prolonged plasma-membrane contact and cause local oxidative membrane damage and lysis (Wang et al., 2025; the underlying process was termed *mitoxyperiosis*).
- **Key Molecules:** BAX, BAK1, BID; mTORC2.
- **Inflammatory?:** Yes (lytic)
- **Biological Relevance:** a death modality at the interface of innate immunity and mitochondrial metabolic stress.
- **Overlaps:** independent of pyroptosis, PANoptosis, necroptosis, ferroptosis, oxeiptosis.
- **C1–C6 (DRAFT):** 3 / 4 / 3 / 8 / 5 / 4 → **S = 4.25**
- **References:** Wang et al. 2025, PMID 41317732 (primary).

## 11. Linker cell-type death
- **Category:** Taxon-specific program (C. elegans; conserved)
- **Year of Discovery:** 2007
- **Operational Definition:** A caspase-independent (ced-3-independent), morphologically conserved non-apoptotic developmental death of the C. elegans linker cell, with nuclear crenellation, absence of chromatin condensation, organelle swelling, and cytoplasmic membrane-bound structures (Abraham et al., 2007).
- **Key Molecules:** let-7 microRNA; LIN-29 (Zn-finger).
- **Inflammatory?:** No
- **Biological Relevance:** developmental cell elimination, conserved in vertebrate neuronal development.
- **Overlaps:** non-apoptotic developmental death (vertebrate spinal cord, ciliary ganglia).
- **C1–C6 (DRAFT):** 3 / 4 / 3 / 4 / 5 / 3 → **S = 3.60**
- **References:** Abraham et al. 2007, PMID 17199042 (primary).

## 12. Cornification
- **Category:** Differentiation program
- **Year of Discovery:** 1947
- **Operational Definition:** Terminal differentiation of keratinocytes producing the cornified (keratinized) barrier; first indexed usage in a bronchial basal-cell papilloma with cornification (Adams & Schatzki, 1947). It is a differentiation endpoint rather than a death executioner.
- **Key Molecules:** not specified in founding abstract (to source from matrix)
- **Inflammatory?:** No
- **Biological Relevance:** formation of the epidermal/keratinized barrier.
- **Overlaps:** terminal differentiation (not a death executioner).
- **C1–C6 (DRAFT):** 4 / 3 / 4 / 3 / 4 / 3 → **S = 3.55**
- **References:** Adams & Schatzki 1947, PMID 20293116 (primary).

## 13. Triaptosis
- **Category:** Emerging RCD form (provisional)
- **Year of Discovery:** 2025
- **Operational Definition:** An endosome-dependent cell death modality (Tang, Kang & Kroemer, 2025).
- **Key Molecules:** endosomal machinery (not enumerated in the founding abstract)
- **Inflammatory?:** not specified
- **Biological Relevance:** a newly proposed modality dependent on endosomal function.
- **Overlaps:** distinct from lysosome-dependent death (endosome-centered).
- **C1–C6 (DRAFT):** 3 / 3 / 2 / 7 / 4 / 2 → **S = 3.45**
- **References:** Tang et al. 2025, PMID 39638924 (primary).

## 14. Spectosis
- **Category:** Emerging RCD form (provisional); cell-type-specific (erythrocytes)
- **Year of Discovery:** 2025
- **Operational Definition:** A programmed cell death of red blood cells in which complement activation initiates (mini)NLRP3–caspase-8 complexes culminating in hemolysis (Coombs, Burgener & Schroder, 2025).
- **Key Molecules:** complement; NLRP3; caspase-8.
- **Inflammatory?:** Yes (complement, hemolysis)
- **Biological Relevance:** RBC death in hemolytic disease.
- **Overlaps:** shares NLRP3–caspase-8 machinery with pyroptosis, but in mature RBCs.
- **C1–C6 (DRAFT):** 3 / 4 / 3 / 7 / 4 / 3 → **S = 3.95**
- **References:** Coombs et al. 2025, PMID 40499516 (primary).

## 15. Pyronecrosis
- **Category:** Legacy / unresolved (provisional)
- **Year of Discovery:** 2007
- **Operational Definition:** A necrosis-like, caspase-1-independent, ASC- and cathepsin B-dependent inflammatory macrophage death induced by pathogen infection (Shigella) or disease-associated CIAS1/cryopyrin (NLRP3) mutations, with spillage of HMGB1 (Willingham et al., 2007).
- **Key Molecules:** NLRP3 (CIAS1/cryopyrin), ASC, cathepsin B, HMGB1.
- **Inflammatory?:** Yes (necrotic, HMGB1 release)
- **Biological Relevance:** innate immune defense against intracellular pathogens.
- **Overlaps:** shares inflammasome components with pyroptosis, but caspase-1/IL-1β-independent.
- **C1–C6 (DRAFT):** 3 / 4 / 3 / 4 / 4 / 3 → **S = 3.50**
- **References:** Willingham et al. 2007, PMID 18005730 (primary). *Committee decision required for promotion from legacy status.*

---

## Audit notes
- All 15 records carry a **founding PMID** (verified against title).
- All prose statements are drawn **only** from the founding abstracts + V026 matrix.
- Fields the founding abstract does not provide are marked *"not specified"* (not invented).
- **C1–C6 are DRAFT** (rubric-informed) and require **two-call human review**; S is computed deterministically.
- Legacy entities (Aponecrosis, Lysoptosis, Pyronecrosis) remain **provisional pending committee promotion**.
