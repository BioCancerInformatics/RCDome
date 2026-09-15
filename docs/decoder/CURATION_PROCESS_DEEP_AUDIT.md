# RCDome — Curation Process Deep Audit

**Scope:** the entire biological-curation process (Victor's audit → decisions → implementation → echo → verification).
**Date:** 2026-09-05/06 · **Truth:** V026 · **Status:** 30/30 global conformity PASS.

---

## 1. Provenance chain (where every change came from)

| Step | Source | Artifact |
|---|---|---|
| Biological audit | Victor dos Santos Lopes, *Relatorio_Auditoria_Biologica_Ontologica_RCDome_V026_V2.docx* (504 paras, 42 tables) | `Victor_analysis/` |
| Decisions | 15 items, 7 groups (A–G) | `Victor_analysis/decisoes_acoes_curadoria_victor.md` |
| Recalibration | strict G0–G6 hard gates (Victor Table 6) | `RCDome Decoder/GROUP_G_canonical_mapping.md` |
| Traceability | every change logged with human approval | `docs/RCDome_Traceability_Contract.md` |

## 2. The 7 groups — what changed

| Group | Change | Result |
|---|---|---|
| **A** | MPT-driven necrosis → L1 (modality); MPT → L3 (trigger); Vacuolar → L4 | 2 corrections |
| **B** | +7 ontological fields (species_scope, evidence_maturity, relationship_type, parent_entity, ontology_curator_verified, independent_replication, primary_discovery_reference) | decoder 31 → 39 cols |
| **C** | hard gates G0–G6 (addition, not replacement) + `hard_gate_status` | L1-ELIGIBLE 16 / NOT-L1 37 |
| **D** | D1 adjudication table (Table S12, 53×26) + D2 two-validation separation | new table + Methods |
| **E** | 23 level recalibrations + Anoikis→L2 (subtype) + Mitotic death→L4 (driven_by) + direction fix | 23 entities re-leveled |
| **F** | 5 framing insertions (mechanistic fraction ≠ validation; subtype > parent; "RCD-related entities"; dynamic nomenclature; curator-governed) | manuscript |
| **G** | 9 ontological relationships (12-value vocabulary + outcome_of) | decoder |

## 3. The recalibration logic (V026 → V026)

- **Original (V014, Enrique 2026-08-12):** permissive — "is it a death form?" → 38 forms at L1.
- **Strict (Victor G0–G6):** "does it have causal machinery (G1) + functional necessity (G2)?" → 16 modalities at L1.
- **Canonical mapping** (decoder `category` → `rcdome_level`):
  - L1 ← Executioner, CORE_RCD_FORM, CORE_PENDING
  - L2 ← SUBTYPE, SYNONYM
  - L3 ← Trigger
  - L4 ← Functional, CONTEXTUAL, CELL_TYPE, DIFFERENTIATION, MORPHOLOGY, CLEARANCE_PROCESS, INTEGRATED_PROGRAM
  - L5 ← CELLULAR_PROCESS, UMBRELLA, LEGACY, TAXON, EMERGING, COMPOSITE

## 4. Level changes (23 entities)

| Transition | Entities |
|---|---|
| L1→L2 | Anoikis |
| L1→L4 | Necrosis, Oncosis, Cornification, Eryptosis, Phagoptosis, Ammonia-induced cell death |
| L1→L5 | Erebosis, Hypersensitive response, Mitoptosis, Spectosis, Pyronecrosis, NECSO, Linker cell-type death, Aponecrosis, Lysozincrosis, Floatptosis, Metalloptosis, Lysoptosis, Mitoxyperilysis, Regulated Necrosis, Triaptosis |
| L2→L4 | Mitotic death |

**Gene-pairs:** L1 12,366 → 10,300 · L2 2,111 → 2,354 · L3 172 · L4 1,219 → 2,684 · L5 6,605 → 6,963 (total 22,473 preserved).

## 5. Matrix schema (67 → 71 columns)

Added the canonical decoder block, side by side with the Rodrigues provenance:
- `decoder_operational_definition` (53/53)
- `decoder_key_molecules` (49/53)
- `decoder_category` (53/53)
- `decoder_hard_gate_status` (53/53)

## 6. Verification record

| Audit | Result |
|---|---|
| GROUP A audit | 7/7 |
| GROUP B ocean-deep | 8/8 |
| GROUP C deep audit | 8/8 |
| V026 recalibration mega audit | 7/7 (Sections 1–7) |
| GROUP D (D1 registration) | 7/7 |
| GROUP E adjudications | 7/7 |
| GROUP F mega audit | 14/14 |
| GROUP G mega audit | 5/5 (corrected) |
| Decoder line-by-line (CSV vs FINAL) | 2,067 cells, 0 mismatch |
| App deepest audit | 27/27 real checks |
| Global conformity (matrix/decoder/manuscript/app/GitHub) | **30/30 PASS** |
| GitHub manifest integrity | 186 entries, 0 hash mismatch |

## 7. Final truth (V026)

- Matrix: 22,473 × 71 (Database S1).
- Decoder: 53 × 39, definitions 53/53, hard_gate_status 16/37.
- Levels: 16 modalities · 5 subtypes · 2 triggers · 12 functional/contextual · 18 generic/umbrella/legacy/taxon/emerging.
- Manuscript: version-free, 71 columns, 381 paragraphs.
- App: fully functional, verbatim decoder definitions, 53-entity grid.
- GitHub: clean, manifest-verified, pushed.

**Conclusion:** the curation was implemented completely, functionally echoed, and verified
value-by-value across every artifact. No superficial echo remains.
