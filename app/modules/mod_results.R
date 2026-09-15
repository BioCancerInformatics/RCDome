# ─── Module: results — shows verified claims and transparent diagnostics ──────

safe_scalar <- function(x, default = "") {
  if (is.null(x) || length(x) == 0) return(default)
  x <- as.character(x[[1]])
  if (is.na(x) || !nzchar(trimws(x))) return(default)
  trimws(x)
}

article_link <- function(article) {
  pmid <- safe_scalar(article$pmid)
  doi <- safe_scalar(article$doi)
  if (nzchar(pmid)) return(paste0("https://pubmed.ncbi.nlm.nih.gov/", pmid, "/"))
  if (nzchar(doi)) return(paste0("https://doi.org/", doi))
  NULL
}

render_candidate_articles <- function(articles, max_show = 5L) {
  if (is.null(articles) || length(articles) == 0) return(NULL)
  shown <- head(articles, max_show)
  items <- lapply(shown, function(art) {
    href <- article_link(art)
    title <- safe_scalar(art$title, "Untitled article")
    pmid <- safe_scalar(art$pmid)
    year <- safe_scalar(art$pub_year)
    tags$li(style = "margin-bottom: 5px;",
      if (!is.null(href)) tags$a(href = href, target = "_blank", title) else title,
      if (nzchar(year)) paste0(" (", year, ")") else "",
      if (nzchar(pmid)) paste0(" — PMID: ", pmid) else "")
  })
  tags$details(style = "margin-top: 8px;",
    tags$summary(style = "cursor: pointer; color: #0b1020; font-weight: 600;",
      paste0("Retrieved candidate articles (", length(shown), " of ", length(articles), ")")),
    tags$ul(style = "margin-top: 8px; padding-left: 20px;", items))
}

mod_results_ui <- function(id) {
  ns <- NS(id)
  uiOutput(ns("content"))
}

mod_results_server <- function(id, results_reactive, alias_reactive = reactive(NULL)) {
  moduleServer(id, function(input, output, session) {
    output$content <- renderUI({
      results <- results_reactive()
      alias <- alias_reactive()
      if (is.null(results)) return(tags$p("Enter a gene and click Search Evidence.", style = "color: #a8a29e; font-style: italic;"))
      if (length(results) == 0) return(tags$p("No pathway result was generated.", style = "color: #a8a29e;"))

      alias_banner <- if (!is.null(alias) && nzchar(alias$alias) && nzchar(alias$gene)) {
        tags$div(
          style = "background: #fff8e1; border: 1px solid #ffe082; border-left: 4px solid #f9a825; padding: 10px 14px; margin-bottom: 16px; border-radius: 4px;",
          tags$p(style = "margin: 0; font-size: 0.95em;",
            tags$strong(alias$alias), " is an alias of ", tags$strong(alias$gene), ".",
            " Showing evidence for the canonical gene ", tags$strong(alias$gene), ".")
        )
      } else NULL

      panels <- lapply(names(results), function(pw) {
        entry <- results[[pw]]
        diagnostics <- entry$diagnostics %||% list()
        n_articles <- as.integer(diagnostics$articles_retrieved %||% length(entry$articles %||% list()))
        n_claims <- as.integer(diagnostics$claims_extracted %||% 0L)
        n_verified <- as.integer(diagnostics$claims_verified %||% length(entry$claims %||% list()))
        status <- safe_scalar(entry$status)

        header <- tags$h5(safe_scalar(entry$label, pw), style = "margin: 0 0 8px 0; color: #0d6efd;")
        diagnostic_line <- tags$p(style = "font-size: 0.82em; color: #a8a29e; margin: 0 0 8px 0;",
          paste0("PMC: ", n_articles, " article(s) · ", n_claims, " claim(s) · ", n_verified, " verified"))

        if (n_verified == 0) {
          explanation <- switch(status,
            "search_error" = "The Europe PMC request failed.",
            "no_articles" = "No article was retrieved by the gene × pathway query.",
            "articles_without_claims" = "Articles found, but no gene–pathway claim could be extracted.",
            "claims_not_verified" = "Claims were extracted, but none passed verification.",
            "No verified claim was produced.")
          return(tags$div(style = "background: #f5f5f4; border-left: 4px solid #0d6efd; padding: 12px 16px; margin-bottom: 14px;",
            header, diagnostic_line,
            tags$p(explanation, style = "color: #a8a29e; font-style: italic; margin-bottom: 6px;"),
            render_candidate_articles(entry$articles)))
        }

        synthesis <- if (!is.null(entry$synthesis) && nzchar(safe_scalar(entry$synthesis)))
          tags$div(style = "background: #e7f1ff; border: 1px solid #b6d4fe; padding: 10px 12px; margin-bottom: 10px; border-radius: 4px;",
            tags$p(tags$strong("Evidence synthesis: "), safe_scalar(entry$synthesis), style = "margin: 0; font-size: 0.92em;")) else NULL

        claims_html <- lapply(entry$claims, function(cl) {
          pmid <- safe_scalar(cl$pmid)
          doi  <- safe_scalar(cl$doi)
          pmid_href <- if (nzchar(pmid)) paste0("https://pubmed.ncbi.nlm.nih.gov/", pmid, "/") else NULL
          doi_href  <- if (nzchar(doi))  paste0("https://doi.org/", doi) else NULL
          ref_links <- tagList()
          if (!is.null(pmid_href)) ref_links <- tagList(ref_links, " · ", tags$a(href = pmid_href, target = "_blank", paste0("PMID: ", pmid)))
          if (!is.null(doi_href))  ref_links <- tagList(ref_links, " · ", tags$a(href = doi_href,  target = "_blank", paste0("DOI: ", doi)))
          tags$div(style = "background: white; border: 1px solid #e7e5e4; padding: 10px 12px; margin: 6px 0; border-radius: 4px; font-size: 0.88em;",
            tags$p(tags$strong(safe_scalar(cl$claim, "Verified claim")), style = "margin-bottom: 5px;"),
            tags$p(safe_scalar(cl$supporting_sentence, safe_scalar(cl$sentence)), style = "color: #4B5563; font-style: italic; margin-bottom: 5px;"),
            tags$p(style = "color: #a8a29e; font-size: 0.85em; margin: 0;", safe_scalar(cl$title, "Article"), ref_links))
        })

        tags$div(style = "background: #f5f5f4; border-left: 4px solid #0d6efd; padding: 12px 16px; margin-bottom: 14px;",
          header, diagnostic_line, synthesis, claims_html)
      })
      tagList(alias_banner, panels)
    })
  })
}
