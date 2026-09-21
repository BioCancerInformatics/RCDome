# RCDome Definition Governance
**Version-stamp:** V025 (truth matrix `unified_gene_rcd_matrix_V025.csv`, 22,473 × 67)
**Scope:** creation, scoring and validation of operational definitions for all **53 RCD entities**.
**Basic policies:** accuracy · reproducibility · no make-believe · traceability.

---

## 1. Purpose

This document governs how the RCDome produces the **"RCDome Decoder"** — the operational
definitions of the 53 RCD entities that the *Digital Molecular RCD Board* uses as its
reference dictionary. It locks the method so that:

1. every definition is **accurate** (verifiable against a source),
2. every computable value is **reproducible** (deterministic, re-runnable),
3. nothing is **invented** (no placeholders, no fabricated PMIDs, no AI imagination).

---

## 2. The definition standard (10 fields)

Every entity's operational definition must fill, at most, the following record. Fields that
cannot be sourced are **left empty** — never guessed.

| # | Field | Source |
|---|---|---|
| 1 | RCD form | `rcd_form_canonical` (V025) |
| 2 | Category | `elic_onto_rcd_type` + `rodr_category` (Executioner / Trigger / Functional / …) |
| 3 | Year of Discovery | founding article |
| 4 | Operational Definition (prose) | **Galluzzi logic** (RS1–RS5: distinct machinery, trigger, morphology, named in publication, modulation) |
| 5 | Key Molecules | `rodr_key_molecules` / founding article |
| 6 | Inflammatory? (Yes/No) | founding article / mechanism |
| 7 | Biological Relevance (cell-biology, NOT cancer-only) | founding article's stated physiological role |
| 8 | Description of Overlaps | shared machinery/genes with other entities |
| 9 | RS1–RS6 scores + Overall Score (S) | see §5 |
| 10 | References (primary + secondary, PMIDs) | `rodr_primary_refs` + `pmid_list` + founding PMID |

> **Scope rule:** the RCDome is a **cell-biology atlas**, not cancer-restricted.
> Field 7 is *general biological relevance*. Cancer is one context, not the defining axis.
> Rodrigues' RS3 ("Impact on Progression") and RS6 ("Clinical Relevance") are therefore
> reinterpreted as **impact on cell/tissue homeostasis** and **pathophysiological relevance**.

---

## 3. Provenance — the only allowed sources

1. **V025 matrix** (columns `rcd_form_canonical`, `rcdome_level_name`, `num_sources`,
   `pmid_list`, `evidence_tier`, `mechanistic_class`, `elic_onto_*`, `rodr_*`).
2. **The original discovery article** (founding PMID) for each entity.
3. **Galluzzi et al. 2018 (NCCD)** — prose-definition logic (RS1–RS5).
4. **Rodrigues et al. 2025** — the 10-field quantified structure (Dataset S1A).

**Nothing else.** No AI prior knowledge, no review-based fill-in, no inference without a citation.

### 3.1 INVARIANCE RULE — Galluzzi NCCD 2018 operational definitions

The 22 operational definitions in **Box 1 of Galluzzi et al. 2018**
(PMID 29362479, `Cell Death Differ` 25:486–541) are **INVARIANT**.

- **Content and meaning must NOT be altered.**
- The RCDome may only **COMPLEMENT** them (Rodrigues RS1–RS6 scoring, key molecules,
  overlaps, references) — never rewrite or paraphrase them as a replacement.
- The fundamentals must be identified **exactly as they appear in the manuscript**.
- Verbatim text is stored in `galluzzi2018_nccd_definitions.json` and attached to each
  mapped entity as `galluzzi_nccd_definition` (status `NCCD_2018_INVARIANT`).
- The Rodrigues `operational_definition` field is a **complement**, never a substitute
  for the NCCD verbatim definition.
- Entities absent from NCCD 2018 (post-2018 forms) carry status `NOT_IN_NCCD_2018`.

### 3.2 PROVENANCE POLICY — primacy of provenance (no deletion)

- **P0** No entity, row, or evidence is ever **deleted** from the truth record. Provenance is preserved.
- **P1** Derived/composite labels (e.g. "Senescence and Autophagy in Cancer", a WikiPathways
  pathway name) are **kept** with an explicit `provenance_note` stating their source
  (`source_databases` + `source_channels`) and nature, and are assigned the **evidence
  PMIDs of their parent entities** (never a fabricated PMID).
- **P2** A non-canonical entity is marked **`RETIRED`** with a note — never removed — so the
  provenance contract remains unbroken.
- **P3** Every entity carries its full provenance chain: `source_databases`, `source_channels`,
  `reference_pmid`, and `provenance_note`.

---

## 4. Deterministic computation (reproducible by construction)

### 4.1 Objective inputs — computed from V025 (per entity)

