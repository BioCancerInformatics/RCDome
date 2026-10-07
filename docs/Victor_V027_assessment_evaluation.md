# Victor V027 Assessment — Verification & Triage (working document)

Source: `analysis/Victor_analysis/Victor_Revisão_v27/Relatorio_Revisao_Final_RCDome_V027_Protocolo_Victor_COMPLETO.docx`
Date: 2026-10-05
Rule: no claim accepted without triple-check against the truth (V027 matrix + amended manuscript/app).

## Truth baseline (recomputed from unified_gene_rcd_matrix_V027.rds)
- Matrix: 22,473 rows × 82 columns ✓
- Unique canonical pairs: 21,568 ✓
- Unique HGNC genes: 9,265 ✓
- cot_mechanistic (unique pairs): 9,785 YES / 11,783 NO ✓
- cot_role (unique pairs): 469 EXECUTOR / 5 MARKER / 9,311 REGULATOR / 11,783 UNCERTAIN ✓
- Genes with ≥1 YES: 5,826 (62.9%) ✓ (manuscript still says 5,928 / 64.0%)
- Pairs with divergent evidence_tier: 553 ✓
- confidence_tier missing: 1,874 ✓
- keyword + NCBI_Gene only: 29 ✓ (Victor says 27 in text, 29 in CSV header)
- MECHANISTIC without PMID: 71 (all MSigDB) ✓
- Elicit genuine rcd_gene_type: 3 CANDIDATE_MODULE + 1 empty; evidence_type empty: 250 ✓

## Status legend
- [STALE] claim confirmed; fix needed
- [RESOLVED] already fixed by our amendments (no action, or verify the artifact image)
- [DECIDE] needs author decision (not a mechanical fix)
- [CHECK] needs further verification before deciding

---

## CRITICAL

- **C01 references temporary** — [DEFERRED] EndNote `{Author, Year #id}` keys will be formatted at submission time (the author runs EndNote in the final document). Not a blocking issue now.
- **C02 word count 15,739 > 12,000** — [DEFERRED] ¶19 confirms 15,739; FAI Original Research limit is 12,000, but the author has published longer Original Research without issue. Policy: do NOT reduce the article size; revisit only if reviewers explicitly request it.
- **C03 abstract >350 words / multi-paragraph** — [DEFERRED] abstract is 367 words in 4 IMRAD subsections; the author's previously published Frontiers article used the same 4-subsection abstract without issue. Policy: no change unless reviewers request it.
- **C04 "53 remain unresolved"** — ✅ DONE: "53 remain/unresolved" removed from the abstract (no such text remains).
- **C05 DATABASE_ONLY ≠ no-paper-trail** — ✅ DONE: 156 Elicit-PMID rows reclassified → INSUFFICIENT_DATA; final split DATABASE_ONLY 286 / INSUFFICIENT_DATA 9,019 (traceability log 2026-10-05).
- **C06 71 MECHANISTIC without PMID** — ✅ DONE: Option C — 71 MSigDB rows filled with collection-source PMIDs (GO 10802651 / Reactome 24243840 / KEGG 10592173); MECHANISTIC now 3,063 with 0 without PMID.
- **C07 "31 of 71 columns" + Figure 1 "71 columns"** — ✅ DONE: ¶297 "of 82 columns" + Figure 1 regenerated (82 columns; M05).
- **C08 rows vs pairs** — ✅ DONE: units defined (22,473 rows / 21,568 unique gene-RCD pairs) in the abstract + Methods.
- **C09 553 divergent evidence_tier** — ✅ DONE: per-row tier documented (¶170 "Each matrix row … received an evidence tier").
- **C09.2 confidence_tier missingness** — ✅ DONE: 1,874 = D-channel-only rows outside the CT universe; documented (¶180). CT1 unpopulated by design.
- **C10 29 keyword-only NCBI_Gene** — ✅ DONE: 14 keyword+PMID → mixed; 15 NECSO keyword-only kept + documented exception (traceability log 2026-10-05).
- **C11 Figure 3 stale numbers** — ✅ DONE: Figure 3 regenerated (Panel C Promotes 5,070→5,025). ¶356 direction 5,070→5,025 + UNCLEAR 11,743→5; ¶396 L1 64.6→63.5% + L5 31.5→30.2%; ¶398 5,070→5,025; ¶476 legend Panel B/C corrected.
- **C12 Figure S3 stale** — ✅ DONE: script V026→V027 matrix + regenerated Figure S3 + CSV (min 2 Elicit Alert, max 6,452 Rodrigues). ¶356 range 21.7%/90.0%→21.6% (XDeathDB)/86.5% (WikiPathways).
- **C13 before/after governance benchmark** — ✅ DONE: ¶334 reframed as non-paired audits; "EXECUTOR precision 47→100" → "unsupported EXECUTOR rate 53→0"; traceability 24% PMID → 98.3% DOI.
- **C14 Table S12 hard gates (NECSO/Mitoxyperilysis/Triaptosis)** — ✅ DONE: Table S12 regenerated to L5→L1 "EMERGING | L1-ELIGIBLE" (matches sentinel adjudication).
- **C15 XDeathDB Mitotic death 239** — ✅ DONE: ¶279 now "XDeathDB: Mitotic death, 216" (reproducible count).

