# ─── Module: rcd_grid ────────────────────────────────────────────────────────
# Exact replica of RCD honeycomb from OncoSurvXai.
# SVG hexagons with logos + text, click → modal with description + figure.
# Auto-scales to fit any screen width via ResizeObserver.

RCD_DESC_DIR <- "data/RCD modulo/descricao RCDs"
RCD_LOGO_DIR <- "data/RCD modulo/logo RCDs"
RCD_FIG_DIR  <- "data/RCD modulo/figuras RCDs"
RCD_VIDEO_DIR <- "data/RCD modulo/videos"
RCD_REF_DIR   <- "data/RCD modulo/referencias"
RCD_SUMMARY_DIR <- "data/RCD modulo/resumo"

mod_rcd_grid_ui <- function(id) {
  ns <- NS(id)
  tagList(
    tags$div(
      style = "padding: 10px 0; background: #ffffff; border-radius: 8px;",
      tags$h2(
        tags$img(src = "rcd_mod/cell.png", style = "height:32px; width:auto; vertical-align:middle; margin-right:8px;"),
        "Regulated Cell Death (RCD) entities",
        style = "font-weight:700; text-align:center; color:#1c1917; margin-bottom:5px;"
      ),
      tags$p("Click an RCD entity to view its description and schematic illustration.",
             style = "text-align:center; color:#a8a29e; font-size:15px; margin-bottom:10px;"),
      uiOutput(ns("rcd_search_ui")),
      uiOutput(ns("honeycomb"))
    )
  )
}

