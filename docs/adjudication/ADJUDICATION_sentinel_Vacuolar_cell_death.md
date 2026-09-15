# 53-Entity Adjudication — SENTINEL CASE: Vacuolar cell death (VCD)

> **Species correction (2026-09-12):** the founding evidence is *Dictyostelium discoideum* (protist, Kosta 2004 PMID 15358773), and the principal literature is *plant* (Norway spruce, Arabidopsis) — NOT human, NOT fungal/yeast. The earlier 'fungal (yeast)' reading was corrected.


Provenance-preserving expert nomenclature and ontological adjudication. Read-only; proposal + flag (final biological call deferred to the human expert).

---

## 1. Data pulled from RCDome artifacts

| Field | Value (decoder) | Value (matrix) |
|---|---|---|
| entity | Vacuolar cell death | — |
| current level | L4 | L4 |
| level name | Functional/contextual | L4 Functional/contextual |
| category | MORPHOLOGY | — |
| hard_gate_status | NOT-L1 | — |
| operational_definition | "A cell death modality demarcated by conspicuous cytoplasmic vacuolization, with a hidden non-vacuolar pathway revealed by autophagy-gene disruption." | — |
| definition source | FOUNDING_DRAFT | — |
| founding / reference PMID | 15358773 (Kosta et al. 2004) | — |
| key molecules | atg1 | — |
| species_scope | cross_species | — |
| evidence_maturity | supported | — |
| relationship_type | associated_with | — |
| independent_replication | pending | — |
| genes | — | 24 rows / 24 genes |
| role | — | UNCERTAIN ×24 |
| mechanistic class | — | INSUFFICIENT_DATA ×24 |
| evidence tier | — | T3 ×24 |

## 2. G0–G6 hard-gate adjudication (proposed)

| Gate | Verdict | Basis |
|---|---|---|
| G0 whole-cell death | PARTIAL | Death reported in Dictyostelium discoideum (protist; Kosta 2004), but vacuolization is a phenotype, not the demonstrated cause of death. |
| G1 causal machinery | **NO** | Only "atg1" named; atg1 is autophagy/vacuolization machinery, not a death-execution machinery. No executioner identified. |
| G2 functional necessity | **NO** | atg1 disruption *reveals a hidden non-vacuolar pathway* — i.e., death still occurs without vacuolization. Not necessary for death. |
| G3 phenotype/trigger | YES (phenotype) | Conspicuous cytoplasmic vacuolization (morphological phenotype). |
| G4 published name | YES | "Vacuolar cell death" / Kosta et al. 2004 (PMID 15358773). Naming alone ≠ mechanism. |
| G5 independent replication | NO / pending | Decoder records "pending". |
| G6 species scope | **plant + protist (not human)** | Founding evidence is S. cerevisiae (atg1). No human/mammalian evidence found. Decoder "cross_species" is unsupported. |

**L1 conclusion:** fails G1 + G2 → NOT a bona fide RCD modality. Current NOT-L1 + L4 is consistent with this.

## 3. Q1–Q20 adjudication (proposed)

1. **What is named?** A morphological description — death accompanied by conspicuous cytoplasmic vacuolization.
2. **Whole-cell death?** Reported in yeast; the vacuolization itself is not shown to be the cause.
3. **Defining trigger?** Not mechanistically defined (vacuolization = phenotype).
4. **Execution machinery?** Not identified.
5. **Causally necessary molecules?** None established (atg1 is necessary for vacuolization, not death).
6. **Perturb machinery → prevent death or alter morphology?** Alters **morphology only** (atg1Δ reveals non-vacuolar death).
7. **Distinguishable mechanism?** No independent mechanism established.
8. **Term type?** **Morphological** (vacuolization).
9. **Species?** Yeast (S. cerevisiae) — founding evidence.
10. **Human cells?** No evidence.
11. **Mammalian cells?** No evidence.
12. **Independently replicated?** No / pending.
13. **Strongest primary literature?** Kosta et al. 2004, PMID 15358773 (yeast).
14. **Counterevidence against independence?** atg1 disruption does not prevent death → vacuolization is not the mechanism; it is a yeast autophagic/morphological phenotype.
15. **Is L4 justified?** Defensible as a morphology/context label; but it is really MORPHOLOGICAL + TAXON_SPECIFIC (yeast).
16. **Move / subtype / umbrella / other?** Keep at L4 (or reconsider L5 taxon-specific); reclassify relationship to MORPHOLOGICAL + TAXON_SPECIFIC. Flag for review.
17. **Definition accurate?** Partly — the "hidden non-vacuolar pathway" is faithful to Kosta 2004; "cell death modality" is inaccurate.
18. **Overstates certainty?** Yes — "modality" overstates mechanistic independence.
19. **"modality" misused?** Yes → replace with "morphology / RCD-related entity".
20. **Evidence maturity?** "supported" is too strong → propose **PROVISIONAL** (single yeast study, no replication).

