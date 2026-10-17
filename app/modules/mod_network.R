# ─── Module: gene_rcd_network ────────────────────────────────────────────────
# Interactive network: genes ↔ RCD entities.
#
# Click RCD → RCD modal.
# Click gene → gene information + literature search modal.
#
# Zoom behavior:
# - Physics is used only to calculate the initial layout.
# - After stabilization, physics is disabled.
# - Zooming and dragging the canvas modify only the camera.
# - Node coordinates remain fixed.
# - Nodes may still be manually dragged because dragNodes = TRUE.
#
# Ontology layer (Tier 1):
# - RCD entity nodes are colored by ontological level (L1–L5).
# - Gene nodes are colored by dominant mechanistic role.
# - Hover: gene → symbol + HGNC name; entity → name + level + definition;
#   edge → role · direction · tier · PMID count.
# ─────────────────────────────────────────────────────────────────────────────


# ─── Ontology / role colors (shared with the OD module where possible) ──────

network_level_colors <- function() {
  if (exists("OD_LEVEL_COLORS", inherits = TRUE)) return(OD_LEVEL_COLORS)
  c(L1 = "#FFD700", L2 = "#00B0FF", L3 = "#00E676",
    L4 = "#E040FB", L5 = "#FF6D00")
}

network_level_names <- function() {
  if (exists("OD_LEVEL_NAMES", inherits = TRUE)) return(OD_LEVEL_NAMES)
  c(L1 = "L1 Modalities", L2 = "L2 Subtypes", L3 = "L3 Triggers",
    L4 = "L4 Functional/contextual",
    L5 = "L5 Generic/umbrella/taxon")
}

# Gene mechanistic role colors (dominant role per gene node).
NET_ROLE_COLORS <- c(
  EXECUTOR  = "#E53935",
  REGULATOR = "#3949AB",
  MARKER    = "#00897B",
  UNCERTAIN = "#9E9E9E"
)

# Direction colors (shown as badges in the legend; direction lives on the edge).
NET_DIR_COLORS <- c(
  PROMOTES = "#2E7D32",
  PROTECTS = "#1565C0",
  UNCLEAR  = "#757575"
)

# First sentence of a decoder definition (compact entity hover).
first_sentence <- function(x) {
  x <- trimws(as.character(x %||% ""))
  if (!nzchar(x)) return("")
  m <- regexpr("\\.\\s", x)
  if (m[1] > 0) substr(x, 1, m[1]) else x
}


# ─── UI ──────────────────────────────────────────────────────────────────────

mod_network_ui <- function(id) {
  
  ns <- NS(id)
  
  tagList(
    
    h4("Gene × RCD Entity Network"),
    
    p(
      paste(
        "Click a gene (circle) for literature evidence.",
        "Click an RCD logo for its top-pair evidence trail."
      )
    ),
    
    div(
      style = paste(
        "display: flex;",
        "gap: 12px;",
        "flex-wrap: wrap;",
        "margin-bottom: 12px;"
      ),
      
      div(
        style = "flex: 1; min-width: 250px;",
        
        selectizeInput(
          inputId = ns("rcd_filter"),
          label = "Filter by RCD entity:",
          choices = NULL,
          multiple = TRUE,
          options = list(
            placeholder = "All entities...",
            create = rcdome_create_js
          )
        )
      ),
      
      div(
        style = "flex: 1; min-width: 250px;",
        
        selectizeInput(
          inputId = ns("gene_search"),
          label = "Search gene:",
          choices = NULL,
          options = list(
            placeholder = "e.g. TP53, BCL2, BAX, GPX4...",
            maxOptions = 30,
            create = rcdome_create_js
          )
        )
      )
    ),

    div(
      style = "margin-bottom: 12px;",
      checkboxGroupInput(
        inputId = ns("edge_sources"),
        label = "Edge classification sources (1 = single, 2+ = compare):",
        choices = c("Evidence-first" = "evidence", "DeepSeek" = "deepseek", "Compiled gene role" = "elicit", "Consensus" = "consensus", "GPT" = "gpt", "Curator 1" = "higor", "Curator 2" = "victor"),
        selected = "evidence",
        inline = TRUE
      )
    ),

    # ── Ontology filters (level + gene role) ─────────────────────────────────
    div(
      style = paste(
        "display: flex;",
        "gap: 12px;",
        "flex-wrap: wrap;",
        "margin-bottom: 12px;"
      ),
      
      div(
        style = "flex: 1; min-width: 200px;",
        
        selectizeInput(
          inputId = ns("level_filter"),
          label = "Filter by level:",
          choices = c("L1", "L2", "L3", "L4", "L5"),
          multiple = TRUE,
          options = list(
            placeholder = "All levels..."
          )
        )
      ),
      
      div(
        style = "flex: 1; min-width: 200px;",
        
        selectizeInput(
          inputId = ns("role_filter"),
          label = "Filter by gene role:",
          choices = c("EXECUTOR", "REGULATOR", "MARKER"),
          multiple = TRUE,
          options = list(
            placeholder = "All roles..."
          )
        )
      ),
      
      div(
        style = "flex: 1; min-width: 200px;",
        
        selectizeInput(
          inputId = ns("mech_filter"),
          label = "Filter by mechanistic class:",
          choices = c(
            "MECHANISTIC", "CO_OCCURRENCE", "LITERATURE_GAP",
            "CONTEXT_GAP", "DATABASE_ONLY", "INSUFFICIENT_DATA"
          ),
          multiple = TRUE,
          options = list(
            placeholder = "All classes..."
          )
        )
      ),
      
      div(
        style = "flex: 1; min-width: 160px;",
        
        selectInput(
          inputId = ns("cap_select"),
          label = "Max genes per entity (top by evidence tier):",
          choices = c("All", "1000", "500", "100", "20"),
          selected = "1000",
          width = "100%"
        )
      )
    ),
    
    # ── Ontology legend (L1–L5 · gene role · edge direction) ────────────────
    div(
      style = paste(
        "display: flex; flex-wrap: wrap; gap: 12px 20px; align-items: center;",
        "padding: 10px 14px; margin-bottom: 12px; background: #ffffff;",
        "border: 1px solid #e7e5e4; border-radius: 10px; font-size: 12.5px;"
      ),
      
      # Entity levels
      div(
        style = "display: flex; align-items: center; gap: 10px; flex-wrap: wrap;",
        tags$span("Entity level", style = "color:#78716c; font-weight:600;"),
        lapply(c("L1", "L2", "L3", "L4", "L5"), function(lv) {
          tags$span(
            style = paste(
              "display: inline-flex; align-items: center; gap: 5px;",
              "white-space: nowrap;"
            ),
            tags$span(
              style = paste0(
                "display: inline-block; width: 10px; height: 10px;",
                "border-radius: 50%; background: ", network_level_colors()[[lv]], ";"
              )
            ),
            tags$span(network_level_names()[[lv]], style = "color:#57534e;")
          )
        })
      ),
      
      tags$span(style = "color:#d6d3d1;", "|"),
      
      # Gene roles
      div(
        style = "display: flex; align-items: center; gap: 10px; flex-wrap: wrap;",
        tags$span("Gene role", style = "color:#78716c; font-weight:600;"),
        lapply(names(NET_ROLE_COLORS), function(r) {
          tags$span(
            style = paste(
              "display: inline-flex; align-items: center; gap: 5px;",
              "white-space: nowrap;"
            ),
            tags$span(
              style = paste0(
                "display: inline-block; width: 10px; height: 10px;",
                "border-radius: 50%; background: ", NET_ROLE_COLORS[[r]], ";"
              )
            ),
            tags$span(r, style = "color:#57534e;")
          )
        })
      ),
      
      tags$span(style = "color:#d6d3d1;", "|"),
      
      # Edge direction + tier + legacy mapping
      div(
        style = "display: flex; align-items: center; gap: 12px; flex-wrap: wrap;",
        tags$span("Edge", style = "color:#78716c; font-weight:600;"),
        tags$span(
          "\u2192 PROMOTES",
          style = paste0("color:", NET_DIR_COLORS[["PROMOTES"]], "; font-weight:600;")
        ),
        tags$span(
          "\u22a3 PROTECTS",
          style = paste0("color:", NET_DIR_COLORS[["PROTECTS"]], "; font-weight:600;")
        ),
        tags$span(
          style = "display: inline-flex; align-items: center; gap: 5px; white-space: nowrap;",
          tags$span(style = "display:inline-block; width:16px; height:0; border-top:3px solid #57534e;"),
          tags$span("ET1", style = "font-size:11px; color:#57534e;"),
          tags$span(style = "display:inline-block; width:16px; height:0; border-top:2px solid #57534e;"),
          tags$span("ET2", style = "font-size:11px; color:#57534e;"),
          tags$span(style = "display:inline-block; width:16px; height:0; border-top:1.5px solid #57534e;"),
          tags$span("ET3", style = "font-size:11px; color:#57534e;"),
          tags$span(style = "display:inline-block; width:16px; height:0; border-top:1px dashed #57534e;"),
          tags$span("ET4", style = "font-size:11px; color:#57534e;")
        ),
        tags$span(
          style = "display: inline-flex; align-items: center; gap: 5px; white-space: nowrap;",
          tags$span(style = "display:inline-block; width:16px; height:0; border-top:1.5px dashed #FF9800;"),
          tags$span("legacy form", style = "font-size:11px; color:#57534e;")
        )
      )
    ),
    
    uiOutput(ns("network_stats")),
    
    withSpinner(
      visNetworkOutput(
        outputId = ns("network"),
        height = "75vh"
      ),
      type = 8,
      color = "#FF9800"
    ),
    div(style = "margin-top:8px;",
      actionButton(ns("export_png"), "Export PNG (300 DPI)",
                   style = "border:2px solid #FF9800; border-radius:6px; color:#FF9800; background:#ffffff; font-weight:600; padding:4px 12px; cursor:pointer; margin-right:8px;"),
      actionButton(ns("export_pdf"), "Export PDF",
                   style = "border:2px solid #FF9800; border-radius:6px; color:#FF9800; background:#ffffff; font-weight:600; padding:4px 12px; cursor:pointer;")
    )
  )
}