mod_rcd_grid_server <- function(id) {
  moduleServer(id, function(input, output, session) {

    rcd_normalize <- function(x) {
      x <- tolower(x)
      x <- gsub("_", " ", x)
      x <- gsub("\\s*\\([^)]*\\)", "", x, perl = TRUE)
      x <- gsub("\\s+", " ", x, perl = TRUE)
      trimws(x)
    }

    # Build the entity detail from the RCDome Decoder (53 operational definitions)
    build_decoder_desc <- function(dr) {
      p <- function(x) {
        if (is.null(x) || length(x) == 0 || is.na(x) || nchar(trimws(as.character(x))) == 0) "—" else trimws(as.character(x))
      }
      paste(c(
        "## Operational definition", p(dr$operational_definition),
        "## Core mechanism", p(dr$core_mechanism),
        "## Key molecules", p(dr$key_molecules),
        "## Ontology",
        paste0("Category: ", p(dr$category), "  ·  Hard gate: ", p(dr$hard_gate_status)),
        paste0("Relationship: ", p(dr$relationship_type), if (p(dr$parent_entity) != "—") paste0(" → ", p(dr$parent_entity)) else ""),
        paste0("Species scope: ", p(dr$species_scope), "  ·  Evidence maturity: ", p(dr$evidence_maturity), "  ·  Replication: ", p(dr$independent_replication)),
        "## Scoring (Rodrigues RS1–RS6)",
        paste0("RS1=", p(dr$RS1), "  RS2=", p(dr$RS2), "  RS3=", p(dr$RS3), "  RS4=", p(dr$RS4), "  RS5=", p(dr$RS5), "  RS6=", p(dr$RS6), "  →  S = ", p(dr$S)),
        "## Provenance",
        paste0("Founding PMID: ", p(dr$founding_pmid), "  ·  Review: ", p(dr$review_status), "  ·  Verdict: ", p(dr$validation_verdict))
      ), collapse = "\n\n")
    }

    # Render **bold** / *italic* markers from reference files as HTML.
    ref_to_html <- function(x) {
      x <- gsub("\\*\\*(.*?)\\*\\*", "<strong>\\1</strong>", x, perl = TRUE)
      x <- gsub("\\*(.*?)\\*", "<em>\\1</em>", x, perl = TRUE)
      x
    }

    # Split description into paragraphs; "##" line becomes a subheading.
    desc_to_html <- function(x) {
      x <- trimws(x)
      blocks <- strsplit(x, "\n[ \t]*\n", perl = TRUE)[[1]]
      blocks <- blocks[nzchar(trimws(blocks))]
      parts <- lapply(blocks, function(b) {
        b <- trimws(gsub("[ \t]*\n[ \t]*", " ", b))
        if (grepl("^##\\s+", b, perl = TRUE)) {
          tags$p(tags$strong(sub("^##\\s+", "", b, perl = TRUE)),
                 style = "font-size:15px; font-weight:700; color:#1c1917; margin:0 0 10px;")
        } else {
          tags$p(b, style = "font-size:15px; line-height:1.75; color:#1c1917; text-align:justify; margin:0 0 12px;")
        }
      })
      if (length(parts) == 0) {
        tags$p("Description not available.", style = "font-size:15px; color:#1c1917; margin:0;")
      } else {
        do.call(tagList, parts)
      }
    }

    rcd_colors <- c(
      "#e74c3c", "#e67e22", "#f39c12", "#8e44ad", "#2ecc71",
      "#d35400", "#c0392b", "#16a085", "#2980b9", "#27ae60",
      "#f1c40f", "#9b59b6", "#1abc9c", "#e91e63", "#00bcd4",
      "#ff5722", "#4caf50", "#ff9800", "#607d8b", "#795548",
      "#3f51b5", "#009688", "#cddc39", "#ff4081", "#536dfe"
    )

    rcd_pathways <- reactive({
      desc_dir <- RCD_DESC_DIR
      logo_dir <- RCD_LOGO_DIR
      fig_dir  <- RCD_FIG_DIR

      # Use the 53 RCD-related entities from the decoder (not the static .txt files)
      if (exists("decoder_df", envir = .GlobalEnv) && nrow(decoder_df) > 0) {
        base_names <- as.character(decoder_df$rcd_form)
      } else {
        desc_files <- list.files(desc_dir, pattern = "\\.txt$")
        base_names <- gsub("\\.txt$", "", desc_files)
      }

      logo_files <- list.files(logo_dir, pattern = "\\.JPG$", ignore.case = TRUE)
      logo_bases <- gsub("\\.JPG$", "", logo_files, ignore.case = TRUE)
      logo_norm  <- rcd_normalize(logo_bases)

      fig_files <- list.files(fig_dir, pattern = "\\.png$", ignore.case = TRUE)
      fig_bases <- gsub("\\.png$", "", fig_files, ignore.case = TRUE)
      fig_norm  <- rcd_normalize(fig_bases)

      video_files <- list.files(RCD_VIDEO_DIR, pattern = "\\.mp4$", ignore.case = TRUE)
      video_norm  <- rcd_normalize(gsub("\\.mp4$", "", video_files, ignore.case = TRUE))

      ref_files <- list.files(RCD_REF_DIR, pattern = "\\.txt$", ignore.case = TRUE)
      ref_bases <- gsub("\\.txt$", "", ref_files, ignore.case = TRUE)
      ref_norm  <- rcd_normalize(ref_bases)

      sum_files <- list.files(RCD_SUMMARY_DIR, pattern = "\\.txt$", ignore.case = TRUE)
      sum_bases <- gsub("\\.txt$", "", sum_files, ignore.case = TRUE)
      sum_norm  <- rcd_normalize(sum_bases)

      results <- list()
      for (bn in base_names) {
        bn_norm <- rcd_normalize(bn)

        logo_idx <- which(logo_norm == bn_norm)
        logo_url <- if (length(logo_idx) > 0) paste0("rcd_logos/", logo_files[logo_idx[1]]) else NULL

        fig_idx <- which(fig_norm == bn_norm)
        fig_url <- if (length(fig_idx) > 0) paste0("rcd_figs/", fig_files[fig_idx[1]]) else NULL

        vid_idx <- which(video_norm == bn_norm)
        video_url <- if (length(vid_idx) > 0) paste0("rcd_videos/", video_files[vid_idx[1]]) else NULL

        decoder_row <- if (exists("decoder_df", envir = .GlobalEnv) && nrow(decoder_df) > 0) {
          decoder_df[tolower(trimws(decoder_df$rcd_form)) == tolower(trimws(bn)), , drop = FALSE]
        } else data.frame()
        desc_text <- if (nrow(decoder_row) == 1) {
          build_decoder_desc(decoder_row[1, , drop = FALSE])
        } else {
          desc_path <- file.path(desc_dir, paste0(bn, ".txt"))
          if (file.exists(desc_path)) {
            txt <- tryCatch(
              paste(readLines(desc_path, warn = FALSE, encoding = "UTF-8"), collapse = "\n"),
              error = function(e) "Description not available."
            )
            if (nchar(trimws(txt)) == 0) "Description not available." else txt
          } else "Description not available."
        }

        ref_idx <- which(ref_norm == bn_norm)
        ref_text <- if (length(ref_idx) > 0) {
          ref_path <- file.path(RCD_REF_DIR, ref_files[ref_idx[1]])
          txt <- tryCatch(
            paste(readLines(ref_path, warn = FALSE, encoding = "UTF-8"), collapse = "\n"),
            error = function(e) NULL
          )
          if (is.null(txt) || nchar(trimws(txt)) == 0) NULL else txt
        } else NULL

        sum_idx <- which(sum_norm == bn_norm)
        sum_text <- if (length(sum_idx) > 0) {
          sum_path <- file.path(RCD_SUMMARY_DIR, sum_files[sum_idx[1]])
          txt <- tryCatch(
            paste(readLines(sum_path, warn = FALSE, encoding = "UTF-8"), collapse = "\n"),
            error = function(e) NULL
          )
          if (is.null(txt) || nchar(trimws(txt)) == 0) NULL else txt
        } else NULL

        results[[length(results) + 1]] <- list(
          name = bn, logo_url = logo_url, desc = desc_text, fig_url = fig_url,
          video_url = video_url, ref = ref_text, summary = sum_text
        )
      }
      results
    })

    # Search dropdown, rendered with its choices so it is always populated.
    # Native <select> (selectize = FALSE) is bulletproof and scrolls on any browser.
    output$rcd_search_ui <- renderUI({
      pathways <- rcd_pathways()
      nm <- if (length(pathways) > 0) vapply(pathways, function(x) x$name, character(1)) else character(0)
      tags$div(
        style = "max-width: 460px; margin: 0 auto 16px;",
        selectizeInput(
          session$ns("rcd_search"),
          label = NULL,
          choices = c("Select an RCD entity…" = "", setNames(nm, nm)),
          selected = "",
          width = "100%",
          options = list(placeholder = "Select or type an RCD entity", create = rcdome_create_js)
        )
      )
    })

    # Selecting an entity in the search box opens the same modal as clicking its cell.

    observeEvent(input$rcd_search, {
      req(input$rcd_search)
      if (!nzchar(input$rcd_search)) return()
      nm <- vapply(rcd_pathways(), function(x) x$name, character(1))
      if (!input$rcd_search %in% nm) {
        showNotification(paste0("Sorry, '", input$rcd_search, "' is not in the RCDome database (53 RCD-related entities)."), type = "error")
        updateSelectizeInput(session, "rcd_search",
                             choices = c("Select an RCD entity…" = "", setNames(nm, nm)),
                             selected = "", server = FALSE)
        return()
      }
      safe <- gsub("'", "\\\\'", input$rcd_search)
      shinyjs::runjs(sprintf(
        "Shiny.setInputValue('%s', '%s', {priority: 'event'})",
        session$ns("rcd_clicked"), safe
      ))
      updateSelectizeInput(session, "rcd_search",
                           choices = c("Select an RCD entity…" = "", setNames(nm, nm)),
                           selected = "", server = FALSE)
    })

    output$honeycomb <- renderUI({
      pathways <- rcd_pathways()
      if (length(pathways) == 0) {
        return(tags$div(
          style = "padding:40px; text-align:center; color:#e74c3c;",
          tags$p("No RCD pathways found.")
        ))
      }

      container_id <- session$ns("honeycomb_container")
      inner_id     <- session$ns("honeycomb_inner")

      pattern <- c(4, 3, 4, 3, 4, 3, 4)
      idx <- 1
      columns <- list()

      for (col_num in seq_along(pattern)) {
        n_cells   <- pattern[col_num]
        is_offset <- (col_num %% 2 == 0)

        col_cells <- list()
        for (j in seq_len(n_cells)) {
          if (idx > length(pathways)) break

          p <- pathways[[idx]]
          color <- rcd_colors[[idx]]
          safe_name <- gsub("'", "\\\\'", p$name)
          name <- p$name
          nch  <- nchar(name)
          three_lines <- FALSE
          two_lines   <- FALSE
          line1 <- name; line2 <- ""; line3 <- ""

          if (nch > 28) {
            two_lines <- TRUE
            mid   <- floor(nch / 2)
            chars <- strsplit(name, "")[[1]]
            spaces <- which(chars == " ")
            if (length(spaces) > 0) {
              split_at <- spaces[which.min(abs(spaces - mid))]
              line1 <- substr(name, 1, split_at - 1)
              line2 <- trimws(substr(name, split_at + 1, nch))
            }
            fs <- "10px"
          } else if (nch > 18) {
            fs <- "12px"
          } else {
            fs <- "13px"
          }

          logo_src <- if (!is.null(p$logo_url)) p$logo_url else ""

          if (three_lines) {
            svg_html <- HTML(sprintf(
              '<svg width="170" height="195" viewBox="0 0 170 195" xmlns="http://www.w3.org/2000/svg" style="display:block;pointer-events:none;overflow:visible;"><defs><clipPath id="c%d"><circle cx="85" cy="102" r="50"/></clipPath></defs><circle cx="85" cy="102" r="53" fill="white" stroke="white" stroke-width="3"/><image href="%s" x="48" y="62" width="74" height="74" clip-path="url(#c%d)" preserveAspectRatio="xMidYMid slice"/><text x="85" y="20" font-size="%s" font-weight="800" fill="#1c1917" text-anchor="middle" font-family="Calibri, Lucida Casual, cursive, sans-serif" letter-spacing="0.2">%s</text><text x="85" y="33" font-size="%s" font-weight="800" fill="#1c1917" text-anchor="middle" font-family="Calibri, Lucida Casual, cursive, sans-serif" letter-spacing="0.2">%s</text><text x="85" y="46" font-size="%s" font-weight="800" fill="#1c1917" text-anchor="middle" font-family="Calibri, Lucida Casual, cursive, sans-serif" letter-spacing="0.2">%s</text></svg>',
              idx, logo_src, idx, fs, line1, fs, line2, fs, line3))
          } else if (two_lines) {
            svg_html <- HTML(sprintf(
              '<svg width="170" height="195" viewBox="0 0 170 195" xmlns="http://www.w3.org/2000/svg" style="display:block;pointer-events:none;overflow:visible;"><defs><clipPath id="c%d"><circle cx="85" cy="102" r="50"/></clipPath></defs><circle cx="85" cy="102" r="53" fill="white" stroke="white" stroke-width="3"/><image href="%s" x="48" y="62" width="74" height="74" clip-path="url(#c%d)" preserveAspectRatio="xMidYMid slice"/><text x="85" y="26" font-size="%s" font-weight="800" fill="#1c1917" text-anchor="middle" font-family="Calibri, Lucida Casual, cursive, sans-serif" letter-spacing="0.2">%s</text><text x="85" y="39" font-size="%s" font-weight="800" fill="#1c1917" text-anchor="middle" font-family="Calibri, Lucida Casual, cursive, sans-serif" letter-spacing="0.2">%s</text></svg>',
              idx, logo_src, idx, fs, line1, fs, line2))
          } else {
            svg_html <- HTML(sprintf(
              '<svg width="170" height="195" viewBox="0 0 170 195" xmlns="http://www.w3.org/2000/svg" style="display:block;pointer-events:none;overflow:visible;"><defs><clipPath id="c%d"><circle cx="85" cy="102" r="50"/></clipPath></defs><circle cx="85" cy="102" r="53" fill="white" stroke="white" stroke-width="3"/><image href="%s" x="48" y="62" width="74" height="74" clip-path="url(#c%d)" preserveAspectRatio="xMidYMid slice"/><text x="85" y="39" font-size="%s" font-weight="800" fill="#1c1917" text-anchor="middle" font-family="Calibri, Lucida Casual, cursive, sans-serif" letter-spacing="0.2">%s</text></svg>',
              idx, logo_src, idx, fs, line1))
          }

          cell <- tags$div(
            class = "honeycomb-cell",
            style = paste0("animation-delay: ", (idx - 1) * 0.04, "s;"),
            onclick = sprintf("Shiny.setInputValue('%s', '%s', {priority: 'event'})",
                              session$ns("rcd_clicked"), safe_name),
            title = p$name,
            svg_html
          )

          col_cells[[length(col_cells) + 1]] <- cell
          idx <- idx + 1
        }

        col_class <- if (is_offset) "honeycomb-column offset" else "honeycomb-column"
        columns[[length(columns) + 1]] <- tags$div(class = col_class, col_cells)
      }

      tagList(
        tags$style(HTML("
          .honeycomb-container {
            width: 100%; max-width: 100%; overflow: hidden;
            padding: 20px 10px 50px; margin: 0 auto;
            position: relative; box-sizing: border-box;
          }
          .honeycomb-inner {
            display: flex; flex-direction: row;
            justify-content: flex-start; align-items: flex-start;
            width: max-content; max-width: none; margin: 0;
            transform-origin: top left;
          }
          .honeycomb-column {
            display: flex; flex-direction: column; align-items: center;
            width: 170px; flex-shrink: 0; margin-right: -14px;
          }
          .honeycomb-column:last-child { margin-right: 0; }
          .honeycomb-column.offset { margin-top: 100px; }
          .honeycomb-cell {
            width: 170px; height: 195px; cursor: pointer;
            flex-shrink: 0; z-index: 1;
            opacity: 0;
            transform: translateY(20px);
            animation: hcFadeIn 0.5s ease-out forwards;
          }
          @keyframes hcFadeIn {
            to { opacity: 1; transform: translateY(0); }
          }
          .honeycomb-cell:hover {
            transform: scale(1.12) !important; z-index: 10;
            filter: drop-shadow(0 8px 25px rgba(0,0,0,0.3)) brightness(1.08);
            transition: transform 0.25s ease, filter 0.25s ease;
          }
          .honeycomb-cell:active { transform: scale(0.96) !important; }
          @media (max-width: 1100px) {
            .honeycomb-column { width: 130px; margin-right: -10px; }
            .honeycomb-cell { width: 130px; height: 149px; }
            .honeycomb-cell svg { width: 130px; height: 149px; }
            .honeycomb-column.offset { margin-top: 78px; }
          }
          @media (max-width: 850px) {
            .honeycomb-column { width: 100px; margin-right: -7px; }
            .honeycomb-cell { width: 100px; height: 115px; }
            .honeycomb-cell svg { width: 100px; height: 115px; }
            .honeycomb-column.offset { margin-top: 60px; }
          }
        ")),
        tags$div(id = container_id, class = "honeycomb-container",
          tags$div(id = inner_id, class = "honeycomb-inner", columns)
        ),
        tags$script(HTML(sprintf(
          "(function() {
            const container = document.getElementById('%s');
            const inner     = document.getElementById('%s');
            if (!container || !inner) return;
            let lastWidth = -1;
            function scaleHoneycomb(force) {
              const cw = Math.round(container.clientWidth);
              if (!cw) return;
              if (!force && cw === lastWidth) return;
              lastWidth = cw;
              inner.style.transform = 'scale(1)';
              inner.style.marginLeft = '0px';
              const iw = inner.scrollWidth, ih = inner.scrollHeight;
              if (!iw) return;
              const avail = Math.max(0, cw - 20);
              const scale = Math.min(1, avail / iw);
              inner.style.marginLeft = Math.max(0, (avail - iw * scale) / 2) + 'px';
              inner.style.transform = 'scale(' + scale + ')';
              container.style.height = Math.ceil(ih * scale + 70) + 'px';
            }
            new ResizeObserver(function() { scaleHoneycomb(false); }).observe(container);
            $(document).on('shown.bs.tab', 'a[data-toggle=\"tab\"], a[data-bs-toggle=\"tab\"]', function() { lastWidth = -1; setTimeout(function() { scaleHoneycomb(true); }, 40); });
            $(document).on('shiny:value', function(event) { if (event.name === '%s') { lastWidth = -1; setTimeout(function() { scaleHoneycomb(true); }, 40); } });
            window.addEventListener('resize', function() { lastWidth = -1; scaleHoneycomb(true); });
            setTimeout(function() { scaleHoneycomb(true); }, 50);
            setTimeout(function() { scaleHoneycomb(true); }, 300);
          })();",
          container_id, inner_id, session$ns("honeycomb")
        )))
      )
    })

    observeEvent(input$rcd_clicked, {
      req(input$rcd_clicked)
      pathways <- rcd_pathways()
      p <- NULL
      for (pw in pathways) {
        if (identical(pw$name, input$rcd_clicked)) { p <- pw; break }
      }
      req(p)

      fig_dl <- if (!is.null(p$fig_url)) paste0("RCDome_", p$name, "_fig.png") else NULL
      vid_dl <- if (!is.null(p$video_url)) paste0("RCDome_", p$name, "_video.mp4") else NULL

      media_html <- if (!is.null(p$fig_url)) {
        safe_url <- gsub("'", "\\\\'", p$fig_url)
        fig_el <- tags$img(src = p$fig_url,
          onclick = sprintf("Shiny.setInputValue('%s', '%s', {priority: 'event'})",
                            session$ns("rcd_fig_clicked"), safe_url),
          style = "width:100%; max-width:550px; border-radius:10px; box-shadow: 0 4px 15px rgba(0,0,0,0.12); cursor:pointer;")

        if (!is.null(p$video_url)) {
          tags$div(
            id = "rcd_media_row",
            style = "display:flex; align-items:center; justify-content:center; gap:12px; margin-top:15px; flex-direction:row-reverse;",
            tags$button(type = "button", class = "rcd-media-toggle",
              onclick = sprintf(
                "var f=document.getElementById('rcd_fig_holder');var v=document.getElementById('rcd_vid_holder');var ve=document.getElementById('rcd_vid_el');var dl=document.getElementById('rcd_dl_btn');var row=document.getElementById('rcd_media_row');if(f.style.display!=='none'){f.style.display='none';v.style.display='block';this.textContent='◀';this.title='Ver figura';row.style.flexDirection='row';if(dl){dl.setAttribute('href','%s');dl.setAttribute('download','%s');dl.textContent='Download MP4';}}else{if(ve&&ve.pause){ve.pause();}f.style.display='block';v.style.display='none';this.textContent='▶';this.title='Ver vídeo';row.style.flexDirection='row-reverse';if(dl){dl.setAttribute('href','%s');dl.setAttribute('download','%s');dl.textContent='Download PNG';}}",
                p$video_url, vid_dl, p$fig_url, fig_dl),
              title = "Ver vídeo", "▶"),
            tags$div(
              style = "flex:1; text-align:center;",
              tags$div(id = "rcd_fig_holder", fig_el),
              tags$div(id = "rcd_vid_holder", style = "display:none;",
                tags$video(id = "rcd_vid_el", src = p$video_url, controls = TRUE,
                           style = "width:100%; max-width:550px; border-radius:10px;"))
            )
          )
        } else {
          tags$div(style = "text-align:center; margin-top:15px;",
            fig_el,
            tags$p("🖱 Click image to enlarge", style = "color:#a8a29e; font-size:12px; margin-top:6px;"))
        }
      } else {
        tags$p("Schematic image not available.", style = "color:#a8a29e; font-style:italic; text-align:center; padding:20px;")
      }

      desc_block <- if (!is.null(p$summary)) {
        tags$div(
          style = "background:#f5f5f4; border-left:4px solid #c0392b; padding:15px 18px; border-radius:6px; margin-bottom:15px;",
          tags$div(
            style = "display:flex; gap:8px; margin-bottom:12px;",
            tags$button(type = "button", class = "rcd-view-toggle active", id = "rcd_view_summary_btn",
              onclick = "document.getElementById('rcd_desc_summary').style.display='block';document.getElementById('rcd_desc_detail').style.display='none';this.classList.add('active');document.getElementById('rcd_view_detail_btn').classList.remove('active');",
              "Summary"),
            tags$button(type = "button", class = "rcd-view-toggle", id = "rcd_view_detail_btn",
              onclick = "document.getElementById('rcd_desc_detail').style.display='block';document.getElementById('rcd_desc_summary').style.display='none';this.classList.add('active');document.getElementById('rcd_view_summary_btn').classList.remove('active');",
              "Detailed")
          ),
          tags$div(id = "rcd_desc_summary", desc_to_html(p$summary)),
          tags$div(id = "rcd_desc_detail", style = "display:none;", desc_to_html(p$desc))
        )
      } else {
        tags$div(
          style = "background:#f5f5f4; border-left:4px solid #c0392b; padding:15px 18px; border-radius:6px; margin-bottom:15px;",
          desc_to_html(p$desc)
        )
      }

      ref_block <- if (!is.null(p$ref)) {
        tags$div(
          style = "margin-bottom:15px;",
          tags$button(
            type = "button",
            class = "rcd-ref-toggle",
            onclick = "var h=document.getElementById('rcd_ref_holder');var b=this;if(h.style.display==='none'){h.style.display='block';b.textContent='Hide references';}else{h.style.display='none';b.textContent='Show references';}",
            "Show references"
          ),
          tags$div(
            id = "rcd_ref_holder",
            style = "display:none; margin-top:10px; background:#f5f5f4; border:1px solid #e7e5e4; border-radius:6px; padding:14px 18px; max-height:280px; overflow-y:auto;",
            tags$div(
              style = "white-space: pre-wrap; font-size:13px; line-height:1.7; color:#1c1917;",
              HTML(ref_to_html(p$ref))
            )
          )
        )
      } else NULL

      showModal(modalDialog(
        title = tags$div(
          style = "display:flex; align-items:center; gap:12px;",
          tags$img(src = "rcd_mod/cell.png", style = "height:26px; width:auto; margin-right:8px;"),
          tags$h3(p$name, style = "color:#1c1917; margin:0; font-weight:700;")
        ),
        tags$div(
          style = "max-height:70vh; overflow-y:auto; padding-right:5px;",
          desc_block,
          ref_block,
          tags$h4(icon("image"), " Schematic Representation", style = "color:#c0392b; margin-top:5px;"),
          media_html
        ),
        size = "l", easyClose = TRUE,
        footer = tagList(
          if (!is.null(fig_dl) || !is.null(vid_dl)) tags$a(
            id = "rcd_dl_btn",
            href = p$fig_url %||% p$video_url,
            download = fig_dl %||% vid_dl,
            class = "rcd-download-btn",
            if (!is.null(fig_dl)) "Download PNG" else "Download MP4"
          ),
          modalButton("Close", icon = icon("times"))
        )
      ))
    })

    observeEvent(input$rcd_fig_clicked, {
      req(input$rcd_fig_clicked)
      url <- input$rcd_fig_clicked
      shinyjs::runjs(sprintf("
        (function(){
          var old = document.getElementById('img-viewer');
          if (old) old.remove();
          var ov = document.createElement('div');
          ov.id = 'img-viewer';
          ov.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;' +
            'background:rgba(0,0,0,0.88);z-index:99999999;display:flex;align-items:center;justify-content:center;';
          var img = document.createElement('img');
          img.src = '%s';
          img.style.cssText = 'max-width:90vw;max-height:90vh;object-fit:contain;box-shadow:0 0 40px rgba(0,0,0,0.5);';
          var cls = document.createElement('button');
          cls.textContent = '\\u2715';
          cls.style.cssText = 'position:fixed;top:18px;right:24px;font-size:30px;color:white;background:none;border:none;cursor:pointer;z-index:100000000;line-height:1;';
          cls.onclick = function(){ ov.remove(); };
          ov.onclick = function(e){ if(e.target === ov) ov.remove(); };
          ov.appendChild(img);
          ov.appendChild(cls);
          document.body.appendChild(ov);
          document.addEventListener('keydown', function esc(e){
            if(e.key === 'Escape'){ ov.remove(); document.removeEventListener('keydown', esc); }
          });
        })();
      ", url))
    })

  })
}
