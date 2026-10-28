df <- readRDS("RCDome_distribution/data/adjudication/disc_df.rds")
cat("TOTAL label-disagreement rows:", nrow(df), "\n")
cat("by label:\n")
print(table(df$label))
up <- df[!duplicated(paste(df$gene_symbol, df$rcd_form_canonical)), ]
cat("\nUNIQUE gene-entity pairs:", nrow(up), "\n")
# verify the SI sentence: 7,905 (role 320 + direction 935 + mechanistic 6,650) on 7,831 unique pairs
r <- sum(df$label == "role"); d <- sum(df$label == "direction"); m <- sum(df$label == "mechanistic")
cat("\nrole", r, "+ direction", d, "+ mechanistic", m, "=", r+d+m, "(SI total 7,905)\n")
cat("SI claims: role 320, direction 935, mechanistic 6,650, unique pairs 7,831\n")
cat("MATCH:", r==320 && d==935 && m==6650 && nrow(up)==7831, "\n")
