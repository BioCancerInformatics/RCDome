# Higor corrections — applied (V026 manuscript)

| # | Correction | Before | After |
|---|---|---|---|
| 2 | Europe PMC | 40 million biomedical articles | 12.3 million full-text articles (of 48.9 million abstracts) |
| 5 | Tier T1 | 2,862 | 2,864 |
| 5 | Tier T3 | 8,213 | 8,212 |
| 6 | EXECUTOR precision | 'precision was 100% because all 192 downgraded' | 'No unsupported EXECUTOR classification remained…' |
| 4,8 | direction scope | (ambiguous) | added 'across all role-resolved associations' |
| 7 | de novo count | 20 de novo | 19 de novo (plus one pre-PubMed term) |
| 9 | 28 entities | 'without a PMID-referenced definition' | 'de novo definitions anchored to a founding PMID' |
| 10 | 'for the first time' (x3) | removed | 'explicit' / 'quantitatively measurable' / 'explicit' |

Not changed (numbers already correct over 21,568 unique pairs): REGULATOR 9,489; EXECUTOR 469; MARKER 5; UNCERTAIN 11,605; PROMOTES 5,070; PROTECTS 4,755; UNCLEAR 11,743.
Point 1 (T1-T4): RESOLVED — Results tier section now cross-references 'as defined in Methods (Evidence Tier Assignment)'; sufficient, no conceptual change.
Point 7 (19/19 vs 20 NCCD): numbers corrected (19 of 20 NCCD terms; 33 non-NCCD entities); the identity of the one 'draft complement unscored' NCCD entity remains to be named (optional).

## Additional corrections (points 1, 4/8, 7 + figures)

| # | Correction |
|---|---|
| 1 | Tier Results cross-referenced to Methods 'Evidence Tier Assignment' |
| 4,8 | Figure 3C: direction now 'across all role-resolved associations' (regulator-only: 4,556 promote / 4,755 protect / 178 unclear) |
| 6 | Figure 2: 'executor precision from 47% to 100%' -> 'no unsupported EXECUTOR classification remained' |
| 7 | '19/19 NCCD' -> '19 of 20 NCCD'; '40 non-NCCD' -> '33 non-NCCD' |

## Point 3 (denominator) — finalized
- Tier: 'across the 22,473 matrix rows'.
- Role/direction: 'across the 21,568 unique gene-RCD pairs'.

## Higor follow-up (HACN) — applied
- Point 1: separated evidence_tier (sources+LLM) from confidence_tier (weighted channels) in Methods.
- Point 6: Table S14 gate G4 'EXECUTOR precision 100%' -> 'Unsupported EXECUTOR claims remaining: 0'.
- Point 7: reverted '19 de novo' -> '20 de novo (19 founding-draft + 1 pre-PubMed)'; '19 of 20' -> '20/20 NCCD'.

## Higor HACN — points 2 + 9 adopted
- Point 2: Europe PMC sentence replaced with Higor's Phase 2B-specific wording (167,868 open-access full-text articles).
- Point 9: '28 entities' reframed as provenance (multi-optosis coverage), not a limitation; note: if Limitations is kept strict, the real remaining limitation (criterion-pending drafts) should be stated in its place.

## Higor S4 unbounded (Board) — 4 points applied
- Point 1 (rules 4/5 'ends with'): already resolved by unified Mandatory-ending section (body -> 3 queries -> disclaimer).
- Point 2: Board prose discipline renamed 'four evidence tiers' -> 'four provenance categories' (P1-P4), distinct from matrix evidence_tier (T1-T4). Applied to RCD_Board_Governance.md + RCD_Board_DeepSeek_Prompt.md (analysis + app + _scratch).
- Point 3: explicit scrub->audit order added ('scrub runs first; audits run on scrubbed output').
- Point 4: 'hallucination-free' -> 'zero hallucination in the performed benchmark (not a general guarantee)'.
- Contract updated (docs/RCDome_Traceability_Contract.md, Board section) + compliance_audit.py extended to 93 checks (62->93).

## Level propagation (VCD L4->L5) — figures + legends FIXED (fiasco correction)
- Root cause: VCD was reclassified L4->L5 in the matrix + text, but the FIGURE layer was never regenerated.
- Fixed with the ORIGINAL generators (no new display): Figure 3 (pcts L4 23.6->23.9, L5 31.4->31.3), Figure 4 (re-read matrix RDS, VCD now L5), Figure S2 (legend entity counts 12->11, 18->19).
- Legends/text: manuscript Figure 3 legend + Results 31.4->31.3; supplementary Figure S2 legend (12)->(11)/(18)->(19).
- Secondary: _scratch HTML LEVEL_COUNTS, Victor deep-audit 12/18->11/19, contract L4/L5 + superseding note.
- compliance_audit.py extended to 101 checks (8 new level-propagation checks). All PASS.
