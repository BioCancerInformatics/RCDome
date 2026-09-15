# ─── Module: gene_list ───────────────────────────────────────────────────────
# Compact gene table + pop-up modal with gene details on click.

mod_gene_list_ui <- function(id) {
  ns <- NS(id)
  tagList(
    h4("Gene Catalog"),
    DTOutput(ns("table"))
  )
}

mod_gene_list_server <- function(id, genes_df) {
  moduleServer(id, function(input, output, session) {

    # Reactive for selected gene name
    selected_gene <- reactiveVal(NULL)

    output$table <- renderDT({
      # ponytail: shortcut RCDs column from Pathway_Categorization
      genes_df$RCDs <- sapply(genes_df$Pathway_Categorization, function(x) {
        if (is.na(x) || x == "") return("")
        paste(trimws(strsplit(x, "/")[[1]]), collapse = ", ")
      })
      df <- genes_df[, c("name", "description", "RCDs")]
      colnames(df) <- c("Gene", "Official Full Name", "RCDs")
      datatable(
        df,
        rownames  = FALSE,
        selection = "single",
        options   = list(
          pageLength = 15,
          search     = list(regex = TRUE, smart = TRUE),
          language   = list(search = "Filter:", zeroRecords = "No genes found.")
        ),
        class = "compact hover row-border"
      )
    })

    observeEvent(input$table_rows_selected, {
      idx <- input$table_rows_selected
      if (is.null(idx) || length(idx) == 0) return()

      row <- genes_df[idx, ]
      gene_name <- row$name

      # Update the selected gene (triggers downstream search)
      selected_gene(gene_name)

      # Build modal content
      pathways <- get_pathways_for_gene(row)
      pathways_str <- if (length(pathways) > 0) {
        paste(pathways, collapse = "  ·  ")
      } else {
        "No pathways categorized"
      }

      showModal(modalDialog(
        title = tags$div(
          tags$strong(gene_name),
          tags$span(
            paste0("— ", row$description),
            style = "font-size: 0.85em; color: #a8a29e; margin-left: 8px;"
          )
        ),
        size = "l",
        easyClose = TRUE,
        footer = modalButton("Close"),

        tags$p(tags$strong("Chromosome: "), row$chromosome %||% "N/A"),
        tags$p(tags$strong("NCBI Summary: "), row$summary %||% "No summary available."),
        tags$p(
          tags$strong("Regulated Cell Death pathways: "),
          tags$span(pathways_str, style = "color: #198754;")
        ),
        tags$hr(),
        tags$p(
          style = "font-size: 0.85em; color: #a8a29e;",
          "To search for literature evidence on this gene, go to the 'Evidence' tab."
        )
      ))
    })

    return(selected_gene)
  })
}
