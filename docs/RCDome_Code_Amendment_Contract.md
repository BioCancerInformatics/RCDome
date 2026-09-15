# RCDome — Code Amendment Contract (Pre-Run Audit)

**Rule: no amended code is run until every audit below PASSES.**

## 1. Scope audit
- State exactly which files and features are being changed.
- `git diff --stat` must show ONLY the intended files. Any unrelated file touched = STOP.

## 2. Syntax audit
- **R**: `parse()` every `.R` file (ui.R, server.R, global.R, R/*.R, modules/*.R).
- **Python**: `py_compile` every `.py`.
- **JS**: `node --check` every `.js`.

## 3. Structural audit (empty / leftover)
- grep for `list(,` · `c(,` · `, ,` · a trailing blank argument in `list(...)`.
- grep for leftover identifiers of REMOVED features (dead code).
- grep for `create = TRUE` / `createFilter` / any option that was supposed to be removed.

## 4. Functional-preservation audit
- For every PREVIOUSLY-WORKING feature, grep its key marker and confirm it is still present.
- Amendments must be ADDITIVE or strictly SCOPED. Deleting an unrelated feature = STOP.
- Examples of protected features:
  - Gene Catalog click → gene page (`navigate_to_gene_page`)
  - Detail page "Jump to a gene/entity" (`geneJump`, `entityJump`, their datalists)
  - Navbar tabs (Home, Explore, RCD entities, Gene Catalog, Board, Network, About)
  - Board + Q&A modules (`mod_board`, `mod_board_qa`)

## 5. Run test
- Launch the app; log must show `Listening on http://127.0.0.1:PORT` and **no** `Error in` / `Warning: Error`.
- HTTP check returns 200.

## 6. Echo
- Any data or statistic change must be verified value-by-value against its source (matrix, decoder, benchmark JSON).

## Sign-off
The amendment is committed ONLY after all six audits pass.
