# ─── Module: live_search — robust retrieval, extraction and diagnostics ───────

mod_live_search_ui <- function(id) {
  ns <- NS(id)
  conditionalPanel(
    condition = paste0("output['", ns("running"), "'] == true"),
    tags$div(class = "spinner-overlay",
      tags$div(class = "spinner-border text-primary", role = "status"),
      tags$p("Searching Europe PMC and extracting evidence with DeepSeek..."))
  )
}

clean_text_value <- function(x) {
  if (is.null(x) || length(x) == 0) return("")
  x <- as.character(x[[1]])
  if (is.na(x)) return("")
  trimws(x)
}

claim_field <- function(claim, names_to_try) {
  for (nm in names_to_try) {
    value <- NULL
    if (is.data.frame(claim) && nm %in% names(claim)) value <- claim[[nm]][1]
    if (is.list(claim) && !is.null(claim[[nm]])) value <- claim[[nm]]
    value <- clean_text_value(value)
    if (nzchar(value)) return(value)
  }
  ""
}

normalize_claim_response <- function(extracted) {
  if (is.null(extracted) || is.null(extracted$claims)) return(list())
  x <- extracted$claims
  if (is.data.frame(x)) return(lapply(seq_len(nrow(x)), function(i) x[i, , drop = FALSE]))
  if (is.list(x)) {
    if (!is.null(names(x)) && "claim" %in% names(x)) return(list(x))
    return(x)
  }
  list()
}

split_abstract_sentences <- function(text) {
  text <- gsub("\\s+", " ", clean_text_value(text))
  if (!nzchar(text)) return(character(0))
  out <- unlist(strsplit(text, "(?<=[.!?])\\s+", perl = TRUE))
  trimws(out[nzchar(trimws(out))])
}

text_has_any <- function(text, terms) {
  text <- tolower(clean_text_value(text))
  any(vapply(terms, function(term) grepl(tolower(term), text, fixed = TRUE), logical(1)))
}

build_literal_candidate <- function(article, gene, pathway_name) {
  sentences <- split_abstract_sentences(article$abstract)
  if (length(sentences) == 0) return(list())
  pathway_terms <- if (exists("get_pathway_terms", mode = "function")) get_pathway_terms(pathway_name) else pathway_name
  for (s in sentences) {
    if (text_has_any(s, gene) && text_has_any(s, pathway_terms)) {
      return(list(list(claim = paste0("The article reports an association between ", gene, " and ", pathway_name, "."),
        supporting_sentence = s, evidence_type = "literal_text_candidate", relation_type = "mechanistic")))
    }
  }
  if (length(sentences) >= 2) {
    for (i in seq_len(length(sentences) - 1)) {
      window <- paste(sentences[i], sentences[i + 1])
      if (text_has_any(window, gene) && text_has_any(window, pathway_terms)) {
        return(list(list(claim = paste0("The article reports an association between ", gene, " and ", pathway_name, "."),
          supporting_sentence = window, evidence_type = "literal_text_candidate", relation_type = "mechanistic")))
      }
    }
  }
  list()
}

