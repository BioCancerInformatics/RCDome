# Higor's 10 points — exact corrected sentences/numbers

## 1. T1–T4 definition (unify)
- BEFORE: two descriptions (source count + LLM, then weighted score A–D).
- AFTER (single): "Confidence tiers were computed as a weighted sum of channels — D = 4, B = 3, A = 1, C = 1 — then refined by the two-call LLM status: **T1 (Gold Standard)** = score ≥ 7, or score ≥ 4 with LLM CONFIRMED; **T2 (Strong)** = 4–6, or 2–3 with CONFIRMED; **T3 (Moderate)** = 2–3 with NEEDS_CONTEXT/NEEDS_LITERATURE, or 1 with CONFIRMED; **T4 (Weak)** = 1 with UNCLEAR/UNVERIFIED."

## 2. Europe PMC
- BEFORE: "…indexes the complete body text of approximately **40 million** biomedical articles…"
- AFTER: "…indexes approximately **12.3 million full-text articles** (of 48.9 million abstracts)…"

## 3. Denominator
- AFTER: state once: "**22,473 matrix rows = 21,568 unique gene–RCD pairs + 905 corroboration rows**; role/direction/tier counts are over the 22,473 rows."

## 4 & 8. Direction counts (update + clarify scope)
- BEFORE: "…9,489 regulators, 469 executors, 5 markers, 11,605 unresolved… PROMOTES 5,070, PROTECTS 4,755, UNCLEAR 11,743."
- AFTER: "…**9,971 regulators, 580 executors, 6 markers, 11,916 unresolved**… direction resolved as **PROMOTES 5,452, PROTECTS 4,964, UNCLEAR 12,057** (across all role-resolved associations)."
- Clarify Figure 3C: replace "among the 9,489 regulators" with "across all role-resolved associations" (or report the REGULATOR-only direction: 4,826 PROMOTES / 4,964 PROTECTS).

## 5. Tier counts
- BEFORE: T1 2,862 · T2 5,686 · T3 8,213 · T4 5,711 (sum 22,472).
- AFTER: **T1 2,864 · T2 5,686 · T3 8,212 · T4 5,711** (sum 22,473 ✓).

## 6. EXECUTOR precision
- BEFORE: "EXECUTOR precision was 100% because all 192 records … were downgraded…"
- AFTER: "After governance, **no unsupported EXECUTOR classifications remained**: all 192 Elicit-EXECUTOR records were downgraded to REGULATOR by the `required_for_death` rule. (Precision is not reported as a percentage here, because with zero retained EXECUTOR predictions it is undefined.)"
- (Keep the benchmark's 10/10 EXECUTOR precision as a *separate* statement about the model-selection benchmark, not the 192 downgrades.)

## 7. Definition-source counts
- Decoder truth: **NCCD 20 · Rodrigues 12 · de novo 19 · PRE_PUBMED 1 · COMPOSITE 1** = 53.
- BEFORE: "20 NCCD, 12 multi-optosis, 20 de novo, 1 composite"; "19/19 NCCD terms"; "40 non-NCCD entities".
- AFTER: "**20 NCCD-verbatim · 12 multi-optosis · 19 de novo · 1 pre-pubmed · 1 composite**"; clarify "verbatim integrity 19/19 NCCD" (one NCCD term not verbatim-checked) and define "40 non-NCCD entities" = 53 − 13 NCCD-represented.

## 9. "28 lack PMID-referenced definition"
- BEFORE: "28 of the 53 … lack multi-optosis operational definitions."
- AFTER: "28 of the 53 RCD-related entities lack **multi-optosis (Rodrigues) operational definitions**; these carry **de novo definitions anchored to a founding PMID**, so all 53 entities remain PMID-anchored."

## 10. "for the first time"
- BEFORE: "…makes this imbalance visible **for the first time**…", "…makes it measurable **for the first time**."
- AFTER: "…makes this imbalance **explicit**…", "…makes it **quantitatively measurable**…" (drop "for the first time").
