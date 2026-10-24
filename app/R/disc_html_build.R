# ─── Discrepancy Radar: pre-rendered HTML builder ────────────────────────────
# Single source of truth for the per-row HTML of the Discrepancy Radar table.
# Used both by the offline precompute script (code/precompute_disc_html.R, which
# writes data/adjudication/disc_html.rds) and as the module's slow fallback when
# that cached RDS is missing or stale. Building the full 7,905-row frame takes
# ~27 s on the fly, so the app reads the precomputed RDS (~0.12 s) instead.
#
# ns_id is the Shiny input namespace id used in the Pair cell onclick
# (the module passes ns("disc_click"); the precompute script passes "@@NS@@" and
# the module substitutes the real namespace at read time).

`%||%` <- function(a, b) if (is.null(a) || length(a) == 0 || is.na(a)) b else a

esc_html <- function(x) {
  x <- as.character(x)
  if (requireNamespace("htmltools", quietly = TRUE)) return(htmltools::htmlEscape(x))
  x <- gsub("&", "&amp;", x, fixed = TRUE)
  x <- gsub("<", "&lt;", x, fixed = TRUE)
  x <- gsub(">", "&gt;", x, fixed = TRUE)
  x
}

build_disc_html <- function(df, ns_id) {
  if (is.null(df) || nrow(df) == 0) return(data.frame())
  axis_vec <- df$label
  n <- nrow(df)

  role_col <- c(EXECUTOR = "#E53935", REGULATOR = "#3949AB", MARKER = "#00897B", UNCERTAIN = "#9E9E9E")
  dir_col  <- c(PROMOTES = "#2E7D32", PROTECTS = "#1565C0", UNCLEAR = "#757575",
                ASSOCIATED = "#8E24AA", BIDIRECTIONAL = "#8E24AA")
  mech_col <- c(YES = "#2E7D32", NO = "#9E9E9E", OUT_OF_CONTEXT = "#F59E0B")

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

  dot_span_f <- function(col) {
    paste0("<span style='display:inline-block;width:11px;height:11px;border-radius:50%;background:", col, ";margin-right:3px;vertical-align:middle;'></span>")
  }
  dot_span_e <- function(col) {
    paste0("<span style='display:inline-block;width:11px;height:11px;border-radius:50%;border:2px solid ", col, ";margin-right:3px;vertical-align:middle;'></span>")
  }
  dot_spans <- function(filled, total, col) {
    paste(c(rep(dot_span_f(col), filled), rep(dot_span_e(col), total - filled)), collapse = "")
  }

  sep <- "\u001f"
  axis_map <- tapply(tolower(as.character(df$label)),
                     paste(df$gene_symbol, df$rcd_form_canonical, sep = sep),
                     function(x) sort(unique(x)), simplify = FALSE)

  ax_cell <- vapply(seq_len(n), function(i) {
    k <- paste(df$gene_symbol[i], df$rcd_form_canonical[i], sep = sep)
    axs <- if (k %in% names(axis_map)) axis_map[[k]] else tolower(as.character(df$label[i]))
    rep_axis <- tolower(as.character(df$label[i]))
    chips <- vapply(axs, function(a) {
      nm <- c(direction = "Direction", role = "Role", mechanistic = "Mechanistic")[[a]]
      col <- c(direction = "#3949AB", role = "#00897B", mechanistic = "#6B7280")[[a]]
      if (is.null(nm) || is.null(col)) return("")
      if (a == rep_axis) {
        sprintf("<span title='Conflict on %s — the evidence columns in this row show this axis' style='display:inline-block;padding:2px 7px;border-radius:999px;font-size:11px;font-weight:700;color:#fff;background:%s;margin-right:3px;'>%s</span>", nm, col, nm)
      } else {
        sprintf("<span title='Additional conflict on %s — switch the Conflict axis selector to %s to see its evidence' style='display:inline-block;padding:2px 7px;border-radius:999px;font-size:11px;font-weight:600;color:%s;background:transparent;border:1.5px solid %s;margin-right:3px;'>%s</span>", nm, nm, col, col, nm)
      }
    }, character(1))
    paste(chips, collapse = "")
  }, character(1))

  pair <- vapply(seq_len(n), function(i) {
    g <- df$gene_symbol[i]; e <- df$rcd_form_canonical[i]; lab <- df$label[i]
    onclick <- sprintf("Shiny.setInputValue('%s', '%s|%s|%s', {priority:'event'}); return false;",
                       ns_id, g, e, lab)
    sprintf("<a href='#' onclick=\"%s\" style='color:#1d4ed8; font-weight:700; text-decoration:none;'><i>%s</i> \u00d7 %s</a>",
            onclick, g, e)
  }, character(1))

  ds_b <- vapply(seq_len(n), function(i) badge(df$ds_val[i], axis_col(axis_vec[i], df$ds_val[i])), character(1))
  el_b <- vapply(seq_len(n), function(i) {
    if (axis_vec[i] == "direction") badge(df$el_val[i], axis_col("direction", df$el_val[i]))
    else "<span style='color:#d6d3d1;'>\u2014</span>"
  }, character(1))
  cs_b <- vapply(seq_len(n), function(i) badge(df$cs_val[i], axis_col(axis_vec[i], df$cs_val[i])), character(1))

  comp_cell <- vapply(seq_len(n), function(i) {
    v <- if (axis_vec[i] == "role") df$compiled_role[i] else if (axis_vec[i] == "direction") df$compiled_dir[i] else NA_character_
    v <- trimws(as.character(v))
    if (is.na(v) || !nzchar(v)) return("<span style='color:#a8a29e;'>—</span>")
    col <- axis_col(axis_vec[i], v)
    if (is.null(col)) col <- "#9E9E9E"
    sprintf("<span title='Source-compiled role/direction (pre-evaluation, channels A–D)' style='display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:600;color:#fff;background:%s;margin-right:3px;'>%s</span>", col, v)
  }, character(1))

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
    if (axis_vec[i] == "direction") votes <- c(votes, trimws(as.character(df$el_val[i])))
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
    col <- axis_col(axis_vec[i], v2)
    if (is.null(col)) col <- "#9E9E9E"
    reason <- esc_html(df$gpt4o_reason[i])
    sprintf("<span title='GPT sided with %s — %s' style='display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:600;color:#fff;background:%s;'>%s</span>",
            v, reason, col, v2)
  }, character(1))

  cur_cell <- function(vals_mapped, vals_raw) {
    vapply(seq_len(n), function(i) {
      v <- trimws(as.character(vals_raw[i]))
      if (is.na(v) || !nzchar(v)) {
        st <- trimws(as.character(df$decision_status[i]))
        if (!is.na(st) && nzchar(st) && st == "PENDING_DELTA") {
          return("<span title='Delta row — evidence-first adjudicated' style='color:#d6d3d1;'>·</span>")
        }
        return("<span style='color:#a8a29e;'>—</span>")
      }
      v2 <- trimws(as.character(vals_mapped[i]))
      if (is.na(v2) || !nzchar(v2)) v2 <- "—"
      col <- axis_col(axis_vec[i], v2)
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
    ev <- esc_html(df$deciding_evidence[i] %||% "")
    col <- axis_col(axis_vec[i], v)
    if (is.null(col)) col <- "#9E9E9E"
    sprintf("<span title='%s' style='display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:700;color:#fff;background:%s;margin-right:3px;box-shadow:0 0 0 1.5px #0b1020;'>%s</span>",
            ev, col, v)
  }, character(1))

  data.frame(Pair = pair, Axis = ax_cell, DeepSeek = ds_b, Elicit = el_b,
             Consensus = cs_b, Compiled = comp_cell, GPT = gpt_cell,
             `Curator 1` = cur1_cell, `Curator 2` = cur2_cell,
             Concordance = dots_cell, `Evidence-first` = fin_cell,
             stringsAsFactors = FALSE, check.names = FALSE)
}
