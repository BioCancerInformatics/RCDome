# Supplementary Note S1 — Canonicalization Logic and Separation from Biological Modality Status

## Purpose

This note defines the term "canonicalized RCD-related entity" as used throughout RCDome, and explains why vocabulary canonicalization must be kept rigorously distinct from biological recognition of an entity as a canonical or bona fide regulated cell-death (RCD) modality.

## 1. What canonicalization means in RCDome

RCDome consolidates gene–RCD association records recovered from 20 heterogeneous sources — curated databases, pathway resources, omic-annotation compendia, and literature-mining channels — each using its own nomenclature. A single biological concept therefore arrives under multiple names (e.g., "Entotic-cell-death", "Entotic cell death", and "Entosis" for the same entity).

**Canonicalization** is the vocabulary operation that maps these heterogeneous source terms onto a single preferred RCDome identifier while the original source term is preserved in a parallel field (`rcd_form`, alongside the normalized identifier `rcd_form_canonical`). The result is a controlled vocabulary of **53 canonicalized RCD-related entities**.

Canonicalization is therefore an **informatics operation on nomenclature**, not a biological verdict.

## 2. What canonicalization does NOT mean

Canonicalization does not imply that an entity is:

- a canonical or established human cell-death modality;
- mechanistically independent;
- validated in human cells;
- accepted by the Nomenclature Committee on Cell Death (NCCD);
- supported by a causal execution machinery; or
- equivalent in evidence maturity to apoptosis, necroptosis, ferroptosis, or pyroptosis.

Membership in the controlled vocabulary records only that the entity's terminology has been normalized into RCDome. Biological and ontological status is adjudicated separately and independently.

## 3. Terminology hierarchy

Four terms are used deliberately, with distinct meanings:

1. **Canonicalized RCD-related entity** — one of the 53 preferred vocabulary identifiers produced by normalization and consolidation of heterogeneous source terminology. This is a vocabulary-normalization statement.

2. **RCD-related entity** — the neutral umbrella term for any member of the 53-entity controlled vocabulary, used when the normalization history is not the point of the sentence.

3. **Bona fide RCD modality** — an entity admitted to level L1 through the RCDome G0–G6 hard-gate framework (identifiable causal machinery and functional necessity/distinguishability). In the current adjudicated ontology, **16 of the 53** entities satisfy this criterion.

4. **Canonical RCD modality** — reserved for contexts that genuinely require a claim of biological establishment or authoritative mechanistic recognition, and only where that claim is supported by the evidence. This term is never used merely because an entity has been canonicalized in RCDome.

## 4. The 53 ↔ 16 relationship

The 53 canonicalized RCD-related entities span five ontological levels:

- **16** bona fide RCD modalities (L1);
- **5** subtypes (L2);
- **2** triggers (L3);
- **11** functional/contextual categories (L4);
- **19** generic/umbrella/legacy/taxon/emerging concepts (L5).

Thus the headline count of 53 is a count of **normalized vocabulary entries**, not of established modalities. Only the 16 L1 entities are described as bona fide RCD modalities.

## 5. Preservation of provenance

Canonicalization never overwrites the original source terminology. Every association row retains its source form (`rcd_form`) in parallel with the normalized identifier (`rcd_form_canonical`), so the provenance of each name — and therefore of each association — remains traceable to its source database or literature origin.

## 6. Avoiding semantic leakage

Because "canonical" in informatics conventionally denotes a preferred normalized identifier, whereas in biology it can imply authoritative establishment, RCDome uses **"canonicalized"** for the vocabulary operation and reserves **"canonical"** and **"bona fide"** for biological/ontological status. This lexical distinction is maintained consistently across the manuscript, supplementary material, figures, tables, and the web application so that a reader cannot conflate inclusion in the controlled vocabulary with biological endorsement.
