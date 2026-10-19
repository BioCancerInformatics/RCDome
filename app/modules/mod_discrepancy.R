# ─── Module: discrepancy (Discrepancy Radar) ────────────────────────────────
# Phase 1: maps the 7,905 classifier-disagreement hotspots (GPT-arbitrated),
# faceted by axis (role / direction / mechanistic), with concordance dots,
# the GPT arbitration verdict, and a PENDING human-adjudication slot.
# Phase 2 (after curator verdicts) will fill the human verdict + final value.

RCD_DISC_DIR <- "data/discrepancy"

mod_discrepancy_ui <- function(id) {
  ns <- NS(id)
  tagList(
    div(style = "max-width:1200px; margin:0 auto; padding:20px;",
      tags$h2("Discrepancy Radar", style = "margin:0 0 10px; color:#1c1917; font-weight:700; font-size:24px;"),
      p("The knowledge frontier: Where the three classifiers disagree, RCDome shows the conflict instead of hiding it. Each row carries the divergent verdicts, the GPT arbitration, the two curator votes, and the evidence-first verdict that resolved it from the verbatim.",
        style = "color:#78716c; font-size:14px;"),
      uiOutput(ns("summary_bar")),
      tags$div(style = "margin:12px 0 6px;",
        radioButtons(ns("facet"), "Conflict axis", inline = TRUE,
          choices = c("All", "Direction", "Role", "Mechanistic"),
          selected = "All"),
        selectizeInput(ns("f_gene"), "Gene", choices = NULL, multiple = TRUE, width = "240px",
                       options = list(placeholder = "All genes")),
        selectizeInput(ns("f_rcd"), "RCD entity", choices = NULL, multiple = TRUE, width = "240px",
                       options = list(placeholder = "All entities")),
        actionButton(ns("reset_filters"), "Reset filters",
                   style = "margin-left:10px; height:32px; padding:0 16px; font-size:12.5px; font-weight:600; background:#FF9800; color:#0b1020; border:none; border-radius:8px; cursor:pointer; box-shadow:0 2px 8px rgba(255,152,0,0.35);")
      ),
      uiOutput(ns("legend")),
      DTOutput(ns("table"))
    )
  )
}

