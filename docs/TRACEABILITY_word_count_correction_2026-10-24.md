# TRACEABILITY — Main-text word count correction (2026-10-24)

## Issue
The manuscript carried a stale main-text word count: **15,739** (from an earlier version).

## Recomputation (read-only, body text only)
Scope: **Introduction + Materials & Methods + Results + Discussion** — excluding title, abstract, the "Every gene-RCD association…" box, headings, statements, figure legends, and references.

| Section | Words |
|---|---|
| Introduction | 868 |
| Materials & Methods | 9,028 |
| Results | 5,439 |
| Discussion | 1,933 |
| **Total** | **17,268** |

## Fix
- Replaced `15,739` → `17,268` in the word-count line (single run `Word count (main text): …`) via **direct XML replacement** (`word/document.xml`), preserving the EndNote citation fields + formatting.
- Files edited:
  - `Submission FAI/RCDome_manuscript_governance_V027.docx`
  - `Submission FAI/RCDome_manuscript_governance_V027_REFs_unformatted_Bckup.docx`

## Propagation
- `manuscript_V027/RCDome_manuscript_governance_V027.docx`
- `RCDome_distribution/manuscript/RCDome_manuscript_governance_V027.docx`
- GitHub: commit `71613ab` (pushed to `main`)
- `RCDome_V027_distribution.zip` rebuilt + synced to `Submission FAI/`

## Verification
- Word-count line reads `Word count (main text): 17,268`.
- 42 formatted references intact (EndNote Bibliography).
- All manuscript copies md5-identical: `a51d69d03052cfe0bd58cbac572d978c`.
