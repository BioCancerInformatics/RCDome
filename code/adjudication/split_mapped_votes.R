t0 <- Sys.time()
df <- read.csv("RCDome_distribution/data/unified_gene_rcd_matrix_V027.csv", check.names = FALSE, stringsAsFactors = FALSE, na.strings = "")
mapped_cols <- c("gpt_mapped_role", "gpt_mapped_dir", "curator_1_mapped_role", "curator_1_mapped_dir", "curator_2_mapped_role", "curator_2_mapped_dir")
mapped <- df[, mapped_cols, drop = FALSE]
df <- df[, !(names(df) %in% mapped_cols), drop = FALSE]
write.csv(df, "RCDome_distribution/data/unified_gene_rcd_matrix_V027.csv", row.names = FALSE, na = "")
saveRDS(df, "RCDome_distribution/data/unified_gene_rcd_matrix_V027.rds")
saveRDS(mapped, "RCDome_distribution/data/mapped_votes.rds")
cat("canonical matrix:", nrow(df), "x", ncol(df), "| mapped_votes:", ncol(mapped), "cols,", round(difftime(Sys.time(), t0, units = "secs"), 1), "s\n")
