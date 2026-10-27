# R4 in-memory index — read the code/log/doc corpus ONCE, then search values in memory (fast, exhaustive).
suppressPackageStartupMessages({library(openxlsx)})

# 1. collect files (code, logs, docs, small CSVs) — skip huge data files + noise
files <- list.files(".", recursive=TRUE, full.names=TRUE, pattern="\\.(py|R|md|txt|csv|json|log)$")
files <- files[!grepl("_archive|node_modules|\\.git/|benchmark_label_error_n800|r4_|elicit_evidence_trail|elicit_articles_explored", files)]
files <- files[file.info(files)$size < 20e6]   # <20 MB each

# 2. read ONCE into memory
cat("indexing", length(files), "files...\n")
corpus <- list()
for (f in files) {
  t <- tryCatch(paste(readLines(f, warn=FALSE), collapse=" "), error=function(e) "")
  if (nzchar(t)) corpus[[f]] <- t
}
cat("indexed", length(corpus), "files into memory\n\n")

search <- function(n, key=NULL) {
  hit <- names(corpus)[vapply(corpus, function(t) grepl(n, t, fixed=TRUE), logical(1))]
  if (!is.null(key) && nzchar(key)) hit <- hit[vapply(hit, function(f) grepl(key, corpus[[f]], ignore.case=TRUE), logical(1))]
  hit
}

cat("=== R4 IN-MEMORY PROVENANCE DIVE ===\n\n")
bench <- c("784"="benchmark|Elicit|governance","192"="EXECUTOR|downgrade","1,143"="pre-fix|baseline|Cuproptosis",
           "1,383"="Phase 2B|full-text|deep","21,283"="Phase 2B|pairs","167,868"="Phase 2B|full-text",
           "10,141"="PMID|title","5,138"="mechanistic|YES")
for (n in names(bench)) {
  src <- search(n, bench[[n]])
  if (length(src)>0) cat(sprintf("  [FOUND] %-10s (%s) -> %s\n", n, bench[[n]], basename(src[1])))
  else cat(sprintf("  [MISSING] %-10s (%s)\n", n, bench[[n]]))
  if (length(src)>1) for (s in head(src,2)[-1]) cat(sprintf("           also: %s\n", basename(s)))
}
