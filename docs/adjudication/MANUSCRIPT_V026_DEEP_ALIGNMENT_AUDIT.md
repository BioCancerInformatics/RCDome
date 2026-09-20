# Manuscript V026 — Deep line-by-line alignment audit (vs matrix, decoder, app, GitHub)

**Method:** every quantitative claim extracted from `RCDome_manuscript_governance_V026.docx` and compared against the truth documents — matrix V026 (`unified_gene_rcd_matrix_V026.csv`, 22,473×71), decoder (`RCDome_Decoder_53.csv`), and the cleaned app (`RCDome_distribution`). Per the governance rule: nothing taken for granted, no placeholder accepted.

## Summary

| | |
|---|---|
| Numeric claims audited | 31 key metrics |
| Aligned (verified correct) | 27 |
| Discrepancies found | **4** |

---

## Findings (tabular)

| # | Manuscript claim | Truth (matrix/decoder) | Why it must be addressed | How to fix |
|---|---|---|---|---|
| 1 | ¶191 (Fig 2 legend): "The full run classified all **21,566** unique (gene, RCD-related entity) pairs" | **21,568** unique pairs | Inconsistent with every other paragraph (¶121, 257, 312, 353, 355, 366, 378 all say 21,568) and with the matrix | Change "21,566" → "21,568" in ¶191 |
| 2 | ¶257: "**22,214** carry PMIDs (**98.8%**), corresponding to **21,309** of these 21,568 unique combinations" | matrix: **22,116** rows (98.4%) and **21,212** unique pairs carry a PMID | Off-by-98 rows / 97 pairs; the two headline denominators disagree with the matrix | Re-derive the PMID-count rule from the matrix (which column(s) define "carry PMID"), re-run the count, and correct the three numbers; document the rule in Methods |
| 3 | ¶153: "the **10,141** curated PMIDs that constitute the association evidence" | not reproducible from the matrix columns (unique `pmid_list` = 2,109; all-channel unique = 324,678) | The provenance of "10,141" is untraceable — no single column/rule yields it | Trace the curation log/script that produced 10,141; either cite the exact derivation or replace with the reproducible matrix count |
| 4 | ¶254: "**23 of 71** matrix columns are 100% populated with traceable data" | matrix: **31** columns are non-null/non-empty (71 total) | The "23" figure has no visible derivation; the matrix shows 31 fully-populated columns | Define "traceable" precisely (e.g., exclude derived/key columns), recompute, and align the number + the definition in Methods |

## Confirmed-aligned (verified correct — no action)

- Rows 22,473 · unique pairs 21,568 · genes 9,265 · 53 entities · 62 original name strings ✓
- Level counts: L1 16 · L2 5 · L3 2 · L4 11 · L5 19 ✓
- Evidence tiers: T1 2,864 · T2 5,686 · T3 8,212 · T4 5,711 ✓
- Roles (unique pairs): REGULATOR 9,489 · EXECUTOR 469 · MARKER 5 · UNCERTAIN 11,605 ✓
- Directions: PROMOTES 5,070 · PROTECTS 4,755 · UNCLEAR 11,743 · (regulators) PROMOTES 4,556 / PROTECTS 4,755 / UNCLEAR 178 ✓
- Mechanistic fraction by level: L1 64.7% · L2 40.5% · L3 33.3% · L4 23.9% · L5 31.3% ✓
- Definition sources: NCCD 20 · Rodrigues 12 · founding-draft 19 + pre-PubMed 1 (20 de novo) · composite 1 ✓
- NCCD status: NCCD_2018_INVARIANT 20 · NOT_IN_NCCD_2018 33 ✓
- 20/20 NCCD verbatim · 33 non-NCCD ✓
- Europe PMC: 167,868 open-access full-text articles · 21,309 pairs (see finding #2) ✓
- num_sources: 10,009 single · 6,313 two-source (Supplementary Fig S1) ✓
- 84 self-inconsistent rows repaired · 231 uncertain retained (reconciliation log) ✓
- species_scope: 49 human + 4 non-human (Erebosis, Hypersensitive response, Linker cell-type death, Vacuolar cell death) ✓

## Governance disposition

- Findings #1 is a **simple typo** → fix directly in the manuscript.
- Findings #2, #3, #4 are **traceability gaps** → they require re-deriving the counting rule from the matrix/code and either correcting the number or documenting the exact derivation. No placeholder, no assumption.

Next step: authorize me to (a) fix #1, and (b) trace the PMID + column-count derivations in the pipeline code (`Phase 2A/D`, `Phase 2B`, `recompute_results_counts.py`) to resolve #2–#4.
