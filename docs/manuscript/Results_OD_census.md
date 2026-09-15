# The RCD entity census and operational definitions

**The 53-entity census.** The RCDome identified 53 canonicalized RCD-related entities,
represented by 22,473 gene–RCD pairs in the unified evidence matrix (V026). Of
these, 20 carried the verbatim operational definitions of the Nomenclature
Committee on Cell Death (NCCD; Galluzzi *et al.* 2018), 12 carried the expanded
operational definitions of Rodrigues *et al.* (2025, Dataset S1A) — of which
five (cuproptosis, disulfidptosis, erebosis, alkaliptosis, and oxeiptosis) were
not described by the NCCD and had been AI-extracted from a 6,603-PDF corpus and
human-validated — and 20 were drafted *de novo* by the RCDome and substantiated
by their founding articles. One additional record ("Senescence and Autophagy in
Cancer") was a composite WikiPathways pathway label and was retained, per the
provenance policy, with the evidence PMIDs of its two parent entities rather
than a fabricated PMID of its own. Thirteen entities carried both an NCCD and a
Rodrigues definition; seven NCCD forms were represented in the matrix as
finer-grained entities that Rodrigues had grouped under a parent term.

**Score distribution.** Among the 25 Rodrigues-anchored entities the overall
score S ranged from 9.70 (apoptosis) to 4.15 (necrosis), and among the 28
RCDome-drafted entities from 7.20 (programmed cell death, an umbrella term) to
3.25 (vacuolar cell death). Across all 53 entities the distribution was
right-skewed (mean 5.20, median 4.85, standard deviation 1.48, skewness +1.09):
the drafts occupied the lower portion of the calibrated scale (mean 4.41 versus
6.09 for the anchors), consistent with the predominance of emerging,
taxon-specific, legacy, and contextual forms among the newly defined entities.

**The definition record.** Each entity's definition is a 29-field record
combining the definitional, scoring, and provenance layers. For example, the
eryptosis record comprises: the operational definition ("A cell-type-specific
form of regulated cell death of erythrocytes, demarcated by cell shrinkage,
membrane blebbing, calpain activation and phosphatidylserine exposure, and
triggered by oxidative stress via prostaglandin E2/Ca2+ and phospholipase
A2/ceramide pathways"); the key molecules (Ca2+ channels, ceramide, calpain,
erythropoietin); the inflammatory status (no); the overlap description
(phosphatidylserine-exposure clearance, apoptosis/efferocytosis-like); the six
criteria C1–C6 (4/4/4/4/5/5) with overall score S = 4.15; and the full
provenance chain (founding PMID 16910766, Lang *et al.* 2006; authoring source
Rodrigues *et al.*, RCDome; source databases Elicit_Phase3 and NCBI_Gene;
channels B and E).

**Provenance and validation outcomes.** All 53 entities were anchored to a
reference PMID. All 52 verifiable founding PMIDs resolved in PubMed (Knock
Test). Verbatim integrity was confirmed for 19/19 NCCD terms and 25/25 Rodrigues
records. Consensus cross-validation corroborated each *de novo* definition
against coinage, mechanism, and PubMed-consensus evidence streams, yielding 13
fully corroborated, 13 partially corroborated (subtypes, umbrellas, and legacy
terms without a single coining paper), and one NCCD-locked definition whose
draft complement only was unscored. DeepSeek full-text validation of the 40
non-NCCD entities — using PMC full text where available and Consensus
full-text-derived takeaways otherwise — returned 6 fully validated and 26 with
minor wording gaps. Eight entities were initially flagged, of which six were
verbatim NCCD/Rodrigues definitions flagged only by a source-mismatch (the
committee text had been checked against the founding paper rather than the
committee source) and were therefore reclassified as verbatim-invariant; the
remaining genuine flags are the criterion-pending and umbrella-scope drafts
described below.

**Incomplete C2/C3 criteria.** Four of the *de novo* drafts — lysoptosis,
PANoptosis, regulated necrosis, and triaptosis — were flagged as
**criterion-pending** because their founding articles describe the mechanism
but not the C2 trigger and/or the C3 morphological phenotype required by the
NCCD definitional logic; these elements remain to be characterized in the
primary literature. Metalloptosis was flagged as **umbrella-scope**: like
mitotic catastrophe and cellular senescence in the NCCD itself, it is an
umbrella category rather than a discrete RCD form and therefore lacks a single
trigger and morphology by definition. These flags are recorded as explicit
definition-status annotations rather than as errors.
