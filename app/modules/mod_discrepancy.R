# ─── Module: discrepancy (Discrepancy Radar) ────────────────────────────────
# Maps the 7,905 classifier-disagreement hotspots (GPT-arbitrated),
# faceted by axis (role / direction / mechanistic), with concordance dots,
# the GPT arbitration verdict, the two curator votes, and the evidence-first
# resolution (DELTA_ADJUDICATED 950 rows + PENDING_DELTA 3).

RCD_DISC_DIR <- "data/discrepancy"

mod_discrepancy_ui <- function(id) {
  ns <- NS(id)
  tagList(
    div(style = "max-width:1200px; margin:0 auto; padding:20px;",
      tags$h2("Discrepancy Radar", style = "margin:0 0 10px; color:#1c1917; font-weight:700; font-size:24px;"),
      p("The knowledge frontier: Where the three classifiers disagree, RCDome shows the conflict instead of hiding it. Each row carries the divergent verdicts, the GPT arbitration, the two curator votes, and the evidence-first verdict that resolved it from the verbatim.",
        style = "color:#78716c; font-size:14px;"),
      uiOutput(ns("summary_bar")),
      tags$div(style = "display:flex; gap:10px; flex-wrap:wrap; align-items:flex-end; margin-bottom:12px;",
        radioButtons(ns("vote_source"), "Direction/Role source:", inline = TRUE,
          choices = c("Evidence-first" = "evidence", "DeepSeek" = "deepseek",
                      "Consensus" = "consensus", "Compiled" = "compiled",
                      "GPT" = "gpt", "Curator 1" = "curator_1", "Curator 2" = "curator_2"),
          selected = "evidence"),
        actionButton(ns("reset_filters"), "Reset filters",
                   style = "margin-left:auto; height:32px; padding:0 16px; font-size:12.5px; font-weight:600; background:#FF9800; color:#0b1020; border:none; border-radius:8px; cursor:pointer; box-shadow:0 2px 8px rgba(255,152,0,0.35);")
      ),
      tags$div(style = "display:flex; gap:10px; flex-wrap:wrap; align-items:center; margin-bottom:12px;",
        radioButtons(ns("facet"), "Conflict axis", inline = TRUE,
          choices = c("All", "Direction", "Role", "Mechanistic"),
          selected = "All")
      ),
      tags$div(style = "display:flex; gap:10px; flex-wrap:wrap; align-items:flex-end; margin-bottom:12px;",
        selectizeInput(ns("f_gene"), "Gene", choices = NULL, multiple = TRUE, width = "200px",
                       options = list(placeholder = "All genes")),
        selectizeInput(ns("f_rcd"), "RCD entity", choices = NULL, multiple = TRUE, width = "200px",
                       options = list(placeholder = "All entities")),
        selectizeInput(ns("f_biotype"), "Biotype", choices = NULL, multiple = TRUE, width = "160px",
                       options = list(placeholder = "All biotypes")),
        selectizeInput(ns("f_cancer"), "Cancer Gene", choices = NULL, multiple = TRUE, width = "160px",
                       options = list(placeholder = "All")),
        selectizeInput(ns("f_db"), "Source DBs", choices = NULL, multiple = TRUE, width = "200px",
                       options = list(placeholder = "All DBs"))
      ),
      tags$div(style = "display:flex; gap:10px; flex-wrap:wrap; align-items:flex-end; margin-bottom:12px;",
        selectizeInput(ns("f_tier"), "Confidence Tier", choices = NULL, multiple = TRUE, width = "160px",
                       options = list(placeholder = "All tiers")),
        selectizeInput(ns("f_mech"), "Mechanistic", choices = NULL, multiple = TRUE, width = "160px",
                       options = list(placeholder = "All")),
        selectizeInput(ns("f_role"), "Role", choices = NULL, multiple = TRUE, width = "150px",
                       options = list(placeholder = "All")),
        selectizeInput(ns("f_dir"), "Direction", choices = NULL, multiple = TRUE, width = "160px",
                       options = list(placeholder = "All")),
        selectizeInput(ns("f_status"), "Adjudication",
                       choices = c("Disagreement" = "UNIFORM_PIPELINE", "Delta adjudicated" = "DELTA_ADJUDICATED"),
                       multiple = TRUE, width = "200px", options = list(placeholder = "All statuses"))
      ),
      uiOutput(ns("legend")),
      DTOutput(ns("table"))
    )
  )
}

