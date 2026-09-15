# ─── Module: signatures ──────────────────────────────────────────────────────
# Localizador de assinaturas: busca por gene/nomenclatura → tabela → pop-up.

mod_signatures_ui <- function(id) {
  ns <- NS(id)
  tagList(
    h4("Prognostic Signature Locator"),
    p("Search by gene, nomenclature, cancer type, RCD pathway, or omic layer."),
    p("See how the signatures were created at: ",
      tags$a(href = "https://doi.org/10.3389/fbinf.2025.1630518",
             target = "_blank", rel = "noopener",
             "https://doi.org/10.3389/fbinf.2025.1630518")),
    div(class = "rcdmap-search-row", style = "margin-bottom: 16px;",
      textInput(ns("search_term"), "Search:",
                placeholder = "e.g. TP53, UVM-99, LIHC, Apoptosis, mRNA, Mutation...",
                width = "450px"),
      actionButton(ns("search_btn"), "Search", icon = icon("search"),
                   class = "search-evidence-btn")
    ),
    # Hidden: trigger search on Enter key
    tags$script(HTML(sprintf(
      "$('#%s').on('keypress', function(e) { if (e.which == 13) { $('#%s').click(); } });",
      ns("search_term"), ns("search_btn")
    ))),
    DT::DTOutput(ns("results_table")),
    div(style = "margin-top: 14px; display: flex; align-items: center; gap: 10px;",
      selectInput(ns("download_format"), "Format:",
                  choices = c("TSV" = "tsv", "XLSX" = "xlsx", "CSV" = "csv"),
                  selected = "tsv", width = "120px"),
      downloadButton(ns("download_btn"), "Download", class = "search-evidence-btn")
    )
  )
}

