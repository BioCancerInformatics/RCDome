# PREAUDIT0_01 — EXECUTIVE SUMMARY
RCDome Pre-Audit 0 · Normalization of "Canonical" Terminology · Terminology-only, read-only

## What was searched
- 703 text/source files under the CURRENT RCDome artifacts (manuscript, Decoder, app modules, www pages, Board, docs, comms, code), excluding data CSVs, third-party bundles, papers, and archives.
- Programmatic case-insensitive search for "canonical" and variants; then every occurrence inspected in context.
- The bulk occurrences in the matrix CSVs (78,000+ lines) are the repeated schema column `rcd_form_canonical` — treated as a single schema finding, not as 78,000 prose occurrences.

## Occurrence counts
- Unique user-facing/source occurrences inspected: **382**.
- Data-column repetitions (matrix + gene NCBI CSV): ~78,000 lines (1 schema identifier).
- Third-party library internals (SigPolytope.html = MapLibre "CanonicalTileID"/"canonicalize*"): **not RCDome terminology — out of scope**.
- Published PMID titles containing "canonical apoptosis/autophagy/inflammasome" etc.: **verbatim external citations — out of scope**.

## Three semantic uses of "canonical" (the core finding)
1. **VOCABULARY_NORMALIZATION** — "53 canonical entities / 53 canonical RCD entities / canonical RCD form" when the meaning is *an entity whose heterogeneous source names were consolidated into the RCDome controlled vocabulary*. This is the HIGH-RISK use: readers may read "canonical" as biological recognition. → prefer "canonicalized RCD-related entity" or, where normalization history is irrelevant, "RCD-related entity".
2. **BIOLOGICAL_CANONICALITY** — "canonical apoptosis / canonical autophagy / canonical inflammasome / canonical ferroptosis inducers / canonical gene set / canonical signaling pathway". These are legitimate biological statements and MUST REMAIN unchanged.
3. **SCHEMA/CODE IDENTIFIER** — `rcd_form_canonical` (matrix column), `canonical_pathways`, `canonical_set`, "canonical name", "canonical symbol". Internal identifiers; not user-facing prose. Flagged, not renamed (renaming would break the pipeline).

## Principal terminology decisions
- Adopt **"canonicalized RCD-related entity"** for vocabulary normalization.
- Use **"RCD-related entity"** as the neutral default.
- Reserve **"bona fide RCD modality"** and **"canonical/established RCD modality"** strictly for biological/mechanistic claims (adjudicated in the subsequent 53-entity audit).
- **Membership in the RCDome controlled vocabulary does NOT imply biological canonicality.**

## Major ambiguity patterns (high-risk)
- "53 canonical entities" (app stats, Board, landing/dome, not-found messages).
- "53 canonical RCD entities" (OD module lede, Board prompt).
- "Canonical RCD entity queried / name" (Board payload labels).
- "canonical regulated cell death entity/modality" (Board example reports).
- "Canonical RCD form name" (gene detail-page tooltip).
- "54 canonical RCD forms" in the obsolete manuscript draft (see cross-artifact).

## Critical version drift found (not a terminology error, but a consistency error)
- `docs/RCDome_manuscript.md` is an ARCHIVED V025 draft (preserved): "54 canonical RCD forms", "9,252 genes", "24,834 rows", "21,371 pairs".
- CURRENT truth (V026): **53 entities**, **9,265 genes**, **22,473 rows**, **21,568 pairs**.
- This drift must be resolved before the ontological audit (deferred, recorded in PREAUDIT0_06).

## What Pre-Audit 0 did NOT do (hard scope respected)
- No entity reclassification, no L1–L5 changes, no G0–G6 changes, no definition edits, no gene-association edits, no PMID changes, no Vacuolar cell death adjudication.
