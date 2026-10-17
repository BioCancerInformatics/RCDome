# ─── Module: discrepancy (Discrepancy Radar) ────────────────────────────────
# Phase 1: maps the 7,895 classifier-disagreement hotspots (GPT-arbitrated),
# faceted by axis (role / direction / mechanistic), with concordance dots,
# the GPT arbitration verdict, and a PENDING human-adjudication slot.
# Phase 2 (after curator verdicts) will fill the human verdict + final value.

RCD_DISC_DIR <- "data/discrepancy"

mod_discrepancy_ui <- function(id) {
  ns <- NS(id)
  tagList(
    div(style = "max-width:1200px; margin:0 auto; padding:20px;",
      p("The knowledge frontier: Where the three classifiers disagree, RCDome shows the conflict instead of hiding it. Each row carries the divergent verdicts, the GPT arbitration, the two curator votes, and the evidence-first verdict that resolved it from the verbatim.",
        style = "color:#78716c; font-size:14px;"),
      uiOutput(ns("summary_bar")),
      tags$div(style = "margin:12px 0 6px;",
        radioButtons(ns("facet"), "Conflict axis", inline = TRUE,
          choices = c("Direction", "Role", "Mechanistic"),
          selected = "Direction"),
        textInput(ns("search"), NULL, width = "320px",
                  placeholder = "Filter by gene or RCD entity")
      ),
      uiOutput(ns("legend")),
      DTOutput(ns("table"))
    )
  )
}

