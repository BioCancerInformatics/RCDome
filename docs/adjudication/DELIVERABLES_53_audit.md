# RCDome 53-Entity Expert Nomenclature and Ontological Adjudication Audit — 12 DELIVERABLES

Consolidated. Read-only audit outputs + the traceable changes already applied (all with `docs/adjudication/*_changelog_*.md` entries).

---

## D1 — Executive summary

**Scope.** 53 canonicalized RCD-related entities audited across: main manuscript, Supplementary Information, Supplementary tables, Decoder, unified matrix V-26, and the web application.

**Outcomes (applied, traceable):**
- **1 level reclassification** — Vacuolar cell death L4 → L5 (TAXON), definition reworded, species corrected (plant + protist, not human).
- **8 definition rewords** — removed "cell death modality" from non-L1 entities (→ process / pattern + level qualifier).
- **8 evidence-maturity updates** — 6 approved changes + case normalization; 5 confirmed "established" keeps.
- **1 species correction** — Erebosis → Drosophila (invertebrate model), maturity → emerging.
- **Terminology normalization** — "canonical" (vocabulary sense) → "canonicalized / normalized / RCD-related entity" across all artifacts (Pre-Audit 0).

**Status.** `expert_adjudication_status`: STABLE / FLAGGED per entity (see D2). `independent_replication` (G5) remains a global deferred item ("pending until curated").

---

## D2 — 53-row expert adjudication table

Full 33-column table (entity, level, level_name, category, hard_gate_status, definition, definition_source, founding_pmid, reference_pmid, reference_citation, species_scope, evidence_maturity, relationship_type, independent_replication, n_genes, n_executor, n_mechanistic, G0, G1, G2, G3, modality_status, human_RCD_status, terminology_flags, proposed_action, expert_adjudication_status, expert_review_required, priority).

→ **`ADJUDICATION_53_entities.xlsx`**

Level distribution: **16 L1 · 5 L2 · 2 L3 · 11 L4 · 19 L5**.

---

## D3 — Entities requiring deep expert review

- **Sentinel (adjudicated, retained + flagged):** Vacuolar cell death — L5, TAXON, plant+protist, provisional.
- **Priority A (resolved):** 8 FORM_MODALITY_CONFLATION entities — reworded (see D12).
- **Priority B (resolved):** 12 maturity-review entities — 7 changed / 5 confirmed (see D12).
- **Global deferred (fill in the audit):** G5 / `independent_replication` (all 53 = "pending until curated").
- **Open biological questions for the team:** modality count (16 L1 vs the earlier "39 modalities" framing); 54→53 V025→V026 versioning (V025 draft archived, preserved).

---

## D4 — Terminology audit of the main manuscript

- "canonical RCD form vocabulary" → "canonicalized RCD-related entity vocabulary".
- "53 canonical RCD entities / forms" → "53 RCD-related entities" (or "canonicalized…").
- Level distribution corrected: **12→11 functional/contextual · 18→19 generic/umbrella/legacy/taxon/emerging**.
- Kept (biological): "canonical gene sets", "canonical executors", "canonical RCD modalities" (→ "bona fide" where used for L1).
- V025 draft `docs/RCDome_manuscript.md` ("54 canonical RCD forms") — ARCHIVED at `_archive/_archive_preV025/` (versioning preserved); truth = V026.

---

## D5 — Terminology audit of Supplementary Information

- "by canonical name or its stem" → "by normalized name or its stem".
- "canonical executors" kept (biological). `audit_canonical.py` kept (code).

---

## D6 — Terminology audit of supplementary tables

- INDEX: "Canonical RCD Form Vocabulary (53 Forms)" → "Canonicalized RCD-Related Entity Vocabulary (53 Entities)".
- Variable Descriptor: "Canonical RCD form/entity name" → "Canonicalized RCD-related entity name"; "Canonical Name" → "Normalized Name".
- Table S5: "Canonical Name" → "Normalized Name".
- Table S9: "53 canonical" → "53 normalized".
- Table S11: category/species/maturity/relationship/definition/provenance updates (VCD, Erebosis, 8 rewords, 6 maturity).
- Matrix Descriptor: "normalized canonical RCD form name" → "normalized RCD-related entity name".
- Kept: Table S4 "delta like canonical Notch ligand" (HGNC gene names); `rcd_form_canonical` (schema).

---

## D7 — Terminology audit of the RCDome Decoder

- Decoder docs: "53 canonical RCD entities" → "53 canonicalized RCD-related entities".
- `build_variable_descriptor.py`: "Canonical RCD form/entity name" → "Canonicalized RCD-related entity name"; "Canonical name" → "Normalized name".
- Decoder `category`/`species_scope`/`evidence_maturity`/`relationship_type`/`operational_definition` updated per adjudication (VCD, Erebosis, 8 rewords, 6 maturity).
- Deferred (ontological): `provenance_note` "canonical concept name / label / mechanism" (Entosis, Lysosome-dependent cell death, MPT-driven necrosis).

