# RCDome — pre-flight data validation
# Verifies every bundled asset before the app serves anything (proactive, not reactive).
# Returns list(ok = logical, issues = character vector).
validate_data_files <- function(data_dir = "data", board_dir = "board", www_dir = "www") {
  issues <- character(0)
  chk <- function(cond, msg) {
    if (!isTRUE(cond)) issues <<- c(issues, msg)
  }

  # matrix RDS (22,473 x 94: 83 original + 11 additive adjudication columns)
  f <- file.path(data_dir, "unified_gene_rcd_matrix_V027.rds")
  if (file.exists(f)) {
    m <- tryCatch(readRDS(f), error = function(e) NULL)
    if (is.null(m)) {
      chk(FALSE, "matrix RDS failed to load")
    } else {
      chk(ncol(m) == 100, sprintf("matrix RDS: %d columns (expected 100)", ncol(m)))
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
      chk(ncol(d) == 42, sprintf("decoder CSV: %d columns (expected 42)", ncol(d)))
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

  # NCBI gene summaries (Gene information block) — existence only; the 6.7 MB
  # JSON is loaded lazily where needed, never parsed at app startup.
  if (!file.exists(file.path(data_dir, "gene_info_lookup.json")))
    chk(FALSE, "missing data/gene_info_lookup.json")

  # Discrepancy Radar precomputed assets (7,905 rows x 11 HTML columns)
  f <- file.path(data_dir, "adjudication", "disc_df.rds")
  if (!file.exists(f)) chk(FALSE, "missing data/adjudication/disc_df.rds")
  f <- file.path(data_dir, "adjudication", "disc_html.rds")
  if (file.exists(f)) {
    h <- tryCatch(readRDS(f), error = function(e) NULL)
    if (is.null(h)) {
      chk(FALSE, "disc_html.rds failed to load")
    } else {
      chk(nrow(h) == 7905, sprintf("disc_html.rds: %d rows (expected 7,905)", nrow(h)))
      chk(ncol(h) == 11, sprintf("disc_html.rds: %d columns (expected 11)", ncol(h)))
    }
  } else chk(FALSE, "missing data/adjudication/disc_html.rds")

  # board prompt + www pages
  if (!file.exists(file.path(board_dir, "RCD_Board_DeepSeek_Prompt.md")))
    chk(FALSE, "missing board/RCD_Board_DeepSeek_Prompt.md")
  for (wf in c("landing_page.html", "explore.html", "detail_page_wireframe.html", "dome_prototype.html")) {
    if (!file.exists(file.path(www_dir, wf)))
      chk(FALSE, paste0("missing www/", wf))
  }

  list(ok = length(issues) == 0, issues = issues)
}