mod_discrepancy_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    ns <- session$ns

    # ── Load + join the four GPT-vote CSVs with the V027 matrix ─────────
    extract_label <- function(concat, lab) {
      if (is.null(concat) || is.na(concat) || !nzchar(trimws(concat))) return(NA_character_)
      parts <- strsplit(trimws(concat), "|", fixed = TRUE)[[1]]
      idx <- match(lab, c("mechanistic", "role", "direction"))
      if (is.na(idx) || length(parts) < idx) return(NA_character_)
      trimws(parts[idx])
    }
    disc_df <- reactive({
      files <- list.files(RCD_DISC_DIR, pattern = "\\.csv$", full.names = TRUE)
      if (length(files) == 0) return(data.frame())
      raw <- do.call(rbind, lapply(files, function(f) {
        tryCatch(read.csv(f, stringsAsFactors = FALSE, fileEncoding = "UTF-8-BOM"),
                 error = function(e) NULL)
      }))
      if (is.null(raw) || nrow(raw) == 0) return(data.frame())

      raw$gene_symbol        <- trimws(as.character(raw$gene_symbol))
      raw$rcd_form_canonical <- trimws(as.character(raw$rcd_form_canonical))
      raw$label              <- tolower(trimws(as.character(raw$label)))
      raw$gpt4o_verdict      <- trimws(as.character(raw$gpt4o_verdict))
      raw$gpt4o_reason       <- trimws(as.character(raw$gpt4o_reason))

      key  <- paste(raw$gene_symbol, raw$rcd_form_canonical, sep = "\r")
      mkey <- paste(genes_df$name, genes_df$Pathway_Categorization, sep = "\r")
      idx  <- match(key, mkey)
      ok   <- !is.na(idx)

      raw$ds_val <- NA_character_
      raw$cs_val <- NA_character_
      raw$el_val <- NA_character_
      raw$final_val <- NA_character_
      raw$cur1_val <- NA_character_
      raw$cur2_val <- NA_character_
      raw$decision_status <- NA_character_
      raw$deciding_evidence <- NA_character_
      lab <- raw$label[ok]
      raw$ds_val[ok] <- ifelse(lab == "role",        as.character(genes_df$cot_role[idx[ok]]),
                        ifelse(lab == "direction",   as.character(genes_df$cot_direction[idx[ok]]),
                        ifelse(lab == "mechanistic", as.character(genes_df$cot_mechanistic[idx[ok]]), NA)))
      raw$cs_val[ok] <- ifelse(lab == "role",        as.character(genes_df$consensus_role[idx[ok]]),
                        ifelse(lab == "direction",   as.character(genes_df$consensus_direction[idx[ok]]),
                        ifelse(lab == "mechanistic", as.character(genes_df$consensus_mechanistic[idx[ok]]), NA)))
      raw$el_val[ok] <- ifelse(lab == "direction", as.character(genes_df$role_direction[idx[ok]]), NA_character_)
      raw$final_val[ok] <- ifelse(lab == "role",        as.character(genes_df$final_role[idx[ok]]),
                           ifelse(lab == "direction",   as.character(genes_df$final_direction[idx[ok]]),
                           ifelse(lab == "mechanistic", as.character(genes_df$final_mechanistic[idx[ok]]), NA)))
      raw$cur1_val[ok] <- vapply(which(ok), function(j) extract_label(genes_df$higor_verdict[idx[j]], lab[j]), character(1))
      raw$cur2_val[ok] <- vapply(which(ok), function(j) extract_label(genes_df$victor_verdict[idx[j]], lab[j]), character(1))
      raw$decision_status[ok] <- as.character(genes_df$decision_status[idx[ok]])
      raw$deciding_evidence[ok] <- as.character(genes_df$deciding_evidence[idx[ok]])

      raw[ok, , drop = FALSE]
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

    # ── Filtered frame ──────────────────────────────────────────────────
    facet_df <- reactive({
      df <- disc_df()
      if (nrow(df) == 0) return(df)
      df <- df[df$label == tolower(input$facet), , drop = FALSE]
      q <- trimws(input$search %||% "")
      if (nzchar(q)) {
        hit <- grepl(tolower(q), tolower(df$gene_symbol), fixed = TRUE) |
               grepl(tolower(q), tolower(df$rcd_form_canonical), fixed = TRUE)
        df <- df[hit, , drop = FALSE]
      }
      df
    })

    # ── Summary bar ─────────────────────────────────────────────────────
    output$summary_bar <- renderUI({
      df <- disc_df()
      if (nrow(df) == 0) return(NULL)
      cnt <- table(df$label)
      tot <- nrow(df)
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
    output$table <- renderDT({
      df <- facet_df()
      if (nrow(df) == 0) {
        return(datatable(data.frame(Message = "No disagreement rows."), rownames = FALSE))
      }
      axis <- tolower(input$facet)
      n <- nrow(df)

      pair <- vapply(seq_len(n), function(i) {
        g <- df$gene_symbol[i]; e <- df$rcd_form_canonical[i]; lab <- df$label[i]
        onclick <- sprintf("Shiny.setInputValue('%s', '%s|%s|%s', {priority:'event'}); return false;",
                           ns("disc_click"), g, e, lab)
        sprintf("<a href='#' onclick=\"%s\" style='color:#1d4ed8; font-weight:700; text-decoration:none;'><i>%s</i> \u00d7 %s</a>",
                onclick, g, e)
      }, character(1))

      ds_b <- vapply(seq_len(n), function(i) badge(df$ds_val[i], axis_col(axis, df$ds_val[i])), character(1))
      el_b <- vapply(seq_len(n), function(i) {
        if (axis == "direction") badge(df$el_val[i], axis_col("direction", df$el_val[i]))
        else "<span style='color:#d6d3d1;'>\u2014</span>"
      }, character(1))
      cs_b <- vapply(seq_len(n), function(i) badge(df$cs_val[i], axis_col(axis, df$cs_val[i])), character(1))

      map_vote <- function(v, ds, cs) {
        v <- trimws(as.character(v))
        if (length(v) == 0 || is.na(v) || !nzchar(v)) return(NA_character_)
        if (v == "DEEPSEEK") return(trimws(as.character(ds)))
        if (v == "CONSENSUS") return(trimws(as.character(cs)))
        v
      }
      gpt_mapped  <- vapply(seq_len(n), function(i) map_vote(df$gpt4o_verdict[i], df$ds_val[i], df$cs_val[i]), character(1))
      cur1_mapped <- vapply(seq_len(n), function(i) map_vote(df$cur1_val[i], df$ds_val[i], df$cs_val[i]), character(1))
      cur2_mapped <- vapply(seq_len(n), function(i) map_vote(df$cur2_val[i], df$ds_val[i], df$cs_val[i]), character(1))

      dots_cell <- vapply(seq_len(n), function(i) {
        votes <- trimws(as.character(df$ds_val[i]))
        if (axis == "direction") votes <- c(votes, trimws(as.character(df$el_val[i])))
        votes <- c(votes, trimws(as.character(df$cs_val[i])), gpt_mapped[i], cur1_mapped[i], cur2_mapped[i])
        votes <- votes[!is.na(votes) & nzchar(votes)]
        ref <- trimws(as.character(df$final_val[i]))
        if (is.na(ref) || !nzchar(ref)) return("")
        agree <- sum(votes == ref)
        total <- length(votes)
        col <- if (agree >= 4) "#2E7D32" else if (agree >= 2) "#F59E0B" else "#E53935"
        dot_spans(agree, total, col)
      }, character(1))

      gpt_cell <- vapply(seq_len(n), function(i) {
        v <- trimws(as.character(df$gpt4o_verdict[i]))
        v2 <- gpt_mapped[i]
        if (is.na(v2) || !nzchar(v2)) v2 <- "—"
        col <- axis_col(axis, v2)
        if (is.null(col)) col <- "#9E9E9E"
        reason <- htmltools::htmlEscape(df$gpt4o_reason[i])
        sprintf("<span title='GPT sided with %s — %s' style='display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:600;color:#fff;background:%s;'>%s</span>",
                v, reason, col, v2)
      }, character(1))

      cur_cell <- function(vals_mapped, vals_raw) {
        vapply(seq_len(n), function(i) {
          v <- trimws(as.character(vals_raw[i]))
          if (is.na(v) || !nzchar(v)) {
            st <- trimws(as.character(df$decision_status[i]))
            if (!is.na(st) && nzchar(st) && st == "PENDING_DELTA") {
              return("<span title='Delta row — curator round not yet sent' style='color:#d6d3d1;'>·</span>")
            }
            return("<span style='color:#a8a29e;'>—</span>")
          }
          v2 <- trimws(as.character(vals_mapped[i]))
          if (is.na(v2) || !nzchar(v2)) v2 <- "—"
          col <- axis_col(axis, v2)
          if (is.null(col)) col <- "#9E9E9E"
          sprintf("<span title='Voted with %s' style='display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:600;color:#fff;background:%s;margin-right:3px;'>%s</span>", v, col, v2)
        }, character(1))
      }
      cur1_cell <- cur_cell(cur1_mapped, df$cur1_val)
      cur2_cell <- cur_cell(cur2_mapped, df$cur2_val)

      fin_cell <- vapply(seq_len(n), function(i) {
        v <- trimws(as.character(df$final_val[i]))
        if (is.na(v) || !nzchar(v)) {
          st <- trimws(as.character(df$decision_status[i]))
          if (!is.na(st) && nzchar(st) && st == "PENDING_DELTA") {
            return("<span title='Disagreement discovered, but the delta round has not been sent to the curators yet' style='display:inline-block;padding:2px 8px;border:1px dashed #f59e0b;border-radius:999px;font-size:12px;font-weight:600;color:#b45309;background:#fef3c7;'>PENDING</span>")
          }
          return("<span style='color:#a8a29e;'>—</span>")
        }
        ev <- htmltools::htmlEscape(df$deciding_evidence[i] %||% "")
        col <- axis_col(axis, v)
        if (is.null(col)) col <- "#9E9E9E"
        sprintf("<span title='%s' style='display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:700;color:#fff;background:%s;margin-right:3px;box-shadow:0 0 0 1.5px #0b1020;'>%s</span>",
                ev, col, v)
      }, character(1))

      out <- data.frame(
        Pair = pair,
        DeepSeek = ds_b,
        Elicit = el_b,
        Consensus = cs_b,
        GPT = gpt_cell,
        `Curator 1` = cur1_cell,
        `Curator 2` = cur2_cell,
        Concordance = dots_cell,
        `Evidence-first` = fin_cell,
        stringsAsFactors = FALSE, check.names = FALSE
      )

      header <- htmltools::withTags(table(
        class = "display",
        thead(
          tr(
            th("Pair", title = "Gene × RCD entity — click for the Evidence Trail"),
            th("DeepSeek", title = "DeepSeek chain-of-thought classifier verdict (Phases 2A–2F)"),
            th("Elicit", title = "Elicit Phase 3 systematic-review extraction"),
            th("Consensus", title = "Consensus evidence-channel classification (neutral query, Phase 2G)"),
            th("GPT", title = "GPT-4o arbitration vote on the conflict"),
            th("Curator 1", title = "First human curator vote"),
            th("Curator 2", title = "Second human curator vote"),
            th("Concordance", title = "How many of the six voters (DeepSeek, Elicit, Consensus, GPT, Curator 1, Curator 2) agree with the evidence-first resolution — filled = agree, hollow = differ"),
            th("Evidence-first", title = "The final verbatim-grounded resolution (the adjudication)")
          )
        )
      ))

      datatable(out, rownames = FALSE, escape = FALSE, selection = "none",
        container = header,
        options = list(
          pageLength = 15, search = list(regex = TRUE, smart = TRUE),
          language = list(search = "Filter:", zeroRecords = "No rows.")
        ),
        class = "compact hover row-border")
    })

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
