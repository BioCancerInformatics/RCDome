t0 <- Sys.time()
df <- read.csv("RCDome_distribution/data/unified_gene_rcd_matrix_V027.csv", check.names = FALSE, stringsAsFactors = FALSE, na.strings = "")
map_vote_col <- function(concat, ds, cs) {
  concat <- trimws(as.character(concat))
  out <- rep(NA_character_, length(concat))
  ok <- !is.na(concat) & nzchar(concat)
  if (any(ok)) {
    parts <- strsplit(concat[ok], "|", fixed = TRUE)
    src <- vapply(parts, function(p) {
      p <- trimws(p); p <- p[nzchar(p)]
      if (length(p) > 0) p[1] else NA_character_
    }, character(1))
    out[ok] <- ifelse(src == "DEEPSEEK", ds[ok], ifelse(src == "CONSENSUS", cs[ok], src))
  }
  out
}
df$gpt_mapped_role    <- map_vote_col(df$gpt4o_verdict,  df$cot_role,      df$consensus_role)
df$gpt_mapped_dir     <- map_vote_col(df$gpt4o_verdict,  df$cot_direction, df$consensus_direction)
df$curator_1_mapped_role  <- map_vote_col(df$curator_1_verdict,  df$cot_role,      df$consensus_role)
df$curator_1_mapped_dir   <- map_vote_col(df$curator_1_verdict,  df$cot_direction, df$consensus_direction)
df$curator_2_mapped_role <- map_vote_col(df$curator_2_verdict, df$cot_role,      df$consensus_role)
df$curator_2_mapped_dir  <- map_vote_col(df$curator_2_verdict, df$cot_direction, df$consensus_direction)
saveRDS(df, "RCDome_distribution/data/unified_gene_rcd_matrix_V027.rds")
write.csv(df, "RCDome_distribution/data/unified_gene_rcd_matrix_V027.csv", row.names = FALSE, na = "")
cat("matrix now", nrow(df), "x", ncol(df), "in", round(difftime(Sys.time(), t0, units = "secs"), 1), "s\n")
