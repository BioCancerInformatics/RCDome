# PREAUDIT0_05 — CROSS-ARTIFACT CONSISTENCY
Terminology discrepancies among manuscript, Supplement, tables, matrix, Decoder, and web application.

## 1. CRITICAL — numeric/version drift (54 vs 53)
- `docs/RCDome_manuscript.md` (ARCHIVED V025 draft (preserved)): "54 canonical RCD forms", "9,252 genes", "24,834 rows", "21,371 pairs", "38 canonical forms", "51-term registry".
- CURRENT V026 (governance docx, matrix, decoder, app): **53 entities**, **9,265 genes**, **22,473 rows**, **21,568 pairs**.
- Effect: any reader opening `docs/RCDome_manuscript.md` sees numbers that contradict the app and the governance manuscript.
- Action: mark the .md draft superseded; do not silently "fix" it (recorded in PREAUDIT0_06).

## 2. MAJOR — "forms" vs "entities" vs "RCD-related entities"
- Decoder/app (current): "entities" / "canonical entities".
- Old draft + several docs: "forms" / "canonical RCD forms".
- `docs/reply_to_Higor_5level.md` already records the decision: "The 54 are no longer called 'forms' … now reads 'canonical RCD-related entities'".
- Action: converge all current artifacts on "RCD-related entities" (or "canonicalized RCD-related entities"), and retire "forms" for the current vocabulary.

## 3. MAJOR — "canonical" meaning drifts across artifacts
- App UI + Board prompt + landing: "53 canonical entities" (reader may read as biological).
- Manuscript (old): "canonical RCD form vocabulary" (normalization sense).
- Paper titles/Board examples: "canonical apoptosis/autophagy/inflammasome" (biological sense).
- Action: apply the controlled vocabulary (PREAUDIT0_04) so "canonicalized"/"RCD-related" marks normalization and "bona fide/canonical modality" marks biology.

## 4. MODERATE — "canonical" in schema vs prose
- Matrix column `rcd_form_canonical` (schema) vs prose "canonical entities".
- Action: keep the column name (pipeline stability); ensure prose does not reuse the bare word "canonical" for the vocabulary.

## 5. MODERATE — "pathway" vs "entity" in a few leftovers
- server.R: "No canonical pathway data available." (app module elsewhere says "entity").
- Action: unify to "entity" (recorded in PREAUDIT0_03).

## 6. MINOR — Board internal "canonical audit/count"
- `audit_canonical.py`, `RCD_Board_Governance.md`: "canonical audit", "canonical count = 28".
- These are internal benchmark labels, not user-facing; no change required.

## Consistency target
After implementation, every artifact should state the same ontology in the same words:
- "53 RCD-related entities" (neutral) or "53 canonicalized RCD-related entities" (normalization emphasized).
- "16 bona fide RCD modalities" (or whatever the 53-entity adjudication concludes) — stated ONLY after that audit.