mod_live_search_server <- function(id, gene_reactive, pathways_reactive, api_key_reactive,
                                    disease_reactive = reactive("All"), article_limit = reactive(5L),
                                    trigger_reactive = reactive(0)) {
  moduleServer(id, function(input, output, session) {

    search_running <- reactiveVal(FALSE)
    output$running <- reactive(search_running())
    outputOptions(output, "running", suspendWhenHidden = FALSE)
    results <- reactiveVal(NULL)

    observeEvent(trigger_reactive(), {
      gene <- trimws(clean_text_value(gene_reactive()))
      pw_names <- pathways_reactive()
      if (!nzchar(gene)) { results(NULL); showNotification("Enter a gene before searching.", type = "warning"); return() }
      if (is.null(pw_names) || length(pw_names) == 0) { results(NULL); showNotification("Gene has no categorized pathways.", type = "warning"); return() }
      key <- clean_text_value(api_key_reactive())
      if (!nzchar(key)) { results(NULL); showNotification("DeepSeek API key not configured.", type = "warning", duration = 6); return() }

      search_running(TRUE); results(NULL); on.exit(search_running(FALSE), add = TRUE)
      all_results <- list()

      withProgress(message = paste0("Searching literature for ", gene, "..."), value = 0, {
        for (i in seq_along(pw_names)) {
          pw <- pw_names[i]
          setProgress(value = (i - 1) / length(pw_names), detail = paste0("Pathway: ", pw))

          search_error <- NULL
          max_per_pathway <- as.integer(article_limit())
          articles <- tryCatch(
            search_europe_pmc_tiered(gene = gene, pathway_name = pw, disease = disease_reactive(),
                                     max_results_per_query = 100, max_total = max_per_pathway),
            error = function(e) { search_error <<- conditionMessage(e); showNotification(paste0("Europe PMC error: ", search_error), type = "error", duration = 10); list() })

          if (length(articles) == 0) {
            all_results[[pw]] <- list(label = pw, claims = list(), synthesis = NULL, articles = list(), empty = TRUE,
              status = if (is.null(search_error)) "no_articles" else "search_error",
              diagnostics = list(articles_retrieved = 0L, claims_extracted = 0L, claims_verified = 0L, search_error = search_error))
            incProgress(1 / length(pw_names)); next
          }

          all_claims <- list(); extraction_errors <- 0L
          for (art in articles) {
            if (length(all_claims) >= max_per_pathway) break
            Sys.sleep(0.15)
            extracted <- tryCatch(extract_claims(art, gene, pw, key),
              error = function(e) { extraction_errors <<- extraction_errors + 1L; list(claims = list()) })
            claims_list <- normalize_claim_response(extracted)
            if (length(claims_list) == 0) claims_list <- build_literal_candidate(art, gene, pw)
            if (length(claims_list) > 0) {
              for (cl in claims_list) {
                if (length(all_claims) >= max_per_pathway) break
                claim_text <- claim_field(cl, c("claim", "statement", "finding"))
                support_text <- claim_field(cl, c("supporting_sentence", "supporting_text", "evidence", "sentence", "quote", "passage"))
                evidence_type <- claim_field(cl, c("evidence_type", "type"))
                relation_type <- claim_field(cl, c("relation_type", "relation"))
                if (!nzchar(claim_text) || !nzchar(support_text)) next
                all_claims[[length(all_claims) + 1L]] <- list(
                  claim = claim_text, supporting_sentence = support_text,
                  evidence_type = if (nzchar(evidence_type)) evidence_type else "unspecified",
                  relation_type = if (nzchar(relation_type)) relation_type else "unspecified",
                  pmid = art$pmid, pmcid = art$pmcid, doi = art$doi, title = art$title, pub_year = art$pub_year)
              }
            }
          }

          verified <- list(); verification_errors <- 0L
          for (cl in all_claims) {
            Sys.sleep(0.1)
            verdict <- tryCatch(verify_claim(cl$claim, cl$supporting_sentence, key),
              error = function(e) { verification_errors <<- verification_errors + 1L; list(verdict = "ERROR") })
            verdict_value <- toupper(trimws(clean_text_value(verdict$verdict)))
            if (identical(verdict_value, "SUPPORTED")) {
              cl$verification_reason <- clean_text_value(verdict$reason)
              verified[[length(verified) + 1L]] <- cl
            }
          }

          synthesis <- NULL
          if (length(verified) > 0) {
            Sys.sleep(0.15)
            synth <- tryCatch(synthesize_pathway(gene, pw, verified, key, disease = disease_reactive()),
              error = function(e) NULL)
            if (!is.null(synth)) { synthesis <- clean_text_value(synth$summary %||% synth$synthesis); if (!nzchar(synthesis)) synthesis <- NULL }
          }

          status <- if (length(verified) > 0) "verified" else if (length(all_claims) > 0) "claims_not_verified" else "articles_without_claims"

          all_results[[pw]] <- list(label = pw, claims = verified, synthesis = synthesis, articles = articles,
            empty = length(verified) == 0, status = status,
            diagnostics = list(articles_retrieved = length(articles), claims_extracted = length(all_claims),
              claims_verified = length(verified), extraction_errors = extraction_errors,
              verification_errors = verification_errors, search_error = search_error))

          if (length(verified) == 0) showNotification(paste0(pw, ": ", length(articles), " article(s), ", length(all_claims), " claim candidate(s), 0 verified."), type = "warning", duration = 8)
          if (length(articles) > 0 && length(verified) > 0 && exists("download_papers_for_gene", mode = "function")) try(download_papers_for_gene(gene, pw, articles), silent = TRUE)
          incProgress(1 / length(pw_names))
        }
      })
      results(all_results); showNotification("Search complete!", type = "message")
    }, ignoreNULL = TRUE, ignoreInit = TRUE)

    results
  })
}
