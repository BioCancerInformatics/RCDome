# Build signatures cache (one-time)
t0 <- Sys.time()
cat("reading signatures.tsv...\n")
df <- read.delim("data/signatures.tsv", sep = "\t", stringsAsFactors = FALSE, check.names = FALSE)
cat("  read time:", round(as.numeric(difftime(Sys.time(), t0, units = "secs")), 1), "s | rows:", nrow(df), "| cols:", ncol(df), "\n")

t1 <- Sys.time()
saveRDS(df, "data/signatures_cache.rds")
cat("  saveRDS time:", round(as.numeric(difftime(Sys.time(), t1, units = "secs")), 1), "s\n")

t2 <- Sys.time()
df2 <- readRDS("data/signatures_cache.rds")
cat("  readRDS time:", round(as.numeric(difftime(Sys.time(), t2, units = "secs")), 1), "s\n")
cat("DONE - cache created\n")
