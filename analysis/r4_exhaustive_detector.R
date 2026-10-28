# R4 EXHAUSTIVE DETECTOR — derivation map ("innocent until proven guilty")
# Mission: trace EVERY value to its derivation, not merely flag it.
#   CONSISTENT  = matches a truth derived from the matrix/decoder
#   DERIVED     = traced to a source file (figure_code/analysis/log/doc/comms) — authenticated by origin
#   UNRESOLVED  = NO source anywhere after an EXHAUSTIVE dive of the master folder (Phase 3 candidates)
# Truth: FULLY DERIVED from matrix + decoder (zero hardcoded counts).
# Denominated: raw rows vs unique pairs vs unique genes — explicit, never conflated.
# Phase 1 (default): READ-ONLY — verify claimed values against the matrix (no re-execution).
# Phase 2: exhaustive derivation dive (read-only) over the master folder + all sub-analyses.
# Phase 3 (gated): re-run a sub-analysis ONLY if still unresolved, and ONLY after discussion + human approval.
suppressPackageStartupMessages({library(openxlsx)})

BASE <- "RCDome_distribution/data"
m <- read.csv(file.path(BASE, "unified_gene_rcd_matrix_V027.csv"), check.names=FALSE, stringsAsFactors=FALSE)
d <- read.csv(file.path(BASE, "RCDome_Decoder_53.csv"), check.names=FALSE, stringsAsFactors=FALSE)

# ---------- 1. T0 truth engine (derived, zero hardcoded) ----------
up <- m[!duplicated(paste(m$gene_symbol, m$rcd_form_canonical)), ]   # unique gene-entity pairs
truth <- list(
  "raw association rows"        = nrow(m),
  "unique gene-entity pairs"    = nrow(up),
  "unique genes"                = length(unique(m$gene_symbol)),
  "canonical RCD entities"      = nrow(d),
  "EXECUTOR (unique pairs)"     = sum(up$final_role == "EXECUTOR", na.rm = TRUE),
  "REGULATOR (unique pairs)"    = sum(up$final_role == "REGULATOR", na.rm = TRUE),
  "MARKER (unique pairs)"       = sum(up$final_role == "MARKER", na.rm = TRUE),
  "UNCERTAIN (unique pairs)"    = sum(up$final_role == "UNCERTAIN", na.rm = TRUE),
  "PROMOTES (unique pairs)"     = sum(up$final_direction == "PROMOTES", na.rm = TRUE),
  "PROTECTS (unique pairs)"     = sum(up$final_direction == "PROTECTS", na.rm = TRUE),
  "UNCLEAR (unique pairs)"      = sum(up$final_direction == "UNCLEAR", na.rm = TRUE),
  "mechanistic YES (pairs)"     = sum(up$final_mechanistic == "YES", na.rm = TRUE)
)
# level percentages (mechanistic-YES denominator, unique pairs)
lv <- up$rcdome_level; mech <- up$final_mechanistic == "YES"
for (L in sort(unique(na.omit(lv)))) truth[[paste0("L", L, " mechanistic %")]] <- round(100 * mean(mech[lv == L], na.rm = TRUE), 1)
# role-resolved direction, per role
for (rl in c("EXECUTOR", "REGULATOR", "MARKER", "UNCERTAIN")) {
  sub <- up[up$final_role == rl, ]
  truth[[paste0(rl, " PROMOTES (role-resolved)")]] <- sum(sub$final_direction == "PROMOTES", na.rm = TRUE)
  truth[[paste0(rl, " PROTECTS (role-resolved)")]] <- sum(sub$final_direction == "PROTECTS", na.rm = TRUE)
}
# role-resolved direction across non-UNCERTAIN roles (EXECUTOR + REGULATOR + MARKER) — Figure 4 panel C
rr <- up[up$final_role %in% c("EXECUTOR", "REGULATOR", "MARKER"), ]
truth[["role-resolved PROMOTES (non-UNCERTAIN)"]] <- sum(rr$final_direction == "PROMOTES", na.rm = TRUE)
truth[["role-resolved PROTECTS (non-UNCERTAIN)"]] <- sum(rr$final_direction == "PROTECTS", na.rm = TRUE)
truth[["role-resolved UNCLEAR (non-UNCERTAIN)"]]  <- sum(rr$final_direction == "UNCLEAR", na.rm = TRUE)

