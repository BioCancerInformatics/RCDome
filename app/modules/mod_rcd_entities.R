# ─── Module: rcd_entities (separate definitions sub-module) ─────────────────
# Displays the 53 audited RCD descriptions verbatim, with FUNCTIONAL citation
# hyperlinks: in-text [n] jumps to the reference entry; each reference's
# DOI -> https://doi.org/DOI  and  PMID -> https://pubmed.ncbi.nlm.nih.gov/PMID.

RCD_ENT_DESC_DIR <- "data/RCD modulo/descricao RCDs"
RCD_ENT_REF_DIR  <- "data/RCD modulo/referencias"

mod_rcd_entities_ui <- function(id) {
  ns <- NS(id)
  tagList(
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
                           choices = c("Select an RCD entity…" = "", setNames(entities(), entities())),
                           server = TRUE)
    })

    # Description -> HTML: "## " heading, [n] -> anchor to the reference entry.
    desc_to_html <- function(x) {
      x <- trimws(x)
      blocks <- strsplit(x, "\n[ \t]*\n", perl = TRUE)[[1]]
      blocks <- blocks[nzchar(trimws(blocks))]
      parts <- lapply(blocks, function(b) {
        b <- trimws(gsub("[ \t]*\n[ \t]*", " ", b))
        if (grepl("^-{3,}$", b, perl = TRUE)) return(NULL)   # drop --- separators
        b <- sub("^#{1,6}\\s+", "", b, perl = TRUE)           # drop # / ## markers
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

    # Reference list -> HTML: per-entry anchor + functional DOI/PMID links.
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
      desc_path <- file.path(RCD_ENT_DESC_DIR, paste0(input$entity, ".txt"))
      ref_path  <- file.path(RCD_ENT_REF_DIR,  paste0(input$entity, ".txt"))
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
        tags$div(style = "background:#f5f5f4; border-left:4px solid #c0392b; padding:16px 18px; border-radius:6px;",
                 desc_to_html(desc)),
        tags$h4("References", style = "color:#c0392b; margin-top:16px;"),
        tags$div(style = "background:#fafaf9; border:1px solid #e7e5e4; border-radius:6px; padding:14px 18px; max-height:340px; overflow-y:auto;",
                 if (is.null(ref)) tags$p("No reference list available.") else HTML(ref_to_html(ref)))
      )
    })
  })
}
