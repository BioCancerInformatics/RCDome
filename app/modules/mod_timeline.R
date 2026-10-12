# ─── Module: timeline (RCD Discovery Timeline) ──────────────────────────────
# Five horizontal lanes, one per ontological level (L1-L5), 1859 -> 2026.
# Clicking a node opens a "discovery card" (founding year + founding paper),
# NOT the description modal (descriptions have their own module).

RCD_FOUNDING_CSV <- "data/discovery/founding_papers.csv"
RCD_DISCOVERY_CSV <- "data/discovery/discovery_papers.csv"

mod_timeline_ui <- function(id) {
  ns <- NS(id)
  tagList(
    tags$div(
      id = "tl_tip",
      style = "position:fixed; display:none; background:#1c1917; color:#e7e5e4; padding:10px 14px; border-radius:8px; font-size:12px; z-index:10000; pointer-events:none; max-width:340px; box-shadow:0 6px 18px rgba(0,0,0,.4);"
    ),
    tags$script(HTML("
      function tlShow(e, el) {
        var tip = document.getElementById('tl_tip');
        tip.innerHTML = '<b style=\"font-style:italic\">' + el.dataset.name + '</b> \u00b7 ' + el.dataset.year +
          '<br><span style=\"color:#d6d3d1\">' + el.dataset.level + '</span>' +
          '<br><span style=\"color:#a8a29e\">' + el.dataset.cit + '</span>' +
          '<br><span style=\"color:#00B0FF\">PMID ' + el.dataset.pmid + '</span>';
        tip.style.display = 'block';
        tip.style.left = (e.clientX + 14) + 'px';
        tip.style.top = (e.clientY + 14) + 'px';
      }
      function tlHide() {
        document.getElementById('tl_tip').style.display = 'none';
      }
    ")),
    div(style = "max-width:1200px; margin:0 auto; padding:20px;",
      h2("Discovery Timeline", style = "font-weight:700; color:#1c1917;"),
      p("From 1859 to 2026: the 53 RCD-related entities plotted by founding year, one lane per ontological level. Hover a point for its founding citation; click it to open the discovery card.",
        style = "color:#78716c; font-size:14px;"),
      uiOutput(ns("timeline"))
    )
  )
}

mod_timeline_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    ns <- session$ns

    level_col <- c(
      "L1 Modalities" = "#E0C04B",
      "L2 Subtypes" = "#00B0FF",
      "L3 Triggers" = "#00E676",
      "L4 Functional/contextual" = "#E040FB",
      "L5 Generic/umbrella/taxon" = "#FF6D00"
    )
    level_short <- c(
      "L1 Modalities" = "L1", "L2 Subtypes" = "L2", "L3 Triggers" = "L3",
      "L4 Functional/contextual" = "L4", "L5 Generic/umbrella/taxon" = "L5"
    )

    # Percent-encode a DOI for a valid https://doi.org/ link (keep / . - _).
    doi_href <- function(doi) {
      x <- trimws(doi)
      x <- gsub(" ", "%20", x, fixed = TRUE)
      x <- gsub("(", "%28", x, fixed = TRUE)
      x <- gsub(")", "%29", x, fixed = TRUE)
      x <- gsub("<", "%3C", x, fixed = TRUE)
      x <- gsub(">", "%3E", x, fixed = TRUE)
      x <- gsub(";", "%3B", x, fixed = TRUE)
      x <- gsub(":", "%3A", x, fixed = TRUE)
      paste0("https://doi.org/", x)
    }

    tl_data <- reactive({
      tl <- merge(
        decoder_df[, c("rcd_form", "year", "founding_pmid", "reference_citation", "primary_refs_pmids", "category")],
        unique(genes_df[, c("Pathway_Categorization", "rcdome_level_name")]),
        by.x = "rcd_form", by.y = "Pathway_Categorization", all.x = TRUE
      )
      fp <- read.csv(RCD_FOUNDING_CSV, stringsAsFactors = FALSE, check.names = FALSE)
      tl <- merge(tl, fp, by.x = "rcd_form", by.y = "rcd_form", all.x = TRUE)
      dp <- read.csv(RCD_DISCOVERY_CSV, stringsAsFactors = FALSE, check.names = FALSE)
      names(dp) <- paste0("disc_", names(dp))
      names(dp)[names(dp) == "disc_rcd_form"] <- "rcd_form"
      tl <- merge(tl, dp, by.x = "rcd_form", by.y = "rcd_form", all.x = TRUE)
      tl$yr <- suppressWarnings(as.numeric(tl$year))   # NA = composite
      tl
    })

    output$timeline <- renderUI({
      tl <- tl_data()
      levels <- c("L1 Modalities", "L2 Subtypes", "L3 Triggers",
                  "L4 Functional/contextual", "L5 Generic/umbrella/taxon")
      lane_y <- setNames(seq(70, 350, by = 70), levels)
      esc <- function(x) htmltools::htmlEscape(as.character(x))
      dot_w <- 12; step <- 12; max_off <- 24

      # ── Helper: render one SVG panel for a given year window ──
      panel_svg <- function(sub0, yr_min, yr_max, include_composite, title_label, filter_id) {
        Xp <- function(yr) 320 + (yr - yr_min) / (yr_max - yr_min) * 760
        keep <- (!is.na(sub0$yr) & sub0$yr >= yr_min & sub0$yr <= yr_max) |
                (include_composite & is.na(sub0$yr))
        sub <- sub0[keep, , drop = FALSE]
        sub$yoff <- 0
        for (lv in levels) {
          idx <- which(sub$rcdome_level_name == lv & !is.na(sub$yr))
          idx <- idx[order(sub$yr[idx])]
          placed <- list()
          for (i in idx) {
            x_i <- Xp(sub$yr[i]); yoff_i <- 0; k <- 0
            repeat {
              hit <- FALSE
              for (p in placed) if (abs(x_i - p$x) < dot_w && abs(yoff_i - p$y) < step) { hit <- TRUE; break }
              if (!hit) break
              k <- k + 1; mag <- ((k + 1) %/% 2) * step
              if (mag > max_off) break
              yoff_i <- if (k %% 2 == 1) mag else -mag
            }
            sub$yoff[i] <- yoff_i
            placed[[length(placed) + 1]] <- list(x = x_i, y = yoff_i)
          }
        }
        d0 <- ceiling(yr_min / 10) * 10
        decades <- seq(d0, floor(yr_max / 10) * 10, by = 10)
        ticks <- paste(vapply(decades, function(d) {
          x <- Xp(d)
          sprintf("<line x1='%.1f' y1='392' x2='%.1f' y2='400' stroke='#334155' stroke-width='1'/><text x='%.1f' y='418' fill='#94a3b8' font-size='14' text-anchor='middle'>%d</text>",
                  x, x, x, d)
        }, character(1)), collapse = "")
        lane_html <- vapply(levels, function(lv) {
          y <- lane_y[[lv]]; col <- level_col[[lv]]
          n <- sum(sub$rcdome_level_name == lv, na.rm = TRUE)
          label <- sprintf("<text x='12' y='%d' fill='%s' font-size='16' font-weight='700'>%s (%d)</text>", y + 4, col, lv, n)
          line <- sprintf("<line x1='320' y1='%d' x2='1080' y2='%d' stroke='#334155' stroke-width='1'/>", y, y)
          s2 <- sub[sub$rcdome_level_name == lv, , drop = FALSE]
          nodes <- vapply(seq_len(nrow(s2)), function(i) {
            e <- s2$rcd_form[i]; yr <- s2$yr[i]
            r <- 6
            if (is.na(yr)) { x <- 1120; yy <- y; yr_label <- "composite" }
            else { x <- Xp(yr); yy <- y + s2$yoff[i]; yr_label <- as.character(yr) }
            pmid <- if (!is.na(s2$founding_pmid[i]) && nzchar(s2$founding_pmid[i])) s2$founding_pmid[i] else ""
            cit <- if (!is.na(s2$reference_citation[i])) s2$reference_citation[i] else ""
            onclick <- sprintf("Shiny.setInputValue('%s', '%s', {priority:'event'})", ns("tl_click"), e)
            paste0(
              sprintf("<circle class='tl-node' cx='%.1f' cy='%.1f' r='%d' fill='%s' filter='url(#%s)' data-name='%s' data-year='%s' data-level='%s' data-pmid='%s' data-cit='%s' onmousemove='tlShow(event, this)' onmouseout='tlHide()' onclick=\"%s\" style='cursor:pointer;'/>",
                      x, yy, r, col, filter_id, esc(e), yr_label, esc(lv), pmid, esc(cit), onclick),
              if (is.na(yr)) sprintf("<text x='%.1f' y='%.1f' fill='#94a3b8' font-size='9' text-anchor='middle' font-style='italic'>composite</text>", x, yy - 14) else ""
            )
          }, character(1))
          paste0(label, line, paste(nodes, collapse = ""))
        }, character(1))
        title_html <- if (nzchar(title_label))
          sprintf("<text x='580' y='36' fill='#e7e5e4' font-size='15' font-weight='600' text-anchor='middle'>%s</text>", title_label) else ""
        paste0(
          "<div style='background:#0b1020; border-radius:12px; padding:18px 12px 8px; box-shadow:0 6px 18px rgba(0,0,0,.35);",
          if (nzchar(title_label)) " margin-top:22px;" else "", "'>",
          "<svg viewBox='0 0 1160 440' width='100%' style='display:block;'>",
          "<defs><filter id='", filter_id, "' x='-50%' y='-50%' width='200%' height='200%'>",
          "<feGaussianBlur stdDeviation='3' result='blur'/>",
          "<feMerge><feMergeNode in='blur'/><feMergeNode in='SourceGraphic'/></feMerge></filter></defs>",
          title_html, ticks, paste(lane_html, collapse = ""),
          "</svg></div>"
        )
      }

      min_yr <- min(tl$yr, na.rm = TRUE)
      max_yr <- max(tl$yr, na.rm = TRUE)
      main_panel <- panel_svg(tl, min_yr, max_yr, TRUE, "", "tlglow")

      HTML(main_panel)
    })

    # ── Discovery card (founding year + founding paper, not the description) ──
    ref_block <- function(pmid, title, authors, journal, pubdate, doi) {
      cite_line <- paste0(trimws(authors), if (nzchar(authors) && (nzchar(journal) || nzchar(pubdate))) ". " else "",
                          journal, if (nzchar(journal) && nzchar(pubdate)) " " else "", pubdate,
                          if (nzchar(authors) || nzchar(journal) || nzchar(pubdate)) "." else "")
      tags$div(
        if (nzchar(title)) tags$div(HTML(paste0("<i>", title, "</i>")),
                                    style = "font-size:15px; color:#e7e5e4; font-style:italic; line-height:1.45;") else NULL,
        if (nzchar(cite_line)) tags$div(cite_line, style = "color:#94a3b8; font-size:13px; margin-top:8px;") else NULL,
        tags$div(style = "margin-top:12px; display:flex; gap:12px;",
          if (nzchar(pmid)) tags$a(paste0("PMID ", pmid),
            href = paste0("https://pubmed.ncbi.nlm.nih.gov/", pmid, "/"),
            target = "_blank",
            style = "background:#00B0FF; color:#0b1020; padding:6px 14px; border-radius:999px; font-size:12px; font-weight:700; text-decoration:none;") else NULL,
          if (nzchar(doi)) tags$a("DOI",
            href = doi_href(doi),
            target = "_blank",
            style = "background:#E040FB; color:#0b1020; padding:6px 14px; border-radius:999px; font-size:12px; font-weight:700; text-decoration:none;") else NULL
        )
      )
    }

    observeEvent(input$tl_click, {
      req(input$tl_click)
      tl <- tl_data()
      row <- tl[tl$rcd_form == input$tl_click, , drop = FALSE]
      if (nrow(row) == 0) return()
      row <- row[1, , drop = FALSE]

      lvl <- row$rcdome_level_name[1]
      col <- if (lvl %in% names(level_col)) level_col[[lvl]] else "#9E9E9E"
      yr_display <- if (is.na(row$yr[1])) "composite" else as.character(row$yr[1])
      is_composite <- !is.na(row$year[1]) && tolower(trimws(row$year[1])) == "composite"
      tl_logo_file <- file.path("data/RCD modulo/logo RCDs", paste0(input$tl_click, ".png"))
      tl_logo_url <- if (file.exists(tl_logo_file)) paste0("rcd_logos/", URLencode(paste0(input$tl_click, ".png"), reserved = TRUE)) else ""
      if (is_composite) {
        cit <- if (!is.na(row$reference_citation[1])) row$reference_citation[1] else ""
        m <- regmatches(cit, gregexpr("[A-Za-z][A-Za-z ]*? \\([^)]*PMID [0-9]+\\)", cit, perl = TRUE))[[1]]
        labels <- if (length(m) > 0) trimws(sub(" \\(.*", "", m)) else character(0)
        pmids <- if (length(m) > 0) sub(".*PMID ([0-9]+)\\).*", "\\1", m) else character(0)
        refs <- strsplit(gsub("[^0-9;]", "", row$primary_refs_pmids[1] %||% ""), ";")[[1]]
        refs <- refs[nzchar(refs)]
        if (length(pmids) == 0) pmids <- refs
        ref_btns <- paste(vapply(seq_along(pmids), function(k) {
          lab <- if (k <= length(labels) && nzchar(labels[k])) paste0(labels[k], " \u00b7 ") else ""
          sprintf("<a href='https://pubmed.ncbi.nlm.nih.gov/%s/' target='_blank' style='background:#00B0FF; color:#0b1020; padding:6px 14px; border-radius:999px; font-size:12px; font-weight:700; text-decoration:none; margin-right:10px;'>%sPMID %s</a>",
                  pmids[k], lab, pmids[k])
        }, character(1)), collapse = "")

        showModal(modalDialog(
          title = NULL, easyClose = TRUE, footer = NULL, size = "m",
          tags$div(style = "background:#0b1020; color:#e7e5e4; border-radius:12px; padding:26px 28px;",
            tags$div(style = "display:flex; align-items:center; gap:22px;",
              if (nzchar(tl_logo_url)) tags$img(src = tl_logo_url, style = "width:72px; height:72px; object-fit:contain;"),
              tags$div("composite", style = "font-size:38px; font-weight:800; color:#e7e5e4; line-height:1;"),
              tags$div(
                tags$div(HTML(paste0("<i>", input$tl_click, "</i>")), style = "font-size:22px; font-weight:700; color:#fff; margin-bottom:8px;"),
                tags$span(lvl, style = paste0("background:", col, "; color:#fff; padding:3px 12px; border-radius:999px; font-size:12px; font-weight:600;"))
              )
            ),
            tags$div("Composite pathway label", style = "color:#94a3b8; font-size:11px; letter-spacing:1px; text-transform:uppercase; margin:20px 0 6px;"),
            tags$div("Not a distinct RCD entity. Combines the constituent pathways below, retained per provenance policy.",
                     style = "font-size:14px; color:#d6d3d1; line-height:1.5;"),
            tags$div(style = "margin-top:16px;", HTML(ref_btns))
          )
        ))
        return()
      }

      disc_pmid <- if (!is.na(row$disc_pmid[1])) row$disc_pmid[1] else ""
      disc_title <- if (!is.na(row$disc_title[1])) row$disc_title[1] else ""
      disc_authors <- if (!is.na(row$disc_authors[1])) row$disc_authors[1] else ""
      disc_journal <- if (!is.na(row$disc_journal[1])) row$disc_journal[1] else ""
      disc_pubdate <- if (!is.na(row$disc_pubdate[1])) row$disc_pubdate[1] else ""
      disc_doi <- if (!is.na(row$disc_doi[1])) row$disc_doi[1] else ""

      fnd_pmid <- if (!is.na(row$pmid[1])) row$pmid[1] else ""
      fnd_title <- if (!is.na(row$title[1])) row$title[1] else ""
      fnd_authors <- if (!is.na(row$authors[1])) row$authors[1] else ""
      fnd_journal <- if (!is.na(row$journal[1])) row$journal[1] else ""
      fnd_pubdate <- if (!is.na(row$pubdate[1])) row$pubdate[1] else ""
      fnd_doi <- if (!is.na(row$doi[1])) row$doi[1] else ""

      showModal(modalDialog(
        title = NULL, easyClose = TRUE, footer = NULL, size = "m",
        tags$div(style = "background:#0b1020; color:#e7e5e4; border-radius:12px; padding:26px 28px;",
          tags$div(style = "display:flex; align-items:center; gap:22px;",
            if (nzchar(tl_logo_url)) tags$img(src = tl_logo_url, style = "width:72px; height:72px; object-fit:contain;"),
            tags$div(yr_display, style = "font-size:58px; font-weight:800; color:#e7e5e4; line-height:1;"),
            tags$div(
              tags$div(HTML(paste0("<i>", input$tl_click, "</i>")),
                       style = "font-size:22px; font-weight:700; color:#fff; margin-bottom:8px;"),
              tags$span(lvl, style = paste0("background:", col, "; color:#fff; padding:3px 12px; border-radius:999px; font-size:12px; font-weight:600;"))
            )
          ),
          tags$div("First described", style = "color:#94a3b8; font-size:11px; letter-spacing:1px; text-transform:uppercase; margin:20px 0 6px;"),
          ref_block(disc_pmid, disc_title, disc_authors, disc_journal, disc_pubdate, disc_doi),
          tags$div("Definition anchored to", style = "color:#94a3b8; font-size:11px; letter-spacing:1px; text-transform:uppercase; margin:20px 0 6px;"),
          ref_block(fnd_pmid, fnd_title, fnd_authors, fnd_journal, fnd_pubdate, fnd_doi)
        )
      ))
    })

  })
}
