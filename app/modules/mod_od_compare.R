# ─── Module: od_compare (Operational Definition Comparator) ─────────────────
# Side-by-side comparison of RCD entities' operational definitions, reusing the
# same decoder sections/fields as the Operational Definitions browser.

mod_od_compare_ui <- function(id) {
  ns <- NS(id)
  div(class = "about-content",
    div(class = "hero", style = "grid-template-columns:1fr; padding:18px 0 24px;",
      div(
        div(class = "eyebrow", style = "text-transform:none; font-size:24px;",
            HTML(paste0(rcdome_span(), " \u00b7 Scientific Module"))),
        h1(HTML(paste0(rcdome_span(), " Operational Definition Comparator"))),
        div(class = "lede",
            HTML("The operational definitions of the 53 RCD entities overlap heavily in wording, and their differences are what make each entity distinct. Compare two or more entities side-by-side to disambiguate similar modalities (apoptosis vs necroptosis vs ferroptosis), understand their ontological relations (subtype, trigger, parent), weigh their evidence maturity and NCCD status, and audit the definitions for consistency. Differing values are highlighted so the contrasts stand out immediately."))
      )
    ),
    fluidRow(
      column(12,
        selectizeInput(ns("cmp_entities"), "Select 2 to 4 RCD entities to compare",
                       choices = NULL, multiple = TRUE, width = "100%",
                       options = list(maxItems = 4, placeholder = "Select RCD entities\u2026")),
        radioButtons(ns("cmp_mode"), "Display",
          choices = c("All fields" = "all",
                      "Differing fields only" = "diff",
                      "Identical fields only" = "same"),
          selected = "all", inline = TRUE),
        uiOutput(ns("cmp_table")),
        uiOutput(ns("cmp_download_ui"))
      )
    )
  )
}

