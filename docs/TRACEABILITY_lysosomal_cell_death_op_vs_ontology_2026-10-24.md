# TRACEABILITY — "Lysosomal cell death": OP vs ontology audit (2026-10-24)

## Status
CLOSED — no changes required.

## Question raised
The RCDome Shiny app showed an apparent disparity for **"Lysosomal cell death"**:
- **RCD Entity Deep Dive** + **Gene Catalog**: `L2 Subtypes`.
- **Operational Definition Comparator**: `SYNONYM`.

Initial hypothesis: the Comparator might be reading a stale decoder file.

## Investigation

### 1. Decoder copies — no stale version exists
All four distinct decoder versions agree (`category=SYNONYM`, `relationship_type=synonym_of`, `parent=Lysosome-dependent cell death`):

| Version | md5 |
|---|---|
| Legacy app (`_archive/Shiny app_legacy/...`) | `0247b3f9` |
| Current (11 copies, incl. `RCDome_distribution/data/`, `Submission FAI/`) | `31af4922` |
| Emergency backup | `8a4ff719` |
| GitHub `docs/decoder` | `a670c9ae` |

### 2. Code trace — who reads what

| App module | Source file | Field shown |
|---|---|---|
| Entity Deep Dive (`mod_rcd_entities.R:67`) | `genes_df` (matrix) | `rcdome_level` → L2 |
| Gene Catalog (`mod_gene_catalog.R:498`) | `genes_df` (matrix) | `rcdome_level_name` → L2 Subtypes |
| OD Comparator (`mod_od_compare.R`) | `decoder_df` ← `global.R:97` → `data/RCDome_Decoder_53.csv` | `category` → SYNONYM |

The Comparator uses the **same global `decoder_df`** as everything else — no stale file.

### 3. Table S11 = the decoder (consistent)
`Table S11` (56×42) in the supplementary tables is the decoder table. Row 27:
`Lysosomal cell death | SYNONYM | NOT-L1 | 2008 | ...` — identical to the Comparator.

### 4. The matrix carries BOTH values (the decisive fact)
For "Lysosomal cell death", the unified matrix holds:
- `decoder_category` = **SYNONYM** (joined from the decoder), and
- `rcdome_level` = **L2** (Higor's 5-level ontology).

So the two values coexist in the *same* truth matrix — no contradiction.

### 5. Provenance of the docx (RCDome_53_canonical_entities.docx)
Its own subtitle states the design:
> "Canonicalized entity names from the RCDome Decoder (RCDome_Decoder_53.csv), with adjudicated ontological levels from the unified matrix."

Verified programmatically:
- The docx's **Entity** column ← decoder `rcd_form`.
- The docx's **Ontological Level** column ← matrix `rcdome_level_name` (53/53, 0 mismatches).
- The decoder has **no level field** (its ontology fields are `category` + `relationship_type` only).

### 6. Provenance of the L2 placement
`docs/reply_to_Higor_5level.md` (adjudication, confirmed by Enrique):
> "Lysosomal cell death → L2 (variant of lysosome-dependent cell death)."

The decoder's `provenance_note` for the row records the pre-adjudication state:
> "Potential lexical variant of lysosome-dependent cell death; retain both labels until source-level adjudication."

The source-level adjudication then concluded **L2** — which the matrix and app correctly reflect.

## Conclusion
The decoder carries **both** operational-definition fields **and** ontological classification (`category`, `relationship_type`, `parent_entity`, `hard_gate_status`). It is not OD-only.

The decoder's fine-grained `category` (15 values) **rolls up** into the matrix's coarse `rcdome_level` (5 levels):

| Decoder `category` (fine) | → | Matrix `rcdome_level` (coarse) |
|---|---|---|
| EXECUTIONER (14) + CORE_PENDING (5) | → | L1 Modalities (19) |
| SUBTYPE (6) | → | L2 Subtypes (6) |
| TRIGGER (2) | → | L3 Triggers (2) |
| FUNCTIONAL + CONTEXTUAL + CELL_TYPE + DIFFERENTIATION + MORPHOLOGY + INTEGRATED_PROGRAM (13) | → | L4 Functional/contextual (13) |
| UMBRELLA + TAXON + CELLULAR_PROCESS + COMPOSITE (11) | → | L5 Generic/umbrella/taxon (11) |
| **SYNONYM (2)** | → | **L2** (Lysosomal cell death) **+ L5** (Pyronecrosis) — the only split |

The Comparator shows the **fine-grained** axis (SYNONYM); the Entity/Catalog/docx show the **coarse** axis (L2). Same ontology, two resolutions — **by design**.

## Decision
**NO CHANGES.**
- Decoder stays `SYNONYM`.
- Matrix and docx stay `L2`.
- 53 entities stay 53.
- No reclassification, no merge, no file edit.

## Authoritative provenance — Table S12 (Ontology Adjudication Table)

Table S12 (`RCDome_manuscript_V027_supplementary_tables.xlsx`) is the provenance of the ontology designation resolution. Its **"Lysosomal cell death"** row records both axes explicitly:

| Field | Value |
|---|---|
| pre_adjudication_level / adjudicated_level | L2 / L2 |
| Q6_independent_vs_subtype | synonym |
| Q9_nature | synonym |
| parent | Lysosome-dependent cell death |
| relationship_type | synonym_of |
| rationale | SYNONYM \| NOT-L1 |

So the adjudication table itself carries the resolution in one row: **level L2** (coarse axis) **and relationship `synonym_of`** (fine axis) — confirming the two taxonomies are complementary, not contradictory.