norm <- function(x) gsub("[%,]", "", trimws(x))
truth_lookup <- list()   # normalized-number -> semantic label(s)
for (nm in names(truth)) {
  key <- norm(as.character(truth[[nm]]))
  truth_lookup[[key]] <- c(truth_lookup[[key]], nm)
}

# ---------- 2. read artifacts (T2 surface) ----------
read_docx <- function(p) {
  ex <- tempfile(); dir.create(ex)
  unzip(p, "word/document.xml", exdir = ex)
  xml <- paste(readLines(file.path(ex, "word/document.xml"), warn = FALSE), collapse = "")
  gsub("\\s+", " ", gsub("<[^>]+>", " ", xml))
}
manu <- read_docx("Submission FAI/RCDome_manuscript_governance_V027.docx")
si   <- read_docx("Submission FAI/RCDome_manuscript_V027_supplementary_information.docx")

tbl <- openxlsx::loadWorkbook("Submission FAI/RCDome_manuscript_V027_supplementary_tables.xlsx")
tbl_txt <- ""
for (sn in names(tbl)) {
  df <- openxlsx::readWorkbook(tbl, sheet = sn, colNames = FALSE)
  tbl_txt <- paste(tbl_txt, sn, paste(as.matrix(df), collapse = " "), collapse = " ")
}

fc <- list.files("code/figure_code", pattern = "[.](py|R)$", full.names = TRUE)
fig_code <- paste(vapply(fc, function(f) paste(readLines(f, warn = FALSE), collapse = " "), ""), collapse = " ")
leg_sents <- unique(c(trimws(strsplit(si, "(?<=[.;:])", perl = TRUE)[[1]]),
                      trimws(strsplit(manu, "(?<=[.;:])", perl = TRUE)[[1]])))
legends <- paste(leg_sents[grepl("Figure|Fig[.]", leg_sents, ignore.case = TRUE)], collapse = " ")

comms <- paste(vapply(list.files("comms", pattern = "[.](md|txt)$", recursive = TRUE, full.names = TRUE),
                      function(f) paste(readLines(f, warn = FALSE), collapse = " "), ""), collapse = " ")

artifacts <- list(manuscript = manu, SI = si, tables = tbl_txt,
                  figure_code = fig_code, figure_legends = legends, comms = comms)

# ---------- 3. extract numbers + context (all artifacts) ----------
noise_pat <- "(orcid|ORCID|doi|DOI|10\\.|Print|Linking|Grant|0000-|@|\\(Print\\)|MA |USA|Japan|Kyoto|Cambridge|Harvard|Broad|Institute|R\\d|D\\d|S\\d)"
rows <- list()
for (an in names(artifacts)) {
  sents <- strsplit(artifacts[[an]], "(?<=[.;:])", perl = TRUE)[[1]]
  sents <- trimws(sents[nzchar(sents)])
  for (s in sents[grepl("[0-9]", sents)]) {
    if (grepl(noise_pat, s)) next
    nums <- unique(regmatches(s, gregexpr("[0-9][0-9,]*([.][0-9]+)?%?", s))[[1]])
    for (n in nums) {
      core <- gsub("[%,]", "", n)
      if (nchar(core) < 2) next
      rows[[length(rows) + 1]] <- data.frame(artifact = an, number = n, context = substr(s, 1, 160), stringsAsFactors = FALSE)
    }
  }
}
vals <- do.call(rbind, rows)
vals <- vals[!duplicated(paste(vals$artifact, vals$number, vals$context)), ]
cat(sprintf("extracted value-context rows across %d artifacts: %d\n", length(artifacts), nrow(vals)))

