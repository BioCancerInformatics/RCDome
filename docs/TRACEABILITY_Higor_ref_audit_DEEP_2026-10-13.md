# Deep Audit — Higor "Relatorio_Versão_02" vs RCDome Decoder (2026-10-13)

Higor's report proposed 23 bibliographic interventions on the Discovery Timeline references.
Each was independently weighed against the truth artifacts — **never accepted blindly** — using
PubMed (title+abstract), Europe PMC + PMC **full text** (open-access), **user-supplied institutional
PDFs** (paywalled), and **DeepSeek RAG arbitration** (discovery-vs-definition semantics).

Governance rule applied: a reference change is only made when the **full-text body** confirms the
term/concept (the Triaptosis lesson — the decisive word may be in the body, not the title/abstract).

---

## Per-item disposition

### FIXED (5 changes, 4 entities)

| # | Entity | Higor proposed | Final applied | Evidence |
|---|---|---|---|---|
| 02 | Apoptosis (extrinsic) | Kischkel 1995 (DISC) | year 2004→**1995**; founding/discovery 15451440→**8521815** | full text: "DISC" ×11 |
| 03 | Apoptosis (intrinsic) | Li 1997 + complements | year 2002→**1996**; discovery→**8689682** (Liu 1996); founding→**9390557** (Li 1997) | Liu full text: "cytochrome c" ×92; Li: "Apaf-1" ×80, "caspase-9" ×112 |
| 10 | Immunogenic cell death | Casares 2005 | discovery **and** founding→**16365148** (Casares 2005); Obeid 2007 (17187072) kept as mechanism ref | full text: "immunogenic" ×60; DeepSeek RAG: Casares = OD anchor |
| 12 | Lysosome-dependent cell death | Appelqvist 2012 | year 1955→**2012**; founding/discovery 13249955→**23166840** | full text: "lysosome-dependent cell death" ×2 |

### REJECTED (1 — Higor's paper is the wrong concept)

| # | Entity | Higor proposed | Why rejected | Kept |
|---|---|---|---|---|
| 16 | Mitotic catastrophe | Russell & Nurse 1986 (3955656) | full text has **0** "mitotic catastrophe" ("cdc25" ×152 = mitotic *control*, not the term) | **Ayscough 1992 (1316996)** — "mitotic catastrophe" ×14 in body |

### KEPT — ours already correct or verified (18)

| # | Entity | Kept reference | Basis |
|---|---|---|---|
| 01 | Apoptosis | Kerr 1972 (4561027) | already correct (discovery) |
| 04 | Autophagy | de Duve 1963 (DOI) | already correct |
| 05 | Autophagy-dependent cell death | Schweichel & Merker 1973 (4807128) | DeepSeek: first described = morphology |
| 06 | Cellular senescence | Hayflick & Moorhead 1961 (13905658) | already correct |
| 07 | Cornification | Candi et al. 2005 (15803139) | DeepSeek: it's the *definition* |
| 08 | Efferocytosis | deCathelineau & Henson 2003 (14585077) | already correct |
| 09 | Hypersensitive response | Morel & Dangl 1997 (16465279) | DeepSeek: it's the *definition* |
| 11 | Lysosomal cell death | Boya & Kroemer 2008 (18955971) | DeepSeek: it's the *definition* (Higor's 2003 = mechanism) |
| 13 | Methuosis | Overmeyer et al. 2008 (18567800) | already correct |
| 14 | MPT | Hunter & Haworth 1979 (383019) | already correct |
| 15 | Mitoptosis | Skulachev 1999 (10626278) | DeepSeek: 1999 = the concept (2001 = the term) |
| 17 | Necroptosis | Degterev et al. 2005 (16408008) | already correct |
| 18 | Necrosis | Virchow 1859 (DOI) | already fixed earlier (founding → Galluzzi NCCD 29362479) |
| 19 | Parthanatos | Andrabi et al. 2008 (19076445) | DeepSeek: it's the *definition* (2008 earlier than David 2009) |
| 20 | Pyroptosis | Cookson & Brennan 2001 (11303500) | already correct |
| 21 | Regulated Necrosis | Vanden Berghe et al. 2014 (24452471) | DeepSeek: it's the *definition* (NOT_IN_NCCD_2018); Galluzzi 2011 = mechanism |
| 22 | PANoptosis | Malireddi et al. 2019 (31850239) | already correct |
| 23 | Phagoptosis | Brown & Neher 2012 (22682109) | already correct |

### REJECTED BY DESIGN — complementary-PMID suggestions (6)

Higor's "associate as complementary" notes (intrinsic +Yang 1997, MPT 1979 series, Parthanatos 2006,
Pyroptosis 11029688, PANoptosis 2020, Phagoptosis Fricker 2012) were **rejected**:

- **Not appropriate** — outside the decoder's OD-anchor scope (discovery + founding).
- **Not needed** — discovery + founding are already correct and full-text verified.
- **Not extensible** — universal application to all 53 entities would require ~100–150 more
  verifications with marginal value; partial adoption would create inconsistency.

---

## Summary

| Disposition | Count |
|---|---|
| FIXED | **5** (extrinsic, intrinsic, lysosome-dependent, ICD ×2) |
| REJECTED (wrong concept) | **1** (mitotic catastrophe → Russell 1986) |
| KEPT (correct/verified) | **17** |
| Complementary-PMID suggestions rejected by design | **6** |

**Net: 5 reference corrections applied, 18 of 23 Higor proposals rejected/kept on evidence, and the
decoder's two-reference model (discovery + definition) preserved.**

## Provenance

- Backups: `RCDome_Decoder_53_pre_Higor_ref_fix_2026-10-13.csv` (+ `_pre_ICD_founding_2026-10-13.csv`),
  `founding_papers_pre_Higor_ref_fix_2026-10-13.csv`, `discovery_papers_pre_Higor_ref_fix_2026-10-13.csv`.
- Full-text PDFs: `analysis/Revisão Higor APP RCDOme/PDF Higor conflicting/` (Russell 1986, Ayscough 1992,
  Liu 1996, Li 1997, Kluck 1997, Kischkel 1995).
- Matrix: no change (fixed variables are not inherited; source-provenance columns byte-identical).
