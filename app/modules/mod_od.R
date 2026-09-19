# ─── Module: od (Operational Definitions) ──────────────────────────────────
# Dedicated browser for the 53 RCD entities' operational definitions, sourced
# from the RCDome Decoder. Searchable list on the left, full record on the right.

OD_LEVEL_COLORS <- c(L1 = "#FFD700", L2 = "#00B0FF", L3 = "#00E676",
                     L4 = "#E040FB", L5 = "#FF6D00")
OD_LEVEL_NAMES <- c(L1 = "L1 modality", L2 = "L2 subtype", L3 = "L3 trigger",
                    L4 = "L4 Functional/contextual",
                    L5 = "L5 Generic/umbrella/taxon")

OD_LEGEND <- list(
  L1 = list(label = "L1 modality",
            desc = "bona fide cell-death modalities (apoptosis, necroptosis, ferroptosis\u2026)"),
  L2 = list(label = "L2 subtype",
            desc = "a subtype of a modality (e.g., extrinsic apoptosis)"),
  L3 = list(label = "L3 trigger",
            desc = "a trigger or mechanism (e.g., MPT)"),
  L4 = list(label = "L4 Functional/contextual",
            desc = "context-dependent or functional forms"),
  L5 = list(label = "L5 Generic/umbrella/taxon",
            desc = "generic, umbrella, legacy, taxon, or emerging terms")
)
OD_LEGEND_ORDER <- c("L1", "L2", "L3", "L4", "L5")

OD_SECTIONS <- list(
  Definition = c("operational_definition", "operational_definition_complement",
                 "operational_definition_source", "definition_status"),
  Ontology = c("category", "hard_gate_status", "evidence_maturity",
               "relationship_type", "parent_entity", "species_scope", "year"),
  Mechanism = c("core_mechanism", "key_molecules", "inflammatory", "overlaps"),
  References = c("founding_pmid", "primary_refs_pmids", "secondary_refs_pmids",
                 "reference_pmid", "reference_citation", "primary_discovery_reference"),
  "NCCD 2018" = c("galluzzi_nccd_definition", "galluzzi_nccd_status"),
  "Adjudication gates" = c("C1", "C2", "C3", "C4", "C5", "C6", "S"),
  Provenance = c("source_databases", "source_channels", "provenance_note",
                 "od_author", "review_status", "validation_verdict",
                 "ontology_curator_verified", "independent_replication")
)

mod_od_ui <- function(id) {
  ns <- NS(id)
  div(class = "about-content",
    div(class = "hero", style = "grid-template-columns:1fr; padding:18px 0 24px;",
      div(
        div(class = "eyebrow", style = "text-transform:none; font-size:24px;",
            HTML(paste0(rcdome_span(), " \u00b7 Scientific Module"))),
        h1(HTML(paste0(rcdome_span(), " Operational Definitions"))),
        div(class = "lede",
            HTML("Browse the 53 canonicalized RCD-related entities and their curated operational definitions, ontological classification, key molecules, evidence, and adjudication gates, sourced from the RCDome decoder."))
      )
    ),
    fluidRow(
      column(4,
        textInput(ns("od_search"), NULL, placeholder = "Search an RCD form\u2026", width = "100%"),
        tags$div(style = "max-height:56vh; overflow-y:auto; padding-right:6px;",
                 uiOutput(ns("od_list"))),
        tags$div(style = "margin-top:16px; padding:12px 14px; background:#ffffff; border:1px solid #e7e5e4; border-radius:10px;",
          tags$div(style = "font-size:13px; font-weight:700; color:#57534e; margin-bottom:8px;", "Ontology levels"),
          lapply(OD_LEGEND_ORDER, function(lv) {
            tags$div(style = "margin-bottom:6px;",
              tags$span(style = paste0("display:inline-block; width:10px; height:10px; border-radius:50%; background:", OD_LEVEL_COLORS[[lv]], "; margin-right:8px;")),
              tags$strong(style = "font-size:12.5px;", OD_LEGEND[[lv]]$label),
              tags$span(style = "color:#57534e; font-size:12.5px;", " \u2014 ", OD_LEGEND[[lv]]$desc)
            )
          })
        )
      ),
      column(8,
        uiOutput(ns("od_detail"))
      )
    )
  )
}

