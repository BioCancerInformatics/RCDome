# Phase 2B Ground-Truth Audit — Selection Criteria & Verified Papers

**Status:** REPAIRED (2026-08-16) — supersedes the original undocumented 4-paper list.
Final verification: every paper's body was checked to actually contain its gene,
and each gene's NCCD role was corrected.

## Purpose
The `--validate` mode runs a ground-truth audit of the Phase 2B full-text RAG pipeline
against landmark papers with definitively known gene–RCD associations. It measures:
- gene symbol recall
- RCD form detection accuracy
- role classification accuracy
- sentence verifiability (exact-string, target 100%)
- hallucination rate (target 0%)

## Selection criteria (documented)
Each ground-truth paper MUST satisfy ALL of the following:

1. **Primary research** (landmark discovery or key mechanism paper), not a review.
2. Establishes a **definitively known gene** in a representative RCD form, with its
   correct NCCD role (EXECUTOR vs REGULATOR).
3. The gene **actually appears in the paper body** (verified by full-text search).
4. **Fetchable full text** via NCBI efetch (`db=pmc&rettype=xml`).
5. **Verified against NCBI** — PMID and PMCID cross-checked at selection time.

## Verified papers (cross-checked against NCBI + body-contains-gene + role-corrected)

| # | RCD form | Paper | Gene | Role | PMID | PMCID | Body check |
|---|----------|-------|------|------|------|-------|-----------|
| 1 | Ferroptosis | Yang et al. 2014, *Cell* 156:317 | GPX4 | **REGULATOR** (repressor) | 24439385 | PMC4076414 | GPX4 ×63 ✓ |
| 2 | Necroptosis | Cai et al. 2014 | MLKL | **EXECUTOR** | 24316671 | PMC8369836 | MLKL ✓ |
| 3 | Pyroptosis | Sborgi et al. 2016, *EMBO J* 35:1766 | GSDMD | **EXECUTOR** | 27418190 | PMC5010048 | GSDMD ✓ |
| 4 | Cuproptosis | Tsvetkov et al. 2022, *Science* 375:1254 | FDX1 | **REGULATOR** (positive) | 35298263 | PMC9273333 | FDX1 ✓ |

## Audit results (2026-08-16, corrected roles)

Local run and Zima production run agree on the three primary metrics (100%).
Verbatim counts vary slightly run-to-run (LLM sampling); shown are the Zima production numbers.

| Metric | Result |
|--------|--------|
| Gene symbol recall | **4/4 (100%)** |
| RCD form detection | **4/4 (100%)** |
| Role classification | **4/4 (100%)** |
| Verbatim sentences verified | 52 (16+15+20+2); 1 rejected |
| Hallucinated sentences | 1 caught (Sborgi 2016) — anti-hallucination framework working |

## Correction log (governance)

| Item | Original (wrong) | Corrected | Reason |
|------|------------------|-----------|--------|
| Ferroptosis paper | Dixon et al. 2012, PMC3367386, GPX4 | Yang et al. 2014, PMC4076414, GPX4 | Dixon 2012 *named* ferroptosis but never mentions GPX4 (0 occurrences in body); GPX4 was established by Yang 2014 |
| Necroptosis paper | Sun et al. 2012, PMC3308724, RIPK3 | Cai et al. 2014, PMC8369836, MLKL | PMC3308724 is a *nursing* paper; Sun 2012 is MLKL (paywalled); MLKL is the necroptosis executor |
| Pyroptosis paper | Shi et al. 2015, PMC4660266, GSDMD | Sborgi et al. 2016, PMC5010048, GSDMD | PMC4660266 is a *chromosomal-loop* paper; Shi 2015 is paywalled |
| GPX4 role | EXECUTOR | REGULATOR (repressor) | GPX4 *prevents* ferroptosis; its loss triggers death — not an executor |
| FDX1 role | EXECUTOR | REGULATOR (positive) | FDX1 is a positive regulator required for cuproptosis, not the membrane-executing protein |

The original list was undocumented (no selection criteria) and carried five errors
(two wrong PMCIDs, one wrong gene, one wrong paper, two wrong roles).
This file now provides the traceable provenance and the measured metrics.

## How to run

```bash
python3 channel_c_deep_xml_rag.py --validate
```
