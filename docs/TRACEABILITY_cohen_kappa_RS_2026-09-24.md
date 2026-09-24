# Traceability — Two-Call Review Agreement (RS1–RS6 drafted vs human-reviewed)

**Date:** 2026-09-24
**Status:** VERIFIED (authoritative source = `definition_review_worksheet.xlsx`)

## Corrected conclusion (supersedes an earlier κ = 0.97 estimate)
The authoritative trace of the two-call (assistant-draft / human-approval) review is
`RCDome Decoder/definition_review_worksheet.xlsx`, not the build script.

- Worksheet: **337 rows** = 1 header + **336 field-rows**
- 28 drafted entities × 12 fields = **336** (the 12 fields: operational_definition,
  key_molecules, inflammatory, overlaps, C1–C6 [RS1–RS6], S, founding_pmid)
- **`reviewer_decision` = APPROVE for all 336 rows — zero EDIT, zero REJECT**

Therefore the drafted-vs-human agreement is **perfect**: every drafted field was
approved unchanged; no edits were required. Cohen's κ is 1.0 (trivial, since there
was no disagreement to measure).

## Why the earlier κ = 0.97 was wrong
A regex used to parse `build_decoder_53.py` spanned across records (lazy `.*?` with
DOTALL) and mis-attributed "Hypersensitive response"'s RS values (4,4,4,3,5,3) to
the composite entity "Senescence and Autophagy in Cancer". The build script itself
is correct: the composite is (4,3,4,4,4,4), matching the worksheet and the decoder.

## Manuscript effect
¶70 now reads:
"Inter-rater agreement between the drafted and human-reviewed values was perfect:
all 336 drafted fields (28 entities × 12 fields) were approved unchanged, with no
edits required."

and

"The assistant-draft/human-approval review was completed with approval of all 336
drafted fields, and each decision is logged."

## Note on a second, unrelated κ
`extraction code snippets/channel_c_evidence_tier.py` contains a `compute_kappa()`
used in the `--validate` Phase 2A benchmark (LLM Call A vs Call B on a 14-pair set).
It is an internal diagnostic, never reported in the manuscript, distinct from the
definition-review agreement above.