# ─── SERVER ──────────────────────────────────────────────────────────────────

mod_network_server <- function(
    id,
    genes_df,
    signatures_df = NULL
) {
  
  moduleServer(id, function(input, output, session) {
    
    export_name_rv <- reactiveVal("rcdome_network_all")
    prov_label_rv <- reactiveVal("all entities \u00b7 all levels \u00b7 all roles")
    
    # ── Edge classification sources (single or multi) ──────────────────────────
    src_list <- reactive({
      s <- input$edge_sources
      if (is.null(s) || length(s) == 0) s <- "evidence"
      lapply(s, function(x) {
        switch(x,
          evidence = list(key = "evidence", label = "Evidence-first", role = "final_role", dir = "final_direction"),
          elicit = list(key = "elicit", label = "Compiled gene role", role = "rcd_gene_type", dir = "role_direction"),
          consensus = list(key = "consensus", label = "Consensus", role = "consensus_role", dir = "consensus_direction"),
          gpt = list(key = "gpt", label = "GPT", role = "gpt_mapped_role", dir = "gpt_mapped_dir"),
          higor = list(key = "higor", label = "Curator 1", role = "higor_mapped_role", dir = "higor_mapped_dir"),
          victor = list(key = "victor", label = "Curator 2", role = "victor_mapped_role", dir = "victor_mapped_dir"),
          list(key = "deepseek", label = "DeepSeek", role = "cot_role", dir = "cot_direction")
        )
      })
    })

    src_cols <- reactive({
      s <- src_list()[[1]]
      list(role = s$role, dir = s$dir, label = s$label)
    })
    
    # role-filter choices follow the selected edge source
    observe({
      sc <- src_cols()
      vals <- sort(unique(genes_df[[sc$role]]))
      vals <- vals[!is.na(vals) & vals != ""]
      updateSelectizeInput(session, "role_filter", choices = vals, server = TRUE)
    })

    # ── Entity → ontological level (from the V027 matrix) ────────────────────
    entity_level <- reactive({
      df <- genes_df[
        !is.na(genes_df$Pathway_Categorization) &
        genes_df$Pathway_Categorization != "",
        ,
        drop = FALSE
      ]
      if (nrow(df) == 0) return(setNames(character(0), character(0)))
      lv <- unique(df[, c("Pathway_Categorization", "rcdome_level")])
      lv <- lv[
        !is.na(lv$rcdome_level) & nzchar(as.character(lv$rcdome_level)),
        ,
        drop = FALSE
      ]
      setNames(as.character(lv$rcdome_level), lv$Pathway_Categorization)
    })
    
    
    # ── Entity → first sentence of operational definition (decoder) ─────────
    entity_def_map <- reactive({
      dd <- decoder_df
      if (
        is.null(dd) || nrow(dd) == 0 ||
        !"operational_definition" %in% names(dd)
      ) {
        return(setNames(character(0), character(0)))
      }
      v <- vapply(dd$operational_definition, first_sentence, character(1))
      setNames(v, dd$rcd_form)
    })
    
    
    # ── Gene → HGNC name (for the gene hover tooltip) ────────────────────────
    gene_name_map <- if (
      exists("hgnc_map", inherits = TRUE) &&
      !is.null(hgnc_map) && nrow(hgnc_map) > 0
    ) {
      setNames(as.character(hgnc_map$name), hgnc_map$symbol)
    } else {
      setNames(character(0), character(0))
    }
    
    
    # ── Resolve selected search term to genes ────────────────────────────────
    
    resolve_search_genes <- function(term) {
      
      if (is.null(term) || term == "") {
        return(character(0))
      }
      
      if (startsWith(term, "GENE::")) {
        
        return(
          sub("^GENE::", "", term)
        )
        
      } else if (
        startsWith(term, "SIG::") &&
        !is.null(signatures_df)
      ) {
        
        nom <- sub("^SIG::", "", term)
        
        sig_row <- signatures_df[
          signatures_df$Nomenclature == nom,
          ,
          drop = FALSE
        ]
        
        if (nrow(sig_row) > 0) {
          
          genes_str <- gsub(
            pattern = "[()]",
            replacement = "",
            x = sig_row$Signature[1]
          )
          
          return(
            trimws(
              strsplit(
                genes_str,
                "\\+"
              )[[1]]
            )
          )
        }
      }
      
      character(0)
    }
    
    
    # ── Populate gene/signature search dropdown ──────────────────────────────
    
    observe({
      
      gene_names <- unique(genes_df$name)
      gene_choices <- setNames(
        object = paste0("GENE::", gene_names),
        nm = gene_names
      )
      
      sig_choices <- if (
        !is.null(signatures_df) &&
        nrow(signatures_df) > 0
      ) {
        
        setNames(
          object = paste0(
            "SIG::",
            signatures_df$Nomenclature
          ),
          nm = signatures_df$Nomenclature
        )
        
      } else {
        
        character(0)
      }
      
      updateSelectizeInput(
        session = session,
        inputId = "gene_search",
        choices = c(
          gene_choices,
          sig_choices
        ),
        server = FALSE,
        selected = character(0)
      )
    })
    
    
    # ── Build gene ↔ entity edges with evidence attributes ───────────────────
    #
    # One edge per (gene, canonical entity). Duplicate rows from distinct
    # original forms are aggregated. The kept row is the one with the
    # strongest role (EXECUTOR > REGULATOR > MARKER > UNCERTAIN), then the
    # strongest direction (PROMOTES/PROTECTS > UNCLEAR), then the strongest
    # tier (ET1 > ET2 > ET3 > ET4). pmid_count counts the unique PMIDs.
    #
    # Vectorized (order + duplicated) instead of split() + lapply(), which
    # took ~35 s over 21,568 groups; this finishes in < 1 s.
    
    all_edges <- reactive({
      
      df <- genes_df[
        !is.na(genes_df$Pathway_Categorization) &
        genes_df$Pathway_Categorization != "",
        ,
        drop = FALSE
      ]
      
      if (nrow(df) == 0) {
        return(data.frame(
          from = character(0), to = character(0),
          role = character(0), direction = character(0),
          tier = character(0), mech = character(0), pmid_count = integer(0),
          stringsAsFactors = FALSE
        ))
      }
      
      srcs <- src_list()
      has_tier <- "evidence_tier" %in% names(df)
      has_mech <- "mechanistic_class" %in% names(df)
      has_pmid <- "pmid_list" %in% names(df)

      key <- paste(df$name, df$Pathway_Categorization, sep = "")

      sc <- srcs[[1]]
      role_pri <- c(EXECUTOR = 3L, REGULATOR = 2L, MARKER = 1L, UNCERTAIN = 0L)
      rp <- role_pri[as.character(df[[sc$role]])]
      rp[is.na(rp)] <- 0L

      dir_pri <- c(PROMOTES = 2L, PROTECTS = 2L, UNCLEAR = 0L)
      dp <- dir_pri[as.character(df[[sc$dir]])]
      dp[is.na(dp)] <- 0L

      tier_pri <- c(ET1 = 4L, ET2 = 3L, ET3 = 2L, ET4 = 1L)
      tp <- if (has_tier) tier_pri[as.character(df$evidence_tier)] else integer(nrow(df))
      tp[is.na(tp)] <- 1L

      mech_pri <- c(MECHANISTIC = 6L, CO_OCCURRENCE = 5L, LITERATURE_GAP = 4L,
                    CONTEXT_GAP = 3L, DATABASE_ONLY = 2L, INSUFFICIENT_DATA = 1L)
      mp <- if (has_mech) mech_pri[as.character(df$mechanistic_class)] else integer(nrow(df))
      mp[is.na(mp)] <- 0L

      ord <- order(key, -rp, -dp, -tp, -mp, method = "radix")
      d2 <- df[ord, , drop = FALSE]
      k2 <- key[ord]
      first <- !duplicated(k2)
      d3 <- d2[first, , drop = FALSE]

      tier <- as.character(d3$evidence_tier)
      tier[is.na(tier) | tier == ""] <- "ET4"
      mech <- if (has_mech) as.character(d3$mechanistic_class) else rep("INSUFFICIENT_DATA", nrow(d3))
      mech[is.na(mech) | mech == ""] <- "INSUFFICIENT_DATA"

      if (length(srcs) == 1) {
        role <- as.character(d3[[sc$role]])
        role[is.na(role) | role == ""] <- "UNCERTAIN"
        direction <- as.character(d3[[sc$dir]])
        direction[is.na(direction) | direction == ""] <- "UNCLEAR"
        edge_color <- rep("#57534e", nrow(d3))
        edge_dashes <- rep(FALSE, nrow(d3))
        edge_label <- rep("", nrow(d3))
        edge_title <- rep("", nrow(d3))
      } else {
        dirs <- lapply(srcs, function(s) {
          v <- as.character(d3[[s$dir]])
          v[is.na(v) | v == ""] <- "UNCLEAR"
          v[v %in% c("ASSOCIATED", "BIDIRECTIONAL")] <- "UNCLEAR"
          v
        })
        roles <- lapply(srcs, function(s) {
          v <- as.character(d3[[s$role]])
          v[is.na(v) | v == ""] <- "UNCERTAIN"
          v
        })
        agreement <- vapply(seq_len(nrow(d3)), function(i) {
          length(unique(vapply(dirs, function(d) d[i], character(1))))
        }, integer(1))
        edge_color <- ifelse(agreement == 1, "#2E7D32",
                      ifelse(agreement == 2, "#F9A825", "#C62828"))
        edge_dashes <- agreement != 1
        initials <- vapply(srcs, function(s) substr(s$label, 1, 1), character(1))
        dir_short <- lapply(dirs, function(d) ifelse(d == "PROMOTES", "P",
                                              ifelse(d == "PROTECTS", "B", "U")))
        edge_label <- vapply(seq_len(nrow(d3)), function(i) {
          paste0(initials, ":", vapply(dir_short, function(d) d[i], character(1)), collapse = " ")
        }, character(1))
        edge_title <- vapply(seq_len(nrow(d3)), function(i) {
          parts <- vapply(seq_along(srcs), function(j) {
            paste0(srcs[[j]]$label, ": ", roles[[j]][i], " / ", dirs[[j]][i])
          }, character(1))
          paste(parts, collapse = "<br>")
        }, character(1))
        role <- vapply(seq_len(nrow(d3)), function(i) {
          tab <- sort(table(vapply(roles, function(r) r[i], character(1))), decreasing = TRUE)
          names(tab)[1]
        }, character(1))
        direction <- vapply(seq_len(nrow(d3)), function(i) {
          tab <- sort(table(vapply(dirs, function(d) d[i], character(1))), decreasing = TRUE)
          names(tab)[1]
        }, character(1))
      }
      
      # Unique PMID count per (gene, entity), computed only over rows with PMIDs.
      pm_count <- integer(sum(first))
      if (has_pmid) {
        pm_has <- !is.na(df$pmid_list) & nzchar(trimws(as.character(df$pmid_list)))
        if (any(pm_has)) {
          pk <- key[pm_has]
          toks <- strsplit(as.character(df$pmid_list[pm_has]), ";", fixed = TRUE)
          uni <- unique(pk)
          uu <- vapply(uni, function(k) {
            length(unique(trimws(unlist(toks[pk == k]))))
          }, integer(1))
          pm_map <- setNames(uu, uni)
          got <- pm_map[k2[first]]
          got[is.na(got)] <- 0L
          pm_count <- got
        }
      }
      
      data.frame(
        from = d2$name[first],
        to = d2$Pathway_Categorization[first],
        role = role,
        direction = direction,
        tier = tier,
        mech = mech,
        pmid_count = pm_count,
        color = edge_color,
        dashes = edge_dashes,
        label = edge_label,
        title = edge_title,
        stringsAsFactors = FALSE
      )
    })
    
    
    # ── Populate RCD filter ──────────────────────────────────────────────────
    
    observe({
      
      edges <- all_edges()
      
      if (nrow(edges) == 0) {
        
        updateSelectizeInput(
          session = session,
          inputId = "rcd_filter",
          choices = character(0),
          server = FALSE
        )
        
        return()
      }
      
      rcds <- sort(
        unique(edges$to)
      )
      
      updateSelectizeInput(
        session = session,
        inputId = "rcd_filter",
        choices = rcds,
        server = FALSE
      )
    })

    # not-found guard: the create callback returns false (no list contamination)
    # and triggers this pop-up for a typed entity absent from the network.
    
    
    # ── View statistics (live strip under the legend) ────────────────────────
    
    stats_rv <- reactiveVal(NULL)
    
    
    # ── Render network ───────────────────────────────────────────────────────
    
    output$network <- renderVisNetwork({
      
      # Require an entity selection: the full unfiltered atlas is not rendered
      # (it would be a ~9,000-node hairball). Select one or more entities.
      shiny::validate(
        shiny::need(
          length(input$rcd_filter) > 0,
          "Select one or more RCD entities to display their full gene network."
        )
      )
      
      edges <- all_edges()
      
      if (nrow(edges) == 0) {
        return(NULL)
      }
      
      lvl_map <- entity_level()
      
      
      # ── Apply selected RCD filters ─────────────────────────────────────────
      
      selected_rcds <- input$rcd_filter
      
      if (
        !is.null(selected_rcds) &&
        length(selected_rcds) > 0
      ) {
        
        edges <- edges[
          edges$to %in% selected_rcds,
          ,
          drop = FALSE
        ]
      }
      
      
      # ── Apply level filter ─────────────────────────────────────────────────
      
      selected_levels <- input$level_filter
      
      if (
        !is.null(selected_levels) &&
        length(selected_levels) > 0
      ) {
        
        edge_lv <- lvl_map[edges$to]
        edge_lv[is.na(edge_lv) | edge_lv == ""] <- "L5"
        
        edges <- edges[
          edge_lv %in% selected_levels,
          ,
          drop = FALSE
        ]
      }
      
      
      # ── Apply gene role filter ─────────────────────────────────────────────
      
      selected_roles <- input$role_filter
      
      if (
        !is.null(selected_roles) &&
        length(selected_roles) > 0
      ) {
        
        edges <- edges[
          edges$role %in% selected_roles,
          ,
          drop = FALSE
        ]
      }
      
      
      # ── Apply mechanistic class filter ─────────────────────────────────────
      
      selected_mech <- input$mech_filter
      
      if (
        !is.null(selected_mech) &&
        length(selected_mech) > 0
      ) {
        
        edges <- edges[
          edges$mech %in% selected_mech,
          ,
          drop = FALSE
        ]
      }
      
      if (nrow(edges) == 0) {
        return(NULL)
      }
      
      
      # ── Searched genes (for emphasis) ───────────────────────────────────────
      
      must_keep <- resolve_search_genes(
        input$gene_search
      )
      
      # ── Totals before any display cap (for transparent stats) ──────────────
      
      total_genes <- length(unique(edges$from))
      total_edges <- nrow(edges)
      
      # ── Optional display cap (tier-prioritized, never random) ──────────────
      # "All" = no cap. Otherwise keep the strongest-evidence genes per entity
      # (ET1 > ET2 > ET3 > ET4); searched genes always bypass the cap.
      
      cap_value <- suppressWarnings(as.numeric(input$cap_select))
      
      if (!is.na(cap_value)) {
        tier_pri <- c(ET1 = 4, ET2 = 3, ET3 = 2, ET4 = 1)
        edges$tp <- tier_pri[edges$tier]
        edges$tp[is.na(edges$tp)] <- 0
        
        edges <- do.call(rbind, lapply(split(edges, edges$to), function(df) {
          genes <- unique(df$from)
          keep_genes <- intersect(genes, must_keep)
          others <- setdiff(genes, keep_genes)
          ord <- order(-df$tp[match(others, df$from)])
          others_sorted <- others[ord]
          slots <- max(0, cap_value - length(keep_genes))
          take <- others_sorted[seq_len(min(slots, length(others_sorted)))]
          df[df$from %in% c(keep_genes, take), , drop = FALSE]
        }))
        edges$tp <- NULL
      }

      # Edge id (from|||to) for the edge-click evidence pop-up.
      edges$id <- paste0(edges$from, "|||", edges$to)
      
      # View statistics (for the live strip)
      stats_rv(list(
        genes = length(unique(edges$from)),
        total_genes = total_genes,
        entities = length(unique(edges$to)),
        edges = nrow(edges),
        total_edges = total_edges,
        t1 = sum(edges$tier == "ET1"),
        t4 = sum(edges$tier == "ET4")
      ))

      # Edge styling: color = entity level, width = evidence tier,
      # dashes = ET4, direction = arrow (PROMOTES) / bar label (PROTECTS).
      edge_lv <- lvl_map[edges$to]
      edge_lv[is.na(edge_lv) | edge_lv == ""] <- "L5"
      edge_col <- network_level_colors()[edge_lv]
      edge_col[is.na(edge_col)] <- "#FF6D00"
      
      tier_width <- c(ET1 = 3, ET2 = 2, ET3 = 1.5, ET4 = 1)
      edge_w <- tier_width[edges$tier]
      edge_w[is.na(edge_w)] <- 1
      
      edges$width  <- edge_w
      edges$arrows <- ifelse(edges$direction == "PROMOTES", "to", "")
      if (length(src_list()) == 1) {
        edges$color  <- edge_col
        edges$dashes <- edges$tier == "ET4"
        edges$label  <- ifelse(edges$direction == "PROTECTS", "⊣", "")
      }
      
      if (
        is.null(edges) ||
        nrow(edges) == 0
      ) {
        return(NULL)
      }
      
      
      # ── Determine connected genes and entities ─────────────────────────────
      
      connected_genes <- unique(
        edges$from
      )
      
      unique_rcds <- unique(
        edges$to
      )
      
      
      # ── Ontology level + definition per visible entity ─────────────────────
      
      def_map <- entity_def_map()
      
      entity_levels <- lvl_map[unique_rcds]
      entity_levels <- ifelse(
        !is.na(entity_levels) & nzchar(entity_levels),
        entity_levels,
        "L5"
      )
      
      lvl_names  <- network_level_names()[entity_levels]
      lvl_colors <- network_level_colors()[entity_levels]
      lvl_colors[is.na(lvl_colors)] <- "#FF6D00"
      
      defs <- def_map[unique_rcds]
      defs <- ifelse(!is.na(defs), defs, "")
      
      entity_titles <- vapply(seq_along(unique_rcds), function(i) {
        parts <- paste0("<b>", unique_rcds[i], "</b>")
        if (nzchar(lvl_names[i])) {
          parts <- paste0(parts, "<br>", lvl_names[i])
        }
        if (nzchar(defs[i])) {
          parts <- paste0(parts, "<br>", defs[i])
        }
        parts
      }, character(1))
      
      
      # ── Dominant role per visible gene (for gene node color) ───────────────
      
      role_by_gene <- tapply(edges$role, edges$from, function(x) {
        x <- x[!is.na(x) & nzchar(x)]
        strong <- x[x != "UNCERTAIN"]
        if (length(strong)) names(sort(table(strong), decreasing = TRUE))[1] else "UNCERTAIN"
      })
      gene_role <- role_by_gene[connected_genes]
      gene_role_color <- NET_ROLE_COLORS[gene_role]
      gene_role_color[is.na(gene_role_color)] <- "#9E9E9E"
      
      
      # ── Gene hover titles (symbol + HGNC name) ─────────────────────────────
      
      gene_titles <- vapply(connected_genes, function(g) {
        nm <- gene_name_map[g]
        if (!is.na(nm) && nzchar(nm)) {
          paste0("<b>", g, "</b><br>", nm)
        } else {
          paste0("<b>", g, "</b>")
        }
      }, character(1))
      
      
      # ── Load RCD logos ─────────────────────────────────────────────────────
      
      logo_dir <- "data/RCD modulo/logo RCDs"
      
      logo_files <- list.files(
        path = logo_dir,
        pattern = "\\.(JPG|PNG)$",
        ignore.case = TRUE
      )
      
      logo_names <- gsub(
        pattern = "\\.(JPG|PNG)$",
        replacement = "",
        x = logo_files,
        ignore.case = TRUE
      )
      
      logo_norm <- rcd_normalize(
        logo_names
      )
      
      rcd_to_logo <- setNames(
        object = paste0(
          "rcd_logos/",
          logo_files
        ),
        nm = logo_norm
      )
      
      
      # ── Gene nodes ─────────────────────────────────────────────────────────
      
      is_hit <- connected_genes %in% must_keep
      
      # Degree-based sizing: hub genes (connected to many entities) get larger.
      gene_deg <- table(edges$from)
      entity_deg <- table(edges$to)
      gene_deg_vec <- as.numeric(gene_deg[connected_genes])
      gene_deg_vec[is.na(gene_deg_vec)] <- 0
      gene_size <- ifelse(is_hit, 14, 6) + 8 * sqrt(gene_deg_vec / max(gene_deg_vec, 1))
      
      gene_nodes <- data.frame(
        
        id = connected_genes,
        
        label = connected_genes,
        
        group = "Gene",
        
        title = gene_titles,
        
        shape = "dot",
        
        size = gene_size,
        
        image = NA_character_,
        
        mass = 1,
        
        color.background = gene_role_color,
        
        color.border = ifelse(
          is_hit,
          "#c0392b",
          gene_role_color
        ),
        
        color.highlight.background = gene_role_color,
        
        color.highlight.border = "#c0392b",
        
        borderWidth = ifelse(
          is_hit,
          3,
          1
        ),
        
        opacity = ifelse(any(is_hit), ifelse(is_hit, 1, 0.35), 1),
        
        font.color = ifelse(
          is_hit,
          "#c0392b",
          "#1c1917"
        ),
        
        stringsAsFactors = FALSE
      )
      
      
      # ── RCD nodes (level-colored) ──────────────────────────────────────────

      canonical_set <- unique(genes_df$Pathway_Categorization[
        !is.na(genes_df$Pathway_Categorization) &
        genes_df$Pathway_Categorization != ""
      ])
      is_canonical <- unique_rcds %in% canonical_set

      rcd_images <- unname(
        rcd_to_logo[
          rcd_normalize(unique_rcds)
        ]
      )

      has_logo <- !is.na(rcd_images) & rcd_images != ""

      # Degree-based sizing: well-populated entities get larger.
      entity_deg_vec <- as.numeric(entity_deg[unique_rcds])
      entity_deg_vec[is.na(entity_deg_vec)] <- 0
      entity_size <- ifelse(has_logo, 35, 25) + 12 * sqrt(entity_deg_vec / max(entity_deg_vec, 1))

      rcd_nodes <- data.frame(
        
        id = unique_rcds,
        
        label = ifelse(has_logo, "", unique_rcds),
        
        group = "RCD",
        
        title = entity_titles,
        
        shape = ifelse(has_logo, "image", "dot"),
        
        image = ifelse(has_logo, rcd_images, NA_character_),
        
        size = entity_size,
        
        mass = 2,
        
        color.background = ifelse(has_logo, "", lvl_colors),
        
        color.border = lvl_colors,
        
        color.highlight.background = ifelse(has_logo, "", lvl_colors),
        
        color.highlight.border = lvl_colors,
        
        borderWidth = ifelse(has_logo, 3, 2),
        
        opacity = 1,
        
        font.color = "#1c1917",
        
        stringsAsFactors = FALSE
      )
      
      
      # ── RCD-to-RCD edges (non-canonical → canonical) ──────────────────────
      
      rcd_map_df <- unique(genes_df[
        !is.na(genes_df$rcd_form_original) & genes_df$rcd_form_original != "" &
        !is.na(genes_df$Pathway_Categorization) & genes_df$Pathway_Categorization != "",
        c("rcd_form_original", "Pathway_Categorization")
      ])
      rcd_map_df <- rcd_map_df[
        rcd_map_df$rcd_form_original != rcd_map_df$Pathway_Categorization,
      ]
      rcd_map_df <- unique(rcd_map_df)

      if (nrow(rcd_map_df) > 0) {
        rcd_edges <- data.frame(
          id = paste0(rcd_map_df$rcd_form_original, "|||", rcd_map_df$Pathway_Categorization),
          from = rcd_map_df$rcd_form_original,
          to = rcd_map_df$Pathway_Categorization,
          role = "",
          direction = "",
          tier = "",
          mech = "",
          pmid_count = 0L,
          dashes = TRUE,
          color = "rgba(255,152,0,0.45)",
          width = 1,
          arrows = "",
          label = "",
          stringsAsFactors = FALSE
        )
        # Keep only edges whose endpoints are visible
        all_node_ids <- c(connected_genes, unique_rcds)
        rcd_edges <- rcd_edges[
          rcd_edges$from %in% all_node_ids &
          rcd_edges$to %in% all_node_ids,
        ]
        if (nrow(rcd_edges) > 0) {
          edges <- rbind(edges, rcd_edges)
        }
      }
      
      
      # ── Edge hover titles (role · direction · tier · PMID count) ───────────
      
      if (length(src_list()) == 1) {
      edges$title <- ifelse(
          nzchar(edges$role),
          paste0(
            edges$role, " \u00b7 ", edges$direction, " \u00b7 ",
            edges$tier, " \u00b7 ", edges$pmid_count, " PMID"
          ),
          "legacy form \u2192 normalized entity"
        )
      }


      # ── Combine node types ─────────────────────────────────────────────────
      
      nodes <- rbind(
        gene_nodes,
        rcd_nodes
      )
      
      
      # ── Provenance caption + export filename from the active selection ────
      
      prov_parts <- c(
        if (length(selected_rcds) > 0) paste0("entity:", paste(selected_rcds, collapse = ",")),
        if (length(selected_levels) > 0) paste0("level:", paste(selected_levels, collapse = ",")),
        if (length(selected_roles) > 0) paste0("role:", paste(selected_roles, collapse = ",")),
        if (length(must_keep) > 0) paste0("gene:", paste(must_keep, collapse = ","))
      )
      
      prov_label <- if (length(prov_parts) > 0) {
        paste(prov_parts, collapse = " \u00b7 ")
      } else {
        "all entities \u00b7 all levels \u00b7 all roles"
      }
      prov_label_rv(prov_label)
      
      prov_caption <- paste0(
        "<span style='font-family:\"Segoe UI\",system-ui,sans-serif;font-size:16px;color:#78716c;'>Selection: ",
        prov_label,
        "</span>"
      )
      
      export_name <- paste0(
        "rcdome_network_",
        gsub("[^A-Za-z0-9._-]+", "_", paste(prov_parts, collapse = "_"))
      )
      if (length(prov_parts) == 0) {
        export_name <- "rcdome_network_all"
      }
      export_name_rv(export_name)
      
      
      # ── Construct visNetwork ───────────────────────────────────────────────
      
      visNetwork(
        nodes = nodes,
        edges = edges,
        width = "100%",
        height = "75vh",
        submain = prov_caption
      ) %>%
        
        visGroups(
          groupname = "Gene"
        ) %>%
        
        visGroups(
          groupname = "RCD"
        ) %>%
        
        visOptions(
          highlightNearest = list(
            enabled = TRUE,
            degree = 1,
            hover = TRUE
          )
        ) %>%
        
        
        # Physics is used only for the initial organization of the network.
        visPhysics(
          
          enabled = TRUE,
          
          solver = "barnesHut",
          
          barnesHut = list(
            
            gravitationalConstant = -3000,
            
            springLength = 130,
            
            springConstant = 0.03,
            
            centralGravity = 0.5,
            
            damping = 0.3,
            
            avoidOverlap = 1
          ),
          
          stabilization = list(
            
            enabled = TRUE,
            
            iterations = 300,
            
            updateInterval = 25,
            
            onlyDynamicEdges = FALSE,
            
            fit = TRUE
          )
        ) %>%
        
        
        # IMPORTANT:
        # afterDrawing was removed because it used moveNode() every time the
        # network was redrawn. Zooming redraws the network, so that event
        # continuously repositioned the nodes.
        visEvents(
          
          click = sprintf(
            paste0(
              "function(n) {",
              "  var nn = (n.nodes && n.nodes.length) ? n.nodes[0] : null;",
              "  var ne = (n.edges && n.edges.length) ? n.edges[0] : null;",
              "  Shiny.setInputValue(",
              "    '%s',",
              "    nn,",
              "    {priority: 'event'}",
              "  );",
              "  Shiny.setInputValue(",
              "    '%s',",
              "    ne,",
              "    {priority: 'event'}",
              "  );",
              "}"
            ),
            session$ns("rcd_clicked"),
            session$ns("edge_clicked")
          ),
          
          
          # Hide the canvas while the initial layout is calculated.
          startStabilizing = "
            function() {

              var frame = this.canvas.frame;

              frame.style.transition = 'none';
              frame.style.opacity = 0;
            }
          ",
          
          
          # Once the initial layout is ready, disable physics completely.
          #
          # From this point onward:
          # - Zoom changes only the camera scale.
          # - Canvas dragging changes only the camera position.
          # - Nodes are not automatically repositioned.
          stabilizationIterationsDone = "
            function() {

              this.stopSimulation();

              this.setOptions({
                physics: {
                  enabled: false
                }
              });

              var frame = this.canvas.frame;

              frame.style.transition = 'opacity 0.6s ease-in';
              frame.style.opacity = 1;
            }
          "
        ) %>%
        
        
        # Camera and node interaction.
        visInteraction(
          
          hover = TRUE,
          
          navigationButtons = TRUE,
          
          keyboard = list(
            enabled = TRUE,
            bindToWindow = FALSE
          ),
          
          dragNodes = TRUE,
          
          dragView = TRUE,
          
          zoomView = TRUE,
          
          multiselect = TRUE,
          
          selectable = TRUE,
          
          selectConnectedEdges = TRUE
        ) %>%
        
        
        # Edge appearance.
        visEdges(
          
          color = list(
            
            opacity = 0.45,
            
            color = "#a8a29e",
            
            highlight = "#FF9800",
            
            hover = "#FF9800"
          ),
          
          smooth = FALSE,
          
          width = 0.8,
          
          selectionWidth = 1.5,
          
          hoverWidth = 1.2
        ) %>%
        visExport(
          type = "png",
          name = export_name,
          label = "",
          style = "display:none;"
        )
    })
    
    # ── High-resolution network export (PNG 300 DPI + PDF) ───────────────────
    observeEvent(input$export_png, {
      nm <- export_name_rv()
      shinyjs::runjs(sprintf(paste0(
        "(function(){var g=document.getElementById('graph%s'); if(!g)return; ",
        "var s=3, ow=g.offsetWidth, oh=g.offsetHeight; ",
        "g.style.width=(ow*s)+'px'; g.style.height=(oh*s)+'px'; window.dispatchEvent(new Event('resize')); ",
        "setTimeout(function(){var cv=g.querySelector('canvas'); if(!cv){g.style.width=ow+'px';g.style.height=oh+'px';window.dispatchEvent(new Event('resize'));return;} ",
        "var cv2=document.createElement('canvas'); cv2.width=cv.width; cv2.height=cv.height; var c=cv2.getContext('2d'); c.fillStyle='#ffffff'; c.fillRect(0,0,cv2.width,cv2.height); c.drawImage(cv,0,0); var cfs=Math.round(cv.width*0.02); c.font='600 '+cfs+'px Segoe UI, sans-serif'; c.fillStyle='#57534e'; c.textAlign='left'; c.textBaseline='top'; c.fillText('Selection: %s',Math.round(cv.width*0.015),Math.round(cv.width*0.02)); var wm='\\u00A9 RCDome Group 2026. Cite us'; ",
        "var fs=Math.max(11,Math.round(cv.width*0.012)); c.font='600 '+fs+'px Segoe UI, sans-serif'; ",
        "c.textAlign='right'; c.textBaseline='alphabetic'; var pad=Math.round(cv.width*0.012); var tw=c.measureText(wm).width; ",
        "c.fillStyle='rgba(0,0,0,0.2)'; c.fillRect(cv.width-tw-pad*2,cv.height-fs-pad*2,tw+pad*2,fs+pad*2); ",
        "c.fillStyle='#ffffff'; c.fillText(wm,cv.width-pad,cv.height-pad); ",
        "cv2.toBlob(function(blob){saveAs(blob,'%s.png');},'image/png'); ",
        "g.style.width=ow+'px'; g.style.height=oh+'px'; window.dispatchEvent(new Event('resize')); }, 900); })();"
      ), session$ns("network"), prov_label_rv(), nm))
    })
    
    observeEvent(input$export_pdf, {
      nm <- export_name_rv()
      shinyjs::runjs(sprintf(paste0(
        "(function(){var g=document.getElementById('graph%s'); if(!g)return; ",
        "var s=3, ow=g.offsetWidth, oh=g.offsetHeight; ",
        "g.style.width=(ow*s)+'px'; g.style.height=(oh*s)+'px'; window.dispatchEvent(new Event('resize')); ",
        "setTimeout(function(){var cv=g.querySelector('canvas'); if(!cv){g.style.width=ow+'px';g.style.height=oh+'px';window.dispatchEvent(new Event('resize'));return;} ",
        "var cv2=document.createElement('canvas'); cv2.width=cv.width; cv2.height=cv.height; var c=cv2.getContext('2d'); c.fillStyle='#ffffff'; c.fillRect(0,0,cv2.width,cv2.height); c.drawImage(cv,0,0); var cfs=Math.round(cv.width*0.02); c.font='600 '+cfs+'px Segoe UI, sans-serif'; c.fillStyle='#57534e'; c.textAlign='left'; c.textBaseline='top'; c.fillText('Selection: %s',Math.round(cv.width*0.015),Math.round(cv.width*0.02)); var wm='\\u00A9 RCDome Group 2026. Cite us'; ",
        "var fs=Math.max(11,Math.round(cv.width*0.012)); c.font='600 '+fs+'px Segoe UI, sans-serif'; ",
        "c.textAlign='right'; c.textBaseline='alphabetic'; var pad=Math.round(cv.width*0.012); var tw=c.measureText(wm).width; ",
        "c.fillStyle='rgba(0,0,0,0.2)'; c.fillRect(cv.width-tw-pad*2,cv.height-fs-pad*2,tw+pad*2,fs+pad*2); ",
        "c.fillStyle='#ffffff'; c.fillText(wm,cv.width-pad,cv.height-pad); ",
        "var img=cv2.toDataURL('image/png',1.0); var pdf=new jsPDF('l','pt',[cv2.width,cv2.height]); pdf.addImage(img,'PNG',0,0,cv2.width,cv2.height); pdf.save('%s.pdf'); ",
        "g.style.width=ow+'px'; g.style.height=oh+'px'; window.dispatchEvent(new Event('resize')); }, 900); })();"
      ), session$ns("network"), prov_label_rv(), nm))
    })
    
    
    # ── Live statistics strip ────────────────────────────────────────────────
    
    output$network_stats <- renderUI({
      s <- stats_rv()
      if (is.null(s)) return(NULL)
      
      tags$div(
        style = paste(
          "display: flex; flex-wrap: wrap; gap: 6px 16px; align-items: center;",
          "padding: 8px 14px; margin-bottom: 12px; background: #ffffff;",
          "border: 1px solid #e7e5e4; border-radius: 10px; font-size: 13px;",
          "color: #57534e;"
        ),
        tags$span(
          style = "font-weight:600; color:#78716c;",
          if (s$genes != s$total_genes) {
            paste0(s$genes, " of ", s$total_genes, " genes")
          } else {
            paste0(s$genes, " genes")
          }
        ),
        tags$span("·", style = "color:#d6d3d1;"),
        tags$span(paste0(s$entities, " entities")),
        tags$span("·", style = "color:#d6d3d1;"),
        tags$span(
          if (s$edges != s$total_edges) {
            paste0(s$edges, " of ", s$total_edges, " edges")
          } else {
            paste0(s$edges, " edges")
          }
        ),
        tags$span("·", style = "color:#d6d3d1;"),
        tags$span(paste0("ET1: ", s$t1), style = "color:#198754; font-weight:600;"),
        tags$span("·", style = "color:#d6d3d1;"),
        tags$span(paste0("ET4: ", s$t4), style = "color:#a8a29e; font-weight:600;")
      )
    })
    
    
    # ── Gene/signature search ────────────────────────────────────────────────
    #
    # The selected genes are highlighted directly in the node data.
    # The proxy call only focuses the camera and selects the nodes.
    
    observeEvent(
      input$gene_search,
      {
        
        term <- input$gene_search
        
        if (
          is.null(term) ||
          term == ""
        ) {
          
          visNetworkProxy(
            shinyId = "network",
            session = session
          ) %>%
            visUnselectAll()
          
          return()
        }
        
        target_genes <- resolve_search_genes(
          term
        )
        
        if (length(target_genes) == 0) {
          return()
        }
        
        session$onFlushed(
          function() {
            
            visNetworkProxy(
              shinyId = "network",
              session = session
            ) %>%
              
              visFocus(
                id = target_genes[1],
                scale = 1.2,
                animation = list(
                  duration = 500,
                  easingFunction = "easeInOutQuad"
                )
              ) %>%
              
              visSelectNodes(
                id = target_genes
              )
          },
          once = TRUE
        )
      },
      ignoreNULL = TRUE,
      ignoreInit = TRUE
    )
    
    
    # ── Node click handler ───────────────────────────────────────────────────
    
    observeEvent(
      input$rcd_clicked,
      {
        
        node_id <- input$rcd_clicked
        
        if (
          is.null(node_id) ||
          node_id == ""
        ) {
          return()
        }
        
        edges <- all_edges()
        proxy <- visNetworkProxy(
          shinyId = "network",
          session = session
        )
        
        if (node_id %in% edges$from) {
          
          # Gene: open the gene modal + pin its neighborhood (persistent).
          show_gene_info_modal(
            node_id,
            genes_df
          )
          
          neighbors <- unique(edges$to[edges$from == node_id])
          
          session$onFlushed(
            function() {
              proxy %>%
                visSelectNodes(
                  id = c(node_id, neighbors)
                )
            },
            once = TRUE
          )
        }
      },
      ignoreNULL = TRUE,
      ignoreInit = TRUE
    )
    
    
    # ── Edge click handler (evidence pop-up) ─────────────────────────────────
    
    observeEvent(
      input$edge_clicked,
      {
        
        edge_id <- input$edge_clicked
        
        if (
          is.null(edge_id) ||
          edge_id == ""
        ) {
          return()
        }
        
        parts <- strsplit(edge_id, "|||", fixed = TRUE)[[1]]
        
        if (length(parts) != 2) {
          return()
        }
        
        # Evidence Trail drawer (upgrades the old edge-evidence modal)
        evidence_trail_rv(list(gene = parts[1], entity = parts[2]))
        shinyjs::runjs("document.getElementById('evidence_drawer').style.display='block';")
      },
      ignoreNULL = TRUE,
      ignoreInit = TRUE
    )
  })
}




