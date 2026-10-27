# R4 provenance dive — benchmark/pipeline values (not matrix-bound) -> hunt code/logs.
read_docx_text <- function(p) {
  z <- unzip(p, "word/document.xml", exdir=tempdir())
  xml <- paste(readLines(file.path(tempdir(),"word/document.xml"), warn=FALSE), collapse="")
  gsub("\\s+", " ", gsub("<[^>]+>", " ", xml))
}
manu <- read_docx_text("Submission FAI/RCDome_manuscript_governance_V027.docx")

# metric words that signal a benchmark/pipeline count
metrics <- "records|downgrades|rows|articles|papers|pairs|PMIDs|references|claims|themes|items|genes|associations|publications|sources"
pat <- sprintf("([0-9][0-9,]*(\\.[0-9]+)?%%?)\\s*(%s)", metrics)
mm <- gregexpr(pat, manu, perl=TRUE)[[1]]
lens <- attr(mm, "match.length")

dive <- function(n, metric) {
  res <- suppressWarnings(system2("grep", c("-rln", shQuote(n),
    "--include=*.py","--include=*.R","--include=*.md","--include=*.txt","--include=*.csv",
    "analysis","code","docs","extraction code snippets","output databases"),
    stdout=TRUE, stderr=FALSE))
  res <- res[!grepl("benchmark_label_error_n800|r4_|_archive", res)]
  res
}

seen <- character(0); n_code <- 0; n_missing <- 0
cat("=== PROVENANCE DIVE (benchmark/pipeline values) ===\n\n")
for (k in seq_along(mm)) {
  seg <- substr(manu, mm[k], mm[k]+lens[k]-1)
  caps <- regmatches(seg, regexec(pat, seg, perl=TRUE))[[1]]
  if (length(caps) < 4) next
  n <- caps[2]; metric <- caps[4]
  v <- suppressWarnings(as.numeric(gsub(",", "", gsub("%","", n))))
  if (is.na(v) || v < 2) next
  key <- paste(metric, n)
  if (key %in% seen) next
  seen <- c(seen, key)
  src <- dive(n, metric)
  if (length(src) > 0) {
    cat(sprintf("  [CODE-FOUND] %-10s %-12s -> %s\n", n, metric, src[1]))
    n_code <- n_code + 1
  } else {
    cat(sprintf("  [NO-CODE]   %-10s %-12s (no script/log computes it)\n", n, metric))
    n_missing <- n_missing + 1
  }
}
cat(sprintf("\nsummary: %d values with code/log provenance | %d without\n", n_code, n_missing))
