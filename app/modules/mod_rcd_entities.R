# ─── Module: rcd_entities (Deep Dive: description + full-page cartoon + legend) ──
# Displays the 53 audited RCD descriptions verbatim with functional citation
# hyperlinks. The cartoon opens FULL PAGE (large modal) with a "Read legend"
# button; the legend opens its own modal.

RCD_ENT_DESC_DIR <- "data/RCD modulo/descricao RCDs"
RCD_ENT_REF_DIR  <- "data/RCD modulo/referencias"
RCD_ENT_FIG_DIR  <- "data/RCD modulo/figuras RCDs"
RCD_ENT_LEG_DIR  <- "data/RCD modulo/legendas"
RCD_ENT_LOGO_DIR <- "data/RCD modulo/logo RCDs"

# Case-insensitive map: lowercase entity name -> actual PNG filename in figuras RCDs
# (9 cartoons use Title Case while the description list uses lowercase; HTTP is case-sensitive)
RCD_ENT_FIG_LOOKUP <- {
  f <- list.files(RCD_ENT_FIG_DIR, pattern = "\\.png$")
  setNames(f, tolower(tools::file_path_sans_ext(f)))
}

LEVEL_COLORS <- c(
  L1 = "#FCBB18", L2 = "#5DADE2", L3 = "#58D68D", L4 = "#AF7AC5", L5 = "#F1948A"
)

mod_rcd_entities_ui <- function(id) {
  ns <- NS(id)

  # ── Background batch preload of ALL 53 cartoons on app startup ──────────
  # Non-blocking: new Image() downloads are async and staggered 120 ms apart.
  preload_ents <- sort(gsub("\\.txt$", "", list.files(RCD_ENT_DESC_DIR, pattern = "\\.txt$")))
  preload_pngs <- RCD_ENT_FIG_LOOKUP[tolower(preload_ents)]
  preload_urls <- paste0("rcd_figs/", URLencode(preload_pngs, reserved = TRUE))
  preload_js <- sprintf(
    "(function(){var u=%s;var i=0;function n(){if(i>=u.length)return;var m=new Image();m.src=u[i++];setTimeout(n,120);}n();})();",
    jsonlite::toJSON(preload_urls)
  )

  tagList(
    tags$script(HTML(preload_js)),
    div(style = "max-width:1100px; margin:0 auto; padding:20px;",
      h2("RCD Entity Deep Dive",
         style = "font-weight:700; color:#1c1917;"),
      p("Human-curated, anti-hallucination-audited narrative beyond the operational definition. Every claim is traceable: the in-text [n] points to its reference, and each DOI/PMID opens the source.",
        style = "color:#78716c; font-size:14px;"),
      selectizeInput(ns("entity"), NULL, choices = NULL, width = "100%",
                     options = list(placeholder = "Select or type an RCD entity")),
      uiOutput(ns("entity_view"))
    )
  )
}

