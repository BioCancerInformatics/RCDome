# ─── Global: bibliotecas, dados, source ──────────────────────────────────────
library(shiny)
library(readxl)
library(dplyr)
library(DT)
library(httr)
library(jsonlite)
library(visNetwork)
library(shinycssloaders)
library(shinyjs)
library(blastula)
library(tidyr)
library(plotly)

# Garante que .Renviron do projeto seja lido (mesmo sem restart da sessão)
if (file.exists(".Renviron")) readRenviron(".Renviron")
if (!nzchar(Sys.getenv("DEEPSEEK_API_KEY"))) {
  stop("DEEPSEEK_API_KEY não configurada. Crie .Renviron com a chave ou defina no sistema.")
}

# Ensure data directories exist

# Serve RCD module static files (match reference app paths)
addResourcePath("rcd_logos", "data/RCD modulo/logo RCDs/thumbs")
addResourcePath("rcd_figs",  "data/RCD modulo/figuras RCDs")
addResourcePath("rcd_videos", "data/RCD modulo/videos")
addResourcePath("rcd_mod",   "data/RCD modulo")
addResourcePath("devs", "data/about/Desenvolvedores")
addResourcePath("see_also", "data/about/see also")

# Source helpers and API wrappers (non-reactive)
source("R/utils.R")
source("R/pathways.R")     # get_pathways_for_gene() — from the matrix
source("R/rcd_modal.R")    # show_rcd_modal — shared RCD pop-up
source("R/validate_data_files.R")

