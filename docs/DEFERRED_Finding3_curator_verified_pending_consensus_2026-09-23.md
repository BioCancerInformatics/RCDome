# Deferral Log — Finding 3 (curator_verified vs ontology_curator_verified)

**Date:** 2026-09-23 (deferred) · **updated 2026-09-24**
**Status:** ¶95 wording fix **APPLIED**; Consensus flag-population still DEFERRED

## Finding
¶95(v) conflated the association-level `curator_verified` flag (Channel C) with the
entity-level `ontology_curator_verified` flag (decoder), implying all 22,473
associations were individually curator-verified.

## Resolution applied (2026-09-24)
¶95(v) now reads:
"every association carries an association-level curation flag (`curator_verified`, set
during Channel C extraction), distinct from the entity-level `ontology_curator_verified`
flag in the decoder, which records that each of the 53 entities, not each association,
was individually reviewed and approved (logged 2026-09-05)."

¶90 already stated the correct distinction and needed no change.

## Still deferred (data, not wording)
The `curator_verified` flag VALUES are populated during the Consensus (Channel C) run,
which is incomplete: 19,443 / 21,568 pairs (90.1%); 2,125 pairs await the October 1st
monthly API quota reset.

Re-open condition: after the Consensus phase completes, verify the final
`curator_verified` population and confirm the ¶95 wording still matches the actual
schema (no further prose change expected unless the flag name moves).

## Related flag values (entity-level, updated 2026-09-24)
- Decoder `ontology_curator_verified` = "TRUE; EM-A (primary) 2026-09-05; HACN (secondary) 2026-09-10; VdSL (secondary) 2026-09-20" (53 rows)
- Table S12 `curator_verified` = same three-curator value (53 rows)
