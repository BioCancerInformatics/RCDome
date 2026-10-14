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
   - After: year 1995 · discovery 7533326 (Nagata & Golstein 1995, Science — "The Fas death factor");
     founding 8521815 (Kischkel et al. 1995, EMBO J — the DISC; full text confirms "DISC" x11).
   - Correction (2026-10-13, post-certification): "First described" was first set to the DISC, but the
     card showed the SAME reference twice; the true first-described is Nagata & Golstein 1995 (7533326),
     making extrinsic a proper Case A (distinct discovery vs definition).

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


## Rejected by design: complementary-PMID suggestions

Higor's "associate as complementary" notes (6 entities: intrinsic +Yang 1997, MPT 1979 series,
Parthanatos 2006, Pyroptosis 11029688, PANoptosis 2020, Phagoptosis Fricker 2012) are REJECTED:
- NOT appropriate — outside the decoder's OD-anchor scope (discovery + founding).
- NOT needed — the discovery + founding references are already correct and full-text verified.
- NOT extensible — universal application to all 53 entities would require ~100-150 more full-text
  verifications with marginal value, and partial adoption would create inconsistency.
The decoder's two-reference model (discovery_pmid + founding_pmid) is the correct granularity.
Source-provenance fields (primary_refs_pmids / primary_discovery_reference) remain byte-identical
per the "never replace, always add" rule.


## Post-certification audit (duplication sweep)

A "same reference on both lines" sweep found two further review-as-discovery cases; both were
REJECTED on review, with one year-fix applied:

- Oncosis: von Recklinghausen 1910 REJECTED as first-described (German book, no PMID); kept Majno & Joris 1995.
- Regulated Necrosis: Galluzzi 2011 (21894190) REJECTED as first-described (FADD/RIP3 mechanism, not the umbrella definition);
  kept Vanden Berghe 2014; year corrected 2011 -> 2014 (consistency with the anchor paper).
- Extrinsic: "First described" corrected to Nagata & Golstein 1995 (7533326), distinct from the DISC (8521815).