mod_discrepancy_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    ns <- session$ns

    # Source → per-axis vote column for the Mechanistic/Role/Direction filters.
    src_val <- function(df, src) {
      if (is.null(src) || length(src) == 0) src <- "evidence"
      switch(src,
        evidence  = df$final_val,
        deepseek  = df$ds_val,
        consensus = df$cs_val,
        compiled  = ifelse(df$label == "role", df$compiled_role,
                    ifelse(df$label == "direction", df$compiled_dir, NA_character_)),
        gpt       = df$gpt_mapped,
        curator_1 = df$cur1_mapped,
        curator_2 = df$cur2_mapped,
        df$final_val)
    }

    # ── Adjudicated row set (precomputed RDS: 7,905 Track + Delta rows) ──
    # Lazy-load once + prefer the globally pre-loaded frame (same pattern as the
    # Gene Catalog's genes_rv/get_genes) so the radar opens as fast as the catalog.
    disc_df_rv <- reactiveVal(NULL)
    disc_df <- function() {
      if (is.null(disc_df_rv())) {
        disc_df_rv(
          if (exists("disc_df_global", inherits = TRUE) && is.data.frame(disc_df_global) && nrow(disc_df_global) > 0) {
            disc_df_global
          } else {
            f <- "data/adjudication/disc_df.rds"
            if (!file.exists(f)) data.frame() else tryCatch(readRDS(f), error = function(e) data.frame())
          }
        )
      }
      disc_df_rv()
    }

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
      updateSelectizeInput(session, "f_biotype", choices = sort(unique(df$gene_biotype[!is.na(df$gene_biotype) & df$gene_biotype != ""])))
      updateSelectizeInput(session, "f_rcd", choices = sort(unique(df$rcd_form_canonical)), server = TRUE)
      updateSelectizeInput(session, "f_cancer", choices = sort(unique(df$cancer_gene_type[!is.na(df$cancer_gene_type) & df$cancer_gene_type != ""])))
      updateSelectizeInput(session, "f_tier", choices = sort(unique(df$confidence_tier[!is.na(df$confidence_tier) & df$confidence_tier != ""])))
      db_choices <- sort(unique(unlist(strsplit(df$source_databases[!is.na(df$source_databases)], ";"))))
      db_choices <- db_choices[db_choices != "" & !is.na(db_choices)]
      updateSelectizeInput(session, "f_db", choices = db_choices)
    })

    # Axis filters (Mechanistic/Role/Direction) follow the selected vote source.
    observe({
      df <- disc_df()
      if (nrow(df) == 0) return()
      sv <- src_val(df, input$vote_source)
      vals <- function(lab) sort(unique(sv[df$label == lab & !is.na(sv) & sv != ""]))
      updateSelectizeInput(session, "f_mech", choices = vals("mechanistic"), selected = character(0))
      updateSelectizeInput(session, "f_role", choices = vals("role"), selected = character(0))
      updateSelectizeInput(session, "f_dir", choices = vals("direction"), selected = character(0))
    })

    # All filters applied, BEFORE the conflict-axis radio dedup.
    filtered_idx <- reactive({
      df <- disc_df()
      if (nrow(df) == 0) return(integer(0))
      idx <- seq_len(nrow(df))
      # Pair-level filters.
      if (!is.null(input$f_gene) && length(input$f_gene) > 0) idx <- idx[df$gene_symbol[idx] %in% input$f_gene]
      if (!is.null(input$f_biotype) && length(input$f_biotype) > 0) idx <- idx[df$gene_biotype[idx] %in% input$f_biotype]
      if (!is.null(input$f_rcd) && length(input$f_rcd) > 0) idx <- idx[df$rcd_form_canonical[idx] %in% input$f_rcd]
      if (!is.null(input$f_cancer) && length(input$f_cancer) > 0) idx <- idx[df$cancer_gene_type[idx] %in% input$f_cancer]
      if (!is.null(input$f_tier) && length(input$f_tier) > 0) idx <- idx[df$confidence_tier[idx] %in% input$f_tier]
      if (!is.null(input$f_status) && length(input$f_status) > 0) idx <- idx[df$decision_status[idx] %in% input$f_status]
      if (!is.null(input$f_db) && length(input$f_db) > 0) {
        keep <- vapply(idx, function(i) {
          s <- df$source_databases[i]
          if (is.na(s) || !nzchar(s)) return(FALSE)
          any(vapply(input$f_db, function(d) grepl(d, s, fixed = TRUE), logical(1)))
        }, logical(1))
        idx <- idx[keep]
      }
      # Axis-level (source-aware) filters.
      sv <- src_val(df, input$vote_source)
      if (!is.null(input$f_mech) && length(input$f_mech) > 0) idx <- idx[df$label[idx] == "mechanistic" & sv[idx] %in% input$f_mech]
      if (!is.null(input$f_role) && length(input$f_role) > 0) idx <- idx[df$label[idx] == "role" & sv[idx] %in% input$f_role]
      if (!is.null(input$f_dir) && length(input$f_dir) > 0) idx <- idx[df$label[idx] == "direction" & sv[idx] %in% input$f_dir]
      idx
    })

    # Row indices for the current view (union dedup for All).
    view_idx <- reactive({
      df <- disc_df()
      idx <- filtered_idx()
      if (length(idx) == 0) return(integer(0))
      if (identical(tolower(input$facet), "all")) {
        # All = union of gene–RCD pairs with ≥1 conflict. A pair flagged on
        # several axes appears once (deduplicated), so totals are not inflated.
        key <- paste(df$gene_symbol, df$rcd_form_canonical, sep = "\u001f")
        idx <- idx[!duplicated(key[idx])]
      } else {
        idx <- idx[df$label[idx] == tolower(input$facet)]
      }
      idx
    })

    # ── Reset filters → restore All as the default conflict axis ───────
    observeEvent(input$reset_filters, {
      updateRadioButtons(session, "facet", selected = "All")
      updateRadioButtons(session, "vote_source", selected = "evidence")
      for (id in c("f_gene", "f_biotype", "f_rcd", "f_cancer", "f_tier", "f_status", "f_db", "f_mech", "f_role", "f_dir")) {
        updateSelectizeInput(session, id, selected = character(0))
      }
    })

    # ── Summary bar ─────────────────────────────────────────────────────
    output$summary_bar <- renderUI({
      idx <- filtered_idx()
      if (length(idx) == 0) return(NULL)
      # Per-axis conflict counts from the fully-filtered (pre-dedup) set.
      base <- disc_df()[idx, , drop = FALSE]
      cnt <- table(base$label)
      tot <- length(view_idx())
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
    disc_html_rv <- reactiveVal(NULL)
    disc_html <- function() {
      if (!is.null(disc_html_rv())) return(disc_html_rv())
      f_df   <- "data/adjudication/disc_df.rds"
      f_html <- "data/adjudication/disc_html.rds"
      h <- NULL
      if (exists("disc_html_global", inherits = TRUE) && is.data.frame(disc_html_global) && nrow(disc_html_global) > 0) {
        h <- disc_html_global
      } else if (file.exists(f_html)) {
        fresh <- file.exists(f_df) && file.info(f_html)$mtime >= file.info(f_df)$mtime
        if (fresh) h <- tryCatch(readRDS(f_html), error = function(e) NULL)
      }
      if (is.null(h) || nrow(h) == 0) {
        h <- build_disc_html(disc_df(), "@@NS@@")
        if (nrow(h) > 0) tryCatch(saveRDS(h, f_html), error = function(e) NULL)
      }
      if (nrow(h) > 0 && "Pair" %in% names(h)) {
        h$Pair <- gsub("@@NS@@", ns("disc_click"), h$Pair, fixed = TRUE)
      }
      disc_html_rv(h)
      h
    }

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
          pageLength = 15,
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
