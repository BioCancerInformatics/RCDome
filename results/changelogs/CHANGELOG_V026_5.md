# RCDome — CHANGELOG V026_5

**Download (zip):** https://drive.google.com/file/d/17FdKm5SFTI9reL9e787DyA0gB_C4Rp0n/view?usp=sharing

## V026_5 — Higor + Emanuell app-review fixes (Board · Q&A · Gene Catalog · Network · Comparator · detail page)

- **Board**: green "No violations" badge gated on `api_ok` (no false "passed" on API failure); `scrub_board` word-boundary hedging (no "Because"→"Beis associated with"); structured fields fed into the context (T06); PMIDs hyperlinked (`PMID:123` and `PMID 123`); `withProgress` loading indicator (RCDome-styled, centered); English-only policy (non-English → exact refusal).
- **Q&A**: short gene symbols (TF/AR/C3/KL…) matched before the length filter (T05); `confidence_tier` + `confidence_score` + `evidence_basis` in the RAG records (T04); gene context propagated from Board (T10); reference discipline (gene PMID vs entity founding PMID never interchanged).
- **Gene Catalog**: load errors logged; pre-flight validation prevents them from reaching the user.
- **Network**: searched gene emphasized (other nodes opacity 0.35); "Search gene:" (nomenclature vestige removed).
- **Comparator**: legend (yellow = differing fields, grey = identical) + grey background for identical fields.
- **Detail page**: "Gene information" block (name, aliases, type, location, NCBI summary + link — 9,264 NCBI summaries pre-fetched into `data/gene_info_lookup.json`); context-dependent level-pill contrast (light text on dark hero, dark text on white table); vestigial "Jump to modules" removed.
- **Pre-flight validation** (`R/validate_data_files.R`): verifies all bundled assets (matrix 22,473×71, decoder 53×39, HGNC, omic xlsx, gene_info_lookup 9,265, board prompt, www pages) at startup and before the ZIP build (`code/build_distribution.py`).
- **Benchmarks (n=100)**: English-only 100% (95% CI 96.4–100%); reference discipline 100% (CI 96.4–100%); T06 context fidelity 100% (CI 96.4–100%); minimal-source 100%; insufficient-data 100%.
