# Precompute the Discrepancy Radar HTML frame once (offline) so the app opens
# instantly. Building 7,905 rows × 11 HTML columns takes ~27 s on the fly; this
# script pays that cost at build time and writes a ~1.7 MB RDS the app reads in
# ~0.12 s. Re-run whenever data/adjudication/disc_df.rds changes (e.g. after the
# delta curator round returns).
t0 <- Sys.time()
source("RCDome_distribution/R/disc_html_build.R")
d <- readRDS("RCDome_distribution/data/adjudication/disc_df.rds")
h <- build_disc_html(d, "@@NS@@")
saveRDS(h, "RCDome_distribution/data/adjudication/disc_html.rds")
cat("saved disc_html.rds:", nrow(h), "rows x", ncol(h), "cols in",
    round(difftime(Sys.time(), t0, units = "secs"), 1), "s\n")
