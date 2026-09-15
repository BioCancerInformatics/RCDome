# Priority B — evidence-maturity vs literature brief (12 entities)

Provisional, data-driven. The `evidence_maturity` label is a *curatorial* judgment; the matrix gene-evidence split is a *supporting signal*, not a verdict. Proposals are flagged for the human expert — nothing applied.

## Proposed maturity changes (7)

| Entity | Level | Current maturity | Gene evidence | Proposed | Reason |
|---|---|---|---|---|---|
| Alkaliptosis | L1 | established | 24 genes · 0 MECH · 9 REG · 13 CTX_GAP | **SUPPORTED** | recent (2018), no strict mechanistic gene evidence |
| Methuosis | L1 | established | 2 genes · 1 EXEC | **SUPPORTED** | only 2 associated genes; concept thin |
| Paraptosis | L1 | established | 5 genes · 1 EXEC | **SUPPORTED** | debated mechanism; few genes |
| Ammonia-induced cell death | L4 | supported | 20 genes · all INSUFFICIENT_DATA | **PROVISIONAL** | no classified mechanistic/regulatory evidence |
| Erebosis | L5 | established | 6 genes · 0 EXEC · single paper | **EMERGING** | Ciesielski 2022, single report, no replication |
| Metalloptosis | L5 | supported | 36 genes · 26 DATABASE_ONLY | **PROVISIONAL** | umbrella; mostly database-only associations |
| Mitoptosis | L5 | established | 5 genes · 2 EXEC | **LEGACY** | mitochondrial quality-control concept; category is already LEGACY |

## Proposed KEEP (5)

| Entity | Level | Current maturity | Basis for keeping |
|---|---|---|---|
| Entosis | L1 | established | Overholtzer 2007 + NCCD 2018; 77 genes, 39 regulators |
| Eryptosis | L4 | established | Lang 2006; well-replicated erythrocyte program |
| Mitotic death | L4 | established | NCCD-recognized contextual outcome; 233 genes |
| Oncosis | L4 | established | Majno & Joris 1995; classic morphological term |
| Linker cell-type death | L5 | established | Abraham 2007; well-established C. elegans developmental death (taxon-specific) |

## Notes

- `MECHANISTIC` = 0 for all 12: this is the *strictest* gene-level class (LLM + PubMed double confirmation). It is a proxy, not proof that maturity is wrong — hence **flag, don't auto-change**.
- `independent_replication` = "pending" for all (global deferred G5 field).
- Species flags: Erebosis ("human" may be inaccurate — gut enterocyte turnover concept); Linker cell-type death (correctly `invertebrate_model`).

Full data table: `ADJUDICATION_priorityB_maturity_brief.xlsx`.
