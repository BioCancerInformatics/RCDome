# Deferral Log — Finding 3 (curator_verified vs ontology_curator_verified)

**Date:** 2026-09-23
**Status:** DEFERRED (pending Consensus phase completion)

## Finding (deferred, not edited)
¶95(v) states: *"every association carries a curator-verification status (the
ontology_curator_verified field)"*. This is doubly wrong:
1. the matrix (71 columns) carries **no** `curator_verified` / `ontology_curator_verified` column;
2. it equates **entity-level** ontology curation (`ontology_curator_verified`, decoder, 53 rows)
   with **association-level** verification (`curator_verified`, Channel C internal).

## Reason for deferral
`curator_verified` is an **association-level flag internal to the Channel C (Consensus)
extraction script**. The Consensus phase is **incomplete**: 19,443 / 21,568 pairs (90.1%)
processed; the remaining 2,125 pairs are blocked on the monthly API quota (10,000/10,000
exhausted) and resume after the **October 1st quota reset**.

The final state and schema of `curator_verified` depend on the completed Consensus run.
Editing ¶95 now would describe a flag whose final population is not yet fixed.

## Agreed fix (to apply after Consensus completion)
Rewrite ¶95(v) to:
> every association carries an association-level curation flag (`curator_verified`, set during
> Channel C extraction), distinct from the entity-level `ontology_curator_verified` flag in the
> decoder, which records that each of the 53 entities (not each association) was individually reviewed.

¶90 already states the correct distinction; only ¶95 needs correcting. Non-numeric (wording),
but the flag names must match the actual Channel C + decoder schema after the run completes.

## Re-open condition
After the Consensus phase completes (post Oct 1 quota reset) and `curator_verified` is finalized
in the matrix, re-open this finding, apply the ¶95(v) fix, and re-verify against the final schema.

## Related pending items (same blocker)
- Consensus: 2,125 pairs awaiting Oct 1 quota reset.
- RCD entities module: 4 of 53 descriptions/cartoons missing (Autophagy, Programmed cell death,
  Hypersensitive response, Eryptosis).
- Anti-hallucination: 284 NOT_SUPPORTED + 534 UNCERTAIN claims awaiting Emanuell.