mod_od_compare_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    ns <- session$ns

    observe({
      req(exists("decoder_df", inherits = TRUE))
      updateSelectizeInput(session, "cmp_entities",
                           choices = sort(unique(decoder_df$rcd_form)), server = TRUE)
    })

    render_field <- function(r, f) {
      v <- r[[f]]
      if (is.null(v) || is.na(v) || as.character(v) == "") return("")
      if (f %in% c("primary_refs_pmids", "secondary_refs_pmids")) {
        pmids <- trimws(strsplit(as.character(v), ";")[[1]])
        pmids <- pmids[pmids != ""]
        if (length(pmids) == 0) return("")
        return(paste(vapply(pmids, function(p) {
          paste0("<a href='https://pubmed.ncbi.nlm.nih.gov/", p, "/' target='_blank'>PMID ", p, "</a>")
        }, character(1)), collapse = " "))
      }
      if (f %in% c("founding_pmid", "reference_pmid", "primary_discovery_reference")) {
        return(paste0("<a href='https://pubmed.ncbi.nlm.nih.gov/", as.character(v),
                      "/' target='_blank'>PMID ", as.character(v), "</a>"))
      }
      if (f %in% c("source_databases", "source_channels")) {
        parts <- trimws(strsplit(as.character(v), ";")[[1]])
        parts <- parts[parts != ""]
        if (length(parts) == 0) return("")
        return(paste(vapply(parts, function(p) {
          paste0("<span style='display:inline-block; background:#f1f5f9; color:#475569; border:1px solid #e2e8f0; border-radius:999px; padding:2px 8px; margin:0 4px 4px 0; font-size:11px;'>", p, "</span>")
        }, character(1)), collapse = ""))
      }
      if (f == "reference_citation") {
        pmid <- r$reference_pmid %||% ""
        if (!nzchar(pmid)) pmid <- r$founding_pmid %||% ""
        if (nzchar(pmid)) {
          return(paste0("<a href='https://pubmed.ncbi.nlm.nih.gov/", pmid, "/' target='_blank'>", as.character(v), "</a>"))
        }
        return(as.character(v))
      }
      as.character(v)
    }

    build_cmp_table <- function(ents, mode = "all") {
      rows <- decoder_df[decoder_df$rcd_form %in% ents, ]
      rownames(rows) <- rows$rcd_form
      desc_map <- get0("DECODER_DESC", inherits = TRUE, ifnotfound = list())
      lv <- get0("genes_df", inherits = TRUE)
      level_col <- function(e) {
        if (is.null(lv)) return("#FF6D00")
        v <- unique(lv$rcdome_level[lv$rcd_form_canonical == e])
        v <- v[!is.na(v)]
        OD_LEVEL_COLORS[[if (length(v)) v[1] else "L5"]] %||% "#FF6D00"
      }
      header_cells <- c("<th style='text-align:left; vertical-align:top;'>Field</th>")
      for (e in ents) {
        r <- rows[e, ]
        col <- level_col(e)
        nccd <- r$galluzzi_nccd_status %||% ""
        header_cells <- c(header_cells, paste0(
          "<th style='text-align:left; vertical-align:top;'>",
          "<span style='display:inline-block; width:10px; height:10px; border-radius:50%; background:", col, "; margin-right:6px;'></span>",
          "<strong>", e, "</strong>",
          if (nzchar(nccd)) paste0("<div style='font-size:10px; color:#a8a29e; font-weight:400;'>", nccd, "</div>") else "",
          "</th>"
        ))
      }
      all_fields <- unlist(unname(OD_SECTIONS), use.names = FALSE)
      body_rows <- character(0)
      for (f in all_fields) {
        values <- vapply(ents, function(e) render_field(rows[e, ], f), character(1))
        same <- length(unique(values)) == 1
        if (mode == "diff" && same) next
        if (mode == "same" && !same) next
        d <- desc_map[[f]]
        label <- if (!is.null(d)) d[1] else f
        cells <- c(paste0("<td style='font-weight:600; color:#57534e; font-size:12px; vertical-align:top;'>", label, "</td>"))
        for (i in seq_along(ents)) {
          val <- values[i]
          diff <- length(unique(values)) > 1
          cells <- c(cells, paste0(
            "<td style='", if (diff) "background:#fffbeb;" else "",
            "font-size:13px; line-height:1.5; vertical-align:top;'>", if (nzchar(val)) val else "—", "</td>"
          ))
        }
        body_rows <- c(body_rows, paste0("<tr>", paste(cells, collapse = ""), "</tr>"))
      }
      paste0("<table style='width:100%; border-collapse:collapse;'>",
             "<thead><tr>", paste(header_cells, collapse = ""), "</tr></thead>",
             "<tbody>", paste(body_rows, collapse = ""), "</tbody></table>")
    }

    output$cmp_table <- renderUI({
      req(exists("decoder_df", inherits = TRUE))
      ents <- input$cmp_entities
      if (is.null(ents) || length(ents) < 2) {
        return(tags$p("Select at least two RCD entities to compare.", style = "color:#a8a29e;"))
      }
      tags$div(style = "overflow-x:auto;", HTML(build_cmp_table(ents, input$cmp_mode %||% "all")))
    })

    output$cmp_download_ui <- renderUI({
      ents <- input$cmp_entities
      if (is.null(ents) || length(ents) < 2) return(NULL)
      downloadButton(ns("cmp_download"), "Download Comparison (HTML)",
                     class = "btn", style = "margin-top:12px;")
    })

    output$cmp_download <- downloadHandler(
      filename = function() {
        ents <- input$cmp_entities
        paste0("RCDome_Compare_", paste(gsub(" ", "_", ents), collapse = "_"), ".html")
      },
      content = function(file) {
        ents <- input$cmp_entities
        tbl <- build_cmp_table(ents, input$cmp_mode %||% "all")
        
        # Small RCDome logo (upper right), embedded base64 so the report is standalone.
        logo_file <- "www/rcdome_logo_full.svg"
        logo_img <- if (file.exists(logo_file)) {
          b64 <- jsonlite::base64_enc(readBin(logo_file, "raw", file.info(logo_file)$size))
          paste0(
            "<div style='position:absolute; top:16px; right:16px; width:120px;'>",
            "<img src='data:image/svg+xml;base64,", b64, "' alt='RCDome' ",
            "style='width:100%; height:auto; display:block;'></div>"
          )
        } else ""
        
        html <- paste0(
          "<!DOCTYPE html><html><head><meta charset='utf-8'><title>RCDome Operational Definition Comparator</title></head>",
          "<body style='background:#f5f5f4; color:#1c1917; font-family:Segoe UI,system-ui,sans-serif; padding:24px; position:relative;'>",
          logo_img,
          "<h1 style='font-weight:500; font-size:24px;'>RCDome Operational Definition Comparator</h1>",
          tbl,
          "</body></html>"
        )
        writeLines(html, file, useBytes = TRUE)
      }
    )
  })
}