mod_signatures_server <- function(id, sig_df) {
  moduleServer(id, function(input, output, session) {

    # Start showing all, filter on search
    search_results <- reactiveVal(sig_df)

    observeEvent(input$search_btn, {
      term <- trimws(input$search_term)
      if (is.null(term) || term == "") {
        search_results(sig_df)
        return()
      }
      matches <- sig_df[
        grepl(term, sig_df$Signature, ignore.case = TRUE) |
        grepl(term, sig_df$Nomenclature, ignore.case = TRUE) |
        grepl(term, sig_df$CTAB, ignore.case = TRUE) |
        grepl(term, sig_df[["RCD form"]], ignore.case = TRUE) |
        grepl(term, sig_df[["Omic feature"]], ignore.case = TRUE),
      ]
      if (nrow(matches) == 0) search_results(data.frame()) else search_results(matches)
    })

    output$results_table <- DT::renderDT({
      res <- search_results()
      if (nrow(res) == 0) {
        return(DT::datatable(
          data.frame(Mensagem = "No signatures found for this term."),
          options = list(dom = "t"), rownames = FALSE,
          class = "compact"
        ))
      }

      # Compact table: only key columns, CTAB abbreviation
      df_show <- res[, c("Nomenclature", "Signature", "Elements", "Omic feature",
                         "CTAB", "RCD form")]
      colnames(df_show) <- c("Nomenclature", "Signature", "Nº Genes", "Omic",
                             "Cancer", "RCD Pathways")

      DT::datatable(
        df_show,
        rownames  = FALSE,
        selection = "single",
        options   = list(pageLength = 15, scrollX = TRUE,
                         language = list(zeroRecords = "Nenhum resultado.")),
        class     = "compact hover row-border"
      )
    })

    observeEvent(input$results_table_rows_selected, {
      sel <- input$results_table_rows_selected
      res <- search_results()
      req(length(sel) > 0, !is.null(res))

      nom <- res$Nomenclature[sel]
      r <- sig_df[sig_df$Nomenclature == nom, ][1, ]

      # ── Helper: format p-value ──
      fmt_p <- function(val) {
        if (is.na(val) || is.null(val) || val == "NS") return("NS")
        v <- suppressWarnings(as.numeric(val))
        if (is.na(v)) return(val)
        if (v < 0.0001) return(sprintf("%.2e", v))
        if (v < 0.001)  return(sprintf("%.4f", v))
        return(sprintf("%.3f", v))
      }

      # ── Cancer type lookup (TCGA study abbreviations) ──
      cancer_names <- c(
        LAML = "Acute Myeloid Leukemia",
        ACC  = "Adrenocortical carcinoma",
        BLCA = "Bladder Urothelial Carcinoma",
        LGG  = "Brain Lower Grade Glioma",
        BRCA = "Breast invasive carcinoma",
        CESC = "Cervical squamous cell carcinoma",
        CHOL = "Cholangiocarcinoma",
        LCML = "Chronic Myelogenous Leukemia",
        COAD = "Colon adenocarcinoma",
        CNTL = "Controls",
        ESCA = "Esophageal carcinoma",
        FPPP = "FFPE Pilot Phase II",
        GBM  = "Glioblastoma multiforme",
        HNSC = "Head and Neck squamous cell carcinoma",
        KICH = "Kidney Chromophobe",
        KIRC = "Kidney renal clear cell carcinoma",
        KIRP = "Kidney renal papillary cell carcinoma",
        LIHC = "Liver hepatocellular carcinoma",
        LUAD = "Lung adenocarcinoma",
        LUSC = "Lung squamous cell carcinoma",
        DLBC = "Lymphoid Neoplasm Diffuse Large B-cell Lymphoma",
        MESO = "Mesothelioma",
        MISC = "Miscellaneous",
        OV   = "Ovarian serous cystadenocarcinoma",
        PAAD = "Pancreatic adenocarcinoma",
        PCPG = "Pheochromocytoma and Paraganglioma",
        PRAD = "Prostate adenocarcinoma",
        READ = "Rectum adenocarcinoma",
        SARC = "Sarcoma",
        SKCM = "Skin Cutaneous Melanoma",
        STAD = "Stomach adenocarcinoma",
        TGCT = "Testicular Germ Cell Tumors",
        THYM = "Thymoma",
        THCA = "Thyroid carcinoma",
        UCS  = "Uterine Carcinosarcoma",
        UCEC = "Uterine Corpus Endometrial Carcinoma",
        UVM  = "Uveal Melanoma"
      )
      translate_ctab <- function(ctab) {
        if (is.na(ctab)) return("N/A")
        full <- cancer_names[ctab]
        if (is.na(full)) return(ctab)
        paste0(full, " (", ctab, ")")
      }

      # ── Helpers: translate abbreviations ──
      translate_phenotype <- function(p) {
        if (is.na(p)) return("N/A")
        switch(as.character(p),
          TMB = "Tumor Mutation Burden (TMB)",
          TSM = "Tumor Stemness (TSM)",
          MSI = "Microsatellite Instability (MSI)",
          p)
      }
      translate_expression <- function(e) {
        if (is.na(e) || e == "No_data") return("No data")
        switch(as.character(e),
          Underexpression = "Underexpressed in tumor",
          Overexpression  = "Overexpressed in tumor",
          Unchanged       = "Unchanged in tumor",
          e)
      }
      translate_scs <- function(s) {
        if (is.na(s)) return("N/A")
        if (s == "P") "Positive (direct correlation)" else if (s == "N") "Negative (inverse correlation)" else s
      }

      scs_label <- translate_scs(r$SCS)

      outcome_color <- switch(r$Combined_Outcome,
        Protective  = "#198754",
        Risky       = "#dc3545",
        Meaningless = "#a8a29e"
      )
      outcome_icon <- switch(r$Combined_Outcome,
        Protective  = "🟢", Risky = "🔴", Meaningless = "⚪"
      )

      showModal(modalDialog(
        title = tags$div(
          tags$strong(r$Signature),
          tags$span(
            paste0(" — ", outcome_icon, " ", r$Combined_Outcome),
            style = sprintf("color: %s; margin-left: 8px; font-size: 0.85em;", outcome_color)
          )
        ),
        size = "l",
        easyClose = TRUE,
        footer = modalButton("Close"),

        # ── Table 1: Basic Info ──
        tags$h5("📋 Signature Information"),
        HTML(paste0(
          "<table class='table table-bordered table-striped table-sm' style='font-size:14px;'>",
          "<tr><th style='width:240px;'>Nomenclature</th><td>", as.character(r$Nomenclature), "</td></tr>",
          "<tr><th>Cancer type</th><td>", translate_ctab(r$CTAB), "</td></tr>",
          "<tr><th>Genes in signature</th><td>", as.character(r$Elements), "</td></tr>",
          "<tr><th>Omic layer</th><td>", as.character(r[["Omic feature"]]), "</td></tr>",
          "<tr><th>Tumor phenotype</th><td>", translate_phenotype(r$Phenotype), "</td></tr>",
          "<tr><th>Regulated Cell Death (RCD)</th><td>", as.character(r[["RCD form"]]), "</td></tr>",
          "<tr><th>Omic-phenotype direction (SCS)</th><td>", scs_label, "</td></tr>",
          "<tr><th>Tumor expression</th><td>", translate_expression(r$Expression), "</td></tr>",
          "<tr><th>Combined outcome</th><td><b style='color:", outcome_color, ";'>",
            outcome_icon, " ", as.character(r$Combined_Outcome),
            " (Protective: ", as.character(r$Protective_Count), " | Risky: ", as.character(r$Risky_Count), " | NS: ", as.character(r$NS_Count), ")</b></td></tr>",
          "</table>"
        )),

        # ── Table 2: Survival Metrics ──
        tags$h5("📊 Métricas de Sobrevida"),
        HTML(paste0(
          "<table class='table table-bordered table-striped table-sm' style='font-size:14px;'>",
          "<thead><tr>",
          "<th>Endpoint</th><th>Tipo Cox</th><th>p-valor Cox</th>",
          "<th>Tipo Log-Rank</th><th>p-valor Log-Rank</th>",
          "</tr></thead><tbody>",
          "<tr><td><b>OS</b></td><td>", as.character(r$Type_Cox_OS), "</td><td>", fmt_p(r$p.value_Cox_OS),
            "</td><td>", as.character(r$Type_log_rank_OS), "</td><td>", fmt_p(r$p.value_log_rank_OS), "</td></tr>",
          "<tr><td><b>DSS</b></td><td>", as.character(r$Type_Cox_DSS), "</td><td>", fmt_p(r$p.value_Cox_DSS),
            "</td><td>", as.character(r$Type_log_rank_DSS), "</td><td>", fmt_p(r$p.value_log_rank_DSS), "</td></tr>",
          "<tr><td><b>DFI</b></td><td>", as.character(r$Type_Cox_DFI), "</td><td>", fmt_p(r$p.value_Cox_DFI),
            "</td><td>", as.character(r$Type_log_rank_DFI), "</td><td>", fmt_p(r$p.value_log_rank_DFI), "</td></tr>",
          "<tr><td><b>PFI</b></td><td>", as.character(r$Type_Cox_PFI), "</td><td>", fmt_p(r$p.value_Cox_PFI),
            "</td><td>", as.character(r$Type_log_rank_PFI), "</td><td>", fmt_p(r$p.value_log_rank_PFI), "</td></tr>",
          "</tbody></table>"
        )),

        # ── Table 3: Microenvironment ──
        tags$h5("🦠 Microambiente Tumoral"),
        HTML(paste0(
          "<table class='table table-bordered table-striped table-sm' style='font-size:14px;'>",
          "<tr><th style='width:200px;'>Classificação TME</th><td>",
            if (!is.na(r$microenvironment_classification) && nzchar(as.character(r$microenvironment_classification)))
              as.character(r$microenvironment_classification) else "Não disponível", "</td></tr>",
          "<tr><th>Perfil imunológico</th><td>",
            if (!is.na(r$immune_classification) && nzchar(as.character(r$immune_classification)))
              as.character(r$immune_classification) else "Não disponível", "</td></tr>",
          "</table>"
        )),

        tags$p(
          style = "font-size: 0.8em; color: #d6d3d1; margin-top: 10px;",
          "OS = Overall Survival · DSS = Disease-Specific Survival · DFI = Disease-Free Interval · PFI = Progression-Free Interval"
        )
      ))
    })

    # ── Download dos resultados (TSV / XLSX / CSV) ───────────────────
    output$download_btn <- downloadHandler(
      filename = function() {
        paste0("signatures.", input$download_format)
      },
      content = function(file) {
        fmt <- input$download_format
        df <- search_results()
        if (fmt == "tsv") {
          write.table(df, file, sep = "\t", row.names = FALSE, quote = FALSE, na = "")
        } else if (fmt == "csv") {
          write.csv(df, file, row.names = FALSE)
        } else {
          writexl::write_xlsx(df, file)
        }
      }
    )

  })
}
