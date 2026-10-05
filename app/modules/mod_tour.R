# ─── Module: tour (Reader Mode — first-visit guided tour) ────────────────────
# A dark modal slideshow that walks a new reader through the app. Each step
# auto-navigates to the relevant tab. Shown once (localStorage flag); replay
# from the About page clears the flag and reloads.

mod_tour_ui <- function(id) {
  NULL
}

mod_tour_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    ns <- session$ns

    steps <- list(
      list(title = "Welcome", icon = "\U0001F9EC", tab = NULL,
           text = "RCDome is a multi-database human gene atlas of regulated cell death, built so every association is traceable to its source. This two-minute tour shows how to read it."),
      list(title = "The dome", icon = "\U0001F52E", tab = "Home",
           text = "The Home dome shows the 53 RCD-related entities, colored by ontological level, from <span style='color:#E0C04B; font-weight:700;'>gold L1 modalities</span> to <span style='color:#FF6D00; font-weight:700;'>orange L5 umbrella terms</span>. Click any node for its detail."),
      list(title = "Operational Definitions", icon = "\U0001F4D6", tab = "Operational Definitions",
           text = "The Operational Definitions module holds the 53 canonicalized definitions, each anchored to its reference. This controlled vocabulary is used consistently across the atlas."),
      list(title = "A gene's evidence", icon = "\U0001F517", tab = "Gene Catalog",
           text = "In the Gene Catalog, every row is a gene-RCD pair. Click the \u29C8 button to open the Evidence Trail: the verbatim claim, the PMID, and the three classifier verdicts."),
      list(title = "The Network", icon = "\U0001F578", tab = "Network",
           text = "The Network shows the death core and its regulators. Click an edge to open the same Evidence Trail for that gene-RCD pair."),
      list(title = "The knowledge frontier", icon = "\u2696", tab = "Discrepancy Radar",
           text = "The Discrepancy Radar shows where DeepSeek, Elicit, and Consensus disagree: 7,892 conflicts, color-coded, with the GPT arbitration and the human adjudication."),
      list(title = "A reference", icon = "\U0001F4C4", tab = NULL,
           text = "Every claim resolves to a real paper. Click a PMID or DOI to read the source; these links were benchmarked at 100% accuracy."),
      list(title = "You're ready", icon = "\u2728", tab = NULL,
           text = "Explore freely. Every column, filter, and control carries a hover explanation, and every value traces back to its source.")
    )
    n_steps <- length(steps)
    step_rv <- reactiveVal(0)

    show_step <- function(i) {
      s <- steps[[i]]
      if (!is.null(s$tab) && nzchar(s$tab)) {
        shinyjs::runjs(sprintf("$('a[data-value=\"%s\"]').tab('show');", s$tab))
      }
      showModal(modalDialog(
        title = NULL, footer = NULL, easyClose = TRUE, size = "m",
        tags$div(style = "background:#0b1020; color:#e7e5e4; border-radius:12px; padding:24px 26px;",
          tags$div(style = "display:flex; justify-content:space-between; align-items:center;",
            tags$span(paste0("Step ", i, " of ", n_steps), style = "color:#94a3b8; font-size:12px; letter-spacing:1px;"),
            tags$span(s$icon, style = "font-size:28px;")
          ),
          tags$h3(s$title, style = "color:#fff; margin:14px 0 6px; font-size:20px; font-weight:700;"),
          tags$p(HTML(s$text), style = "color:#d6d3d1; font-size:14px; line-height:1.6;"),
          tags$div(style = "margin-top:20px; display:flex; justify-content:space-between; align-items:center;",
            if (i > 1) actionButton(ns("back"), "Back",
              style = "background:transparent; color:#94a3b8; border:1px solid #334155; border-radius:8px; padding:6px 16px; font-size:13px;") else tags$span(""),
            tags$div(style = "display:flex; gap:10px;",
              actionButton(ns("skip"), "Skip tour",
                style = "background:transparent; color:#94a3b8; border:1px solid #334155; border-radius:8px; padding:6px 16px; font-size:13px;"),
              if (i < n_steps) actionButton(ns("tour_next"), "Next",
                style = "background:#FF9800; color:#0b1020; border:none; border-radius:8px; padding:6px 18px; font-size:13px; font-weight:700;")
              else actionButton(ns("done"), "Done",
                style = "background:#FF9800; color:#0b1020; border:none; border-radius:8px; padding:6px 18px; font-size:13px; font-weight:700;")
            )
          )
        )
      ))
    }

    observeEvent(input$first_visit, {
      shinyjs::runjs("localStorage.setItem('rcdome_tour_seen','1'); $('a[data-value=\"Home\"]').tab('show');")
      step_rv(1)
      show_step(1)
    })
    observeEvent(input$tour_next, {
      i <- step_rv()
      if (i > 0 && i < n_steps) { step_rv(i + 1); show_step(i + 1) }
    })
    observeEvent(input$back, {
      i <- step_rv()
      if (i > 1) { step_rv(i - 1); show_step(i - 1) }
    })
    observeEvent(input$skip, { removeModal(); step_rv(0) })
    observeEvent(input$done, {
      removeModal()
      step_rv(0)
      shinyjs::runjs("$('a[data-value=\"Home\"]').tab('show');")
    })

    # First-visit trigger, fired once the session is fully ready (so the
    # namespaced input is registered before the JS sets it).
    session$onFlushed(function() {
      shinyjs::runjs(sprintf(
        "if (!localStorage.getItem('rcdome_tour_seen')) { Shiny.setInputValue('%s', Math.random(), {priority:'event'}); }",
        ns("first_visit")
      ))
    }, once = TRUE)

  })
}
