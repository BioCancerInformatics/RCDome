# R4 exhaustive provenance dive — search EVERY source: matrix(100 cols), decoder, S1-S15, figure/legend code, benchmarks, whole tree.
suppressPackageStartupMessages({library(openxlsx)})
vals <- c("1,143", "1,383", "21,283", "5,138", "784", "192")

# ── 1. the matrix (all 100 columns, values + any column that CONTAINS the number) ──
m <- read.csv("RCDome_distribution/data/unified_gene_rcd_matrix_V027.csv", check.names=FALSE, stringsAsFactors=FALSE)

# ── 2. supplementary tables S1-S15 ──
tbl_txt <- ""
wb <- loadWorkbook("Submission FAI/RCDome_manuscript_V027_supplementary_tables.xlsx")
sheet_hits <- list()
for (s in names(wb)) {
  cells <- unlist(readWorkbook(wb, sheet=s, colNames=FALSE), use.names=FALSE)
  cells <- as.character(cells[!is.na(cells)])
  sheet_hits[[s]] <- cells
}

# ── 3. figure + legend code ──
fig_code <- list.files("code/figure_code", pattern="\\.(R|py)$", full.names=TRUE)
leg_code <- list.files("code", pattern="legend|replace", full.names=TRUE)

cat("=== EXHAUSTIVE PROVENANCE DIVE ===\n\n")
for (v in vals) {
  cat(sprintf("--- value %s ---\n", v))
  found <- character(0)
  # matrix columns: any column containing this value as a literal
  for (col in colnames(m)) {
    if (any(grepl(v, as.character(m[[col]]), fixed=TRUE), na.rm=TRUE)) found <- c(found, paste0("matrix column: ", col))
  }
  # decoder
  d <- read.csv("RCDome_distribution/data/RCDome_Decoder_53.csv", check.names=FALSE, stringsAsFactors=FALSE)
  for (col in colnames(d)) if (any(grepl(v, as.character(d[[col]]), fixed=TRUE), na.rm=TRUE)) found <- c(found, paste0("decoder column: ", col))
  # supplementary tables
  for (s in names(sheet_hits)) {
    hit <- sheet_hits[[s]][grepl(v, sheet_hits[[s]], fixed=TRUE)]
    if (length(hit)>0) found <- c(found, sprintf("table %s: %s", s, substr(hit[1],1,80)))
  }
  # figure/legend code
  for (f in c(fig_code, leg_code)) {
    txt <- paste(readLines(f, warn=FALSE), collapse=" ")
    if (grepl(v, txt, fixed=TRUE)) found <- c(found, paste0("code: ", basename(f)))
  }
  # whole tree (benchmarks + logs), with lines
  g <- suppressWarnings(system2("grep", c("-rn", shQuote(v), "--include=*.py","--include=*.R","--include=*.md","--include=*.txt","--include=*.csv", "."), stdout=TRUE, stderr=FALSE))
  g <- g[!grepl("benchmark_label_error_n800|r4_", g)]
  if (length(g)>0) found <- c(found, paste0("tree(", length(g), " hits): ", substr(head(g,1),1,90)))
  if (length(found)==0) cat("    (exhaustive search: NOT FOUND anywhere)\n") else for (x in head(found,6)) cat("    -", x, "\n")
}
