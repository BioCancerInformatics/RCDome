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
