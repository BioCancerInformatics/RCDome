# Operational definitions of RCD entities

**Vocabulary and scope.** The RCDome controlled vocabulary comprises 53 canonicalized RCD-related entities,
derived from the unified gene–RCD evidence matrix (version V025; 22,473 rows;
21,568 gene–RCD pairs). The controlled vocabulary is fixed at V025 and is not
modified by downstream definition work.

**Three-tier definition hierarchy.** Each entity's operational definition (OD)
was assigned from the highest-priority source available, in the order:
(i) the verbatim operational definitions of the Nomenclature Committee on Cell
Death (NCCD; Galluzzi *et al.* 2018, PMID 29362479), treated as **invariant**
(content and meaning never altered); (ii) the expanded operational definitions
of our prior study (Rodrigues de Souza *et al.* 2025, Dataset S1A), preserved
**verbatim**; and (iii) for
entities lacking a committee definition, a *de novo* definition drafted from the
**original discovery article** (founding PMID), written in the NCCD C1–C5 logic
(distinct molecular machinery, biochemical/biophysical trigger, reproducible
morphology, explicit naming in a peer-reviewed publication, and pharmacological
or genetic modulation) and structured in the ten-field Rodrigues format, which
the RCDome record expands to the 29 definition fields described below (plus a
review-status annotation in the locked version).

**Definition record.** Each entity is represented by a 29-field record
comprising three evidence layers: (i) *definition* — the operational definition
(prose), key molecules, inflammatory status, description of overlaps, category,
and year of discovery; (ii) *quantified ranking* — the six criteria C1–C6 and
the overall score S; and (iii) *provenance* — the founding PMID, reference PMID
and citation, primary and secondary evidence PMIDs, the authoring source, the
contributing source databases and channels, the provenance note, the definition
status, and the source-of-definition flag (NCCD-verbatim, Rodrigues-S1A, or
RCDome-drafted).

**Evidence maturity.** The evidence_maturity dimension records the consensus status of each entity as established, supported, emerging, legacy, or provisional.

