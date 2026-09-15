# ─── Europe PMC API — broad retrieval, ranking and disease-aware fallback ─────

escape_epmc_term <- function(x) {
  x <- trimws(as.character(x %||% ""))
  x <- gsub("\\\\", "\\\\\\\\", x)
  gsub('"', '\\"', x, fixed = TRUE)
}

get_pathway_terms <- function(pathway_name) {
  key <- tolower(trimws(pathway_name))
  aliases <- list(
    "apoptosis" = c("apoptosis", "apoptotic", "programmed cell death"),
    "necroptosis" = c("necroptosis", "necroptotic"),
    "pyroptosis" = c("pyroptosis", "pyroptotic"),
    "ferroptosis" = c("ferroptosis", "ferroptotic"),
    "autophagy" = c("autophagy", "autophagic cell death", "autophagy-dependent cell death"),
    "necrosis" = c("necrosis", "necrotic cell death"),
    "anoikis" = c("anoikis", "detachment-induced cell death"),
    "cuproptosis" = c("cuproptosis", "copper-dependent cell death"),
    "netosis" = c("NETosis", "neutrophil extracellular trap cell death"),
    "entosis" = c("entosis", "cell-in-cell death"),
    "parthanatos" = c("parthanatos", "PARP1-dependent cell death"),
    "disulfidptosis" = c("disulfidptosis", "disulfide stress-induced cell death"),
    "oxeiptosis" = c("oxeiptosis"),
    "paraptosis" = c("paraptosis", "paraptotic"),
    "alkaliptosis" = c("alkaliptosis"),
    "lysosome-dependent cell death" = c("lysosome-dependent cell death", "lysosomal cell death"),
    "mitoptosis" = c("mitoptosis"),
    "autosis" = c("autosis"),
    "erebosis" = c("erebosis"),
    "methuosis" = c("methuosis"),
    "mitotic catastrophe" = c("mitotic catastrophe", "mitotic cell death"),
    "mitochondrial permeability transition" = c("mitochondrial permeability transition", "MPT-driven necrosis"),
    "immunogenic cell death" = c("immunogenic cell death", "ICD"),
    "efferocytosis" = c("efferocytosis", "apoptotic cell clearance"),
    "cellular senescence" = c("cellular senescence", "senescent cell")
  )
  unique(c(pathway_name, aliases[[key]] %||% character(0)))
}

get_disease_terms <- function(disease = "All") {
  key <- tolower(trimws(as.character(disease %||% "All")))
  if (key == "all") {
    # ponytail: "All" = every term from disease_terms.tsv, not unfiltered
    tsv_path <- "data/disease_terms.tsv"
    if (file.exists(tsv_path)) {
      tsv <- tryCatch(
        read.delim(tsv_path, sep = "\t", stringsAsFactors = FALSE),
        error = function(e) NULL
      )
      if (!is.null(tsv) && "term" %in% names(tsv)) {
        terms <- trimws(tsv$term)
        return(unique(terms[nzchar(terms)]))
      }
    }
    return(character(0))
  }

  # Hardcoded curated terms
  hardcoded <- switch(key,
    "cancer" = c("cancer", "tumor", "tumour", "neoplasm", "malignancy", "leukemia", "leukaemia", "lymphoma", "carcinoma", "sarcoma"),
    "hematological diseases" = c("leukemia", "leukaemia", "lymphoma", "myeloma", "myelodysplastic", "AML", "ALL", "CML", "CLL", "anemia"),
    "neurodegenerative diseases" = c("Alzheimer", "Parkinson", "Huntington", "ALS", "multiple sclerosis", "neurodegeneration", "dementia"),
    "cardiovascular diseases" = c("myocardial infarction", "atherosclerosis", "heart failure", "cardiomyopathy", "hypertension"),
    "cerebrovascular diseases" = c("stroke", "brain ischemia", "cerebral infarction", "cerebral hemorrhage"),
    "infectious diseases" = c("infection", "sepsis", "tuberculosis", "COVID", "influenza", "hepatitis", "HIV", "malaria"),
    "autoimmune diseases" = c("autoimmune", "lupus", "rheumatoid arthritis", "type 1 diabetes", "multiple sclerosis", "Sjogren"),
    "chronic inflammatory diseases" = c("inflammatory", "Crohn", "ulcerative colitis", "psoriasis", "gout", "osteoarthritis"),
    "kidney diseases" = c("kidney", "renal", "nephropathy", "glomerulonephritis", "acute kidney injury"),
    "liver diseases" = c("liver", "hepatic", "hepatitis", "cirrhosis", "steatohepatitis", "MASLD"),
    "metabolic diseases" = c("diabetes", "obesity", "metabolic syndrome", "insulin resistance"),
    "respiratory diseases" = c("respiratory", "COPD", "asthma", "pulmonary fibrosis", "pneumonia", "ARDS"),
    "ischemia-reperfusion injury" = c("ischemia-reperfusion", "reperfusion injury", "transplant"),
    "muscle diseases" = c("myopathy", "muscular dystrophy", "sarcopenia", "rhabdomyolysis"),
    "ocular diseases" = c("retinal", "glaucoma", "macular degeneration", "retinopathy", "optic nerve"),
    "developmental diseases" = c("congenital", "malformation", "developmental disorder", "neural tube defect"),
    character(0)
  )

  # ponytail: load tsv per call, cache when performance matters
  tsv_terms <- character(0)
  tsv_path <- "data/disease_terms.tsv"
  if (file.exists(tsv_path)) {
    tsv <- tryCatch(
      read.delim(tsv_path, sep = "\t", stringsAsFactors = FALSE),
      error = function(e) NULL
    )
    if (!is.null(tsv) && "group" %in% names(tsv) && "term" %in% names(tsv)) {
      tsv$group <- tolower(trimws(tsv$group))
      tsv_terms <- tsv$term[tsv$group == key]
      tsv_terms <- trimws(tsv_terms)
      tsv_terms <- tsv_terms[nzchar(tsv_terms)]
    }
  }

  terms <- unique(c(hardcoded, tsv_terms))
  terms[nzchar(terms)]
}