---

## D8 — Terminology audit of the web application

- "53 canonical entities" → "53 RCD-related entities" (landing, dome, mod_omic, mod_board, mod_rcd_grid).
- "Canonical RCD entity queried/name" → "RCD-related entity queried / Canonicalized RCD-related entity name".
- "legacy form → canonical entity" → "legacy form → normalized entity".
- L1 legend "canonical cell-death forms" → "bona fide cell-death modalities".
- "No canonical pathway data" → "No RCD entity data".
- Tooltip "Canonical RCD form name" → "RCD-related entity name".
- Board prompt "53 canonical RCD entities" → "53 canonicalized RCD-related entities".
- Kept: `rcd_form_canonical`, `canonical_pathways`, `canonical_symbol`, `canonical transcript` (schema/biology); MapLibre "CanonicalTileID" (third-party).

---

## D9 — Controlled vocabulary / style guide

1. **canonicalized RCD-related entity** — an entity normalized into the RCDome controlled vocabulary. Use when normalization history matters.
2. **RCD-related entity** — neutral default for any entity in the atlas.
3. **RCDome entity** — internal/UI shorthand.
4. **RCD form** — source-literature/database terminology; avoid for the current vocabulary collectively.
5. **bona fide RCD modality** — L1 entity satisfying G0–G6 (esp. G1 + G2).
6. **canonical / established RCD modality** — only for consensus modalities (e.g., NCCD 12).
7. **gene–RCD association** — raw recorded relationship (no causality claim).
8. **mechanistically validated gene–RCD relationship** — only where evidence class supports mechanism (e.g., MECHANISTIC + EXECUTOR).

**Governing rule: canonicalized vocabulary membership ≠ biological canonicality.**

---

## D10 — Proposed manuscript statement (definitions)

> RCDome is a provenance-preserving evidence atlas of **RCD-related entities** and their human gene associations. A **canonicalized RCDome vocabulary term** is an entity name normalized from heterogeneous source terminology; inclusion in the controlled vocabulary does **not** imply biological endorsement. A **bona fide RCD modality** is an entity that satisfies the G0–G6 hard gates (identifiable causal machinery and functional necessity/distinguishability). A **gene–RCD association** is a recorded evidence relationship (which may be mechanistic, regulatory, contextual, or co-occurrence-based); a **mechanistically validated gene–RCD relationship** is the subset for which the evidence classification supports a mechanistic link. These distinctions are maintained throughout the manuscript, supplement, tables, Decoder, matrix, and web interface.

---

## D11 — Manuscript sentences corrected BEFORE submission

1. Level distribution: "12 functional/contextual … 18 generic/umbrella/legacy/taxon/emerging" → "**11** … **19**".
2. "establishment of a canonical RCD form vocabulary" → "…canonicalized RCD-related entity vocabulary".
3. "53 canonical RCD entities/forms" → "53 RCD-related entities".
4. "canonical RCD form) pairs" → "(RCD-related entity) pairs".
5. "canonical vocabulary" → "controlled vocabulary"; "canonical name" → "normalized name".
6. Non-L1 definitions: "cell death modality" → "process/pattern + qualifier".
7. VCD species: "cross_species" → "plant + protist (not human)".

---

## D12 — Change log (A/B/C/D/E)

**A. Terminology-only:** canonical → canonicalized/normalized/RCD-related (manuscript, supplement, tables, Decoder, app); "modality" removed from non-L1 definitions (8); "Canonical Name" → "Normalized Name".

**B. Ontology changes:** Vacuolar cell death L4→L5 (TAXON); relationship_type → TAXON_SPECIFIC (VCD); category updates (VCD MORPHOLOGY→TAXON).

**C. Biological interpretation:** VCD species → plant + protist (not human); Erebosis → Drosophila + maturity → emerging; 6 maturity changes (Alkaliptosis/Methuosis/Paraptosis → supported; Ammonia-induced cell death/Metalloptosis → provisional; Mitoptosis → legacy).

**D. Database/schema changes:** matrix `rcdome_level`/`rcdome_level_name`/`decoder_category`/`elic_onto_rcd_type`/`elic_onto_operational_note` for VCD (24 rows); decoder 8 rewords + 8 maturity + 1 species; Table S11 mirror.

**E. Web-interface changes:** "53 canonical entities" → "53 RCD-related entities"; Board payload labels; tooltips; network edge "normalized entity".

---

*All changes traceable in `docs/adjudication/`: PREAUDIT0_01–07, ADJUDICATION_sentinel_*, ADJUDICATION_53_entities.*, ADJUDICATION_changelog_*.*
