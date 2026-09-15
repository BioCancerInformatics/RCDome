# ─── Module: gene_info ────────────────────────────────────────────────────────
# Displays static gene information from the Excel reference file.

mod_gene_info_ui <- function(id) {
  ns <- NS(id)
  uiOutput(ns("panel"))
}

mod_gene_info_server <- function(id, gene_reactive, genes_df) {
  moduleServer(id, function(input, output, session) {

    output$panel <- renderUI({
      gene <- gene_reactive()
      if (is.null(gene) || gene == "") return(NULL)

      row <- genes_df[genes_df$name == gene, ]
      if (nrow(row) == 0) return(NULL)

      pathways <- get_pathways_for_gene(row)
      pathways_str <- if (length(pathways) > 0) {
        paste(pathways, collapse = "  ·  ")
      } else {
        "No pathways categorized"
      }

      tags$div(
        style = "background: #fff3cd; padding: 12px 16px; border-radius: 6px; margin-bottom: 16px;",
        tags$h4(paste0(gene, " — ", row$description)),
        tags$p(tags$strong("Chromosome: "), row$chromosome %||% "N/A"),
        tags$p(tags$strong("NCBI Summary: "), row$summary %||% "No summary available."),
        tags$p(
          tags$strong("Cell death pathways: "),
          tags$span(pathways_str, style = "color: #198754;")
        ),
        tags$p(
          style = "font-size: 0.8em; margin-top: 8px; color: #a8a29e;",
          "Upon selecting a gene, the system automatically searches Europe PMC ",
          "for these pathways and extracts claims with DeepSeek."
        )
      )
    })

  })
}
