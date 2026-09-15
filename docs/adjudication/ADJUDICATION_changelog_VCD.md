# Adjudication change log — Vacuolar cell death (sentinel)

Decision: reclassify L4 -> L5 (TAXON) with definition reword + species/maturity/relationship updates.
Date: 2026-09-12 (expert adjudication, sentinel case)

| Field | Before | After |
|---|---|---|
| rcdome_level | L4 | L5 |
| rcdome_level_name | L4 Functional/contextual | L5 Generic/umbrella/legacy/taxon/emerging |
| category (decoder/matrix) | MORPHOLOGY | TAXON |
| species_scope | cross_species | fungal (yeast) |
| evidence_maturity | supported | PROVISIONAL |
| relationship_type | associated_with | TAXON_SPECIFIC |
| operational_definition | 'cell death modality...' | 'morphological, taxon-specific pattern...' |
| provenance_note | morphology/context label | + adjudication note |

Rationale: founding evidence is yeast (atg1, Kosta 2004, PMID 15358773); atg1 disruption reveals a hidden non-vacuolar death pathway, so vacuolization is a phenotype, not the execution mechanism. Fails G1/G2. Provenance preserved (entity retained at L5).
Traceability: see ADJUDICATION_sentinel_Vacuolar_cell_death.md/.xlsx.

## Species correction (2026-09-12)
- species_scope: 'fungal (yeast)' -> 'plant + protist (not human)'.
- Rationale: founding evidence is Dictyostelium discoideum (protist; Kosta 2004 PMID 15358773, 'Autophagy Gene Disruption Reveals a Non-vacuolar Cell Death Pathway in Dictyostelium'); principal literature is plant (Norway spruce Picea abies, Arabidopsis). NOT human, NOT fungal/yeast.

## Plant reference PMIDs added (2026-09-13)
- secondary_refs_pmids: '' -> '24344187;35390283' (Minina et al. 2013, Autophagy and metacaspase determine the mode of cell death in plants, Picea abies; Feng et al. 2022, Autophagy promotes programmed cell death and corpse clearance in specific cell types of the Arabidopsis root cap).
