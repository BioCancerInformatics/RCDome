# RCDome — pre-flight data validation
# Verifies every bundled asset before the app serves anything (proactive, not reactive).
# Returns list(ok = logical, issues = character vector).
validate_data_files <- function(data_dir = "data", board_dir = "board", www_dir = "www") {
  issues <- character(0)
  chk <- function(cond, msg) {
    if (!isTRUE(cond)) issues <<- c(issues, msg)
  }

  # matrix RDS (22,473 x 82)
  f <- file.path(data_dir, "unified_gene_rcd_matrix_V027.rds")
  if (file.exists(f)) {
    m <- tryCatch(readRDS(f), error = function(e) NULL)
    if (is.null(m)) {
      chk(FALSE, "matrix RDS failed to load")
    } else {
      chk(ncol(m) == 94, sprintf("matrix RDS: %d columns (expected 94)", ncol(m)))
      chk(nrow(m) == 22473, sprintf("matrix RDS: %d rows (expected 22,473)", nrow(m)))
    }
  } else chk(FALSE, "missing data/unified_gene_rcd_matrix_V027.rds")

  # decoder CSV (53 x 39)
  f <- file.path(data_dir, "RCDome_Decoder_53.csv")
  if (file.exists(f)) {
    d <- tryCatch(read.csv(f, stringsAsFactors = FALSE), error = function(e) NULL)
    if (is.null(d)) {
      chk(FALSE, "decoder CSV failed to load")
    } else {
      chk(nrow(d) == 53, sprintf("decoder CSV: %d rows (expected 53)", nrow(d)))
      chk(ncol(d) == 39, sprintf("decoder CSV: %d columns (expected 39)", ncol(d)))
    }
  } else chk(FALSE, "missing data/RCDome_Decoder_53.csv")

  # HGNC
  if (!file.exists(file.path(data_dir, "hgnc_complete_set.txt")))
    chk(FALSE, "missing data/hgnc_complete_set.txt")

  # omic xlsx (Gene Catalog auxiliary datasets)
  for (xf in c("ensembl_transcripts.xlsx", "gene_with_mature_miRNA.xlsx", "protein_coding_complete_annotation.xlsx")) {
    if (!file.exists(file.path(data_dir, "omic", xf)))
      chk(FALSE, paste0("missing data/omic/", xf))
  }

  # NCBI gene summaries (Gene information block)
  f <- file.path(data_dir, "gene_info_lookup.json")
  if (file.exists(f)) {
    g <- tryCatch(jsonlite::fromJSON(f), error = function(e) NULL)
    if (is.null(g)) chk(FALSE, "gene_info_lookup.json failed to parse")
    else chk(length(g) == 9265, sprintf("gene_info_lookup.json: %d entries (expected 9,265)", length(g)))
  } else chk(FALSE, "missing data/gene_info_lookup.json")

  # board prompt + www pages
  if (!file.exists(file.path(board_dir, "RCD_Board_DeepSeek_Prompt.md")))
    chk(FALSE, "missing board/RCD_Board_DeepSeek_Prompt.md")
  for (wf in c("landing_page.html", "explore.html", "detail_page_wireframe.html", "dome_prototype.html")) {
    if (!file.exists(file.path(www_dir, wf)))
      chk(FALSE, paste0("missing www/", wf))
  }

  list(ok = length(issues) == 0, issues = issues)
}
