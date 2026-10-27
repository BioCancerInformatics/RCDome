# R4 computation-line finder — locate the exact code line that COMPUTES each value.
# For each value, grep the code/logs WITH line numbers, then keep lines carrying a computation.
targets <- c("784", "192", "1,143", "1,383", "5,138", "5,711", "167,868", "21,283", "10,141")

dirs <- c("analysis","code","docs","extraction code snippets","output databases")
comp_pat <- "nrow|length\\(unique|sum\\(|count|len\\(|value_counts|groupby|\\.shape\\[0\\]|table\\("

cat("=== COMPUTATION-LINE FINDER ===\n\n")
for (t in targets) {
  res <- suppressWarnings(system2("grep", c("-rn", shQuote(t),
    "--include=*.py","--include=*.R",
    dirs), stdout=TRUE, stderr=FALSE))
  res <- res[!grepl("benchmark_label_error_n800|r4_|_archive", res)]
  hits <- res[grepl(comp_pat, res)]
  cat(sprintf("--- %s ---\n", t))
  if (length(hits)==0) cat("    (no computation line found)\n") else for (h in head(hits,3)) cat("    ", substr(h,1,150), "\n")
}
