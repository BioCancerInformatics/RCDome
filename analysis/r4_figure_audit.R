m <- read.csv("RCDome_distribution/data/unified_gene_rcd_matrix_V027.csv", check.names=FALSE, stringsAsFactors=FALSE)
up <- m[!duplicated(paste(m$gene_symbol, m$rcd_form_canonical)), ]
tr <- table(factor(up$final_role, levels=c("EXECUTOR","REGULATOR","MARKER","UNCERTAIN")))
dirs <- table(factor(up$final_direction, levels=c("PROMOTES","PROTECTS","UNCLEAR")))
lv <- up$rcdome_level; mech <- up$final_mechanistic=="YES"
lvl_pct <- sapply(sort(unique(na.omit(lv))), function(L) 100*mean(mech[lv==L], na.rm=TRUE))

fc <- list.files("code/figure_code", pattern="[.](py|R)$", full.names=TRUE)
cat("=== R4 FIGURE-CODE AUDIT ===\n")
cat("matrix truth: EXECUTOR", tr["EXECUTOR"], "| REGULATOR", tr["REGULATOR"], "| MARKER", tr["MARKER"], "| UNCERTAIN", tr["UNCERTAIN"], "\n")
cat("matrix truth: PROMOTES", dirs["PROMOTES"], "| PROTECTS", dirs["PROTECTS"], "\n")
cat(sprintf("matrix truth: L1 %.1f%% | L4 %.1f%% | L5 %.1f%%\n\n", lvl_pct["L1"], lvl_pct["L4"], lvl_pct["L5"]))
for (f in fc) {
  txt <- paste(readLines(f, warn=FALSE), collapse=" ")
  flags <- c()
  for (v in c("REGULATOR","UNCERTAIN","EXECUTOR","MARKER","PROMOTES","PROTECTS")) {
    mm <- regexpr(paste0(v, "[^0-9]{0,8}([0-9][0-9,]{2,})"), txt)
    if (mm > 0) {
      seg <- regmatches(txt, mm)
      val <- gsub("[^0-9]", "", sub(paste0(".*", v), "", seg))
      val <- gsub("[^0-9]", "", val)
      tv <- if (v %in% names(tr)) as.character(tr[[v]]) else if (v %in% names(dirs)) as.character(dirs[[v]]) else NA
      if (!is.na(tv) && nzchar(val) && val != tv) flags <- c(flags, sprintf("%s=%s (matrix %s)", v, val, tv))
    }
  }
  if (length(flags) > 0) cat(sprintf("  [STALE] %s : %s\n", basename(f), paste(flags, collapse=" | ")))
}
cat("\nRule: any STALE figure value blocks closure until the figure is regenerated from the matrix.\n")
