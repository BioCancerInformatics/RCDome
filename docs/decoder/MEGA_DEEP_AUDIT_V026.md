# MEGA DEEP AUDIT — V026 Ontological Recalibration

**Scope:** recalibration of `rcdome_level` (permissive → strict G0–G6) and its spread, echo,
compliance, and approval. **Date:** 2026-09-05. **Truth:** V026.

---

## Section 1 — Ontology mapping integrity (PASS)
- 17 decoder `category` values, all mapped to L1–L5.
- 53 unique entities (decoder) = 53 unique forms (matrix).

## Section 2 — Decoder category → matrix level (PASS 53/53)
Every entity's `rcdome_level` equals the GROUP G canonical mapping of its `category`.
**0 mismatches.**

## Section 3 — hard_gate_status ↔ level (PASS)
- `hard_gate_status = L1-ELIGIBLE` (16) == matrix `rcdome_level = L1` (16).
- The 16 L1 modalities: Alkaliptosis, Apoptosis, Autophagy-dependent cell death, Cuproptosis,
  Disulfidptosis, Entosis, Ferroptosis, Lysosome-dependent cell death, MPT-driven necrosis,
  Methuosis, NETosis, Necroptosis, Oxeiptosis, Paraptosis, Parthanatos, Pyroptosis.

## Section 4 — Level distribution (V026)
| L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|
| 10,300 | 1,866 | 172 | 2,927 | 7,208 |
(22,473 rows total; 16 + 4 + 2 + 12 + 19 = 53 forms)

## Section 5 — RDS ↔ CSV consistency (PASS)
`unified_gene_rcd_matrix_V026.rds` = 22,473 × 67; L1 = 10,300; L5 = 7,208 — identical to CSV.

## Section 6 — Echo spread (PASS 8/8)
- Manuscript `RCDome_manuscript_governance_V026.docx` — V026, 16/53, recalibration note.
- Supplementary `RCDome_manuscript_V026_supplementary_tables.xlsx` — Table S11 (39 cols),
  Variable Descriptor, Matrix Descriptor (L4/L5 names updated).
- Figure 4 regenerated (V026 level colors).
- App (global.R, mod_omic.R, server.R, data RDS) — V026, no V026 leakage.
- Decoder CSV + XLSX (working and FINAL) — 39 cols, 7 category corrections, hgs 16/37.
- Docs: GROUP_G_canonical_mapping.md, GROUP_C_compliance_declaration.md,
  MandM_operational_definitions.md, TODO_curadoria_victor.md (12 entities).
- Traceability contract — provenance + recalibration + governance cycle.
- GitHub mirror — commit `16d7146`, 179 manifest files.

## Section 7 — Policy compliance + approval (PASS)
- **Provenance** registered: `rcdome_level` author (Enrique 2026-08-12), script
  `add_rcdome_ontology.py` (V013→V014), permissive criterion documented.
- **Human approval** recorded: "yes register and proceed the recalibration which is approved".
- **Governance cycle** documented (PROPOR → ACORDO HUMANO → EXECUTAR → ECOAR → AUDITAR).
- **No version leakage**: V026 absent from all truth artifacts; V026 files preserved
  in working directory (no deletion, provenance P0–P3); GitHub carries V026 snapshot only.
- **No make-believe**: `hard_gate_status` is a deterministic derivation of `category`;
  the 7 category corrections are evidenced by matrix `elic_onto_rcd_type`.

---

## VERDICT

**V026 recalibration: COMPLIANT.** Ontology mapping 53/53, hard-gate status ↔ level 16/16,
RDS↔CSV identical, echo complete across 8 artifacts, policies satisfied, approval recorded.

**Status: V026 RECALIBRATION CLOSED — APPROVED.**
