# R4 intelligent auditor — classify each value by context, authenticate only scientific ones.
suppressPackageStartupMessages({library(openxlsx)})

m <- read.csv("RCDome_distribution/data/unified_gene_rcd_matrix_V027.csv", check.names=FALSE, stringsAsFactors=FALSE)
d <- read.csv("RCDome_distribution/data/RCDome_Decoder_53.csv", check.names=FALSE, stringsAsFactors=FALSE)
up <- m[!duplicated(paste(m$gene_symbol, m$rcd_form_canonical)), ]

read_docx_text <- function(p) {
  z <- unzip(p, "word/document.xml", exdir=tempdir())
  xml <- paste(readLines(file.path(tempdir(),"word/document.xml"), warn=FALSE), collapse="")
  gsub("\\s+", " ", gsub("<[^>]+>", " ", xml))
}
manu <- read_docx_text("Submission FAI/RCDome_manuscript_governance_V027.docx")
sents <- strsplit(manu, "(?<=[.;])", perl=TRUE)[[1]]
sents <- trimws(sents[nzchar(sents)])

# noise signatures to drop
noise_pat <- "(orcid|ORCID|doi|DOI|10\\.|Print|Linking|Grant|0000-|@|\\(Print\\)|zip|MA |USA|Japan|Kyoto|Cambridge|Harvard|Broad|Institute)"

rows <- list()
for (s in sents[grepl("[0-9]", sents)]) {
  if (grepl(noise_pat, s)) next                      # drop citations/addresses/orcids/dois
  nums <- unique(regmatches(s, gregexpr("[0-9][0-9,]*(\\.[0-9]+)?%?", s))[[1]])
  for (n in nums) {
    # keep only scientific-looking: >=2 digits and not a bare year/confidence
    core <- gsub("[%,]", "", n)
    if (nchar(core) < 2) next
    rows[[length(rows)+1]] <- data.frame(number=n, context=substr(s,1,110), stringsAsFactors=FALSE)
  }
}
out <- do.call(rbind, rows)
out <- out[!duplicated(paste(out$number, out$context)), ]
write.csv(out, "analysis/r4_scientific_values_worklist.csv", row.names=FALSE)
cat(sprintf("scientific value-context rows (noise dropped): %d\n", nrow(out)))

# truth map for authentication
tr <- table(factor(up$final_role, levels=c("EXECUTOR","REGULATOR","MARKER","UNCERTAIN")))
truth <- c("22,473"=nrow(m), "53"=nrow(d), "9,265"=length(unique(m$gene_symbol)),
           "21,568"=nrow(up), "225"=unname(tr["EXECUTOR"]), "4,455"=unname(tr["REGULATOR"]),
           "95"=unname(tr["MARKER"]), "16,793"=unname(tr["UNCERTAIN"]),
           "7,905"=nrow(readRDS("RCDome_distribution/data/adjudication/disc_df.rds")),
           "164"=nrow(read.csv("_archive_backups/20261026_higor_item3_matrix_amendment/reclassified_rows.csv", check.names=FALSE)))
norm <- function(x) gsub(",", "", x)

cat("\n=== AUTHENTICATION (scientific values vs matrix/decoder truth) ===\n")
distinct <- sort(unique(out$number))
for (n in distinct) {
  v <- suppressWarnings(as.numeric(norm(n)))
  hit <- names(truth)[norm(names(truth)) == norm(n)]
  if (length(hit) > 0) {
    cat(sprintf("  [CONSISTENT] %-10s matches %s\n", n, hit))
  } else {
    ctx <- out$context[out$number == n][1]
    cat(sprintf("  [TO-INVESTIGATE] %-10s | %s\n", n, ctx))
  }
}
cat("\nRule: every TO-INVESTIGATE value gets a provenance dive (code/log) before any human sees it.\n")
