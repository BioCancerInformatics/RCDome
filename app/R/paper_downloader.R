# ─── Paper Downloader ───────────────────────────────────────────────────────
# Downloads FULL-TEXT PDFs via PMID → multi-source cascade:
#  1. Europe PMC PDF    2. NCBI PMC PDF    3. Unpaywall (DOI → PDF)
# Falls back to abstract ONLY when no open-access full text exists.
# Stores in data/papers/{pathway}/{gene}/PMID_XXXXX.txt

#' Link a single PMID to PMCID
link_pmid_to_pmcid <- function(pmid) {
  url <- paste0(
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?",
    "dbfrom=pubmed&db=pmc&id=", pmid, "&api_key=***REMOVED***"
  )
  resp <- tryCatch(httr::GET(url, httr::timeout(10)), error = function(e) NULL)
  if (is.null(resp) || httr::status_code(resp) != 200) return(NULL)
  xml <- tryCatch(httr::content(resp, "parsed", "text/xml"), error = function(e) NULL)
  if (is.null(xml)) return(NULL)
  nodes <- xml2::xml_find_all(xml, "//LinkSetDb[DbTo='pmc']/Link/Id")
  if (length(nodes) == 0) return(NULL)
  raw <- xml2::xml_text(nodes[1])
  if (is.na(raw)) return(NULL)
  ifelse(grepl("^PMC", raw, ignore.case = TRUE), raw, paste0("PMC", raw))
}

#' Get DOI for a PMID via NCBI
fetch_doi_for_pmid <- function(pmid) {
  url <- paste0(
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?",
    "db=pubmed&id=", pmid, "&api_key=***REMOVED***&retmode=json"
  )
  resp <- tryCatch(httr::GET(url, httr::timeout(10)), error = function(e) NULL)
  if (is.null(resp) || httr::status_code(resp) != 200) return(NULL)
  json <- tryCatch(jsonlite::fromJSON(httr::content(resp, "text", encoding="UTF-8")), error = function(e) NULL)
  if (is.null(json)) return(NULL)
  ids <- json$result$uids
  if (length(ids) == 0) return(NULL)
  articleids <- json$result[[ids[1]]]$articleids
  if (is.null(articleids)) return(NULL)
  doi_row <- articleids[articleids$idtype == "doi", ]
  if (nrow(doi_row) == 0) return(NULL)
  doi_row$value[1]
}

#' Download PDF via Unpaywall (legal OA copies from repositories)
download_unpaywall_pdf <- function(doi, out_pdf) {
  uw_url <- paste0("https://api.unpaywall.org/v2/", doi, "?email=research@example.org")
  uw <- tryCatch(httr::GET(uw_url, httr::timeout(15)), error = function(e) NULL)
  if (is.null(uw) || httr::status_code(uw) != 200) return(FALSE)
  uw_data <- tryCatch(jsonlite::fromJSON(httr::content(uw, "text", encoding="UTF-8")), error = function(e) NULL)
  if (is.null(uw_data) || !isTRUE(uw_data$is_oa)) return(FALSE)

  pdf_url <- uw_data$best_oa_location$url_for_pdf %||% uw_data$best_oa_location$url
  if (is.null(pdf_url)) return(FALSE)

  resp <- tryCatch(
    httr::GET(pdf_url, httr::write_disk(out_pdf, overwrite = TRUE), httr::timeout(60)),
    error = function(e) NULL
  )
  if (is.null(resp) || httr::status_code(resp) != 200) return(FALSE)
  if (!is_valid_pdf(out_pdf)) { unlink(out_pdf); return(FALSE) }
  TRUE
}

#' Get DOI for a PMID via NCBI

#' Check that a downloaded file is really a PDF (magic bytes: %PDF-)
is_valid_pdf <- function(path) {
  if (!file.exists(path)) return(FALSE)
  sz <- file.info(path)$size
  if (is.na(sz) || sz < 1000) return(FALSE)
  con <- file(path, "rb")
  on.exit(close(con))
  header <- tryCatch(readBin(con, "raw", n = 5), error = function(e) raw(0))
  identical(rawToChar(header), "%PDF-")
}