mod_od_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    ns <- session$ns
    selected <- reactiveVal("Apoptosis")

    ents <- reactive({
      req(exists("decoder_df", inherits = TRUE))
      sort(unique(decoder_df$rcd_form))
    })

    entity_level <- reactive({
      req(exists("genes_df", inherits = TRUE))
      lv <- unique(genes_df[genes_df$rcd_form_canonical %in% ents(),
                            c("rcd_form_canonical", "rcdome_level")])
      setNames(lv$rcdome_level, lv$rcd_form_canonical)
    })

    filtered <- reactive({
      q <- tolower(trimws(input$od_search %||% ""))
      e <- ents()
      if (nzchar(q)) e <- e[grepl(q, tolower(e), fixed = TRUE)]
      e
    })

    output$od_list <- renderUI({
      e <- filtered()
      lv <- entity_level()
      lapply(e, function(x) {
        lvl <- lv[[x]] %||% "L5"
        col <- OD_LEVEL_COLORS[[lvl]] %||% "#FF6D00"
        sel <- identical(x, selected())
        tags$button(
          class = "btn",
          style = paste0("display:block; width:100%; text-align:left; margin-bottom:6px; padding:9px 12px;",
                         if (sel) "border:2px solid #c2410c; background:#fff7ed;" else "background:#ffffff;"),
          tags$span(style = paste0("display:inline-block; width:10px; height:10px; border-radius:50%; background:", col, "; margin-right:8px;")),
          tags$strong(x),
          onclick = sprintf("Shiny.setInputValue('%s', '%s', {priority:'event'})", ns("od_select"), x)
        )
      })
    })

    observeEvent(input$od_select, {
      if (!is.null(input$od_select) && nzchar(input$od_select)) selected(input$od_select)
    }, ignoreNULL = TRUE)

    render_pmids <- function(v) {
      pmids <- trimws(strsplit(as.character(v), ";")[[1]])
      pmids <- pmids[pmids != ""]
      if (length(pmids) == 0) return("")
      paste(vapply(pmids, function(p) {
        paste0("<a href='https://pubmed.ncbi.nlm.nih.gov/", p,
               "/' target='_blank' style='margin-right:6px;'>PMID ", p, "</a>")
      }, character(1)), collapse = "")
    }

    render_pills <- function(v) {
      parts <- trimws(strsplit(as.character(v), ";")[[1]])
      parts <- parts[parts != ""]
      if (length(parts) == 0) return("")
      paste(vapply(parts, function(p) {
        paste0("<span style='display:inline-block; background:#f1f5f9; color:#475569; border:1px solid #e2e8f0; border-radius:999px; padding:2px 10px; margin:0 4px 4px 0; font-size:12px; font-weight:500;'>",
               p, "</span>")
      }, character(1)), collapse = "")
    }

    output$od_detail <- renderUI({
      x <- selected()
      req(exists("decoder_df", inherits = TRUE))
      dr <- decoder_df[decoder_df$rcd_form == x, ]
      if (nrow(dr) == 0) return(tags$p("No data for this entity."))
      r <- dr[1, ]
      lv <- entity_level()[[x]] %||% "L5"
      col <- OD_LEVEL_COLORS[[lv]] %||% "#FF6D00"
      desc_map <- get0("DECODER_DESC", inherits = TRUE, ifnotfound = list())

      blocks <- lapply(names(OD_SECTIONS), function(sec) {
        flds <- OD_SECTIONS[[sec]]
        rows <- lapply(flds, function(f) {
          v <- r[[f]]
          if (is.null(v) || is.na(v) || as.character(v) == "") return(NULL)
          d <- desc_map[[f]]
          label <- if (!is.null(d)) d[1] else f
          if (f %in% c("primary_refs_pmids", "secondary_refs_pmids")) {
            val <- render_pmids(v)
            if (!nzchar(val)) return(NULL)
          } else if (f %in% c("source_databases", "source_channels")) {
            val <- render_pills(v)
            if (!nzchar(val)) return(NULL)
          } else if (f == "founding_pmid") {
            fv <- as.character(v)
            if (grepl("[0-9]", fv) && !grepl("[^0-9; ]", fv)) {
              val <- render_pmids(fv)
              if (!nzchar(val)) return(NULL)
            } else {
              rp <- as.character(r$reference_pmid %||% "")
              links <- render_pmids(rp)
              val <- if (nzchar(links)) paste0("Composite — ", links) else fv
            }
          } else if (f %in% c("reference_pmid", "primary_discovery_reference")) {
            val <- render_pmids(v)
            if (!nzchar(val)) return(NULL)
          } else if (f == "reference_citation") {
            pmid <- as.character(r$reference_pmid %||% "")
            if (!nzchar(pmid)) pmid <- as.character(r$founding_pmid %||% "")
            if (nzchar(pmid) && grepl("[0-9]", pmid)) {
              first <- trimws(strsplit(pmid, ";")[[1]])[1]
              val <- paste0("<a href='https://pubmed.ncbi.nlm.nih.gov/", first,
                            "/' target='_blank'>", as.character(v), "</a>")
            } else {
              val <- as.character(v)
            }
          } else {
            val <- as.character(v)
          }
          tags$div(style = "margin-bottom:10px;",
            tags$div(style = "font-size:11px; text-transform:uppercase; letter-spacing:0.05em; color:#a8a29e;", label),
            tags$div(style = "font-size:14px; line-height:1.5; color:#1c1917;", HTML(val))
          )
        })
        rows <- Filter(Negate(is.null), rows)
        if (length(rows) == 0) return(NULL)
        tags$div(style = "background:#ffffff; border:1px solid #e7e5e4; border-radius:10px; padding:16px 18px; margin-bottom:14px;",
          tags$div(style = "font-size:13px; font-weight:700; color:#c2410c; margin-bottom:12px;", sec),
          rows
        )
      })
      blocks <- Filter(Negate(is.null), blocks)

      tags$div(
        tags$div(style = "background:#0b1020; color:#e7e5e4; border-radius:12px; padding:22px 24px; margin-bottom:14px;",
          tags$div(
            tags$span(style = paste0("display:inline-block; width:12px; height:12px; border-radius:50%; background:", col, "; margin-right:8px;")),
            tags$strong(x, style = "font-size:18px;")
          ),
          tags$div(style = paste0("margin-top:6px; color:", col, "; font-size:13px;"),
                   paste0(OD_LEVEL_NAMES[[lv]] %||% "", " \u00b7 ", r$hard_gate_status %||% ""))
        ),
        blocks
      )
    })
  })
}
