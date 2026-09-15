# PREAUDIT0_06 — DEFERRED ISSUES
Biological / ontological / provenance / reference / data issues found incidentally during Pre-Audit 0, but INTENTIONALLY NOT resolved here (they belong to the subsequent 53-entity expert audit).

## D-1. Versioning — V025 draft ARCHIVED (preserved, not a deferred fix)
- The V025 draft (`docs/RCDome_manuscript.md`, "54 canonical RCD forms / 9,252 genes / 24,834 rows / 21,371 pairs") has been ARCHIVED at `_archive/_archive_preV025/`.
- V026 truth: 53 entities / 9,265 genes / 22,473 rows / 21,568 pairs.
- Versioning policy: versions are preserved, never wiped. The old draft is a historical artifact, NOT a correction target. Truth = V026.

## D-2. Vacuolar cell death adjudication
- Explicitly listed in the master prompt as an entity requiring adjudication.
- Pre-Audit 0 does not touch it. Deferred to the 53-entity audit.

## D-3. Modality count — 16 vs 39
- Current decoder/matrix: 16 L1 (L1-ELIGIBLE).
- `docs/reply_to_Higor_5level.md` mentions "39 RCD modalities" (an earlier framing).
- Deferred: reconcile the modality count during the ontological adjudication.

## D-4. "bona fide RCD modality" wording in Board example (RIPK3–Pyroptosis)
- Board example says "inclusion as a canonical regulated cell death modality".
- Deferred: after hard-gate adjudication, decide whether to state "bona fide RCD modality" per entity.

## D-5. Entity-name vs biological-status distinction
- Several entity labels (e.g., "Autophagy", "Necrosis", "Cellular senescence") are biologically imperfect as "death modalities".
- Pre-Audit 0 does not rename source-derived entity labels. The 53-entity audit will adjudicate labels vs status.

## D-6. Reference/PMID mapping (already resolved in a prior session, recorded for continuity)
- Rodrigues et al. 2025 (Dataset S1A) PMID 41048343 — corrected.
- Rodrigues de Souza et al. 2026 (#784804, SuperLearner) — distinct publication, preserved.
- Wang et al. 2025 disambiguated (Metalloptosis umbrella / Mitoxyperilysis).
- No further action in Pre-Audit 0.

## D-7. "pathway" leftovers in app text
- server.R "No canonical pathway data available." — terminology-only, but grouped with the broader "pathway → entity" normalization already underway. Deferred to implementation after author review.

## Completion note
These are recorded, not resolved. Pre-Audit 0 has performed NO biological adjudication.

## D-8. Decoder provenance_note "canonical" = ontological judgment (not terminology)
- Decoder CSV + xlsx, `provenance_note` (3 entities):
  - Entosis: "Use entotic cell death as the canonical concept name."
  - Lysosome-dependent cell death: "Use as canonical label; map lysosomal cell death as a synonym candidate…"
  - MPT-driven necrosis: "Canonical mechanism; see mitochondrial permeability transition for a synonym candidate."
- These decide the PREFERRED (canonical) label/mechanism per entity — an ontological decision, not a vocabulary-normalization term. Defer to the 53-entity adjudication. Do not rename during Pre-Audit 0.