## HIGH

- **H01 Consensus partial** — ✅ DONE: Consensus 21,568/21,568 (100%); stale limitation text removed.
- **H02 Elicit "every pair"** — ✅ DONE: Elicit partial-coverage wording (¶401 "covers the subset").
- **H03 four vs five channels** — ✅ DONE: "A–D at compile, E at validation" (¶92 + Figure 1 channels box).
- **H04 "20 source databases"** — ✅ DONE: "20 source databases and resources".
- **H05 "outputs from all five channels merged"** — ✅ DONE: ¶118 A/B/E materialize rows; C/D governance.
- **H06 Elicit CANDIDATE_MODULE + 250 empty evidence_type** — ✅ DONE: provenance traced (Elicit LLM left evidence_type blank at source; NOT a propagation error — raw CSVs show Mitoxyperilysis 1,410/1,421 empty). ¶340 now reports "CANDIDATE_MODULE 3; and 1 unassigned" + "CITATION_ONLY 3; and 250 (6.6%) unassigned, where the extraction model left the field blank because no clean evidence type was determinable from the source abstract." No rows dropped; no fabrication.
- **H07 Elicit 50 vs 53 forms** — ✅ DONE: 50 forms (executed) vs 53 entities; Erebosis/HR/Regulated Necrosis out of scope (¶340).
- **H08 "two-fold enrichment"** — ✅ DONE: recomputed from matrix. ¶347 now "4.3-fold enrichment of strong-tier" (54.5%/12.74% = 4.28×) + "4.5-fold enrichment of mechanistic pairs" (60.7%/13.63% = 4.46×).
- **H09 definition denominators (13+13+1=27; 6+26=32 vs 33)** — ✅ DONE: ¶290 now explicit "27 of the 53 entities" + "33 non-NCCD = 32 + composite" summing to 6 fully validated + 9 minor + 4 criterion-pending + 1 umbrella-scope + 1 abstract-limited (composite) + 12 verbatim-locked.
- **H10 20 vs 21 drafted definitions** — ✅ DONE: 20 de novo + 1 composite (¶284).
- **H11 53-entity chronology** — ✅ DONE: chronology rewritten with intermediate counts.
- **H12 species asymmetry (iPCD)** — ✅ DONE: gene species = HGNC human vs entity species scope declared.
- **H13 mitotic death vs catastrophe** — ✅ DONE (Option A, wording-only): decoder already correct (Mitotic catastrophe = TRIGGER/root "not an RCD form per se"; Mitotic death = CONTEXTUAL/driven_by). FerrDB "Mitotic-death" verified = catastrophe-process genes (BUB3, RAD51, BRCA2, CDK1). ¶145 now states they are not synonyms + the driven_by relationship. Full cross-artifact audit: ¶39/¶81/¶292 + Tables S1/S3/S11/S12 all consistent; Table S5 row 10 rationale copy-paste fixed ("Same trigger event" → "Hyphenation variant"). No data re-mapping.
- **H14 26-pair benchmark = model-selection** — ✅ DONE: ¶351/¶352/¶474 "model-selection benchmark" + ¶352 disclaimer "not an estimate of the error rate".
- **H15 "three independent CoT"** — ✅ DONE: "three separately sampled runs of the same classifier" (¶231/¶358).
- **H16 NLRX1/PPIF provenance** — ✅ DONE: ¶225 specifies cot_* by CoT five-vote mini-run; mechanistic_class by Phase 2A/D two-call.
- **H17 "per-row verbatim check"** — ✅ DONE: QC scope reworded (self-consistency vote + contradiction audit + scoped verbatim).
- **H18 matrix freeze date** — ✅ DONE: freeze date 2026-10-15 declared; version tag removed from text (internal-only).
- **H19 overclaims ("validates every association")** — ✅ DONE: "systematically evaluates" (¶465 + cover letter).
- **H20 biological over-generalization** — ✅ DONE: "Within the compiled RCDome association universe and under the CoT classification" (¶281/¶394).
- **H21 AI disclosure in Acknowledgements** — ✅ DONE: Acknowledgements AI sentence added.
- **H22 SI title/authors/affiliation** — ✅ DONE: SI cover page removed.
- **H23 Figure 2 wrong refs** — ✅ DONE: script aligned (A: S2→S5, B: S10→S14, C: S3) + Panel B metrics fixed (EXECUTOR precision→Unsupported rate 53→0; Traceability→(PMID→DOI)) + Figure_2 regenerated 2026-10-06.

