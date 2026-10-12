# TRACEABILITY — Discovery references added to the decoder (2026-10-12)

Trigger: Higor's Discovery Timeline audit (founding year vs founding paper mismatch for 19 entities).

## Change

- Added 3 decoder columns: `discovery_pmid`, `discovery_year`, `discovery_citation`.
- 19 historical entities (Case A): discovery = the verified original manuscript (16 PMIDs + 1 journal PMID + 2 DOIs).
- 33 recent entities (Case B): discovery = the definition anchor (the same paper).
- 1 composite (Senescence and Autophagy in Cancer): discovery = empty.
- Corrected "Mitotic catastrophe": `year` 1970 -> 1992; discovery = Ayscough et al. 1992 (PMID 1316996),
  the earliest "mitotic catastrophe" in PubMed (Rodrigues 2025 S1A listed 1970, unsupported).

## Provenance

- The 19 discovery references were verified via PubMed / Europe PMC / Crossref (title + authors + year match).
- The "Mitotic catastrophe" 1970 was traced: Rodrigues 2025 S1A -> "Pashootan-2024, page 7" -> Pashootan et al.
  2024 (PMID 37989403) -> page 7 does NOT state 1970 (cites Mascaraque 2019). No primary 1970 source exists.
- Pre-change backup: `RCDome_distribution/data/RCDome_Decoder_53_pre_discovery_2026-10-12.csv`.

## The 19 Case-A discovery references (verified)

| Entity | Discovery | PMID/DOI | Year |
|---|---|---|---|
| Necrosis | Virchow, Cellularpathologie | 10.1007/bf01945141 | 1859 |
| Autophagy | de Duve, Ciba Symp ch.1 | 10.1002/9780470715314.ch1 | 1963 |
| Lysosome-dependent cell death | de Duve et al., Biochem J | 13249955 | 1955 |
| Cellular senescence | Hayflick & Moorhead | 13905658 | 1961 |
| Apoptosis | Kerr, Wyllie & Currie | 4561027 | 1972 |
| Autophagy-dependent cell death | Schweichel & Merker | 4807128 | 1973 |
| MPT | Hunter & Haworth | 383019 | 1979 |
| Mitotic catastrophe | Ayscough et al. | 1316996 | 1992 |
| Hypersensitive response | Morel & Dangl | 16465279 | 1997 |
| Mitoptosis | Skulachev | 10626278 | 1999 |
| Pyroptosis | Cookson & Brennan | 11303500 | 2001 |
| Efferocytosis | deCathelineau & Henson | 14585077 | 2003 |
| Cornification | Candi, Schmidt & Melino | 15803139 | 2005 |
| Necroptosis | Degterev et al. | 16408008 | 2005 |
| ICD | Obeid et al. | 17187072 | 2007 |
| Parthanatos | Andrabi et al. | 19076445 | 2008 |
| Lysosomal cell death | Boya & Kroemer | 18955971 | 2008 |
| Methuosis | Overmeyer et al. | 18567800 | 2008 |
| Regulated Necrosis | Vanden Berghe et al. | 24452471 | 2014 |


## Spread to the Timeline module (2026-10-12)

- New file: `RCDome_distribution/data/discovery/discovery_papers.csv` (52 rows: 19 Case A + 33 Case B; composite skipped).
- `mod_timeline.R` now merges both CSVs and the discovery card shows two sections:
  - "First described" = `discovery_papers.csv` (e.g., Mitotic catastrophe -> Ayscough et al. 1992, PMID 1316996).
  - "Definition anchored to" = `founding_papers.csv` (e.g., Mitotic catastrophe -> Castedo et al. 2004, PMID 15077146).
- Node year still = decoder `year` (now the discovery year, 1992 for Mitotic catastrophe).
- All 17 discovery PMIDs verified via PubMed esummary (title/authors/journal/pubdate/DOI); 2 DOI-only entries entered from the verified source (de Duve 1963, Virchow 1859).
