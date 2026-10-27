# R4 context-guided provenance dive — the manuscript's own words name the analysis; the agent follows to the code.
# Each value is paired with its analysis key (from the manuscript context), then the dive targets that analysis.
vals <- list(
  c(value="784",      key="benchmark|Elicit|governance"),
  c(value="192",      key="EXECUTOR|downgrade|governance"),
  c(value="1,143",    key="pre-fix|baseline|Cuproptosis"),
  c(value="1,383",    key="Phase 2B|full-text|deep evidence"),
  c(value="167,868",  key="Phase 2B|full-text|PMC"),
  c(value="21,283",   key="Phase 2B|pairs|PMID"),
  c(value="10,141",   key="PMID|title|verified"),
  c(value="5,138",    key="mechanistic|YES|pairs")
)
dirs <- c("analysis","code","docs","extraction code snippets","output databases")
comp_pat <- "nrow|length\\(unique|sum\\(|count|len\\(|value_counts|groupby|table\\(|\\.shape"

cat("=== CONTEXT-GUIDED PROVENANCE DIVE ===\n\n")
for (v in vals) {
  cat(sprintf("--- value %s  (analysis key: %s) ---\n", v["value"], v["key"]))
  res <- suppressWarnings(system2("grep", c("-rn", shQuote(v["value"]),
    "--include=*.py","--include=*.R", dirs), stdout=TRUE, stderr=FALSE))
  res <- res[!grepl("benchmark_label_error_n800|r4_|_archive", res)]
  # lines that BOTH carry the value AND the analysis key
  hits <- res[grepl(v["key"], res, ignore.case=TRUE)]
  if (length(hits)==0) {
    cat("    (no code/log line ties this value to that analysis)\n")
  } else {
    for (h in head(hits,3)) cat("    ", substr(h,1,160), "\n")
  }
}
