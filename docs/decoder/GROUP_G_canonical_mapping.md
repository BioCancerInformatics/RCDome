# GROUP G — Canonical type→level mapping (recalibration target)

**Adopted criterion:** strict (Victor G0–G6) — L1 requires G1 (causal machinery) + G2 (functional necessity).
**Source of type:** decoder `category` (curated), after the 7 category corrections.

## Decoder `category` → `rcdome_level`

| Level | Category values |
|---|---|
| L1 Modalities | Executioner, CORE_RCD_FORM, CORE_PENDING |
| L2 Subtypes | SUBTYPE, SYNONYM |
| L3 Triggers | Trigger |
| L4 Functional/contextual | Functional, CONTEXTUAL, CELL_TYPE, DIFFERENTIATION, MORPHOLOGY, CLEARANCE_PROCESS, INTEGRATED_PROGRAM |
| L5 Generic/umbrella/legacy/taxon/emerging | CELLULAR_PROCESS, UMBRELLA, LEGACY, TAXON, EMERGING, COMPOSITE |

## 7 category corrections (decoder, align with matrix type)

| Entity | Old category | New category |
|---|---|---|
| Anoikis | Executioner | CONTEXTUAL |
| Autophagy | Executioner | CELLULAR_PROCESS |
| Autosis | Executioner | SUBTYPE |
| Erebosis | Executioner | TAXON |
| Mitoptosis | Executioner | LEGACY |
| Necrosis | Executioner | MORPHOLOGY |
| PANoptosis | INTEGRATED | INTEGRATED_PROGRAM |

## Result

L1 = 16 true modalities (10,300 rows); L2 = 5 (2,354); L3 = 2 (172); L4 = 11 (2,660); L5 = 19 (6,987).
`hard_gate_status` auto-re-derives: L1-ELIGIBLE = 16 (was 23); NOT-L1 = 37 (was 30).


## Sentinel adjudication (2026-09-12)
Vacuolar cell death: L4 (MORPHOLOGY) -> L5 (TAXON). Rationale: yeast founding evidence (atg1, Kosta 2004); vacuolization is a phenotype, not a mechanism. Provenance preserved. See ADJUDICATION_sentinel_Vacuolar_cell_death.md/.xlsx.
