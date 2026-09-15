# RCDome change-compliance audit — per-artifact (documented)

Every change from Pre-Audit 0 + the 53-entity adjudication, checked individually per artifact.

**Total checks:** 101 · **PASS:** 101 · **FAIL:** 0

## Manuscript

- [✓] 11 functional/contextual present
- [✓] 12 functional/contextual absent
- [✓] 19 generic/umbrella present
- [✓] 18 generic/umbrella absent
- [✓] canonicalized RCD-related entity present
- [✓] canonical RCD form vocabulary absent
- [✓] 53 canonical RCD entities absent
- [✓] VCD L1->L5 sentence absent
- [✓] VCD cross-species category absent

## Supplementary info

- [✓] normalized name present
- [✓] canonical name absent

## Supp tables

- [✓] INDEX canonicalized vocab
- [✓] INDEX old vocab absent
- [✓] VarDesc Canonicalized entity name
- [✓] VarDesc no 'Canonical RCD form name'
- [✓] VarDesc no 'Canonical name'
- [✓] S11 VCD category=TAXON
- [✓] S11 VCD species plant+protist
- [✓] S11 VCD maturity provisional
- [✓] S11 Erebosis Drosophila
- [✓] S11 Erebosis emerging

## Matrix CSV

- [✓] VCD 24 rows L5
- [✓] VCD category TAXON
- [✓] VCD note Dictyostelium
- [✓] levels 16/5/2/11/19 — {'L5': 19, 'L1': 16, 'L4': 11, 'L2': 5, 'L3': 2}

## Decoder CSV

- [✓] VCD TAXON
- [✓] VCD plant+protist
- [✓] VCD provisional
- [✓] VCD def reworded
- [✓] Erebosis Drosophila
- [✓] Erebosis emerging
- [✓] no modality in non-L1 defs
- [✓] maturity lowercase
- [✓] Rodrigues 2025 + 41048343
- [✓] VCD def: Dictyostelium (not yeast)

## App

- [✓] mod_omic.R: '53 canonical entities' absent
- [✓] mod_board.R: '53 canonical entities' absent
- [✓] mod_rcd_grid.R: '53 canonical entities' absent
- [✓] landing_page.html: '53 canonical entities' absent
- [✓] dome_prototype.html: '53 canonical entities' absent
- [✓] mod_od: canonicalized + bona fide
- [✓] mod_network: normalized entity
- [✓] app decoder == source

## Decoder docs/code

- [✓] MandM: canonicalized
- [✓] Results_OD_census: canonicalized
- [✓] build_variable_descriptor: Canonicalized
- [✓] build_variable_descriptor: Normalized name

## docs

- [✓] Traceability: Canonicalized RCD-related entities
- [✓] Traceability: 11/19 (not 12/18)
- [✓] Gene_Traceability_Spec: CANONICALIZED

## Level counts

- [✓] www/explore.html: 11/19 present
- [✓] www/explore.html: 12/18 absent
- [✓] Shiny app/explore.html: 11/19 present
- [✓] Shiny app/explore.html: 12/18 absent
- [✓] landing_page.html: LEVEL_COUNTS 11/19
- [✓] dome_prototype.html: LEVEL_COUNTS 11/19
- [✓] landing_page.html: LEVEL_COUNTS 11/19
- [✓] dome_prototype.html: LEVEL_COUNTS 11/19

## Alignment

- [✓] decoder CSV == app CSV
- [✓] decoder CSV == XLSX
- [✓] Table S11 == decoder (non-empty) — (0 diffs)
- [✓] matrix decoder_category == decoder category

## Higor follow-up

- [✓] Board RCD_Board_Governance.md: 'four evidence tiers' absent
- [✓] Board RCD_Board_Governance.md: 'T1 Observed' absent
- [✓] Board RCD_Board_Governance.md: 'EVIDENCE HIERARCHY' absent
- [✓] Board RCD_Board_Governance.md: 'hallucination-free' absent
- [✓] Board RCD_Board_Governance.md: 'four evidence tiers' absent
- [✓] Board RCD_Board_Governance.md: 'T1 Observed' absent
- [✓] Board RCD_Board_Governance.md: 'EVIDENCE HIERARCHY' absent
- [✓] Board RCD_Board_Governance.md: 'hallucination-free' absent
- [✓] Board RCD_Board_DeepSeek_Prompt.md: 'four evidence tiers' absent
- [✓] Board RCD_Board_DeepSeek_Prompt.md: 'T1 Observed' absent
- [✓] Board RCD_Board_DeepSeek_Prompt.md: 'EVIDENCE HIERARCHY' absent
- [✓] Board RCD_Board_DeepSeek_Prompt.md: 'hallucination-free' absent
- [✓] Board RCD_Board_DeepSeek_Prompt.md: 'four evidence tiers' absent
- [✓] Board RCD_Board_DeepSeek_Prompt.md: 'T1 Observed' absent
- [✓] Board RCD_Board_DeepSeek_Prompt.md: 'EVIDENCE HIERARCHY' absent
- [✓] Board RCD_Board_DeepSeek_Prompt.md: 'hallucination-free' absent
- [✓] Board RCD_Board_Governance.md: 'four provenance categories' present
- [✓] Board RCD_Board_Governance.md: 'P1 Observed' present
- [✓] Board RCD_Board_Governance.md: scrub runs first
- [✓] Board RCD_Board_Governance.md: zero hallucination benchmark
- [✓] Board RCD_Board_Governance.md: 'four provenance categories' present
- [✓] Board RCD_Board_Governance.md: 'P1 Observed' present
- [✓] Board RCD_Board_Governance.md: scrub runs first
- [✓] Board RCD_Board_Governance.md: zero hallucination benchmark
- [✓] MS: confidence tier distinct from evidence tier
- [✓] MS: 167,868 Phase 2B
- [✓] MS: 20 de novo
- [✓] MS: 20/20 NCCD
- [✓] MS: 28-entities provenance
- [✓] Table S14: 'EXECUTOR precision' absent
- [✓] Table S14: unsupported EXECUTOR claims

## Level propagation

- [✓] Fig4 data: VCD = L5
- [✓] Fig4 data: L4=11 / L5=19
- [✓] Fig3 script: pcts 23.9/31.3 (not 23.6/31.4)
- [✓] FigS2 py legend: (11)/(19)
- [✓] FigS2 R legend: (11)/(19)
- [✓] MS: 23.6% absent
- [✓] MS: 31.4% absent
- [✓] SUP legend: (12)/(18) absent

## FAILURES (must fix)

None.
