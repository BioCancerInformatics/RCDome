# App Fix Traceability Log

Date: 2026-09-18

| # | File | Issue | Fix | Source | Result |
|---|---|---|---|---|---|
| 1 | `app/modules/mod_board_qa.R` (RCDome_distribution + GitHub mirror) | Q&A RAG dropped 1–2 char gene symbols (TF, AR, C3, C5, C7, C9, C2, CP, CS, F2, F3, F5, F7, F8, FH, GC, HP, HR, KL, PC) because `nchar(toks) >= 3` ran before gene-vocabulary matching | Reordered: match `genes_all` first, then length-filter only the remaining tokens | Higor's static code review (finding #4), verified against matrix | APPLIED |

## Fix detail

Before:
```r
toks <- toks[nchar(toks) >= 3]           # dropped short symbols
...
matched_genes <- toks[toupper(toks) %in% toupper(genes_all)]
```

After:
```r
genes_all <- unique(genes_df$gene_symbol)
matched_genes <- toks[toupper(toks) %in% toupper(genes_all)]  # match FIRST
toks <- toks[!toupper(toks) %in% toupper(genes_all)]
toks <- toks[nchar(toks) >= 3]                                 # filter rest
```

Propagation: RCDome_distribution/modules/mod_board_qa.R → GitHub app/modules/mod_board_qa.R → RCDome_V026_distribution.zip.

| 2 | `app/modules/mod_board.R` | Green “No violations detected” box rendered unconditionally — showed “passed all automated checks” even when the DeepSeek API failed (res = "Error: HTTP \<status\>") | Added `api_ok = !grepl("^Error:", res)` to `report()`; UI + downloaded HTML green box now gated on `isTRUE(r$api_ok)`, with an amber “Generation failed” box otherwise | Higor's finding #1 (partially valid — API-failure edge case) | APPLIED |

| 3 | `app/modules/mod_board.R` (scrub_board) | Naive substring gsub mangled words containing assertive verbs ("Because" → "Beis associated with", "driver" → "contributes tor") | Added word boundaries () + perl=TRUE to the 7 hedge patterns, so only whole verbs are replaced | Observed in generated synthesis text | APPLIED |
| 4 | `app/modules/mod_board_qa.R` + `mod_chat.R` | User/LLM content rendered via `HTML(gsub(...))` without escaping (HTML/XSS surface) | Corrected: escape RAW LLM reply BEFORE linkify (PMID/DOI links then added to escaped text); user bubble escaped at render; assistant render left raw so app-owned links survive | Higor's finding #2 (low severity, local app) | APPLIED |
| 5 | `app/modules/mod_gene_catalog.R` | Load errors converted silently to empty data.frame (no diagnostic) | Added `message("RCDome load error: ...")` in both error handlers (ensure_loaded + get_genes) | Higor's finding #3 (low, latent) | APPLIED |
| 6 | `mod_board_qa.R` full decoder + gene index per prompt | Flagged as redundancy | NOT a bug — intentional “no data funnel” policy (complete 22,473-index always available) | Higor's finding #5 | CLOSED (intentional) |
| 7 | `mod_board_qa.R` + `mod_board.R` | Higor T04/T06/T10: Q&A omitted confidence_tier; Board gene context reduced to symbol; Board gene not propagated | (T04) added ET:evidence_tier + CT:confidence_tier to RAG records + ET-vs-CT note; (T06) build_entity_context now includes role/direction/mechanistic/tiers/PMID for the selected gene; (T10) board_reactive carries gene + Q&A prompt has Current-gene-on-board | Higor Novo_relatório (verified code gaps) | APPLIED |
| 8 | `mod_board_qa.R` + `mod_board.R` | Higor T04/T06 (remaining): confidence_score + evidence_basis + required_for_death omitted | T04 RAG records now include EB:evidence_basis + CS:confidence_score; T06 gene context now includes required_for_death | Higor Novo_relatório “correção sugerida” | APPLIED |
