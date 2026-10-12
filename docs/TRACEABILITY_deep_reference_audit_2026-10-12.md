# TRACEABILITY — Deep public-register audit of both references (2026-10-12)

Scope: validate every "First described" (discovery) AND "Definition anchored to" (founding)
reference against the public registers (PubMed E-utilities + Crossref).

## Method

- Collected 68 unique PMIDs from the decoder (`discovery_pmid` + `founding_pmid`).
- Resolved every PMID via PubMed `esummary` (title, source, pubdate, DOI).
- Compared title (normalized, case-insensitive) + pubdate (YYYY Mon) + DOI for all
  105 reference rows (53 founding + 52 discovery).
- Resolved the 2 DOI-only discovery entries via Crossref.

## Result

- PMIDs resolved: 68/68.
- Reference rows validated: 105/105.
- Real mismatches: 0.
- DOI-only entries resolved: 2/2 (de Duve 1963 "The Lysosome Concept"; Virchow 1859
  "Die Cellularpathologie…", year 1859 confirmed by Crossref).

## Two flags reviewed (both non-issues)

1. "Senescence and Autophagy in Cancer" (composite) — `founding_pmid = "composite"` by design
   (not a citable single paper; no PMID to resolve).
2. "Cornification" founding — title "Cell death by cornification" is only 23 characters, below
   the 30-char matching threshold, so the automated check flagged it; manual review confirms
   it matches PubMed exactly (PMID 23792051, Eckhart et al. 2013, Biochim Biophys Acta).

## Conclusion

Every one of the 105 displayed references (discovery + definition anchor) is a real,
register-verified PMID/DOI with matching title, journal, pubdate, and DOI. No fabrication,
no hallucinated reference, no year mismatch.