#' Download PDF from Europe PMC via PMCID
download_europe_pmc_pdf <- function(pmcid, out_pdf) {
  url <- paste0("https://europepmc.org/articles/", pmcid, "?pdf=render")
  resp <- tryCatch(
    httr::GET(url, httr::write_disk(out_pdf, overwrite = TRUE), httr::timeout(60),
              httr::user_agent("R/3.6")),
    error = function(e) NULL
  )
  if (is.null(resp) || httr::status_code(resp) != 200) return(FALSE)
  ctype <- httr::headers(resp)[["content-type"]] %||% ""
  if (!grepl("pdf", ctype, ignore.case = TRUE) && !is_valid_pdf(out_pdf)) {
    unlink(out_pdf)
    return(FALSE)
  }
  is_valid_pdf(out_pdf)
}

#' Download PDF from NCBI PMC via PMCID
download_ncbi_pmc_pdf <- function(pmcid, out_pdf) {
  url <- paste0("https://www.ncbi.nlm.nih.gov/pmc/articles/", pmcid, "/pdf/")
  resp <- tryCatch(
    httr::GET(url, httr::write_disk(out_pdf, overwrite = TRUE), httr::timeout(60),
              httr::user_agent("R/3.6")),
    error = function(e) NULL
  )
  if (is.null(resp) || httr::status_code(resp) != 200) return(FALSE)
  ctype <- httr::headers(resp)[["content-type"]] %||% ""
  if (!grepl("pdf", ctype, ignore.case = TRUE) && !is_valid_pdf(out_pdf)) {
    unlink(out_pdf)
    return(FALSE)
  }
  is_valid_pdf(out_pdf)
}

#' Extract text from PDF
pdf_to_text <- function(pdf_path) {
  if (!is_valid_pdf(pdf_path)) return(NULL)
  txt <- tryCatch(suppressWarnings(pdftools::pdf_text(pdf_path)), error = function(e) NULL)
  if (is.null(txt) || length(txt) == 0) return(NULL)
  txt <- paste(txt, collapse = "\n")
  txt <- gsub("\\s+", " ", txt)
  trimws(txt)
}

download_papers_for_gene <- function(gene, pathway, articles, base_dir = "data/papers/Overall") {
  if (length(articles) == 0) return(0L)

  out_dir <- file.path(base_dir, pathway, gene)
  dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
  downloaded <- 0L

  for (art in articles) {
    pmid <- art$pmid
    if (is.null(pmid) || is.na(pmid) || pmid == "" || pmid == "NA") next

    # Check manifest + existing files across entire overall/
    if (is_paper_downloaded(pmid)) next
    existing <- list.files(base_dir, pattern = paste0("^PMID_", pmid, ".*\\.txt$"),
                           recursive = TRUE, full.names = TRUE)
    if (length(existing) > 0 && !is.na(file.info(existing[1])$size) && file.info(existing[1])$size > 500) {
      add_to_manifest(pmid, art$doi, art$title, dirname(existing[1]))
      next
    }

    title <- art$title %||% ""
    abstr <- art$abstract
    if (is.null(abstr) || is.na(abstr)) abstr <- ""

    full_text <- NULL

    # Cascade 1 & 2: PMCID → Europe PMC / NCBI PMC PDF
    pmcid <- link_pmid_to_pmcid(pmid)
    if (!is.null(pmcid)) {
      tmp_pdf <- file.path(tempdir(), paste0(pmcid, ".pdf"))
      ok <- download_europe_pmc_pdf(pmcid, tmp_pdf) || download_ncbi_pmc_pdf(pmcid, tmp_pdf)
      if (ok) {
        full_text <- pdf_to_text(tmp_pdf)
        unlink(tmp_pdf)
      }
    }

    # Cascade 3: Unpaywall via DOI
    if (is.null(full_text)) {
      doi <- fetch_doi_for_pmid(pmid)
      if (!is.null(doi)) {
        tmp_pdf <- file.path(tempdir(), paste0("DOI_", gsub("[^a-zA-Z0-9]", "_", doi), ".pdf"))
        if (download_unpaywall_pdf(doi, tmp_pdf)) {
          full_text <- pdf_to_text(tmp_pdf)
        }
        unlink(tmp_pdf)
      }
    }

    # Cascade 4: Semantic Scholar (free API, no key required)
    if (is.null(full_text)) {
      full_text <- tryCatch({
        s2_url <- paste0("https://api.semanticscholar.org/graph/v1/paper/PMID:", pmid, "?fields=openAccessPdf")
        s2 <- httr::GET(s2_url, httr::timeout(10))
        if (httr::status_code(s2) == 200) {
          s2_data <- jsonlite::fromJSON(httr::content(s2, "text", encoding="UTF-8"))
          pdf_url <- s2_data$openAccessPdf$url
          if (!is.null(pdf_url)) {
            tmp_pdf <- file.path(tempdir(), paste0("S2_", pmid, ".pdf"))
            resp <- httr::GET(pdf_url, httr::write_disk(tmp_pdf, overwrite=TRUE), httr::timeout(60))
            if (httr::status_code(resp) == 200 && is_valid_pdf(tmp_pdf)) {
              txt <- pdf_to_text(tmp_pdf)
              unlink(tmp_pdf)
              txt
            } else { unlink(tmp_pdf); NULL }
          }
        }
      }, error = function(e) NULL)
    }

    # Build final content
    if (!is.null(full_text) && nchar(full_text) > 1000) {
      txt <- paste0("TITLE: ", title, "\n\n[FULL TEXT - Open Access]\n", full_text)
    } else {
      txt <- paste0("TITLE: ", title, "\n\n[ABSTRACT ONLY - Full text behind paywall]\n",
                    "ABSTRACT: ", abstr)
    }

    if (nchar(txt) > 100) {
      out_txt <- file.path(out_dir, paste0("PMID_", pmid, ".txt"))
      writeLines(txt, out_txt, useBytes = TRUE)
      add_to_manifest(pmid, art$doi %||% "", art$title %||% "", out_dir)
      downloaded <- downloaded + 1L
    }
    Sys.sleep(0.5)
  }
  downloaded
}