# Pre-flight data validation — fail fast if any bundled asset is missing/invalid.
# Proactive: the error is caught + fixed at startup/build time, never shown to the user.
v <- validate_data_files()
if (!v$ok) {
  stop(paste("RCDome data validation failed:
", paste0("- ", v$issues, collapse = "
")))
}

# Source Shiny modules
source("modules/mod_gene_catalog.R")
source("modules/mod_network.R")
source("modules/mod_rcd_grid.R")
source("modules/mod_rcd_entities.R")
source("modules/mod_od.R")
source("modules/mod_od_compare.R")
source("modules/mod_board_qa.R")
source("modules/mod_board.R")

# Signatures removed (vestigial legacy module).
signatures_df <- NULL

# Load gene reference data (from omic directory) — with RDS cache
# Fingerprint v2: sourced from the V027 matrix (the truth).
v24_file <- "data/unified_gene_rcd_matrix_V027.rds"
v24_mtime <- file.info(v24_file)$mtime
fingerprint_cache_file <- "data/omic/fingerprint_cache.rds"
fingerprint_cache_version <- 7L
expected_canonical_pathways <- 53L

# ── Gene table (V027 matrix — the truth) ─────────────────────────────────────
message("Loading genes from V027 matrix...")
genes_df <- tryCatch({
  df <- readRDS(v24_file)
  df$name                   <- as.character(df$gene_symbol)
  df$Pathway_Categorization <- trimws(as.character(df$rcd_form_canonical))
  df$rcd_form_original      <- trimws(as.character(df$rcd_form))
  df$description            <- NA_character_
  df$otheraliases           <- NA_character_
  df
}, error = function(e) {
  warning("Could not load V027 matrix: ", conditionMessage(e))
  data.frame(
    name = character(0), Pathway_Categorization = character(0),
    rcd_form_original = character(0), stringsAsFactors = FALSE
  )
})

# ── RCDome Decoder (53 operational definitions — the curation truth) ─────────
decoder_file <- "data/RCDome_Decoder_53.csv"
decoder_df <- tryCatch({
  read.csv(decoder_file, stringsAsFactors = FALSE, check.names = FALSE)
}, error = function(e) {
  warning("Could not load RCDome Decoder: ", conditionMessage(e))
  data.frame(rcd_form = character(0), stringsAsFactors = FALSE)
})
message("Decoder loaded: ", nrow(decoder_df), " entities, ", ncol(decoder_df), " fields.")

# ── HGNC gene metadata (name, location, HGNC id, Entrez id) ──────────────────
# Used by the Network gene pop-up for external links + the gene name summary.
hgnc_map <- tryCatch({
  hf <- read.delim("data/hgnc_complete_set.txt", stringsAsFactors = FALSE,
                   quote = "", check.names = FALSE)
  hf[, c("symbol", "name", "location", "hgnc_id", "entrez_id")]
}, error = function(e) {
  data.frame(symbol = character(0), name = character(0), location = character(0),
             hgnc_id = character(0), entrez_id = character(0),
             stringsAsFactors = FALSE)
})

# Universe used by the Fingerprint. This intentionally comes from the canonical
# annotation column, not from the subset that happens to have Exclusive genes.
canonical_pathways <- sort(unique(trimws(genes_df$Pathway_Categorization)))
canonical_pathways <- canonical_pathways[!is.na(canonical_pathways) & nzchar(canonical_pathways)]

if (length(canonical_pathways) != expected_canonical_pathways) {
  warning(
    "Fingerprint expected ", expected_canonical_pathways,
    " RCD-related pathways, but rcd_form_canonical currently contains ",
    length(canonical_pathways), ". All pathways present in that canonical column will be shown."
  )
}

# Unique references (databases + article PMIDs) cited for a set of genes.
split_refs <- function(x) {
  x <- as.character(x)
  x <- x[!is.na(x) & nzchar(trimws(x))]
  if (length(x) == 0) return(character(0))
  unique(trimws(unlist(strsplit(x, ";", fixed = TRUE))))
}

# PMIDs only: keep numeric identifiers, drop sentinels (NOT_RECOVERED, etc.).
split_pmids <- function(x) {
  x <- split_refs(x)
  x[grepl("^[0-9]+$", x)]
}

# ── Fingerprint cache ─────────────────────────────────────────────────────────
fingerprint_cache_valid <- file.exists(fingerprint_cache_file) &&
  !is.na(v24_mtime) &&
  file.info(fingerprint_cache_file)$mtime > v24_mtime

if (fingerprint_cache_valid) {
  cached_fp <- tryCatch(readRDS(fingerprint_cache_file), error = function(e) NULL)
  fingerprint_cache_valid <-
    is.data.frame(cached_fp) &&
    identical(attr(cached_fp, "fingerprint_cache_version"), fingerprint_cache_version) &&
    all(c("pathway", "total", "Exclusive", "Shared", "databases", "references") %in% names(cached_fp)) &&
    setequal(as.character(cached_fp$pathway), canonical_pathways)
}

if (fingerprint_cache_valid) {
  message("Loading fingerprint from cache...")
  fingerprint_df <- cached_fp
} else {
  message("Building fingerprint cache (vectorized)...")

  fingerprint_df <- tryCatch({
    # One row per unique gene × RCD-related pathway association.
    gene_pathway_pairs <- genes_df %>%
      transmute(
        gene = trimws(as.character(name)),
        pathway = trimws(as.character(Pathway_Categorization))
      ) %>%
      filter(!is.na(gene), nzchar(gene), !is.na(pathway), nzchar(pathway)) %>%
      distinct(gene, pathway)

    # A gene is Exclusive when it occurs in exactly one RCD-related pathway;
    # otherwise it is Shared.
    gene_membership <- gene_pathway_pairs %>%
      count(gene, name = "n_pathways")

    fp_counts <- gene_pathway_pairs %>%
      left_join(gene_membership, by = "gene") %>%
      group_by(pathway) %>%
      summarise(
        Exclusive = sum(n_pathways == 1L),
        Shared    = sum(n_pathways > 1L),
        total     = n_distinct(gene),
        .groups   = "drop"
      )

    # Unique databases and article PMIDs per RCD-related pathway.
    refs_per_pathway <- genes_df %>%
      filter(!is.na(Pathway_Categorization), nzchar(trimws(Pathway_Categorization))) %>%
      group_by(pathway = trimws(as.character(Pathway_Categorization))) %>%
      summarise(
        databases  = length(unique(split_refs(source_databases))),
        references = length(unique(c(
          split_pmids(pmid_list),
          split_pmids(epmc_pmids),
          split_pmids(llm_pmids),
          split_pmids(elicit_pmids)
        ))),
        .groups = "drop"
      )

    # Left join against the complete canonical universe so pathways with zero
    # Exclusive or zero Shared genes are never dropped from the initial plot.
    fp <- data.frame(
      pathway = canonical_pathways,
      stringsAsFactors = FALSE
    ) %>%
      left_join(fp_counts, by = "pathway") %>%
      left_join(refs_per_pathway, by = "pathway") %>%
      mutate(
        Exclusive  = tidyr::replace_na(as.integer(Exclusive), 0L),
        Shared     = tidyr::replace_na(as.integer(Shared), 0L),
        total      = tidyr::replace_na(as.integer(total), 0L),
        databases  = tidyr::replace_na(as.integer(databases), 0L),
        references = tidyr::replace_na(as.integer(references), 0L)
      ) %>%
      arrange(desc(total), pathway) %>%
      as.data.frame()

    attr(fp, "fingerprint_cache_version") <- fingerprint_cache_version
    fp
  }, error = function(e) {
    warning("Could not compute Pathway Fingerprint: ", conditionMessage(e))
    fp <- data.frame(
      pathway = canonical_pathways,
      total = integer(length(canonical_pathways)),
      Exclusive = integer(length(canonical_pathways)),
      Shared = integer(length(canonical_pathways)),
      databases = integer(length(canonical_pathways)),
      references = integer(length(canonical_pathways)),
      stringsAsFactors = FALSE
    )
    attr(fp, "fingerprint_cache_version") <- fingerprint_cache_version
    fp
  })

  saveRDS(fingerprint_df, fingerprint_cache_file)
  message("Fingerprint cache saved.")
}