mod_discrepancy_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    ns <- session$ns

    # ── Adjudicated row set (precomputed RDS: 7,905 Track + Delta rows) ──
    disc_df <- reactive({
      f <- "data/adjudication/disc_df.rds"
      if (!file.exists(f)) return(data.frame())
      tryCatch(readRDS(f), error = function(e) data.frame())
    })

    # ── Shared color palettes (same as the Evidence Trail drawer) ──────
    role_col <- c(EXECUTOR = "#E53935", REGULATOR = "#3949AB", MARKER = "#00897B", UNCERTAIN = "#9E9E9E")
    dir_col  <- c(PROMOTES = "#2E7D32", PROTECTS = "#1565C0", UNCLEAR = "#757575",
                  ASSOCIATED = "#8E24AA", BIDIRECTIONAL = "#8E24AA")
    mech_col <- c(YES = "#2E7D32", NO = "#9E9E9E", OUT_OF_CONTEXT = "#F59E0B")
    gpt_col  <- c(DEEPSEEK = "#3949AB", CONSENSUS = "#00897B", UNCLEAR = "#757575",
                  OUT_OF_CONTEXT = "#F59E0B", NEITHER = "#E53935", ERROR = "#57534E")

    badge <- function(txt, col) {
      txt <- trimws(as.character(txt))
      if (length(txt) == 0 || is.na(txt) || !nzchar(txt)) {
        return("<span style='color:#a8a29e;'>\u2014</span>")
      }
      if (is.null(col)) col <- "#9E9E9E"
      sprintf("<span style='display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:600;color:#fff;background:%s;margin-right:3px;'>%s</span>",
              col, txt)
    }

    axis_col <- function(axis, txt) {
      txt <- trimws(as.character(txt))
      if (length(txt) == 0 || is.na(txt) || !nzchar(txt)) return("#9E9E9E")
      if (axis == "role") {
        if (txt %in% names(role_col)) return(role_col[[txt]]) else return("#9E9E9E")
      } else if (axis == "direction") {
        if (txt %in% names(dir_col)) return(dir_col[[txt]]) else return("#757575")
      } else if (axis == "mechanistic") {
        if (txt %in% names(mech_col)) return(mech_col[[txt]]) else return("#9E9E9E")
      } else "#9E9E9E"
    }

    dots <- function(axis, ds, cs, el) {
      if (axis == "direction") {
        el_shared <- el %in% c("PROMOTES", "PROTECTS", "UNCLEAR")
        vals <- c(ds, cs)
        if (el_shared) vals <- c(vals, el)
        if (length(vals) == 3) {
          u <- unique(vals)
          if (length(u) == 1)      return(list(filled = 3, total = 3, col = "#2E7D32"))
          else if (length(u) == 2) return(list(filled = 2, total = 3, col = "#F59E0B"))
          else                     return(list(filled = 1, total = 3, col = "#E53935"))
        }
      }
      if (!is.na(ds) && !is.na(cs) && ds == cs) return(list(filled = 2, total = 2, col = "#2E7D32"))
      list(filled = 1, total = 2, col = "#E53935")
    }

    dot_span_f <- function(col) {
      paste0("<span style='display:inline-block;width:11px;height:11px;border-radius:50%;background:", col, ";margin-right:3px;vertical-align:middle;'></span>")
    }
    dot_span_e <- function(col) {
      paste0("<span style='display:inline-block;width:11px;height:11px;border-radius:50%;border:2px solid ", col, ";margin-right:3px;vertical-align:middle;'></span>")
    }
    dot_spans <- function(filled, total, col) {
      paste(c(rep(dot_span_f(col), filled), rep(dot_span_e(col), total - filled)), collapse = "")
    }

    # ── Populate the gene + entity filter dropdowns ────────────────────
    observe({
      df <- disc_df()
      if (nrow(df) == 0) return()
      updateSelectizeInput(session, "f_gene", choices = sort(unique(df$gene_symbol)), server = TRUE)
      updateSelectizeInput(session, "f_rcd", choices = sort(unique(df$rcd_form_canonical)), server = TRUE)
    })

    # ── Row indices for the current view (union dedup for All) ──────────
    view_idx <- reactive({
      df <- disc_df()
      if (nrow(df) == 0) return(integer(0))
      idx <- seq_len(nrow(df))
      if (identical(tolower(input$facet), "all")) {
        # All = union of gene–RCD pairs with ≥1 conflict. A pair flagged on
        # several axes appears once (deduplicated), so totals are not inflated.
        key <- paste(df$gene_symbol, df$rcd_form_canonical, sep = "\u001f")
        idx <- idx[!duplicated(key)]
      } else {
        idx <- idx[df$label == tolower(input$facet)]
      }
      if (!is.null(input$f_gene) && length(input$f_gene) > 0) idx <- idx[df$gene_symbol[idx] %in% input$f_gene]
      if (!is.null(input$f_rcd) && length(input$f_rcd) > 0) idx <- idx[df$rcd_form_canonical[idx] %in% input$f_rcd]
      idx
    })

    # ── Reset filters → restore All as the default conflict axis ───────
    observeEvent(input$reset_filters, {
      updateRadioButtons(session, "facet", selected = "All")
      updateSelectizeInput(session, "f_gene", selected = character(0))
      updateSelectizeInput(session, "f_rcd", selected = character(0))
    })

    # ── Summary bar ─────────────────────────────────────────────────────
    output$summary_bar <- renderUI({
      idx <- view_idx()
      if (length(idx) == 0) return(NULL)
      # Per-axis conflict counts from the gene/entity-filtered (pre-dedup) set.
      base <- disc_df()
      if (!is.null(input$f_gene) && length(input$f_gene) > 0) base <- base[base$gene_symbol %in% input$f_gene, , drop = FALSE]
      if (!is.null(input$f_rcd) && length(input$f_rcd) > 0) base <- base[base$rcd_form_canonical %in% input$f_rcd, , drop = FALSE]
      cnt <- table(base$label)
      tot <- length(idx)
      parts <- vapply(c("direction", "role", "mechanistic"), function(l) {
        n <- if (l %in% names(cnt)) cnt[[l]] else 0
        lab <- switch(l, direction = "Direction", role = "Role", mechanistic = "Mechanistic")
        sprintf("<span style='background:#0b1020;color:#fff;border-radius:999px;padding:3px 12px;font-size:12px;font-weight:600;margin-right:6px;'>%s %d</span>", lab, n)
      }, character(1))
      tags$div(style = "margin:10px 0 0;",
        HTML(paste0(parts, collapse = "")),
        tags$span(sprintf("Total %d · evidence-first adjudicated", tot),
                  style = "color:#78716c; font-size:12px; margin-left:4px;")
      )
    })

    # ── Legend ──────────────────────────────────────────────────────────
    output$legend <- renderUI({
      tags$div(style = "margin:4px 0 10px; font-size:12px; color:#57534e;",
        tags$strong("Concordance with the resolution: "),
        HTML(paste0(
          dot_spans(4, 6, "#2E7D32"), " 4–6 of 6 \u00b7 ",
          dot_spans(2, 6, "#F59E0B"), " 2–3 of 6 \u00b7 ",
          dot_spans(1, 6, "#E53935"), " 0–1 of 6"
        )),
        tags$span("  \u00b7  GPT: ", HTML(
          paste0(badge("DEEPSEEK", gpt_col["DEEPSEEK"]), badge("CONSENSUS", gpt_col["CONSENSUS"]),
                 badge("UNCLEAR", gpt_col["UNCLEAR"]), badge("OUT_OF_CONTEXT", gpt_col["OUT_OF_CONTEXT"]),
                 badge("NEITHER", gpt_col["NEITHER"]))
        )),
        tags$span("  \u00b7  ", HTML(
          "<span style='display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:700;color:#fff;background:#0b1020;box-shadow:0 0 0 1.5px #0b1020;'>Evidence-first</span>"
        ))
      )
    })

    # ── Verdict-strip table ─────────────────────────────────────────────
    # Static column header (built once).
    table_header <- htmltools::withTags(table(
      class = "display",
      thead(
        tr(
          th("Pair", title = "Gene × RCD entity — click for the Evidence Trail"),
          th("Axis", title = "Conflict axes for this pair — filled = the axis shown in this row, outlined = additional conflicts on other axes"),
          th("DeepSeek", title = "DeepSeek chain-of-thought classifier verdict (Phases 2A–2F)"),
          th("Elicit", title = "Elicit Phase 3 systematic-review extraction"),
          th("Consensus", title = "Consensus evidence-channel classification (neutral query, Phase 2G)"),
          th("Compiled", title = "Source-compiled role/direction from the extraction channels (A–D), before the independent validations"),
          th("GPT", title = "GPT-4o arbitration vote on the conflict"),
          th("Curator 1", title = "First human curator vote"),
          th("Curator 2", title = "Second human curator vote"),
          th("Concordance", title = "How many of the six voters (DeepSeek, Elicit, Consensus, GPT, Curator 1, Curator 2) agree with the evidence-first resolution — filled = agree, hollow = differ"),
          th("Evidence-first", title = "The final verbatim-grounded resolution (the adjudication)")
        )
      )
    ))

    # Pre-rendered HTML frame. Served from the precomputed RDS (written by
    # code/precompute_disc_html.R, ~0.12 s read) so the module opens instantly.
    # If the cached RDS is missing or older than disc_df.rds, rebuild once via
    # build_disc_html() (slow, ~27 s) and cache it for the next session.
    disc_html <- reactive({
      f_df   <- "data/adjudication/disc_df.rds"
      f_html <- "data/adjudication/disc_html.rds"
      if (!file.exists(f_df)) return(data.frame())
      fresh <- file.exists(f_html) &&
               file.info(f_html)$mtime >= file.info(f_df)$mtime
      h <- NULL
      if (fresh) h <- tryCatch(readRDS(f_html), error = function(e) NULL)
      if (is.null(h) || nrow(h) == 0) {
        h <- build_disc_html(disc_df(), "@@NS@@")
        if (nrow(h) > 0) tryCatch(saveRDS(h, f_html), error = function(e) NULL)
      }
      if (nrow(h) > 0 && "Pair" %in% names(h)) {
        h$Pair <- gsub("@@NS@@", ns("disc_click"), h$Pair, fixed = TRUE)
      }
      h
    })

    output$table <- renderDT({
      html <- disc_html()
      idx <- view_idx()
      if (length(idx) == 0 || nrow(html) == 0) {
        return(datatable(data.frame(Message = "No disagreement rows."), rownames = FALSE))
      }
      out <- html[idx, , drop = FALSE]
      datatable(out, rownames = FALSE, escape = FALSE, selection = "none",
        container = table_header,
        options = list(
          pageLength = 100,
          lengthMenu = list(c(15, 100, 500, 1000, 2000, -1),
                            c("15", "100", "500", "1000", "2000", "All")),
          search = list(regex = TRUE, smart = TRUE),
          language = list(search = "Filter:", zeroRecords = "No rows.")
        ),
        class = "compact hover row-border")
    }, server = TRUE)

    # ── Row click → global Evidence Trail drawer (extended) ─────────────
    observeEvent(input$disc_click, {
      req(input$disc_click)
      parts <- strsplit(input$disc_click, "|", fixed = TRUE)[[1]]
      if (length(parts) != 3) return()
      gene <- parts[1]; entity <- parts[2]; lab <- parts[3]
      row <- disc_df()[disc_df()$gene_symbol == gene &
                       disc_df()$rcd_form_canonical == entity &
                       disc_df()$label == lab, , drop = FALSE]
      extra <- NULL
      if (nrow(row) > 0) {
        extra <- list(
          axis         = row$label[1],
          gpt_verdict  = row$gpt4o_verdict[1],
          gpt_reason   = row$gpt4o_reason[1],
          human_verdict = "",
          note         = ""
        )
      }
      evidence_trail_rv(list(gene = gene, entity = entity, extra = extra))
      shinyjs::runjs("document.getElementById('evidence_drawer').style.display='block';")
    })

  })
}