make_title_abs_group <- function(terms) {
  terms <- unique(trimws(as.character(terms)))
  terms <- terms[nzchar(terms)]
  if (length(terms) == 0) return(NULL)
  paste0("(", paste(sprintf('TITLE_ABS:"%s"', sapply(terms, escape_epmc_term)), collapse = " OR "), ")")
}

# Human-only post-filter: an article is dropped only when it is clearly an
# animal study (animal-model terms present AND no human terms). Comparative
# human+animal studies and ambiguous studies are kept.
ANIMAL_PATTERN <- "\\b(mouse|mice|murine|rats?|zebrafish|drosophila|caenorhabditis|c\\. elegans|xenopus|rabbits?|porcine|bovine|canine|equine|swine|macaque|monkey|rodents?|animal models?)\\b"
HUMAN_PATTERN <- "\\b(humans?|patients?|homo sapiens|subjects?)\\b"

is_human_article <- function(article) {
  text <- tolower(paste(article$title %||% "", article$abstract %||% ""))
  has_animal <- grepl(ANIMAL_PATTERN, text, perl = TRUE, ignore.case = TRUE)
  has_human  <- grepl(HUMAN_PATTERN, text, perl = TRUE, ignore.case = TRUE)
  !(has_animal && !has_human)
}

build_query <- function(gene, pathway_name, disease = "All") {
  parts <- Filter(Negate(is.null), list(
    make_title_abs_group(gene),
    make_title_abs_group(get_pathway_terms(pathway_name)),
    make_title_abs_group(get_disease_terms(disease))
  ))
  paste(parts, collapse = " AND ")
}

build_query_variants <- function(gene, pathway_name, disease = "All") {
  gene_group <- make_title_abs_group(gene)
  pathway_group <- make_title_abs_group(get_pathway_terms(pathway_name))
  disease_group <- make_title_abs_group(get_disease_terms(disease))
  c(strict = paste(Filter(Negate(is.null), list(gene_group, pathway_group, disease_group)), collapse = " AND "))
}

search_europe_pmc <- function(query, max_results = 100) {
  max_results <- max(1L, min(as.integer(max_results), 1000L))
  resp <- httr::GET("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
    query = list(query = query, format = "json", resultType = "core", pageSize = max_results),
    httr::timeout(30))
  status <- httr::status_code(resp)
  if (status != 200) stop(sprintf("Europe PMC HTTP %s", status), call. = FALSE)
  parsed <- jsonlite::fromJSON(httr::content(resp, "text", encoding = "UTF-8"), simplifyDataFrame = TRUE)
  results <- parsed$resultList$result
  if (is.null(results) || length(results) == 0) return(list())
  if (!is.data.frame(results)) results <- as.data.frame(results, stringsAsFactors = FALSE)
  if (nrow(results) == 0) return(list())
  lapply(seq_len(nrow(results)), function(i) {
    r <- results[i, , drop = FALSE]
    list(pmid = as.character(r$pmid[1] %||% NA_character_),
         doi = as.character(r$doi[1] %||% NA_character_),
         title = as.character(r$title[1] %||% ""),
         abstract = as.character(r$abstractText[1] %||% ""),
         source = as.character(r$source[1] %||% "UNKNOWN"),
         pub_year = as.character(r$pubYear[1] %||% NA_character_))
  })
}

contains_term <- function(text, terms) {
  text <- tolower(as.character(text %||% ""))
  any(vapply(terms, function(term) grepl(tolower(term), text, fixed = TRUE), logical(1)))
}

article_relevance_score <- function(article, gene, pathway_name) {
  title <- as.character(article$title %||% "")
  abstract <- as.character(article$abstract %||% "")
  pathway_terms <- get_pathway_terms(pathway_name)
  score <- 0
  if (contains_term(title, gene)) score <- score + 12
  if (contains_term(abstract, gene)) score <- score + 4
  if (contains_term(title, pathway_terms)) score <- score + 8
  if (contains_term(abstract, pathway_terms)) score <- score + 5
  year <- suppressWarnings(as.numeric(article$pub_year))
  if (is.finite(year)) score <- score + max(0, year - 2000) / 100
  score
}

search_europe_pmc_tiered <- function(gene, pathway_name, disease = "All",
                                     max_results_per_query = 100, max_total = 40) {
  queries <- build_query_variants(gene, pathway_name, disease)
  collected <- list()
  for (q in queries) {
    batch <- tryCatch(search_europe_pmc(q, max_results = max_results_per_query), error = function(e) list())
    if (length(batch) > 0) collected <- c(collected, batch)
  }
  if (length(collected) == 0) return(list())
  keys <- vapply(collected, function(x) {
    cand <- c(x$pmid, x$doi, tolower(x$title %||% ""))
    cand <- cand[!is.na(cand) & nzchar(cand)]
    if (length(cand) == 0) paste0("row_", sample.int(1e9, 1)) else cand[1]
  }, character(1))
  collected <- collected[!duplicated(keys)]
  # keep human studies only (drop animal-exclusive articles)
  collected <- Filter(is_human_article, collected)
  if (length(collected) == 0) return(list())
  scores <- vapply(collected, article_relevance_score, numeric(1), gene = gene, pathway_name = pathway_name)
  collected <- collected[order(scores, decreasing = TRUE)]
  head(collected, max_total)
}