## 4. Proposed 29-column adjudication row

| # | Column | Value (proposed) |
|---|---|---|
| 1 | entity | Vacuolar cell death |
| 2 | current_rcdome_level | L4 |
| 3 | current_level_name | L4 Functional/contextual |
| 4 | current_operational_definition | (see above) |
| 5 | source_of_definition | FOUNDING_DRAFT (Kosta 2004) |
| 6 | founding_PMID | 15358773 |
| 7 | reference_PMID | 15358773 |
| 8 | species_scope | cross_species → **proposed plant + protist (not human)** |
| 9 | evidence_maturity | supported → **proposed PROVISIONAL** |
| 10 | whole_cell_death_G0 | PARTIAL |
| 11 | causal_machinery_G1 | NO |
| 12 | functional_necessity_G2 | NO |
| 13 | phenotype_trigger_G3 | YES (morphological phenotype) |
| 14 | published_name_G4 | YES |
| 15 | independent_replication_G5 | NO / pending |
| 16 | species_scope_G6 | plant + protist (not human) |
| 17 | proposed_level | L4 (keep; flag L5 taxon-specific as alternative) |
| 18 | proposed_relationship_type | MORPHOLOGICAL + TAXON_SPECIFIC |
| 19 | modality_status | NOT a modality |
| 20 | human_RCD_status | NOT human |
| 21 | definition_status | REWORD (remove "modality") |
| 22 | terminology_status | FORM_MODALITY_CONFLATION |
| 23 | strongest_supporting_evidence | Kosta et al. 2004 (Dictyostelium discoideum, protist, atg1 vacuolization) |
| 24 | strongest_counterevidence | atg1Δ → hidden non-vacuolar death (vacuolization ≠ mechanism) |
| 25 | unresolved_question | Is vacuolization the mechanism or a phenotype? |
| 26 | expert_review_required | TRUE |
| 27 | recommended_action | KEEP_AND_FLAG · KEEP_BUT_REWORD · UPDATE_SPECIES_SCOPE · UPDATE_EVIDENCE_MATURITY · RECLASSIFY_RELATIONSHIP |
| 28 | confidence | HIGH (counterevidence) / MODERATE (level placement) |
| 29 | rationale | Yeast, single-study, morphological; atg1 gates vacuolization not death. |
| 30 | references | Kosta et al. 2004, PMID 15358773 |

## 5. Proposed definition reword (terminology-only + minimal biological precision)

- ORIGINAL: "A cell death modality demarcated by conspicuous cytoplasmic vacuolization, with a hidden non-vacuolar pathway revealed by autophagy-gene disruption."
- PROPOSED: "A **morphological pattern of cell death** demarcated by conspicuous cytoplasmic vacuolization; in the founding Dictyostelium (protist) study, autophagy-gene (atg1) disruption reveals a hidden non-vacuolar death pathway, indicating vacuolization is a phenotype rather than the execution mechanism."

## 6. Sentry status

- `expert_adjudication_status = FLAGGED`
- `recommended_action = KEEP_AND_FLAG` (+ the four updates above)
- `expert_review_required = TRUE`
- Priority: **A** (deep expert adjudication required before submission)
