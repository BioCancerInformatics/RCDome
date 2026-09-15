# RCDome — Final Propagation / Governance Gate

**Rule:** a change is *not* complete when the master source is corrected. It is complete only when it is **adjudicated → propagated → independently verified** across every dependent artifact, horizontally (all artifacts) and vertically (counts, summaries, distributions, labels, figures, narrative, UI).

**Verification instrument:** `code/compliance_audit.py` — 62 automated checks + cross-artifact field alignment. Re-run before submission.

**Status:** ALL accepted audit-driven changes propagated + verified — **62/62 PASS · 0 real field mismatches.**

**Residual disagreement policy:** any downstream artifact that disagrees with the authoritative source is treated as a propagation failure, even if minor/presentational; recorded (source, dependency, stale representation, corrective action, post-correction verification), never silently repaired.

**Closure gate:** the 53-entity audit is closed only because every accepted change is traceable in `CHANGE_PROPAGATION_MATRIX.md/.xlsx` and verified in `COMPLIANCE_AUDIT.md/.xlsx`.

**Resolved / archived (not deferred):**
- Modality count = **16 bona fide modalities (L1)** — the adjudicated truth. The earlier "39 modalities" is a historical correspondence (reply_to_Higor_5level.md), not a truth artifact.
- V025→V026 (54→53) — V025 draft ARCHIVED at `_archive/_archive_preV025/` (preserved; truth = V026).

**Global deferred (the ONLY remaining expert-review item):**
- G5 / `independent_replication` — "pending until curated" (all 53; allowed values none / limited / multiple).
