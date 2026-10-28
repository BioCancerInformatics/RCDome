# The Highlander Rule — RCDome honesty/traceability/reproducibility/transparency audit
Version 1 · adopted 2026-10-27 · born from the ELICIT192 propagation failure.

## The principle

**There can be only one** authoritative value for any scientific fact. That value lives in the
truth matrix (`unified_gene_rcd_matrix_V027.csv`) and the decoder (`RCDome_Decoder_53.csv`).
Every manuscript sentence, table cell, figure label, figure legend, dataset export, app value,
and email must derive from — and equal — that single value. No email, no prior report, and no
implementation log is ever a source of truth.

## The five rules (the ELICIT192 lessons)

### R1 — Source hierarchy (enforced)
- T0 truth: matrix + decoder. Nothing else.
- T1 derived: Dataset S1, app RDS, disc_df — must be byte-identical exports of T0.
- T2 documents: manuscript, SI, tables, figures, emails — checked against T0, never trusted.
- Any number whose derivation cannot be traced to T0 is **NOT_VERIFIABLE**, not "assumed correct."

### R2 — Log the decision before you propagate
- Before editing any artifact, record: the decision, the exact before→after values, the
  computation (script + inputs + output), and the human approval.
- The log is the **only** place a correction may originate. An email may *report* a value but
  may never *introduce* one.

### R3 — Atomic, bidirectional propagation
- One correction → one step that updates: manuscript (all passages), SI, tables, figures +
  legends, email `.md` **and** `.docx`, mirrors, and the distribution ZIP.
- Horizontal = every passage of the same artifact. Vertical = every dependent artifact.
- A half-propagated fix (e.g., `.md` updated but `.docx` stale) is a **failure**, not a partial success.

### R4 — Numerical verification, not presence verification
- The audit recomputes every count, denominator, percentage, and split against T0.
- A "36/36" that only checks that an edit exists is not a verification — it is a checklist.
- Verification status: **CONFIRMED / SUSPECTED / CONSISTENT / NOT_VERIFIABLE** — with the
  exact source rows or a declared gap.

### R5 — The close gate
- A correction is **open** until R1–R4 pass on every artifact.
- "Closed" requires: the numerical audit shows all artifacts equal the T0-derived value, the
  ZIP/mirrors/docx are rebuilt, and the log records the reconciliation.

## The ELICIT192 verdict, per this rule

- R1 violated (email introduced 172/20 as if authoritative).
- R2 violated (172/20 had no logged computation).
- R3 violated (email `.docx` and mirrors not propagated).
- R4 violated (36/36 checked presence, not numbers).
- R5 violated (declared complete while artifacts disagreed).

## Standing order

Any future correction follows R1→R5 in order. A correction that skips a rule is rejected at
review, regardless of how obvious the edit appears.

## R4 amendment (2026-10-27) — the denominator rule
A count is comparable only if its DENOMINATOR is explicit (raw rows vs unique gene-RCD pairs vs unique genes). The role-distribution check must use UNIQUE PAIRS (the manuscript's evidence-first/death-core establishment), not raw rows. A detector that ignores the denominator invents false inconsistencies. (ELICIT-role lesson: "225/4,455/95/16,793" = unique pairs, CONSISTENT; the raw "303/4,703/126/17,341" is a different layer.)

## R4 amendment (2026-10-27) — the detector is a DETECTIVE, not a comparator
A detector that flags a number as INCONSISTENT without first establishing (a) what the number SEMANTICALLY refers to and (b) which source/denominator is authoritative for that semantics, is a **fabricator of inconsistencies** — worse than no detector, because it manufactures false flags that then require re-audit.

Therefore, before any inconsistency may be reported:
1. Establish the SEMANTICS (raw rows vs unique pairs vs unique genes; benchmark run vs production run; evidence-first vs DeepSeek/Consensus/Elicit).
2. Establish the PROVENANCE (the exact file/run/column/denominator in the tree).
3. Only then compare.
4. If the semantics cannot be established, the verdict is NOT_VERIFIABLE — never INCONSISTENT.

An inconsistency is reported only when it is CONFIRMED against the correct semantics + provenance. Anything less is the detector hallucinating.

## CLOSURE LOG
- ELICIT192 — RESOLVED + LOCKED (2026-10-27). Correction 172/20 → ~167/~25 propagated everywhere.
  Evidence: TRACEABILITY_higor_review_implementation_2026-10-26.md (logged ~167/~25); raw CSVs 283→250/33.
  Guarded by R1–R5 + the R4 agent. Do not reopen without new evidence.
- R4 EXHAUSTIVE DETECTOR + DENOMINATED CORRECTNESS PASS — COMPLETE (2026-10-28).
  4,688 values audited (after decimal-split fix): 385 CONSISTENT (matrix/decoder/disc_df truth) + 3,759 DERIVED (denominated + verified correct) + 544 external/noise (508 PMIDs/DOIs/pages + 36 computed decimal scores/percentages).
  **Nothing unexplained, nothing incorrect.** Evidence: docs/AUDIT_R4_exhaustive_detector_2026-10-28.md.
  The auto-STALE keyword flag was reverted (it fabricated discordances); STALE is human-adjudicated only.

## STANDING ORDER — USE THE AGENT (not just log it)
- `analysis/r4_agent.R` is the **mandatory pre-submission audit**. Run it before every manuscript/submission propagation.
- `analysis/r4_exhaustive_detector.R` is the **mandatory derivation map** — every value must land CONSISTENT (matrix truth) or DERIVED (traced + denominated). UNRESOLVED must be earned by an exhaustive dive, then human-adjudicated.
- Pipeline: classify noise → bind local tuples → verify matrix-bound counts → in-memory provenance dive (~8,000 files).
- Any DISCORDANT or MISSING verdict blocks closure until resolved with human approval.
- **The denominated correctness pass (human-adjudicated, detective-style) is the final gate before claiming "all values correct"** — denominate (raw vs pairs vs genes vs role-resolved vs benchmark) before comparing; never auto-flag; innocent until proven guilty.
- The agent is a single codebase, logged here, and must be run — not just stored.
