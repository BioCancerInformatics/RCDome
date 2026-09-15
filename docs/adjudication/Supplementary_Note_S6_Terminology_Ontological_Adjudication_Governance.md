# Supplementary Note S6 — Canonical-Terminology Pre-Audit and 53-Entity Expert Nomenclature and Ontological Adjudication

## Purpose

This note documents the governance and quality-control framework applied to RCDome's terminology and ontology: a terminology pre-audit performed before entity-level adjudication, a 53-entity expert nomenclature and ontological adjudication, and a project-wide propagation verification that closes each audit.

## 1. The canonical-terminology pre-audit

Before any biological adjudication, RCDome terminology was subjected to a dedicated **pre-audit** of the word "canonical" and its variants across the manuscript, supplementary information, tables, decoder, matrix metadata, and the web application.

The risk being managed was semantic conflation: a reader could interpret "canonical" (vocabulary normalization) as "canonical" (biological establishment), and thereby read the 53-entity vocabulary as a list of 53 established cell-death modalities.

The pre-audit therefore required that **every** occurrence of "canonical" be adjudicated semantically into one of four categories:

- **vocabulary normalization** — the term was renamed "canonicalized" or "normalized";
- **neutral entity designation** — the term was replaced by "RCD-related entity";
- **biological canonicality** — "canonical" was retained only where the claim of biological establishment was scientifically justified; or
- **bona fide modality status** — the term "bona fide RCD modality" was used for L1 entities admitted through the hard gates.

A global find-and-replace of "canonical" → "canonicalized" was deliberately prohibited, because it would have altered legitimate biological uses (e.g., "canonical executors", "canonical apoptosis", "canonical inflammasome") and corrupted scientific meaning.

## 2. The 53-entity expert nomenclature and ontological adjudication

Each of the 53 canonicalized RCD-related entities was then assessed against a five-level ontology and a set of hard gates.

**Ontology levels.** L1 (bona fide RCD modality — distinct causal machinery and functional necessity); L2 (subtype — mechanistic subdivision of a parent modality); L3 (trigger — an initiating event that is not itself a complete death mechanism); L4 (functional/contextual — context-dependent programs, morphological outcomes, cell-type-specific and differentiation-associated phenomena); L5 (generic/umbrella/legacy/taxon/emerging).

**Hard gates G0–G6.** G0 whole-cell death; G1 identifiable causal machinery (obligatory for L1); G2 functional necessity and distinguishability (obligatory for L1); G3 supportive phenotype/trigger; G4 published naming/provenance; G5 independent replication (defines maturity); G6 species scope. Naming alone (G4) is not evidence of mechanistic independence.

**Association vs modality.** Two dimensions are kept separate: (i) whether a gene is associated with an RCD-related entity in the evidence base, and (ii) whether the entity itself qualifies as a bona fide RCD modality. Evidence of the former does not establish the latter. Accordingly, the associated-gene list is not described as a "death signature" or "death machinery" unless the evidence classification supports that statement; the preferred formulation is "genes associated with [entity] in RCDome".

**Uncertainty and provenance.** Entities that fail L1 admission are not deleted. They are retained at an appropriate level (contextual category, morphology, subtype, trigger, umbrella, taxon-specific concept, legacy term, or provisional/emerging entity) with explicit provenance. Database inclusion is never treated as biological endorsement.

## 3. The propagation governance gate

The audit established a rule that has since governed all subsequent corrections: **a change is not considered implemented when the authoritative source has been corrected alone.**

Every accepted adjudication must be propagated:

- **horizontally** — to every artifact that reproduces the affected information (manuscript, supplementary information, supplementary tables, decoder, unified matrix, database fields, figures and legends, application components, landing pages, explanatory text, and downloadable outputs); and
- **vertically** — through every dependent representation derived from it (counts, group distributions, summaries, labels, colors, tooltips, and narrative prose).

For example, reclassifying one entity from L4 to L5 is not complete until the entity's classification, the level counts (e.g., the L4/L5 totals), the figures, the legends, the landing-page summaries, the supplementary tables, and the application display have all been updated and independently verified.

Any residual disagreement between the authoritative adjudicated source and a downstream artifact is treated as a propagation failure and recorded — original state, adjudicated state, affected dependency, stale representation, corrective action, and post-correction verification — never silently repaired.

## 4. Traceability and reproducibility

Every change carries an audit trail: what changed, why it changed, the prior state, the evidence, and where the consequences were applied. Versions are archived rather than overwritten, preserving the history of the project. This propagation gate — **adjudicated → propagated → independently verified** — is the final governance check before an audit is declared complete, and it is re-run after any subsequent modification to guarantee internal concordance across the entire RCDome ecosystem.