| Input | Definition |
|---|---|
| `n_pairs` | number of gene–entity rows |
| `n_genes` | number of unique gene symbols |
| `n_sources_sum` | Σ `num_sources` |
| `n_mechanistic` | rows with `mechanistic_class == MECHANISTIC` |
| `n_context_gap` | rows with `mechanistic_class == CONTEXT_GAP` |
| `mechanistic_ratio` | `n_mechanistic / (n_mechanistic + n_context_gap)` |
| `n_unique_pmids` | unique PMIDs in `pmid_list` |
| `min_year` | earliest `elicit_year` |
| `tier_ET1..ET4` | counts per `evidence_tier` |

These are **pure functions of the matrix** → anyone re-running the script gets identical values.

### 4.2 Overall Score S — deterministic weighted formula (reverse-engineered, verified)

```
S = 0.25·RS1 + 0.25·RS2 + 0.20·RS3 + 0.15·RS4 + 0.10·RS5 + 0.05·RS6
```

**Verification:** reproduces **25/25** Rodrigues Dataset S1A anchors **exactly** (0 mismatch).

### 4.3 RS1–RS6 — expert judgment (two-call), NOT a hidden formula

The six criteria are **semantic judgments**, not computable from counts alone
(proof: Necrosis has 1,092 genes yet RS1 = 4; Apoptosis 5,897 genes → RS1 = 10).
Therefore they are assigned by the **two-call process** (§5), using this **anchoring rubric**:

| Crit. | RCDome meaning | Anchoring evidence |
|---|---|---|
| RS1 Extent of Research | literature volume | `n_genes`, `n_unique_pmids`, down-weight for UMBRELLA / MORPHOLOGY / LEGACY |
| RS2 Direct Involvement | causal role in death | `mechanistic_ratio`, `rcd_type` (CORE > CONTEXTUAL > MORPHOLOGY) |
| RS3 Impact on homeostasis | tissue/homeostasis impact | `tier_ET1..ET4`, `rcd_type` |
| RS4 Emerging Potential | novelty/future promise | `min_year`, `rcd_type == EMERGING` → up; LEGACY → down |
| RS5 Biological Significance | importance | expert reading of founding article |
| RS6 Pathophysiological relevance | translational relevance | `evidence_tier`, PMID coverage |

The rubric produces a **draft**; the draft is **never final until a human approves it**.

---

## 5. Two-call verification (human-in-the-loop)

- **Call A (draft):** assistant proposes prose + RS1–RS6 + S, every field carrying its source tag.
- **Call B (review):** a human approves, edits, or rejects each field; the decision is logged.

Both calls are recorded in the **traceability contract** (`docs/RCDome_Traceability_Contract.md`).

---

## 6. Statistical audit (accuracy + reproducibility)

| Statistic | What it verifies | Target |
|---|---|---|
| Completeness | 10/10 fields × 53/53 entities | **100%** (or field explicitly EMPTY, not fake) |
| Citation verifiability | every PMID resolves in PubMed (Knock Test) | **100% real** |
| Reproducibility | re-run §4 → identical objective inputs + S | **100% bitwise** |
| Inter-rater agreement | draft RS1–RS6 vs review RS1–RS6 | **Cohen's κ / ICC ≥ 0.80** |
| Score calibration | new S distribution vs existing 25 anchors | same 0–10 scale, no inflation |
| Confidence intervals | any proportion (e.g., completeness) | **95% CI (Wilson)** |
| Deterministic seed | any sampling (e.g., founding-PMID selection) | fixed `set.seed()` |

---

## 7. Versioning and traceability

- Definitions are stamped **V025** and re-stamped on every matrix version bump (V026, …).
- Every change is logged with **who / what / why** in the traceability contract.
- No version leakage: only the current truth version ships.

---

## 8. Definition pipeline (per entity)

```
1.  Identify the entity
2.  Locate the ORIGINAL discovery article  ← pmid_list / rodr_primary_refs (+ PubMed lookup)
3.  Extract mechanism, trigger, morphology, key molecules, physiological role
4.  Write prose Operational Definition  (Galluzzi RS1–RS5 logic)
5.  Compute objective inputs + draft RS1–RS6 (rubric) + S (deterministic formula)
6.  Two-call review → approve/edit/reject → traceability log
7.  Statistical audit (completeness, PMIDs, reproducibility, κ, calibration)
```

---

## 9. Reference assets

| Asset | Location |
|---|---|
| V025 matrix | `output databases/Phase 2C output/unified_gene_rcd_matrix_V025.csv/.rds` |
| Rodrigues Dataset S1A (25 anchors) | `output databases/Dataset S1_Rodrigues et al 2025.xlsx` |
| Rodrigues reference table | `output databases/RCD_25_Forms_Reference_Table_FINAL.docx` |
| Per-entity evidence | `RCDome Decoder/entity_evidence_V025.csv` |
| Gap inventory | `RCDome Decoder/gap_inventory_V025.csv` |
| Scoring reference (S formula) | `RCDome Decoder/scoring_formulas.py` |