# ---------- 4. exhaustive derivation dive (Phase 2): number -> (source file, class) over the MASTER folder ----------
src_files <- list.files(c("code", "analysis", "docs", "comms", "manuscript_V027"),
                        recursive = TRUE, full.names = TRUE,
                        pattern = "\\.(py|R|md|txt|csv|json|log)$")
src_files <- src_files[!grepl("node_modules|\\.git/|_archive|\\.Renviron|\\.docx", src_files)]
src_files <- src_files[file.info(src_files)$size < 1e6]

classify <- function(f) {
  if (grepl("figure_code", f)) return("figure_code")
  if (grepl("unified_gene_rcd_matrix|RCDome_Decoder|Dataset S1", f)) return("matrix")
  if (grepl("[.]log$", f)) return("log")
  if (grepl("analysis/", f)) return("analysis")
  if (grepl("docs/", f)) return("doc")
  if (grepl("comms/", f)) return("comms")
  return("other")
}

cat("exhaustive dive into", length(src_files), "source files...\n")
num2src <- list()
for (f in src_files) {
  t <- tryCatch(paste(readLines(f, warn = FALSE), collapse = " "), error = function(e) "")
  if (nzchar(t)) {
    nums <- tryCatch(unique(regmatches(t, gregexpr("[0-9][0-9,]*([.][0-9]+)?%?", t, useBytes = TRUE))[[1]]), error = function(e) character())
    for (nn in nums) {
      key <- norm(nn)
      if (nchar(key) >= 2) num2src[[key]] <- c(num2src[[key]], paste0(basename(f), " [", classify(f), "]"))
    }
  }
}
cat("number->source index built\n")

# ---------- 5. authenticate: CONSISTENT / DERIVED / UNRESOLVED ----------
N <- nrow(vals)
v_art <- vals$artifact; v_num <- vals$number; v_ctx <- vals$context
v_verdict <- character(N); v_truth <- character(N)
cat("authenticating", N, "values...\n")
for (i in seq_len(N)) {
  nn <- norm(v_num[i])
  exact <- truth_lookup[[nn]]
  if (length(exact) > 0) {
    v_verdict[i] <- "CONSISTENT"; v_truth[i] <- paste(exact, collapse = "; ")
  } else {
    hits <- num2src[[nn]]
    if (length(hits) > 0) {
      v_verdict[i] <- "DERIVED"; v_truth[i] <- paste(unique(head(hits, 3)), collapse = ", ")
    } else {
      v_verdict[i] <- "UNRESOLVED"; v_truth[i] <- ""
    }
  }
}
rep <- data.frame(artifact = v_art, number = v_num, context = v_ctx,
                  verdict = v_verdict, derivation = v_truth, stringsAsFactors = FALSE)
write.csv(rep, "analysis/r4_exhaustive_detector_report.csv", row.names = FALSE)

# ---------- 6. report: derivation map ----------
cat("\n=== R4 EXHAUSTIVE DETECTOR — derivation map ===\n")
cat(sprintf("CONSISTENT (matrix truth): %d\n", sum(rep$verdict == "CONSISTENT")))
cat(sprintf("DERIVED (traced to a source): %d\n", sum(rep$verdict == "DERIVED")))
cat(sprintf("UNRESOLVED (no source after exhaustive dive): %d\n", sum(rep$verdict == "UNRESOLVED")))
cat("\nUNRESOLVED (Phase 3 candidates):\n")
ur <- rep[rep$verdict == "UNRESOLVED", ]
if (nrow(ur) > 0) for (k in seq_len(min(60, nrow(ur)))) cat(sprintf("  [%s] %-12s | %s\n", ur$artifact[k], ur$number[k], ur$context[k]))
cat("\nRule: UNRESOLVED is earned ONLY after the exhaustive master-folder dive. DERIVED is authenticated by origin. Never auto-flag STALE; human adjudicates against the matrix. Unresolved -> Phase 3 (re-run, gated, human-approved).\n")