## MODERATE

- **M01 lysosomal vs lysosome-dependent** — ✅ DONE: ¶81 now lists "subtypes (anoikis, extrinsic and intrinsic apoptosis, autosis), a synonym (lysosomal cell death, of lysosome-dependent cell death)". Decoder verified: Lysosome-dependent cell death = EXECUTIONER/L1 (NCCD modality); Lysosomal cell death = SYNONYM/NOT-L1 (synonym_of).
- **M03 "all 100 PMIDs"** — ✅ DONE: ¶303 now "Up to the first 100 retrieved PMIDs per pair used for content verification are retained in the unified matrix, and the full retrieved paper count is stored separately as the evidence force." (matrix deep_pmids_total verified variable 100–110+, not all 100; ¶163 already states "ALL available PMIDs, no cap" + "first 100 abstracts").
- **M05 Figure 1 old app architecture** — ✅ DONE: canonical `generate_rcdome_flowchart.R` fixed (71→82 columns; app box → Home dome, Explore RCDome, Operational Definitions, Compare Definitions, RCD entities, RCD Entity Deep Dive, Gene Catalog, Discrepancy Radar, Discovery Timeline, 3D RCDome, Digital Molecular RCD Board, Network; channels box → "Five evidence channels (A-D at compile, E at validation)") + regenerated 2026-10-06; ¶472 legend app list also updated (RCDchat removed).
- **M06 Figure 2/S1 refs + nomenclature** — ✅ DONE: Figure 2A/B refs fixed under H23 (S2→S5, S10→S14). Figure S1: fix in `code/translate_infographic_EN.py` (erase 3 sequential arrows with x1955-2015 below card borders; draw 3 parallel arrows from Sources bottom y=778: solid center→ET, dashed left→CT, dashed right→Role; shaft 13px/head 52px). Portuguese source restored from ZIP. Verified 0 residues + card borders intact. Regenerated + copied to Figures/, drafs/, distribution/.
- **M07 Table S14 Q1–Q5 vs EG1–EG5** — ✅ DONE: Table S14 gate labels renamed Q1-Q5 → EG1-EG5 (5 cells). Manuscript ¶243/¶328 already use EG1-EG5 + Table S14. No other Q1-Q5 references remain (Q1-Q13 evidence checklist is separate + correct).
- **M08 Table S12 MPT-driven necrosis L1→L1 + Erebosis species** — ✅ DONE: MPT-driven necrosis pre_adjudication_level L1→L3 (now L3→L1, matches ¶294); Erebosis Q11_species human→Drosophila (invertebrate model) (matches decoder + Table S11).
- **M09 auxiliary artifacts V026 metadata** — ✅ DONE: 53-entity docx "V026 unified matrix"→"unified matrix" (version removed, per no-versioning-in-artifacts policy); Table S2 TCGA added (Tier 4, omic annotation, #26; STRING/BioGRID renumbered 27/28); cover letter ¶2 overclaims softened ("20 public databases"→"20 public databases and resources"; "validates every gene-RCD association"→"systematically evaluates every gene-RCD association"; "with exact-string source verification"→"with exact-string verification applied to extracted full-text evidence").
- **M10 Significance/Data wording** — ✅ DONE: ¶465 Significance Statement softened ("validates every gene-RCD association"→"systematically evaluates every gene-RCD association"; "access to verified gene-RCD evidence"→"access to traceable and audited gene-RCD evidence"); ¶424 leftover "freeze date 2026-10-15; )"→"freeze date 2026-10-15)".

## EDITORIAL

- **E01 Author Contributions typos + CRediT** — ✅ DONE: typos fixed (Pyhton→Python, mansucriot→manuscript, generayed→generated); incomplete sentences completed (VdSL/HACN/EMA); terminology harmonized (gene–RCD + Gene-RCD → gene-RCD, now 87 hyphen-only; impactful→high-impact; retained as honest uncertainty→retained as unresolved); MSigDB file copied to RCDome_distribution/data/ as RCDome_MSigDB_Manual_Curation.xlsx + ¶102 citation updated.
- **E02 affiliation + equal-contribution symbol** — ✅ DONE: manuscript first page fixed (¶4 #→† for the two first authors; ¶6 street/ZIP removed → "Laboratório de Biotecnologia, Centro de Biociências e Biotecnologia, Universidade Estadual do Norte Fluminense, Campos dos Goytacazes, RJ, Brazil"; ¶16 "# Authors share first authorship"→"† These authors contributed equally to this work and share first authorship"). SI already clean (cover page removed per H22).

## Proposed working order
1. Confirm C03/C07-figure/C23/C09-PMID-split facts still open.
2. Work CRITICAL → HIGH → MODERATE → EDITORIAL, each decided with Enrique before fixing.