**Quantified scoring.** The six Rodrigues criteria were retained — C1 extent of
research (25%), C2 direct involvement (25%), C3 impact on cell/tissue
homeostasis (20%), C4 emerging potential (15%), C5 biological significance
(10%), and C6 pathophysiological relevance (5%) — each scored 1–10. Three
criteria were reinterpreted from the cancer-oriented Rodrigues usage to the
cell-biology scope of the RCDome: C2 ("direct involvement in cancer therapy" →
"direct involvement"), C3 ("impact on cancer progression" → "impact on
cell/tissue homeostasis"), and C6 ("clinical relevance" → "pathophysiological
relevance"). The overall score follows the deterministic weighted formula

S = 0.25·C1 + 0.25·C2 + 0.20·C3 + 0.15·C4 + 0.10·C5 + 0.05·C6,

which reproduces all 25 Rodrigues S1A anchors exactly. The C1–C6 values are
**expert judgments**, not computable from gene counts (necrosis, 1,092 genes, is
scored C1 = 4 whereas cuproptosis, 77 genes, is scored C1 = 7), demonstrating
that the criteria are semantic. Consequently, for the entities without a
committee definition the C1–C6 values were drafted from a rubric informed by
matrix objective inputs (gene count, mechanistic classification ratio,
evidence-tier distribution, and discovery year) and then subjected to two-call
human review.

**Hard gates (L1 admission).** Following the biological curation, admission of an entity to the modality level (L1) was governed by hard gates G0-G6: G0 whole-cell death (irreversible), G1 identifiable causal machinery (obligatory), G2 functional necessity/distinguishability (obligatory), G3 supportive phenotype/trigger, G4 published name (necessary for traceability, not sufficient for mechanism), G5 independent replication (defines maturity), and G6 species scope. These gates operationalize the NCCD C1-C5 criteria (G1 ~ C1 machinery; G2 ~ C5 modulation; G3 ~ C2/C3 trigger and morphology; G4 ~ C4 naming). Entities passing G1 and G2 were classified hard_gate_status = L1-ELIGIBLE (16/53); the remainder were NOT-L1 (subtypes, triggers, umbrellas, morphology, contextual, and taxon-specific programs). The Rodrigues C1-C6 scoring remains an orthogonal ranking metric, not an admission gate.

**Governance policy.** Four principles governed definition construction.
(1) *Invariance*: published committee definitions (NCCD and Rodrigues) are
preserved byte-identical to their sources and may only be complemented, never
rewritten; verbatim integrity was verified programmatically against the PMC XML
and the S1A spreadsheet. (2) *Primacy of provenance* (P0–P3): no entity is ever
deleted; composite or derived labels are retained with an explicit provenance
note and the evidence PMIDs of their parent entities; a non-canonical entity is
marked retired rather than removed; and every entity carries its full
provenance chain (source databases, source channels, reference PMID, provenance
note). (3) *No make-believe*: no field is filled without a source; unsourced
fields are left empty or marked "not specified"; PMIDs are verified to resolve
in PubMed (Knock Test). (4) *Two-call human verification*: each drafted field
was produced by an assistant (call A) and is approved, edited, or rejected by a
human (call B), with every decision logged to its source for traceability.

**Evidence-based anchoring and validation.** Every OD is anchored to a
reference PMID: the NCCD verbatim definitions to Galluzzi *et al.*
(PMID 29362479), the Rodrigues definitions to their primary characterization
PMIDs, and the *de novo* definitions to their founding PMID. The 25 Rodrigues
entities additionally carry their full primary and secondary evidence PMIDs from
the Rodrigues reference table. Each *de novo* definition was corroborated
against independent evidence streams — coinage (a coining verb proximal to the
entity name in the founding abstract), mechanism (the drafted key molecules
appearing in the founding abstract), and PubMed consensus (a fresh search
returning the founding PMID). Where a founding article was open-access, the
full text (PMC) was used for claim-level validation; where no PMC full text
was available, full-text recovery was additionally attempted via Europe PMC,
and where the article remained paywalled the Consensus academic search API
provided a full-text-derived takeaway as the richest available evidence, so
that no definition was rejected on an abstract gap alone. Definitions whose
founding article does not yet describe the C2
trigger or C3 morphology required by the NCCD logic were flagged
**criterion-pending**, and umbrella categories were flagged **umbrella-scope**
rather than as errors.

**AI-assisted definition and human validation.** Consistent with the two-call
principle of our prior study (Rodrigues de Souza *et al.* 2025) — in which the
operational definitions of
the five RCD forms not described by the NCCD were extracted by generative AI
(GPT-4o, via the PDF Ai Drive tool, over a corpus of 6,603 free-access PDFs)
and subsequently validated by manual review — the RCDome employed a distinct AI
instrument set. Definitions lacking a committee definition were drafted by an
assistant and substantiated by a three-stream validation: (i) DeepSeek
(deepseek-chat and deepseek-reasoner) for claim-level validation of each
operational definition against the founding article's full text where
open-access and against its abstract plus a Consensus full-text-derived
takeaway otherwise; (ii) the Consensus academic search API as an
independent cross-reference for the founding reference; and (iii) PubMed
E-utilities for deep search and PMID verification. Every AI-drafted field was
then subjected to two-call human review (approve, edit, or reject), with each
decision logged to its source; no definition was accepted on the basis of AI
output alone. The NCCD-verbatim and Rodrigues-verbatim definitions were
preserved byte-identical to their sources and were not re-generated.

**Statistical audit.** The decoder was audited for completeness, score
reproducibility (S recomputed bitwise for every record), PMID verifiability
(Knock Test), calibration (draft scores versus the locked anchors), and
invariance (NCCD definitions byte-identical to the source). Inter-rater
agreement between the drafted and human-reviewed C1–C6 values is reported as
Cohen's κ (target ≥ 0.80). All definition-building code and the resulting
53-entity decoder are provided in the reproducibility repository. The two-call
human review was completed with a bulk approval of all 336 drafted fields, and
each decision is logged; inter-rater agreement between the drafted and
human-reviewed values is reported as Cohen's κ where the review includes
independent edits.
