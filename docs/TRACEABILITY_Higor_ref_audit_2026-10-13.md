# TRACEABILITY — Higor v2 reference audit applied (2026-10-13)

Trigger: Higor's Relatorio_Versão_02.docx (23 bibliographic interventions). Each was weighed
against the truth artifacts (PubMed/Europe PMC full text + DeepSeek RAG), NOT accepted blindly.

## Verification method
- Title + abstract (PubMed) for all candidates.
- FULL TEXT body for the open-access papers (PMC efetch): Boya 2003, Appelqvist 2012, Casares 2005, Kischkel 1995.
- User-supplied institutional PDFs (full text): Russell & Nurse 1986, Ayscough 1992, Liu 1996, Li 1997, Kluck 1997.
- DeepSeek RAG arbitration for discovery-vs-definition semantics.

## Changes applied (4)

1. Apoptosis (extrinsic)
   - Before: year 2004 · founding/discovery 15451440 (an INTRINSIC-pathway paper).
   - After: year 1995 · founding/discovery 8521815 (Kischkel et al. 1995, EMBO J — the DISC; full text confirms "DISC" x11).

2. Apoptosis (intrinsic)
   - Before: year 2002 · founding/discovery 12186923 (an HIV neuronal model).
   - After: year 1996 · discovery 8689682 (Liu et al. 1996, Cell — cytochrome c/dATP; full text confirms "cytochrome c" x92);
     founding 9390557 (Li et al. 1997, Cell — Apaf-1/caspase-9; full text confirms Apaf-1 x80, caspase-9 x112);
     complementary 9027315 (Kluck et al. 1997, Science — cytochrome c release).

3. Lysosome-dependent cell death
   - Before: year 1955 · 13249955 (de Duve 1955 = lysosome ORGANELLE discovery, not the death modality).
   - After: year 2012 · founding/discovery 23166840 (Appelqvist et al. 2012, PLoS One; full text confirms the term x2).

4. Immunogenic cell death (discovery only)
   - Discovery: 17187072 -> 16365148 (Casares et al. 2005, J Exp Med — first doxorubicin ICD demonstration).
   - Founding: 23157435 (Kroemer 2013 review) -> 16365148 (Casares et al. 2005, J Exp Med) — per DeepSeek + Europe PMC RAG,
     Casares 2005 is the operational-definition anchor (doxorubicin-induced immunogenic tumor death);
     Obeid 2007 (17187072, calreticulin) retained in primary_refs_pmids as the mechanism.

## Rejected / kept (verified, no change)
- Mitotic catastrophe: KEEP Ayscough 1992 (1316996) — "mitotic catastrophe" x14 in body.
  Russell & Nurse 1986 (3955656) REJECTED — full text has 0 "mitotic catastrophe" (it is mitotic CONTROL, cdc25 x152).
- Lysosomal cell death: KEEP Boya 2008 (18955971) = definition (Higor's 2003 is the mechanism).
- Regulated Necrosis: KEEP Vanden Berghe 2014 (24452471) = definition (NOT_IN_NCCD_2018; Galluzzi 2011 = FADD/RIP3 mechanism).
- ADCD, Cornification, HR, Mitoptosis, Parthanatos and 11 others: KEEP ours (consistent or already applied).

## Propagation
- Matrix: NO change. The fixed variables (year/founding_pmid/discovery_pmid/reference_citation)
  are NOT inherited by the matrix; the matrix's decoder-derived columns are identity/level/category only,
  and its pmid_list/llm_pmids/etc are gene-pair evidence PMIDs. Source-provenance columns preserved byte-identical.

## Provenance
- Backups: RCDome_Decoder_53_pre_Higor_ref_fix_2026-10-13.csv,
  founding_papers_pre_Higor_ref_fix_2026-10-13.csv, discovery_papers_pre_Higor_ref_fix_2026-10-13.csv.
- PDFs used for full-text verification: analysis/Revisão Higor APP RCDOme/PDF Higor conflicting/.