# ─── Simple gene info modal (same info as Genes tab pop-up) ─────────────────

show_gene_info_modal <- function(gene_name, genes_df) {
  row <- genes_df[genes_df$name == gene_name, , drop = FALSE]
  if (nrow(row) == 0) return()
  first_row <- row[1, ]
  pathways <- get_pathways_for_gene(first_row, genes_df)
  pathways_str <- if (length(pathways) > 0) paste(pathways, collapse = "  ·  ") else "No RCD entities associated"

  hg <- hgnc_map[hgnc_map$symbol == gene_name, , drop = FALSE]
  hg <- if (nrow(hg) > 0) hg[1, ] else NULL
  gene_name_desc <- if (!is.null(hg) && !is.na(hg$name) && nzchar(hg$name)) hg$name else ""
  hgnc_id <- if (!is.null(hg)) hg$hgnc_id %||% "" else ""
  entrez <- if (!is.null(hg)) hg$entrez_id %||% "" else ""
  ensembl <- first_row$ensembl_id %||% ""
  uniprot <- first_row$uniprot_id %||% ""

  links <- character(0)
  if (nzchar(hgnc_id)) links <- c(links, paste0("<a href='https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/", hgnc_id, "' target='_blank'>HGNC ↗</a>"))
  if (nzchar(ensembl)) links <- c(links, paste0("<a href='https://www.ensembl.org/Homo_sapiens/Gene/Summary?g=", ensembl, "' target='_blank'>Ensembl ↗</a>"))
  if (nzchar(entrez)) links <- c(links, paste0("<a href='https://www.ncbi.nlm.nih.gov/gene/", entrez, "' target='_blank'>NCBI Gene ↗</a>"))
  if (nzchar(uniprot)) links <- c(links, paste0("<a href='https://www.uniprot.org/uniprot/", uniprot, "' target='_blank'>UniProt ↗</a>"))

  showModal(modalDialog(
    title = tags$div(
      tags$strong(gene_name),
      if (nzchar(gene_name_desc)) tags$span(paste0(" — ", gene_name_desc), style = "font-size: 0.85em; color: #a8a29e; margin-left: 8px;")
    ),
    size = "l", easyClose = TRUE, footer = modalButton("Close"),
    if (length(links) > 0) tags$p(HTML(paste(links, collapse = " · "))) else NULL,
    tags$p(
      tags$strong("RCD entities associated: "),
      tags$span(pathways_str, style = "color: #198754;")
    )
  ))
}


