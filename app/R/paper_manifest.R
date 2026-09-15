# ─── Paper Manifest ─────────────────────────────────────────────────────────
# Tracks all downloaded papers to avoid re-downloading.
# Columns: pmid, doi, title, folder

MANIFEST_PATH <- "data/papers/paper_manifest.tsv"

#' Load the paper manifest
load_manifest <- function() {
  if (!file.exists(MANIFEST_PATH)) {
    return(data.frame(pmid = character(0), doi = character(0),
                      title = character(0), folder = character(0),
                      stringsAsFactors = FALSE))
  }
  read.delim(MANIFEST_PATH, sep = "\t", stringsAsFactors = FALSE)
}

#' Check if a PMID is already downloaded (exists in manifest)
is_paper_downloaded <- function(pmid) {
  m <- load_manifest()
  pmid %in% m$pmid
}

#' Add a paper to the manifest
add_to_manifest <- function(pmid, doi, title, folder) {
  m <- load_manifest()
  if (pmid %in% m$pmid) return(invisible(NULL))
  new_row <- data.frame(pmid = pmid, doi = doi %||% "", title = title %||% "",
                        folder = folder, stringsAsFactors = FALSE)
  m <- rbind(m, new_row)
  write.table(m, MANIFEST_PATH, sep = "\t", row.names = FALSE, quote = FALSE)
}

#' Rebuild manifest from existing folder structure
rebuild_manifest <- function(base_dir = "data/papers/Overall") {
  m <- data.frame(pmid = character(0), doi = character(0),
                  title = character(0), folder = character(0),
                  stringsAsFactors = FALSE)
  if (!dir.exists(base_dir)) {
    write.table(m, MANIFEST_PATH, sep = "\t", row.names = FALSE, quote = FALSE)
    return(m)
  }
  txt_files <- list.files(base_dir, pattern = "PMID_.*\\.txt$", recursive = TRUE, full.names = TRUE)
  for (f in txt_files) {
    pmid <- gsub("^PMID_|\\.txt$", "", basename(f))
    folder <- dirname(f)
    content <- tryCatch(readLines(f, n = 1, warn = FALSE), error = function(e) "")
    title <- gsub("^TITLE: ", "", content[1])
    m <- rbind(m, data.frame(pmid = pmid, doi = "", title = title,
                             folder = folder, stringsAsFactors = FALSE))
  }
  write.table(m, MANIFEST_PATH, sep = "\t", row.names = FALSE, quote = FALSE)
  m
}