load_papers_for_gene <- function(gene, base_dir = "data/papers/Overall") {
  papers <- list()
  if (!dir.exists(base_dir)) return(papers)
  pathways <- list.dirs(base_dir, full.names = FALSE, recursive = FALSE)
  for (pw in pathways) {
    gene_dir <- file.path(base_dir, pw, gene)
    if (!dir.exists(gene_dir)) next
    txt_files <- list.files(gene_dir, pattern = "\\.txt$", full.names = TRUE)
    for (f in txt_files) {
      pmid <- gsub("^PMID_|\\.txt$", "", basename(f))
      content <- tryCatch(
        paste(readLines(f, warn = FALSE, encoding = "UTF-8"), collapse = "\n"),
        error = function(e) ""
      )
      if (nchar(content) < 200) next
      is_full <- grepl("FULL TEXT", content, fixed = TRUE)
      papers[[length(papers) + 1]] <- list(
        pmid = pmid, pathway = pw, gene = gene, content = content, is_full = is_full
      )
    }
  }
  papers
}

#' Load all papers across all genes and pathways (for free chat mode)
load_all_papers <- function(base_dir = "data/papers/Overall") {
  papers <- list()
  if (!dir.exists(base_dir)) return(papers)
  pathways <- list.dirs(base_dir, full.names = FALSE, recursive = FALSE)
  for (pw in pathways) {
    gene_dirs <- list.dirs(file.path(base_dir, pw), full.names = FALSE, recursive = FALSE)
    for (gene in gene_dirs) {
      txt_files <- list.files(file.path(base_dir, pw, gene), pattern = "\\.txt$", full.names = TRUE)
      for (f in txt_files) {
        pmid <- gsub("^PMID_|\\.txt$", "", basename(f))
        content <- tryCatch(
          paste(readLines(f, warn = FALSE, encoding = "UTF-8"), collapse = "\n"),
          error = function(e) ""
        )
        if (nchar(content) < 200) next
        is_full <- grepl("FULL TEXT", content, fixed = TRUE)
        papers[[length(papers) + 1]] <- list(
          pmid = pmid, pathway = pw, gene = gene, content = content, is_full = is_full
        )
      }
    }
  }
  papers
}