mod_rcd_entities_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    ns <- session$ns

    entities <- reactive({
      f <- list.files(RCD_ENT_DESC_DIR, pattern = "\\.txt$")
      sort(gsub("\\.txt$", "", f))
    })

    observe({
      updateSelectizeInput(session, "entity",
                           choices = c("Select an RCD entity\u2026" = "", setNames(entities(), entities())),
                           server = TRUE)
    })

    ent_level <- reactive({
      req(input$entity)
      lv <- genes_df$rcdome_level[genes_df$rcd_form_canonical == input$entity]
      lv <- lv[!is.na(lv) & nzchar(lv)]
      if (length(lv) > 0) lv[[1]] else "L1"
    })

    desc_to_html <- function(x) {
      x <- trimws(x)
      blocks <- strsplit(x, "\n[ \t]*\n", perl = TRUE)[[1]]
      blocks <- blocks[nzchar(trimws(blocks))]
      parts <- lapply(blocks, function(b) {
        b <- trimws(gsub("[ \t]*\n[ \t]*", " ", b))
        if (grepl("^-{3,}$", b, perl = TRUE)) return(NULL)
        b <- sub("^#{1,6}\\s+", "", b, perl = TRUE)
        b <- gsub("\\[(\\d+)([0-9,\\-\\s]*)\\]",
                  '<a href="#ent-ref-\\1" class="ent-cite">[\\1\\2]</a>', b, perl = TRUE)
        b <- gsub("\\*\\*(.*?)\\*\\*", "<em>\\1</em>", b, perl = TRUE)
        b <- gsub("\\*(.*?)\\*", "<em>\\1</em>", b, perl = TRUE)
        tags$p(HTML(b),
               style = "font-size:15px; line-height:1.75; color:#1c1917; text-align:justify; margin:0 0 12px;")
      })
      parts <- Filter(Negate(is.null), parts)
      if (length(parts) == 0) {
        tags$p("Description not available.", style = "font-size:15px; color:#1c1917; margin:0;")
      } else {
        do.call(tagList, parts)
      }
    }

    ref_to_html <- function(x) {
      lines <- strsplit(x, "\n", perl = TRUE)[[1]]
      lines <- lines[nzchar(trimws(lines))]
      if (length(lines) == 0) return("")
      entries <- vapply(lines, function(ln) {
        n <- sub("^\\*{0,2}\\[?(\\d+)\\]?\\*{0,2}[.)]?.*$", "\\1", ln, perl = TRUE)
        ln2 <- gsub("\\*\\*(.*?)\\*\\*", "<em>\\1</em>", ln, perl = TRUE)
        ln2 <- gsub("\\*(.*?)\\*", "<em>\\1</em>", ln2, perl = TRUE)
        ln2 <- gsub("(10\\.\\d{4,9}/[A-Za-z0-9._()/-]+)",
                    '<a href="https://doi.org/\\1" target="_blank" rel="noopener" class="ent-ref-link">\\1</a>',
                    ln2, perl = TRUE)
        ln2 <- gsub("PMID:\\s*(\\d{7,8})",
                    '<a href="https://pubmed.ncbi.nlm.nih.gov/\\1" target="_blank" rel="noopener" class="ent-ref-link">PMID: \\1</a>',
                    ln2, perl = TRUE)
        paste0('<div id="ent-ref-', n, '" class="ent-ref-entry">', ln2, '</div>')
      }, character(1), USE.NAMES = FALSE)
      paste(entries, collapse = "")
    }

    output$entity_view <- renderUI({
      req(input$entity)
      ent <- input$entity
      lvl <- ent_level()
      lcol <- LEVEL_COLORS[[lvl]]
      if (is.null(lcol)) lcol <- "#FCBB18"

      logo_file <- file.path(RCD_ENT_LOGO_DIR, paste0(ent, ".png"))
      logo_url <- if (file.exists(logo_file)) {
        paste0("rcd_mod/logo%20RCDs/", URLencode(paste0(ent, ".png"), reserved = TRUE))
      } else ""

      # preload the cartoon image so the full-page modal opens instantly on click
      fig_file_pre <- file.path(RCD_ENT_FIG_DIR, RCD_ENT_FIG_LOOKUP[[tolower(ent)]])
      fig_url_pre  <- if (!is.null(fig_file_pre) && file.exists(fig_file_pre)) {
        paste0("rcd_figs/", URLencode(RCD_ENT_FIG_LOOKUP[[tolower(ent)]], reserved = TRUE))
      } else ""

      desc_path <- file.path(RCD_ENT_DESC_DIR, paste0(ent, ".txt"))
      ref_path  <- file.path(RCD_ENT_REF_DIR,  paste0(ent, ".txt"))
      desc <- if (file.exists(desc_path))
        paste(readLines(desc_path, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
        else "Description not available."
      ref <- if (file.exists(ref_path))
        paste(readLines(ref_path, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
        else NULL

      tags$div(
        tags$style(HTML("
          .ent-cite { color:#1d4ed8; text-decoration:none; border-bottom:1px dotted #1d4ed8; cursor:pointer; }
          .ent-ref-link { color:#1d4ed8; text-decoration:none; }
          .ent-ref-link:hover { text-decoration:underline; }
          .ent-ref-entry { margin-bottom:8px; font-size:13px; line-height:1.7; color:#1c1917; }
        ")),
        tags$div(style = "display:flex; align-items:center; gap:22px; margin:20px 0 16px;",
          if (nzchar(logo_url)) tags$img(src = logo_url, style = "width:120px; height:120px; object-fit:contain;"),
          tags$div(
            tags$div(ent, style = "font-size:26px; font-weight:800; color:#1c1917;"),
            tags$div(paste0("Ontological level ", lvl),
                     style = paste0("display:inline-block; margin-top:8px; padding:5px 16px; border-radius:999px; background:", lcol, "; color:#1c1917; font-weight:800;"))
          )
        ),
        if (nzchar(fig_url_pre)) tags$div(style = "margin:0 0 18px;",
          tags$div("Visual overview", style = "font-size:13px; font-weight:800; color:#1c1917; text-transform:uppercase; letter-spacing:0.4px; margin-bottom:8px;"),
          tags$img(src = fig_url_pre,
                   onclick = sprintf("Shiny.setInputValue('%s', Math.random(), {priority:'event'})", session$ns("open_cartoon")),
                   alt = paste0(ent, " mechanistic cartoon"),
                   style = "max-width:360px; width:100%; border-radius:8px; border:1px solid #e7e5e4; cursor:zoom-in; display:block; box-shadow:0 1px 3px rgba(0,0,0,0.08);")
        ),
        if (nzchar(fig_url_pre)) tagList(
          tags$img(src = fig_url_pre, style = "position:absolute; left:-9999px; width:1px; height:1px; opacity:0.01; pointer-events:none;"),
          tags$script(HTML(sprintf("(function(){var i=new Image(); i.src='%s';})();", fig_url_pre)))
        ),
        tags$div(style = "margin:4px 0 18px;",
          actionButton(ns("open_cartoon"), "View full schematic",
                       style = "background:#0b1020; color:#fff; border:none; border-radius:999px; padding:10px 22px; font-weight:700; cursor:pointer; margin-right:10px;"),
          actionButton(ns("open_legend"), "How to read this figure",
                       style = "background:#f1f5f9; color:#1c1917; border:none; border-radius:999px; padding:10px 22px; font-weight:700; cursor:pointer;")
        ),
        tags$h4("Scientific description", style = "color:#1c1917; margin:18px 0 8px;"),
        tags$div(style = "background:#f5f5f4; border-left:4px solid #c0392b; padding:16px 18px; border-radius:6px;",
                 desc_to_html(desc)),
        tags$div(style = "margin-top:16px;",
          tags$button(
            "View associated genes",
            onclick = sprintf("Shiny.setInputValue('%s', '%s', {priority:'event'})",
                              session$ns("view_genes"), gsub("'", "\u2019", ent, fixed = TRUE)),
            style = "padding:8px 14px; background:#0b1020; color:#fff; border:none; border-radius:8px; cursor:pointer; font-weight:600;"
          )
        ),
        tags$h4("References", style = "color:#c0392b; margin-top:16px;"),
        tags$div(style = "background:#fafaf9; border:1px solid #e7e5e4; border-radius:6px; padding:14px 18px; max-height:340px; overflow-y:auto;",
                 if (is.null(ref)) tags$p("No reference list available.") else HTML(ref_to_html(ref)))
      )
    })

    # ── Full-page cartoon (large modal) ─────────────────────────────────────
    observeEvent(input$open_cartoon, {
      req(input$entity)
      ent <- input$entity
      fig_file <- file.path(RCD_ENT_FIG_DIR, RCD_ENT_FIG_LOOKUP[[tolower(ent)]])
      fig_url <- if (!is.null(fig_file) && file.exists(fig_file)) {
        paste0("rcd_figs/", URLencode(RCD_ENT_FIG_LOOKUP[[tolower(ent)]], reserved = TRUE))
      } else ""
      showModal(modalDialog(
        title = tags$div(tags$strong(ent), style = "color:#1c1917;"),
        size = "l",
        easyClose = TRUE,
        tags$style(HTML("
          .modal-dialog{width:96vw !important;max-width:96vw !important;margin:2vh auto !important;}
          .modal-content{height:94vh !important;}
          .modal-body{max-height:78vh !important;overflow:auto !important;}
        ")),
        footer = tagList(
          downloadButton(ns("download_cartoon"), "Download PNG",
                         style = "background:#0b1020; color:#fff; border:none; border-radius:999px; padding:8px 18px; font-weight:700; cursor:pointer;"),
          actionButton(ns("read_legend_from_cartoon"), "Read legend",
                       style = "background:#FF9800; color:#0b1020; border:none; border-radius:999px; padding:8px 18px; font-weight:700; cursor:pointer;"),
          modalButton("Close")
        ),
        tags$div(style = "text-align:center; overflow:auto; max-height:76vh;",
          if (nzchar(fig_url)) tags$img(
            id = ns("cartoon_zoom"),
            src = fig_url,
            onclick = sprintf(
              "var i=document.getElementById('%s'); if(i.dataset.zoomed!=='1'){var b=i.offsetWidth||i.naturalWidth||600;i.dataset.zoomed='1';i.style.maxWidth='none';i.style.maxHeight='none';i.style.width=(b*1.5)+'px';i.style.cursor='zoom-out';}else{i.dataset.zoomed='0';i.style.maxWidth='100%%';i.style.maxHeight='80vh';i.style.width='auto';i.style.cursor='zoom-in';}",
              ns("cartoon_zoom")
            ),
            style = "max-width:100%; max-height:80vh; border-radius:8px; cursor:zoom-in; transition:width 0.25s ease, max-width 0.25s ease;"
          )
          else tags$p("Cartoon not available for this entity.", style = "color:#78716c;")
        )
      ))
    })

    # ── Watermarked download (© RCDome Group 2026. Cite us) ───────────────
    output$download_cartoon <- downloadHandler(
      filename = function() {
        ent <- input$entity
        paste0(gsub("[^A-Za-z0-9_-]", "_", ent), "_cartoon_RCDome_Group_2026.png")
      },
      content = function(file) {
        req(input$entity)
        ent <- input$entity
        png_name <- RCD_ENT_FIG_LOOKUP[[tolower(ent)]]
        req(!is.null(png_name))
        fig_file <- file.path(RCD_ENT_FIG_DIR, png_name)
        req(file.exists(fig_file))
        img <- magick::image_read(fig_file)
        w <- magick::image_info(img)$width
        size <- max(12, round(w * 0.015))
        off  <- max(8, round(w * 0.015))
        img <- magick::image_annotate(
          img,
          "\u00A9 RCDome Group 2026. Cite us",
          gravity = "southeast",
          location = paste0("+", off, "+", off),
          size = size,
          color = "white",
          boxcolor = "rgba(0,0,0,0.35)"
        )
        magick::image_write(img, file, format = "png")
      }
    )

    # ── Legend (modal) ──────────────────────────────────────────────────────
    show_legend_modal <- function() {
      req(input$entity)
      ent <- input$entity
      leg_file <- file.path(RCD_ENT_LEG_DIR, paste0(ent, ".txt"))
      leg <- if (file.exists(leg_file))
        paste(readLines(leg_file, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
        else "Legend not available."
      showModal(modalDialog(
        title = tags$div(tags$strong(paste0(ent, " \u2014 Legend")), style = "color:#1c1917;"),
        size = "l",
        easyClose = TRUE,
        footer = modalButton("Close"),
        tags$p(HTML(gsub("\n", "<br>", leg, fixed = TRUE)),
               style = "font-size:14px; line-height:1.8; color:#1c1917;")
      ))
    }

    observeEvent(input$open_legend, {
      show_legend_modal()
    })
    observeEvent(input$read_legend_from_cartoon, {
      show_legend_modal()
    })

    observeEvent(input$view_genes, {
      req(input$view_genes)
      gene_catalog_entity_rv(input$view_genes)
      shinyjs::runjs("$('a[data-value=\"Gene Catalog\"]').tab('show');")
    })
  })
}
