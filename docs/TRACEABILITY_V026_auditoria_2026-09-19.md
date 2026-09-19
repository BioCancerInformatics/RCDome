# Traceability — V026 Auditoria changes (2026-09-19)

## §9 Lysoptosis → L2 (SUBTYPE) + matrix decoder-column re-sync

- Decision: Lysoptosis = distinct serpin/SERPINB3-moderated subtype of lysosome-dependent cell death (Luke et al. 2022, PMID 35022507). Approved L2.
- Decoder: category LEGACY→SUBTYPE; evidence_maturity legacy→supported; operational_definition reworded.
- Matrix: re-synced 4 decoder-mirrored columns from decoder (fixes 10 OP meaning-drift + 19 category case-drift); Lysoptosis rcdome_level L5→L2, rcdome_level_name→L2 Subtypes, elic_onto_rcd_type→SUBTYPE.
- Spread: decoder → matrix → S3/S11/S12 → manuscript ¶319 → app data → GitHub.

- AUDIT: 13/13 checks PASS (decoder, matrix OP/category drift=0, Lysoptosis L2 ×33 rows, S3/S11/S12, manuscript ¶319, landing page LEVEL_COUNTS).
- CLOSED: §9 executed + audited + propagated (GitHub commit).

## PENDING — ontology proportion re-tally + figure regeneration (cumulative)

After all level re-adjudications are done (§9 Lysoptosis done; §8 NECSO, §10 EMERGING decoupling, §3/§4 splits still open), the L1–L5 proportions must be re-tallied and the level-consuming figures regenerated:

| Artifact | Consumes level | Impact |
|---|---|---|
| Figure 4 (entity coverage) | `make_figure_entity_coverage.R` (colors bars by `rcdome_level`) | YES — bar color + legend + proportions |
| Figure S2 (stacked by level) | `make_figure_s2_stacked_by_level.py` | YES — stacked proportions |
| Figure 3 (death core) | `make_figure3_composite.py` (verify level usage) | possibly |
| Landing page dome + LEVEL_COUNTS | `www/landing_page.html` | already updated for §9 (L2=6, L5=18) |
| Manuscript ¶319 + Figure legends | governance docx | already updated for §9 |

Current §9 state: L1=16, L2=6, L3=2, L4=11, L5=18 (was 16/5/2/11/19).

## §10 evidence-maturity ≠ level — clear cases (Lysozincrosis, Aponecrosis, Pyronecrosis) + L5 rename

- Principle: category reflects biology, not novelty; evidence_maturity stays the separate maturity field.
- L5 name: 'L5 Generic/umbrella/legacy/taxon/emerging' -> 'L5 Generic/umbrella/taxon' (drop maturity words).
- Lysozincrosis: EMERGING->SUBTYPE, subtype_of Lysosome-dependent cell death, L5->L2.
- Aponecrosis: LEGACY->UMBRELLA, umbrella_for Apoptosis; Necrosis, stays L5.
- Pyronecrosis: LEGACY->SYNONYM, synonym_of Regulated Necrosis, stays L5.
- Deferred (biology pass): Floatptosis, Mitoxyperilysis, Spectosis, Triaptosis (EMERGING), Mitoptosis, NECSO (LEGACY).

- AUDIT: 11/11 checks PASS (decoder 3 entities, matrix levels + L5 rename, S3, manuscript ¶319, landing page, mod_od.R).
- CLOSED: §10 clear cases executed + audited + propagated (GitHub commit 0ee2e43).
- Ontology proportions now: L1=16, L2=7, L3=2, L4=11, L5=17.
- STILL DEFERRED (biology pass): Floatptosis, Mitoxyperilysis, Spectosis, Triaptosis (EMERGING); Mitoptosis, NECSO (LEGACY).

## §23 held-out benchmark — executed

- Script: code/benchmark_heldout_20260919.R (seed 20260919, n=100 each, excludes dev cases).
- Reference discipline held-out: 100/100, 95% CI 96.4-100%.
- T06 context fidelity held-out: 100/100, 95% CI 96.4-100%.
- Result doc updated (dev + held-out).

## §25 human review — documented
- Actual process (from curator): per-entity review — Enrique read and validated each of the 28 drafted definitions individually against its founding evidence before approving; the shared 2026-09-05 timestamp is a single curation session in which each entity was checked separately, not an unattended batch approval.
- Manuscript: added "Human review granularity" paragraph after the human-supervision paragraph (governance docx).

## §25 human review — final wording (two-curator process)

- Primary curator (EM-A): read, inspected, approved each of the 53 entities separately in a single curation session (no unattended batch approval).
- 28 drafted definitions: EM-A validated each against founding evidence before APPROVED; 25 committee definitions byte-identical (LOCKED-VERBATIM).
- Second curator (VdSL): independently assessed each classification entity-by-entity; disagreements jointly adjudicated by both curators; consensus recorded as final.
