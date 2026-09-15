# RCDome — Audit Propagation Gate (Standard Operating Procedure)

**Status: MANDATORY for every audit, re-adjudication, and data correction performed on RCDome.**

## Governing principle

> **adjudicated → propagated → independently verified**

Correcting the authoritative source (decoder, matrix, manuscript) is **not** completion. A change is complete only when its consequences have propagated to **every dependent artifact** and each dependency has been **independently verified**. Any residual disagreement between the authoritative source and a downstream artifact is a **propagation failure** — recorded and corrected, never silently patched.

## The five mandatory phases

### Phase 0 — Scope + pre-audit
- Define the change class (terminology / ontology / reference / evidence / schema / interface).
- Identify the **authoritative source** for the affected information.
- Identify every artifact that **consumes or reproduces** that information.

### Phase 1 — Adjudication
- Decide the change (propose + flag; never silently edit).
- Record: original state → adjudicated state → rationale → evidence/PMID.

### Phase 2 — Propagation (horizontal + vertical)
Apply the change to **every** dependent representation:
- **Horizontal** — manuscript, supplementary info, supplementary tables (all sheets), decoder (CSV/XLSX), matrix (CSV/RDS), app data, modules, www pages, landing pages, board prompts, figures/legends, descriptors, docs.
- **Vertical** — every *derived* value: counts, group distributions, summaries, labels, colors, tooltips, narrative prose, downloadable outputs.
- A level reclassification is **not done** until all level counts, legends, labels, and UI colors have been recalculated.

### Phase 3 — Independent verification
- Re-run `code/compliance_audit.py` (extend it with any new checks for this change).
- Re-run the cross-artifact **field-alignment** audit (decoder CSV == XLSX == app == Table S11; matrix mirror fields == decoder).
- Every check must PASS. A FAIL is a propagation failure.

### Phase 4 — Change-propagation matrix
Document every change in `CHANGE_PROPAGATION_MATRIX.md/.xlsx` with these columns:

| change_id | change | original_state | adjudicated_state | authoritative_source | dependent_artifacts | downstream_consequences | verification_status | corrections_performed | unresolved |

### Phase 5 — Governance gate
- The audit is **closed only when**: all accepted changes are propagated, all checks PASS, and the matrix is complete.
- Record **global deferred** items (expert review) separately — they are not propagation failures, but they must be explicit.

## Reusable instruments (keep these current)

- `code/compliance_audit.py` — automated checks (62 as of now); **extend, do not delete**.
- `CHANGE_PROPAGATION_MATRIX.md/.xlsx` — per-audit record.
- `FINAL_GOVERNANCE_GATE.md` — closure statement per audit.

## Anti-patterns (forbidden)

- ❌ "I updated the decoder; the audit is done."
- ❌ Silent search-and-replace across artifacts.
- ❌ Treating a presentational discrepancy as "minor" and leaving it.
- ❌ Correcting one mirror (e.g., Table S11) without checking the others.

## Traceability contract

Every change carries: what changed, why, where, and its verification result — preserving history and reproducibility, in line with the RCDome governance contract.
