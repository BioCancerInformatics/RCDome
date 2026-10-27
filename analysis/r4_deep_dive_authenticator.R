# R4 investigative agent — bind local tuple, verify vs matrix/decoder, else dive code/logs for provenance.
m <- read.csv("RCDome_distribution/data/unified_gene_rcd_matrix_V027.csv", check.names=FALSE, stringsAsFactors=FALSE)
ents <- sort(unique(m$rcd_form_canonical)); ents <- ents[order(nchar(ents), decreasing=TRUE)]

read_docx_text <- function(p) {
  z <- unzip(p, "word/document.xml", exdir=tempdir())
  xml <- paste(readLines(file.path(tempdir(),"word/document.xml"), warn=FALSE), collapse="")
  gsub("\\s+", " ", gsub("<[^>]+>", " ", xml))
}
manu <- read_docx_text("Submission FAI/RCDome_manuscript_governance_V027.docx")

compute <- function(entity, metric) {
  sub <- m[m$rcd_form_canonical == entity, , drop=FALSE]
  if (nrow(sub)==0) return(NA_integer_)
  if (metric %in% c("genes","unique genes")) length(unique(sub$gene_symbol)) else if (metric %in% c("rows","association rows","records","associations")) nrow(sub) else NA_integer_
}

dive <- function(n, ctx) {
  res <- suppressWarnings(system2("grep", c("-rln", shQuote(n),
    "--include=*.py","--include=*.R","--include=*.md","--include=*.txt","--include=*.csv",
    "analysis","code","docs","extraction code snippets","output databases"),
    stdout=TRUE, stderr=FALSE))
  res <- res[!grepl("benchmark_label_error_n800|r4_|_archive", res)]
  res
}

# bind local tuples: entity (number metric)
pat <- "([A-Za-z][A-Za-z -]{2,40}?)\\s*\\(?\\s*([0-9][0-9,]*)\\s*\\)?\\s*((?:unique )?genes|(?:association )?rows|records|associations)"
mm <- gregexpr(pat, manu, perl=TRUE)[[1]]
lens <- attr(mm, "match.length")
cat("=== INVESTIGATIVE PASS (matrix + code/log provenance) ===\n\n")
seen <- character(0); n_ok <- 0; n_disc <- 0; n_dive <- 0
for (k in seq_along(mm)) {
  seg <- substr(manu, mm[k], mm[k]+lens[k]-1)
  caps <- regmatches(seg, regexec(pat, seg, perl=TRUE))[[1]]
  if (length(caps) < 4) next
  e <- trimws(caps[2]); n <- caps[3]; metric <- caps[4]
  v <- suppressWarnings(as.numeric(gsub(",", "", n)))
  if (is.na(v)) next
  # entity must be a known entity
  hit <- ents[vapply(ents, function(x) grepl(x, e, fixed=TRUE), logical(1))]
  if (length(hit)==0) next
  e <- hit[1]
  tv <- compute(e, metric)
  key <- paste(e, metric, n)
  if (key %in% seen) next
  seen <- c(seen, key)
  if (!is.na(tv)) {
    if (v==tv) { cat(sprintf("  [CONSISTENT] %-22s %s = %s (matrix)\n", paste0(e," ",metric), n, tv)); n_ok<-n_ok+1 }
    else { cat(sprintf("  [DISCORDANT] %-22s %s vs matrix %s\n", paste0(e," ",metric), n, tv)); n_disc<-n_disc+1 }
  } else {
    # not a direct matrix aggregation -> dive code/logs for provenance
    src <- dive(n, e)
    tag <- if (length(src)==0) "NO PROVENANCE FOUND" else paste0(length(src)," file(s)")
    cat(sprintf("  [SUB-ANALYSIS] %-22s %s -> %s\n", paste0(e," ",metric), n, tag))
    if (length(src)>0 && length(src)<=3) for (s in src) cat(sprintf("        -> %s\n", s))
    n_dive <- n_dive+1
  }
}
cat(sprintf("\nsummary: %d consistent | %d discordant | %d sub-analysis/benchmark (dived)\n", n_ok, n_disc, n_dive))
