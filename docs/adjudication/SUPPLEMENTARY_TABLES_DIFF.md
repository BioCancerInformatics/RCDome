# Supplementary Tables S1–S15 — sheet-by-sheet diff (vs matrix + decoder)

**Findings:** 3

## SUP-001 — INDEX / Database S1 row

- **Exact:** 22,473 rows x 67 columns
- **Artifact:** workbook INDEX vs matrix
- **Evidence:** matrix dim = 22,473 x 71 (4 decoder columns added)
- **Issue:** Stale matrix dimension
- **Why:** INDEX still says 67 columns; matrix is 71
- **Severity:** Medium
- **Action:** Update INDEX
- **Amendment:** 67 columns → 71 columns
- **ReAdjud:** No
- **Downstream:** INDEX, any doc citing 67
- **Vert:** Yes
- **Horiz:** Yes
- **Status:** VERIFIED — CORRECTION REQUIRED

## SUP-002 — Table S12 / Vacuolar cell death

- **Exact:** adjudicated_level = L4
- **Artifact:** Table S12 vs matrix
- **Evidence:** matrix Vacuolar cell death = L5
- **Issue:** Stale adjudicated level (L4 vs L5)
- **Why:** Propagation failure — S12 not updated to final level
- **Severity:** High
- **Action:** Update S12 adjudicated_level
- **Amendment:** L4 → L5
- **ReAdjud:** No
- **Downstream:** S12, manuscript, app
- **Vert:** Yes
- **Horiz:** Yes
- **Status:** VERIFIED — PROPAGATION FAILURE

## SUP-003 — Matrix Descriptor

- **Exact:** column count 67
- **Artifact:** Matrix Descriptor vs matrix
- **Evidence:** matrix = 71 columns
- **Issue:** Stale column count
- **Why:** Descriptor may still say 67
- **Severity:** Medium
- **Action:** Update to 71
- **Amendment:** 67 → 71
- **ReAdjud:** No
- **Downstream:** Matrix Descriptor
- **Vert:** Yes
- **Horiz:** Yes
- **Status:** VERIFIED — CORRECTION REQUIRED