# ─── Edge evidence modal (actual PMIDs for a clicked gene↔entity edge) ───────

show_edge_evidence_modal <- function(gene, entity, genes_df) {
  rows <- genes_df[
    genes_df$name == gene & genes_df$Pathway_Categorization == entity,
    ,
    drop = FALSE
  ]
  if (nrow(rows) == 0) return()
  
  pm <- rows$pmid_list
  pm <- pm[!is.na(pm) & nzchar(trimws(as.character(pm)))]
  pmids <- unique(trimws(unlist(strsplit(
    paste(pm, collapse = ";"), ";", fixed = TRUE
  ))))
  pmids <- pmids[nzchar(pmids)]
  
  links <- if (length(pmids) > 0) {
    vapply(pmids, function(p) {
      paste0(
        "<a href='https://pubmed.ncbi.nlm.nih.gov/", p, "/' target='_blank'>",
        p, "</a>"
      )
    }, character(1))
  } else {
    character(0)
  }
  
  showModal(modalDialog(
    title = tags$div(
      tags$strong(gene),
      tags$span(paste0(" \u00b7 ", entity), style = "font-weight:400; color:#57534e;")
    ),
    size = "l", easyClose = TRUE, footer = modalButton("Close"),
    if (length(links) > 0) {
      tags$p(
        tags$strong(paste0("Evidence PMIDs (", length(pmids), "): ")),
        HTML(paste(links, collapse = " · "))
      )
    } else {
      tags$p("No PMID recorded for this association.")
    }
  ))
}
