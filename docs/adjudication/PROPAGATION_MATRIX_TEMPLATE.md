# Change-Propagation Matrix — TEMPLATE (for every future audit)

Fill one row per accepted audit-driven change. Re-run `code/compliance_audit.py` after every change.

| change_id | change | original_state | adjudicated_state | authoritative_source | dependent_artifacts | downstream_consequences | verification_status | corrections_performed | unresolved |
|---|---|---|---|---|---|---|---|---|---|
| C1 | | | | | | | | | |
| C2 | | | | | | | | | |
| C3 | | | | | | | | | |

## Instructions

1. **change** — one sentence, e.g., "Entity X reclassified L4 → L5 (TAXON)".
2. **original_state** — the value before adjudication (with artifact).
3. **adjudicated_state** — the accepted value after adjudication.
4. **authoritative_source** — the single source of truth (e.g., Decoder `category`, Matrix `rcdome_level`).
5. **dependent_artifacts** — every file/field that must change (manuscript, supplementary, decoder, matrix, app, landing pages, figures, descriptors…).
6. **downstream_consequences** — every derived value that must be recalculated (counts, distributions, labels, colors, tooltips, prose).
7. **verification_status** — PASS/FAIL from `compliance_audit.py` + alignment audit.
8. **corrections_performed** — what was fixed after verification found a gap.
9. **unresolved** — anything requiring expert review (or "none").

## Horizontal + vertical checklist (per change)

**Horizontal (every artifact):**
- [ ] manuscript · [ ] supplementary info · [ ] supplementary tables (all sheets) · [ ] decoder CSV · [ ] decoder XLSX · [ ] matrix CSV · [ ] matrix RDS · [ ] app data · [ ] app modules · [ ] www/landing pages · [ ] board prompts · [ ] figures/legends · [ ] descriptors · [ ] docs

**Vertical (every derived value):**
- [ ] counts · [ ] distributions · [ ] labels · [ ] colors · [ ] tooltips · [ ] narrative/prose · [ ] downloadable outputs

## Closure gate

The audit is closed **only** when every row is PASS and no stale representation remains at any downstream level. Record global deferred items separately.
