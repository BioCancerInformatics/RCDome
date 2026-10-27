# ─── Module: omic ────────────────────────────────────────────────────────────
# Multi-omics catalog: Genes · Isoforms · miRNA · Proteins
# 4 sub-tabs, each with a DT table + gene detail modal on click.
# Data is lazy-loaded: each table loads only when its tab is first opened.

mod_gene_catalog_ui <- function(id) {
  ns <- NS(id)
  tagList(
    tags$div(style = "background:#0b1020; color:#e7e5e4; border-radius:12px; padding:28px 26px; margin-bottom:16px;",
      tags$h1("Gene Catalog", style = "font-size:35px; margin:0;"),
      tags$p(
        tags$span(paste0(format(rcd_counts$n_genes, big.mark = ","), " HGNC-validated genes"), style = "color:#FFD700; font-weight:600;"), " · ",
        tags$span("53 RCD-related entities", style = "color:#FFD700; font-weight:600;"), " · ",
        tags$span(paste0(format(rcd_counts$n_pairs, big.mark = ","), " unique gene–RCD pairs"), style = "color:#FFD700; font-weight:600;"),
        style = "color:#d6d3d1; margin:6px 0 0; font-size:15px;"
      ),
      tags$p(
        tags$span("Evidence-first:", style = "color:#a8a29e; font-weight:600;"), " ",
        tags$span(paste0(format(rcd_counts$ef_mech, big.mark = ","), " mechanistic"), style = "color:#FF9800; font-weight:600;"), " · ",
        tags$span(paste0(format(rcd_counts$ef_exec, big.mark = ","), " executors"), style = "color:#FF9800; font-weight:600;"), " · ",
        tags$span(paste0(format(rcd_counts$ef_reg, big.mark = ","), " regulators"), style = "color:#FF9800; font-weight:600;"), " · ",
        tags$span("verbatim-grounded", style = "color:#a8a29e; font-weight:600;"),
        style = "color:#d6d3d1; margin:4px 0 0; font-size:14px;"
      ),
      tags$p(
        tags$span("DeepSeek:", style = "color:#a8a29e; font-weight:600;"), " ",
        tags$span(paste0(format(rcd_counts$mech_yes, big.mark = ","), " mechanistic"), style = "color:#FF9800; font-weight:600;"), " · ",
        tags$span(paste0(format(rcd_counts$role_exec, big.mark = ","), " executor pairs"), style = "color:#FF9800; font-weight:600;"), " · ",
        tags$span(paste0(format(rcd_counts$role_reg, big.mark = ","), " regulator pairs"), style = "color:#FF9800; font-weight:600;"), " · ",
        tags$span("complete (100% classified)", style = "color:#a8a29e; font-weight:600;"),
        style = "color:#d6d3d1; margin:4px 0 0; font-size:14px;"
      ),
      tags$p(
        tags$span("Compiled gene role:", style = "color:#a8a29e; font-weight:600;"), " ",
        tags$span(paste0(format(rcd_counts$compiled_exec, big.mark = ","), " executor pairs"), style = "color:#FF9800; font-weight:600;"), " · ",
        tags$span(paste0(format(rcd_counts$compiled_reg, big.mark = ","), " regulator pairs"), style = "color:#FF9800; font-weight:600;"), " · ",
        tags$span("source-derived role", style = "color:#a8a29e; font-weight:600;"),
        style = "color:#d6d3d1; margin:2px 0 0; font-size:14px;"
      ),
      tags$p("Click a row to see detailed information for that gene.",
             style = "color:#a8a29e; margin:12px 0 0; font-size:14px;")
    ),
    tags$div(style = "margin-bottom:12px;",
      tags$div("Direction/Role source (applies only to the Role and Direction columns):",
        `data-tip` = "Choose which analysis's Role/Direction values to show. Evidence-first = the final verbatim-grounded resolution (default). DeepSeek/Consensus/Compiled = the source classifications. GPT/Curator 1/Curator 2 = the arbitration votes (mapped to the source they sided with).",
        style = "font-weight:600; color:#1c1917; font-size:14px; margin:0 0 4px 0;"),
      tags$div(style = "display:flex; align-items:center; flex-wrap:wrap;",
      tags$label(
        `data-tip` = "Evidence-first resolution — the final verbatim-grounded verdict. Role: EXECUTOR/REGULATOR/MARKER/UNCERTAIN · Direction: PROMOTES/PROTECTS/UNCLEAR.",
        style = "margin:0 14px 0 0; display:inline-flex; align-items:center; gap:5px; cursor:pointer; font-weight:600; font-size:14px;",
        tags$input(type = "radio", name = ns("source_sel_r"), value = "evidence", checked = "checked", style = "margin:0;"),
        "Evidence-first"),
      tags$label(
        `data-tip` = "DeepSeek chain-of-thought classification — complete (100%). Role: EXECUTOR/REGULATOR/MARKER/UNCERTAIN · Direction: PROMOTES/PROTECTS/UNCLEAR.",
        style = "margin:0 0 0 14px; display:inline-flex; align-items:center; gap:5px; cursor:pointer; font-weight:400; font-size:14px;",
        tags$input(type = "radio", name = ns("source_sel_r"), value = "deepseek", style = "margin:0;"),
        "DeepSeek"),
      tags$label(
        `data-tip` = "Source-derived functional role compiled from the source databases and Elicit Phase 3 extraction (not an Elicit-only classification). Role: EXECUTOR/REGULATOR/MARKER/UNCERTAIN · Direction: PROMOTES/PROTECTS/UNCLEAR.",
        style = "margin:0 0 0 14px; display:inline-flex; align-items:center; gap:5px; cursor:pointer; font-weight:400; font-size:14px;",
        tags$input(type = "radio", name = ns("source_sel_r"), value = "elicit", style = "margin:0;"),
        "Compiled gene role"),
      tags$label(
        `data-tip` = "Consensus API classification — complete (100% of 21,568 pairs). Role: EXECUTOR/REGULATOR/MARKER/UNCERTAIN · Direction: PROMOTES/PROTECTS/UNCLEAR · Mechanistic: YES/NO.",
        style = "margin:0 0 0 14px; display:inline-flex; align-items:center; gap:5px; cursor:pointer; font-weight:400; font-size:14px;",
        tags$input(type = "radio", name = ns("source_sel_r"), value = "consensus", style = "margin:0;"),
        "Consensus"),
      tags$label(
        `data-tip` = "GPT-4o arbitration vote, mapped to the source it sided with (DEEPSEEK → DeepSeek value, CONSENSUS → Consensus value).",
        style = "margin:0 0 0 14px; display:inline-flex; align-items:center; gap:5px; cursor:pointer; font-weight:400; font-size:14px;",
        tags$input(type = "radio", name = ns("source_sel_r"), value = "gpt", style = "margin:0;"),
        "GPT"),
      tags$label(
        `data-tip` = "Curator 1 vote, mapped to the source it sided with (DEEPSEEK → DeepSeek value, CONSENSUS → Consensus value).",
        style = "margin:0 0 0 14px; display:inline-flex; align-items:center; gap:5px; cursor:pointer; font-weight:400; font-size:14px;",
        tags$input(type = "radio", name = ns("source_sel_r"), value = "curator_1", style = "margin:0;"),
        "Curator 1"),
      tags$label(
        `data-tip` = "Curator 2 vote, mapped to the source it sided with (DEEPSEEK → DeepSeek value, CONSENSUS → Consensus value).",
        style = "margin:0 0 0 14px; display:inline-flex; align-items:center; gap:5px; cursor:pointer; font-weight:400; font-size:14px;",
        tags$input(type = "radio", name = ns("source_sel_r"), value = "curator_2", style = "margin:0;"),
        "Curator 2"),
      actionButton(ns("death_core"), "Death core (executors)",
        `data-tip` = "One-click filter to the 225 EXECUTOR gene-RCD pairs (evidence-first) — the genes the verbatim grounds as directly executing cell death.",
        class = "search-evidence-btn", style = "margin-left:auto; height:32px; padding:0 14px; font-size:12.5px;"),
      downloadButton(ns("download_death_core"), "Download death core (CSV)",
        `data-tip` = "Download the 225 EXECUTOR gene-RCD pairs (evidence-first, pair-level) as a CSV file with all provenance columns.",
        class = "search-evidence-btn", style = "height:32px; padding:0 14px; font-size:12.5px;"),
      actionButton(ns("reset_filters"), "Reset filters",
        class = "search-evidence-btn",
        style = "margin-left:10px; height:32px; padding:0 16px; font-size:12.5px; font-weight:600; background:#FF9800 !important; color:#0b1020 !important; border:none; border-radius:8px; cursor:pointer; box-shadow:0 2px 8px rgba(255,152,0,0.35);")
      )
    ),
    tags$div(style = "display:flex; gap:10px; flex-wrap:wrap; align-items:flex-end; margin-bottom:12px;",
      selectizeInput(ns("f_gene"), "Gene", choices = NULL, multiple = TRUE, width = "200px", options = list(placeholder = "All genes", create = rcdome_create_js)),
      selectizeInput(ns("f_rcd"), "RCD entity", choices = NULL, multiple = TRUE, width = "200px", options = list(create = rcdome_create_js)),
      selectizeInput(ns("f_biotype"), "Biotype", choices = NULL, multiple = TRUE, width = "160px", options = list(create = rcdome_create_js)),
      selectizeInput(ns("f_cancer"), "Cancer Gene", choices = NULL, multiple = TRUE, width = "160px", options = list(create = rcdome_create_js)),
      selectizeInput(ns("f_db"), "Source DBs", choices = NULL, multiple = TRUE, width = "200px", options = list(create = rcdome_create_js))
    ),
    tags$div(style = "display:flex; gap:10px; flex-wrap:wrap; align-items:flex-end; margin-bottom:12px;",
      selectizeInput(ns("f_tier"), "Confidence Tier", choices = NULL, multiple = TRUE, width = "160px", options = list(create = rcdome_create_js)),
      selectizeInput(ns("f_mech"), "Mechanistic", choices = NULL, multiple = TRUE, width = "170px", options = list(create = rcdome_create_js)),
      selectizeInput(ns("f_role"), "Role", choices = NULL, multiple = TRUE, width = "150px", options = list(create = rcdome_create_js)),
      selectizeInput(ns("f_dir"), "Direction", choices = NULL, multiple = TRUE, width = "170px", options = list(create = rcdome_create_js)),
      selectizeInput(ns("f_status"), "Adjudication", choices = c("Disagreement" = "UNIFORM_PIPELINE", "Agreement" = "AGREED_LABEL_ABSTRACT", "Pending" = "PENDING_DELTA"), multiple = TRUE, width = "180px", options = list(placeholder = "All statuses"))
    ),
    tags$script(HTML(sprintf(
      "document.querySelectorAll('input[name=\"%s\"]').forEach(function(r){ r.addEventListener('change', function(){ Shiny.setInputValue('%s', r.value, {priority:'event'}); }); });",
      ns("source_sel_r"), ns("source_sel")
    ))),
    DTOutput(ns("table_genes")),
    div(style = "margin-top: 14px; display: flex; align-items: center; gap: 10px;",
      selectInput(ns("download_format"), tags$span("Format:", style = "color:#1c1917; font-weight:600;"),
                  choices = c("TSV" = "tsv", "XLSX" = "xlsx", "CSV" = "csv"),
                  selected = "tsv", width = "120px"),
      downloadButton(ns("download_btn"), "Download", class = "search-evidence-btn"),
      downloadButton(ns("download_full"), "Download RCDome matrix (CSV)",
        `data-tip` = "Export the complete truth matrix — all 22,473 rows x 100 columns (all analyses: Elicit, DeepSeek, and every provenance column).",
        class = "search-evidence-btn")
    ),
    tags$p("Total corpus: 22,473 rows = 21,568 unique gene-RCD pairs + 905 rows of multi-database corroboration (same gene+entity reported by 2+ databases). ",
           textOutput(ns("shown_count"), inline = TRUE),
           style = "color:#1c1917; font-size:13px; font-weight:700; margin-top:6px;"),
    tags$div(style = "margin-top: 28px; display:flex; align-items:center; gap:12px; flex-wrap:wrap;",
      tags$h4("RCD Entities — Compiled gene role vs DeepSeek (executors / regulators)", style = "margin:0; color:#1c1917;"),
      downloadButton(ns("download_entities"), "Download comparison table (CSV)",
        `data-tip` = "Download the 53-entity comparison (Compiled gene role vs DeepSeek executors and regulators) as a CSV file.",
        class = "search-evidence-btn")
    ),
    DTOutput(ns("table_entities")),
    tags$div(id = ns("omic_tip"), class = "omic-tip"),
    tags$style(HTML("
      .omic-tip {
        position: fixed; background:#1c1917; color:#e7e5e4;
        padding:8px 12px; border-radius:8px; font-size:12px;
        max-width:340px; pointer-events:none; opacity:0;
        transition:opacity .15s; z-index:9999;
        font-family:'Segoe UI', system-ui, sans-serif;
        box-shadow:0 4px 15px rgba(0,0,0,0.3);
      }
    ")),
    tags$script(HTML(sprintf(
      "(function(){
        var tip = document.getElementById('%s');
        if(!tip) return;
        document.addEventListener('mouseover', function(ev){
          var el = ev.target.closest('[data-tip]');
          if(!el) return;
          tip.textContent = el.getAttribute('data-tip');
          tip.style.opacity = 1;
          tip.style.left = (ev.clientX + 12) + 'px';
          tip.style.top = (ev.clientY - 10) + 'px';
        });
        document.addEventListener('mousemove', function(ev){
          var el = ev.target.closest('[data-tip]');
          if(!el) return;
          tip.style.left = (ev.clientX + 12) + 'px';
          tip.style.top = (ev.clientY - 10) + 'px';
        });
        document.addEventListener('mouseout', function(ev){
          var el = ev.target.closest('[data-tip]');
          if(el && !el.contains(ev.relatedTarget)) tip.style.opacity = 0;
        });
      })();", ns("omic_tip")
    )))
  )
}

mod_gene_catalog_server <- function(id, evidence_trail_rv, gene_catalog_entity_rv) {
  moduleServer(id, function(input, output, session) {


    # ── Lazy-loaded data (NULL = not loaded yet) ───────────────────────
    genes_rv    <- reactiveVal(NULL)
    get_genes <- function() {
      if (is.null(genes_rv())) {
        genes_rv(if (exists("genes_df", inherits = TRUE) && is.data.frame(genes_df) && nrow(genes_df) > 0) {
          genes_df
        } else {
          tryCatch(readRDS("data/unified_gene_rcd_matrix_V027.rds"),
                   error = function(e) { message("RCDome load error: unified_gene_rcd_matrix_V027.rds - ", conditionMessage(e)); data.frame(gene_symbol = character(0)) })
        })
      }
      genes_rv()
    }
    # ── Gene landing page navigation ──────────────────────────────────
    # Clicking a gene in the catalog opens the full gene landing page
    # (detail_page_wireframe.html?type=gene&name=GENE), which shows the gene
    # symbol, HGNC/Ensembl/NCBI Gene links, and the RCD distribution.
    navigate_to_gene_page <- function(gene_sym) {
      if (is.null(gene_sym) || !nzchar(gene_sym)) return()
      js_sym <- gsub("'", "\\'", gene_sym, fixed = TRUE)
      shinyjs::runjs(sprintf(
        "$('a[data-value=\"Home\"]').tab('show');
         var ov = document.getElementById('home_loading_overlay');
         if (ov) ov.style.display = 'flex';
         var f = document.getElementById('home_iframe');
         var callShow = function(){ try { f.contentWindow.showGene('%s'); } catch(e){} };
         var done = function(){ var o = document.getElementById('home_loading_overlay'); if(o){ o.style.display = 'none'; } };
         setTimeout(function(){
           f.onload = function(){ callShow(); done(); };
           f.src = 'detail_page_wireframe.html?v=5';
         }, 100);", js_sym)
      )
    }

    # ── Shared gene detail modal ───────────────────────────────────────
    show_gene_modal <- function(gene_sym) {
      g <- get_genes()
      g <- g[g$gene_symbol == gene_sym, , drop = FALSE]

      if (nrow(g) == 0) {
        showModal(modalDialog(
          title = gene_sym, size = "m", easyClose = TRUE,
          footer = modalButton("Close"),
          tags$p("No data found for this gene.")
        ))
        return()
      }

      row <- g[1, ]

      # Aggregate RCD forms across all rows for this gene
      rcd_all <- unique(g$rcd_form_canonical[!is.na(g$rcd_form_canonical) & g$rcd_form_canonical != ""])
      rcd_str <- if (length(rcd_all) > 0) paste(rcd_all, collapse = " · ") else "N/A"

      # Field helpers
      f <- function(col, default = "N/A") {
        val <- row[[col]]
        if (is.null(val) || is.na(val) || val == "") default else as.character(val)
      }
      collapse_field <- function(col) {
        val <- row[[col]]
        if (is.null(val) || is.na(val) || val == "") return("N/A")
        parts <- trimws(strsplit(as.character(val), ";")[[1]])
        parts <- parts[parts != ""]
        if (length(parts) == 0) "N/A" else paste(unique(parts), collapse = " · ")
      }

      showModal(modalDialog(
        title = tags$div(
          tags$strong(gene_sym),
          tags$span(paste0(" — ", f("gene_biotype")),
                    style = "font-size: 0.85em; color: #a8a29e; margin-left: 8px;")
        ),
        size = "l", easyClose = TRUE, footer = modalButton("Close"),

        # RCD entities (canonical, from V027)
        tags$h5(paste0("RCD entities (", length(rcd_all), ")")),
        tags$div(
          style = "display:flex; flex-wrap:wrap; gap:4px;",
          lapply(rcd_all, function(ent) {
            logo_file <- file.path("data/RCD modulo/logo RCDs", paste0(ent, ".png"))
            logo_url <- if (file.exists(logo_file)) paste0("rcd_logos/", URLencode(paste0(ent, ".png"), reserved = TRUE)) else ""
            if (nzchar(logo_url)) {
              tags$span(
                style = "display:inline-flex; align-items:center; gap:5px; margin-right:12px; margin-bottom:6px;",
                tags$img(src = logo_url, style = "width:22px; height:22px; object-fit:contain;"),
                tags$span(ent, style = "font-size:13px; color:#1c1917;")
              )
            } else tags$span(ent, style = "font-size:13px; color:#1c1917; margin-right:12px;")
          })
        ),

        # Cross-references
        tags$hr(),
        tags$h5("Cross-references"),
        tags$p(
          tags$strong("Ensembl: "),
          tags$span(style = "font-family: 'Segoe UI', system-ui, sans-serif; font-size: 13px; color: var(--ink);", f("ensembl_id")),
          tags$br(),
          tags$strong("UniProt: "),
          tags$span(style = "font-family: 'Segoe UI', system-ui, sans-serif; font-size: 13px; color: var(--ink);", f("uniprot_id"))
        ),

        # Evidence & Provenance (collapsible)
        tags$hr(),
        tags$a(
          onclick = "var d=document.getElementById('evid_detail');d.style.display=d.style.display==='none'?'block':'none';",
          style = "cursor: pointer; font-size: 13px; color: var(--navy);",
          "ⓘ Evidence & Provenance"
        ),
        tags$div(id = "evid_detail", style = "display: none; margin-top: 12px; word-wrap: break-word; overflow-wrap: break-word; max-width: 100%;",
          tags$p(tags$strong("Source Databases: "), f("source_databases")),
          tags$p(tags$strong("Source Channels: "), f("source_channels")),
          tags$p(tags$strong("Number of Sources: "), f("num_sources")),
          tags$p(tags$strong("Evidence Quality: "), f("evidence_quality")),
          tags$p(tags$strong("Evidence Types: "), f("evidence_types")),
          tags$p(tags$strong("Evidence Tier: "), f("evidence_tier")),
          tags$p(tags$strong("Evidence Basis: "), f("evidence_basis")),
          tags$p(tags$strong("Confidence Score: "), f("confidence_score")),
          tags$p(tags$strong("Confidence Tier: "), f("confidence_tier")),
          tags$p(tags$strong("Mechanistic Class: "), f("mechanistic_class")),
          tags$p(tags$strong("Phase 2C Mechanistic Class: "), f("phase2c_mechanistic_class")),
          tags$p(tags$strong("DeepSeek Mechanistic: "), f("cot_mechanistic")),
          tags$p(tags$strong("DeepSeek Role: "), f("cot_role")),
          tags$p(tags$strong("DeepSeek Direction: "), f("cot_direction")),
          tags$p(tags$strong("Consensus Role: "), f("consensus_role")),
          tags$p(tags$strong("Consensus Direction: "), f("consensus_direction")),
          tags$p(tags$strong("Consensus Mechanistic: "), f("consensus_mechanistic")),
          tags$p(tags$strong("Consensus Role Form: "), f("consensus_role_form")),
          tags$p(tags$strong("Consensus DOI: "), f("consensus_doi")),
          tags$p(tags$strong("Consensus Title: "), f("consensus_title")),
          tags$p(tags$strong("Consensus Takeaway: "), f("consensus_takeaway")),
          tags$p(tags$strong("Consensus Citation Count: "), f("consensus_citation_count")),
          tags$p(tags$strong("Consensus SJR: "), f("consensus_sjr")),
          tags$p(tags$strong("Consensus Year: "), f("consensus_year")),
          tags$p(tags$strong("Consensus Status: "), f("consensus_status")),
          tags$p(tags$strong("Evidence-first Mechanistic: "), f("final_mechanistic")),
          tags$p(tags$strong("Evidence-first Role: "), f("final_role")),
          tags$p(tags$strong("Evidence-first Direction: "), f("final_direction")),
          tags$p(tags$strong("Decision Status: "), f("decision_status")),
          tags$p(tags$strong("Abstract Check: "), f("abstract_check")),
          tags$p(tags$strong("Evidence Source: "), f("evidence_source")),
          tags$p(tags$strong("Required for Death: "), f("required_for_death")),
          tags$p(tags$strong("Evidence Type: "), f("evidence_type")),
          tags$p(tags$strong("PMIDs: "), collapse_field("pmid_list")),
          tags$p(tags$strong("LLM Status: "), f("llm_status")),
          tags$p(tags$strong("LLM PMIDs: "), f("llm_pmids")),
          tags$p(tags$strong("LLM Evidence Force: "), f("llm_evidence_force")),
          tags$p(tags$strong("Europe PMC Hits: "), f("epmc_hits")),
          tags$p(tags$strong("Europe PMC Status: "), f("epmc_status")),
          tags$p(tags$strong("Europe PMC PMIDs: "), f("epmc_pmids")),
          tags$p(tags$strong("Elicit PMIDs: "), f("elicit_pmids"))
        )
      ))
    }

    # ── RCDome-style pill helpers ──────────────────────────────────────
    rc_pill <- function(text, cls) {
      ifelse(is.na(text) | text == "", "—",
             sprintf('<span class="rc-pill %s">%s</span>', cls, text))
    }
    biotype_class <- function(x) {
      cls <- rep("pill-gray", length(x))
      cls[x == "protein_coding"] <- "pill-green"
      cls[x == "miRNA"] <- "pill-blue"
      cls[x == "lncRNA"] <- "pill-purple"
      cls[x == "other_RNA"] <- "pill-teal"
      cls
    }
    level_class <- function(x) {
      cls <- rep("pill-gray", length(x))
      cls[grepl("L1", x)] <- "pill-gold"
      cls[grepl("L2", x)] <- "pill-blue"
      cls[grepl("L3", x)] <- "pill-green"
      cls[grepl("L4", x)] <- "pill-purple"
      cls[grepl("L5", x)] <- "pill-orange"
      cls
    }
    cancer_class <- function(x) {
      cls <- rep("pill-gray", length(x))
      cls[x == "suppressor"] <- "pill-green"
      cls[x == "driver"] <- "pill-red"
      cls[x == "mixed"] <- "pill-amber"
      cls
    }
    tier_class <- function(x) {
      cls <- rep("pill-gray", length(x))
      cls[x == "CT1"] <- "pill-gold"
      cls[x == "CT2"] <- "pill-green"
      cls[x == "CT3"] <- "pill-blue"
      cls
    }
    mech_class <- function(x) {
      cls <- rep("pill-gray", length(x))
      cls[x == "YES"] <- "pill-green"
      cls
    }
    role_class <- function(x) {
      cls <- rep("pill-gray", length(x))
      cls[x == "EXECUTOR"] <- "pill-red"
      cls[x == "REGULATOR"] <- "pill-blue"
      cls[x == "MARKER"] <- "pill-amber"
      cls
    }
    direction_class <- function(x) {
      cls <- rep("pill-gray", length(x))
      cls[x == "PROMOTES"] <- "pill-orange"
      cls[x == "PROTECTS"] <- "pill-teal"
      cls[x == "BIDIRECTIONAL"] <- "pill-purple"
      cls
    }

    # Direction/Role source selector → which analysis's columns to show
    src_cols <- reactive({
      src <- if (is.null(input$source_sel) || length(input$source_sel) == 0) "evidence" else input$source_sel[1]
      switch(src,
        evidence = list(role = "final_role", dir = "final_direction", mech = "final_mechanistic", label = "Evidence-first"),
        deepseek = list(role = "cot_role", dir = "cot_direction", mech = "cot_mechanistic", label = "DeepSeek"),
        consensus = list(role = "consensus_role", dir = "consensus_direction", mech = "consensus_mechanistic", label = "Consensus"),
        elicit = list(role = "rcd_gene_type", dir = "role_direction", mech = "cot_mechanistic", label = "Compiled gene role"),
        gpt = list(role = "gpt_mapped_role", dir = "gpt_mapped_dir", mech = "cot_mechanistic", label = "GPT"),
        curator_1 = list(role = "curator_1_mapped_role", dir = "curator_1_mapped_dir", mech = "cot_mechanistic", label = "Curator 1"),
        curator_2 = list(role = "curator_2_mapped_role", dir = "curator_2_mapped_dir", mech = "cot_mechanistic", label = "Curator 2"),
        list(role = "final_role", dir = "final_direction", mech = "final_mechanistic", label = "Evidence-first")
      )
    })

    # Death core preset: switch to DeepSeek + filter to EXECUTOR pairs (unique gene-entity pairs)
    dedup_flag <- reactiveVal(FALSE)
    suppress_reset <- reactiveVal(FALSE)
    observeEvent(input$death_core, {
      shinyjs::runjs(sprintf(
        "var r = document.querySelector('input[name=\"%s\"][value=\"evidence\"]'); if(r && !r.checked){ r.checked = true; Shiny.setInputValue('%s', 'evidence', {priority:'event'}); }",
        session$ns("source_sel_r"), session$ns("source_sel")))
      dedup_flag(TRUE)
      suppress_reset(TRUE)
      df <- get_genes()
      updateSelectizeInput(session, "f_role",
        choices = sort(unique(df$final_role[df$final_role != ""])),
        selected = "EXECUTOR")
    })

    # Reset filters → restore Evidence-first as the default source + clear all filters.
    observeEvent(input$reset_filters, {
      shinyjs::runjs(sprintf(
        "var r = document.querySelector('input[name=\"%s\"][value=\"evidence\"]'); if(r && !r.checked){ r.checked = true; Shiny.setInputValue('%s', 'evidence', {priority:'event'}); }",
        session$ns("source_sel_r"), session$ns("source_sel")))
      dedup_flag(FALSE)
      for (id in c("f_gene", "f_biotype", "f_rcd", "f_cancer", "f_tier", "f_mech", "f_role", "f_dir", "f_status", "f_db")) {
        updateSelectizeInput(session, id, selected = character(0))
      }
      shinyjs::runjs(sprintf("$('#%s input[type=\"search\"]').val('').trigger('input');", session$ns("table_genes")))
    })

    # Auto-reset the dedup preset when the user manually changes the Role filter.
    observeEvent(input$f_role, {
      if (suppress_reset()) {
        suppress_reset(FALSE)
      } else {
        dedup_flag(FALSE)
      }
    }, ignoreInit = TRUE, ignoreNULL = TRUE)

    # Download the death core (pair-level EXECUTOR rows, all columns)
    output$download_death_core <- downloadHandler(
      filename = function() { "RCDome_death_core_executors.csv" },
      content = function(file) {
        df <- get_genes()
        pairs <- df[!duplicated(paste(df$gene_symbol, df$rcd_form_canonical)), , drop = FALSE]
        ex <- pairs[pairs$final_role == "EXECUTOR", , drop = FALSE]
        write.csv(ex, file, row.names = FALSE)
      }
    )

    # ── Column filters (per variable, per value) ───────────────────────
    observe({
      df <- get_genes()
      if (nrow(df) == 0) return()
      updateSelectizeInput(session, "f_gene", choices = sort(unique(df$gene_symbol)))
      updateSelectizeInput(session, "f_biotype", choices = sort(unique(df$gene_biotype)))
      updateSelectizeInput(session, "f_rcd", choices = sort(unique(df$rcd_form_canonical)))
      updateSelectizeInput(session, "f_cancer", choices = sort(unique(df$cancer_gene_type[df$cancer_gene_type != ""])))
      updateSelectizeInput(session, "f_tier", choices = sort(unique(df$confidence_tier[df$confidence_tier != ""])))
      db_choices <- sort(unique(unlist(strsplit(df$source_databases, ";"))))
      db_choices <- db_choices[db_choices != "" & !is.na(db_choices)]
      updateSelectizeInput(session, "f_db", choices = db_choices)
      sc <- src_cols()
      updateSelectizeInput(session, "f_mech", choices = sort(unique(df[[sc$mech]][df[[sc$mech]] != ""])))
      updateSelectizeInput(session, "f_role", choices = sort(unique(df[[sc$role]][df[[sc$role]] != ""])))
      updateSelectizeInput(session, "f_dir", choices = sort(unique(df[[sc$dir]][df[[sc$dir]] != ""])))
    })

    # ── Not-found guard: a typed value absent from the options triggers a pop-up.
    #    The selectize create callback returns false, so the value is NEVER added
    #    to the dropdown list (no contamination). ──

    filtered_genes <- reactive({
      df <- get_genes()
      if (dedup_flag()) df <- df[!duplicated(paste(df$gene_symbol, df$rcd_form_canonical)), , drop = FALSE]
      if (!is.null(input$f_gene) && length(input$f_gene) > 0) df <- df[df$gene_symbol %in% input$f_gene, , drop = FALSE]
      if (!is.null(input$f_biotype) && length(input$f_biotype) > 0) df <- df[df$gene_biotype %in% input$f_biotype, , drop = FALSE]
      if (!is.null(input$f_rcd) && length(input$f_rcd) > 0) df <- df[df$rcd_form_canonical %in% input$f_rcd, , drop = FALSE]
      if (!is.null(input$f_cancer) && length(input$f_cancer) > 0) df <- df[df$cancer_gene_type %in% input$f_cancer, , drop = FALSE]
      if (!is.null(input$f_tier) && length(input$f_tier) > 0) df <- df[df$confidence_tier %in% input$f_tier, , drop = FALSE]
      if (!is.null(input$f_status) && length(input$f_status) > 0) df <- df[df$decision_status %in% input$f_status, , drop = FALSE]
      if (!is.null(input$f_db) && length(input$f_db) > 0) {
        keep <- sapply(df$source_databases, function(s) any(vapply(input$f_db, function(d) grepl(d, s, fixed = TRUE), logical(1))))
        df <- df[keep, , drop = FALSE]
      }
      sc <- src_cols()
      if (!is.null(input$f_mech) && length(input$f_mech) > 0) df <- df[df[[sc$mech]] %in% input$f_mech, , drop = FALSE]
      if (!is.null(input$f_role) && length(input$f_role) > 0) df <- df[df[[sc$role]] %in% input$f_role, , drop = FALSE]
      if (!is.null(input$f_dir) && length(input$f_dir) > 0) df <- df[df[[sc$dir]] %in% input$f_dir, , drop = FALSE]
      df
    })

    # ── Per-entity comparison (Compiled gene role vs DeepSeek, pair-level) ─────
    entity_compare <- reactive({
      df <- get_genes()
      if (nrow(df) == 0) return(data.frame())
      pairs <- df[!duplicated(paste(df$gene_symbol, df$rcd_form_canonical)), , drop = FALSE]
      ents <- sort(unique(pairs$rcd_form_canonical))
      do.call(rbind, lapply(ents, function(e) {
        g <- pairs[pairs$rcd_form_canonical == e, , drop = FALSE]
        data.frame(
          Entity = e,
          Level = g$rcdome_level_name[1],
          `Compiled executors` = sum(g$rcd_gene_type == "EXECUTOR"),
          `DeepSeek executors` = sum(g$cot_role == "EXECUTOR"),
          `Compiled regulators` = sum(g$rcd_gene_type == "REGULATOR"),
          `DeepSeek regulators` = sum(g$cot_role == "REGULATOR"),
          check.names = FALSE
        )
      }))
    })

    output$table_entities <- renderDT({
      ec <- entity_compare()
      if (nrow(ec) == 0) return(datatable(data.frame(Message = "No data")))
      ec$Level <- rc_pill(ec$Level, level_class(ec$Level))
      datatable(ec, rownames = FALSE, escape = FALSE,
        options = list(
          pageLength = 53, dom = "t", autoWidth = TRUE,
          headerCallback = JS(
            "function(thead, data, start, end, display){",
            "  var tips = [",
            "    'RCD-related entity (one of 53).',",
            "    'RCDome ontological level (L1 Modalities, L2 Subtypes, L3 Triggers, L4 Functional/contextual, L5 Generic/umbrella/taxon).',",
            "    'Number of EXECUTOR pairs from the Elicit Phase 2/3 extraction (~20% annotated).',",
            "    'Number of EXECUTOR pairs from DeepSeek (complete, 100% classified).',",
            "    'Number of REGULATOR pairs from Compiled gene role.',",
            "    'Number of REGULATOR pairs from DeepSeek.'",
            "  ];",
            "  $('th', thead).each(function(i){ if(tips[i]) $(this).attr('data-tip', tips[i]); });",
            "}"
          )
        ),
        class = "compact hover row-border")
    })

    output$download_entities <- downloadHandler(
      filename = function() { "RCDome_entities_elicit_vs_deepseek.csv" },
      content = function(file) {
        write.csv(entity_compare(), file, row.names = FALSE)
      }
    )

    # ── Genes table ────────────────────────────────────────────────────
    output$shown_count <- renderText({
      n <- nrow(filtered_genes())
      idx <- input$table_genes_rows_all
      if (!is.null(idx) && length(idx) > 0) n <- length(idx)
      paste0("Showing ", n, " rows after filters.")
    })

    output$table_genes <- renderDT({
      df <- filtered_genes()
      if (nrow(df) == 0) return(datatable(data.frame(Message = "No data")))
      sc <- src_cols()
      cols <- c("gene_symbol", "gene_biotype", "rcd_form_canonical", "rcdome_level_name", "cancer_gene_type", "confidence_tier", "cot_mechanistic", sc$role, sc$dir, "source_databases")
      cols <- intersect(cols, names(df))
      show <- df[, cols, drop = FALSE]
      raw_gene <- df$gene_symbol
      raw_entity <- df$rcd_form_canonical
      show$gene_symbol <- sprintf("<a href='#' onclick=\"Shiny.setInputValue('%s', '%s|%s', {priority:'event'}); return false;\" style='color:#1d4ed8;font-weight:700;font-style:italic;'>%s</a>", session$ns("gene_click"), raw_gene, raw_entity, raw_gene)
      show$gene_biotype <- rc_pill(show$gene_biotype, biotype_class(show$gene_biotype))
      show$rcd_form_canonical <- rc_pill(show$rcd_form_canonical, level_class(show$rcdome_level_name))
      show$cancer_gene_type <- rc_pill(show$cancer_gene_type, cancer_class(show$cancer_gene_type))
      show$confidence_tier <- rc_pill(show$confidence_tier, tier_class(show$confidence_tier))
      show$cot_mechanistic <- rc_pill(show$cot_mechanistic, mech_class(show$cot_mechanistic))
      show[[sc$role]] <- rc_pill(show[[sc$role]], role_class(show[[sc$role]]))
      show[[sc$dir]] <- rc_pill(show[[sc$dir]], direction_class(show[[sc$dir]]))
      show$rcdome_level_name <- NULL
      ef_badge <- function(v, col) sprintf("<span style='display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:600;color:#fff;background:%s;margin-right:3px;'>%s</span>", col, v)
      m  <- trimws(as.character(df$final_mechanistic)); ro <- trimws(as.character(df$final_role)); di <- trimws(as.character(df$final_direction))
      m[is.na(m) | !nzchar(m)] <- "—"; ro[is.na(ro) | !nzchar(ro)] <- "—"; di[is.na(di) | !nzchar(di)] <- "—"
      mc <- ifelse(m == "YES", "#2E7D32", ifelse(m == "OUT_OF_CONTEXT", "#F59E0B", "#9E9E9E"))
      rc <- c(EXECUTOR = "#E53935", REGULATOR = "#3949AB", MARKER = "#00897B", UNCERTAIN = "#9E9E9E")
      dc <- c(PROMOTES = "#2E7D32", PROTECTS = "#1565C0", UNCLEAR = "#757575")
      rcc <- unname(rc[ro]); rcc[is.na(rcc)] <- "#9E9E9E"
      dcc <- unname(dc[di]); dcc[is.na(dcc)] <- "#757575"
      show$evidence_first <- paste0(ef_badge(m, mc), ef_badge(ro, rcc), ef_badge(di, dcc))
      show$evidence <- sprintf(
        "<button type=\"button\" onmousedown=\"event.stopPropagation();\" onclick=\"event.stopPropagation(); Shiny.setInputValue('%s', '%s|%s', {priority:'event'})\" style=\"border:none;background:#1d4ed8;color:#fff;cursor:pointer;font-size:12px;font-weight:600;padding:3px 10px;border-radius:999px;\" title=\"Open the Evidence Trail\">⧈ Trail</button>",
        session$ns("evidence_click"), raw_gene, raw_entity
      )
      show <- show[, c("gene_symbol","gene_biotype","rcd_form_canonical","cancer_gene_type","confidence_tier","cot_mechanistic", sc$role, sc$dir, "evidence_first","source_databases","evidence")]
      colnames(show) <- c("Gene", "Biotype", "RCD entity", "Cancer Gene", "Confidence Tier", "Mechanistic (DeepSeek)", paste0("Role (", sc$label, ")"), paste0("Direction (", sc$label, ")"), "Evidence-first", "Source DBs", "Evidence Trail")
      datatable(show, rownames = FALSE, selection = "none", escape = FALSE,
        options = list(
          pageLength = 15, search = list(regex = TRUE, smart = TRUE),
          language = list(search = "Filter:", zeroRecords = "No genes found."),
          headerCallback = JS(
            "function(thead, data, start, end, display){",
            "  var tips = [",
            "    'Official HGNC-approved gene symbol (italicized per HGNC convention).',",
            "    'Gene biotype from HGNC (protein_coding, lncRNA, miRNA, pseudogene, etc.).',",
            "    'The RCD-related entity (one of 53) that this gene is associated with.',",
            "    'Cancer gene classification (oncogene / tumor suppressor) if annotated in the source databases.',",
            "    'Confidence tier derived from the weighted sum of source channels (CT1 strongest, CT4 weakest).',",
            "    'Mechanistic verdict of the selected source: YES = gene mechanistically participates in this RCD form; NO = association without mechanistic evidence.',",
            "    'Role of the selected source: EXECUTOR = directly executes death; REGULATOR = controls (promotes/inhibits); MARKER = associated but not causal; UNCERTAIN = unresolved.',",
            "    'Direction of the selected source: PROMOTES = favors death; PROTECTS = inhibits death; UNCLEAR = unresolved.',",
            "    'Final evidence-first resolution (final_mechanistic · final_role · final_direction), read from the verbatim.',",
            "    'Semicolon-separated source databases that reported this gene-RCD association (joined provenance).',",
            "    'Opens the global Evidence Trail drawer: classifiers, curator votes, and the evidence-first adjudication for this gene-RCD pair.'",
            "  ];",
            "  $('th', thead).each(function(i){ if(tips[i]) $(this).attr('data-tip', tips[i]); });",
            "}"
          )
        ),
        class = "compact hover row-border")
    }, server = TRUE)

    observeEvent(input$gene_click, {
      req(input$gene_click)
      parts <- strsplit(input$gene_click, "|", fixed = TRUE)[[1]]
      gene <- parts[1]
      entity <- if (length(parts) > 1) parts[2] else ""
      show_gene_modal(gene)
      evidence_trail_rv(list(gene = gene, entity = entity))
      shinyjs::runjs("document.getElementById('evidence_drawer').style.display='block';")
    })

    # ── Download da aba ativa (TSV / XLSX / CSV) ────────────────────
    output$download_btn <- downloadHandler(
      filename = function() {
        paste0("gene_catalog", ".", input$download_format)
      },
      content = function(file) {
        fmt <- input$download_format
        df <- filtered_genes()
        idx <- input$table_genes_rows_all
        if (!is.null(idx) && length(idx) > 0) df <- df[idx, , drop = FALSE]
        if (fmt == "tsv") {
          write.table(df, file, sep = "\t", row.names = FALSE, quote = FALSE, na = "")
        } else if (fmt == "csv") {
          write.csv(df, file, row.names = FALSE)
        } else {
          # Excel cells are capped at 32,767 characters; truncate any longer string.
          df[] <- lapply(df, function(x) {
            if (!is.character(x)) return(x)
            too_long <- nchar(x) > 32767
            too_long[is.na(too_long)] <- FALSE
            x[too_long] <- paste0(substr(x[too_long], 1, 32700), "...[truncated]")
            x
          })
          writexl::write_xlsx(df, file)
        }
      }
    )

    # ── Cross-link from RCD Entity Deep Dive -> filter this entity ─────
    observeEvent(gene_catalog_entity_rv(), {
      req(gene_catalog_entity_rv())
      updateSelectizeInput(session, "f_rcd", selected = gene_catalog_entity_rv())
    })

    # ── Evidence Trail: the per-row ⧈ button opens the global drawer ──
    observeEvent(input$evidence_click, {
      req(input$evidence_click)
      parts <- strsplit(input$evidence_click, "|", fixed = TRUE)[[1]]
      if (length(parts) != 2) return()
      evidence_trail_rv(list(gene = parts[1], entity = parts[2]))
      shinyjs::runjs("document.getElementById('evidence_drawer').style.display='block';")
    })

    # ── Download the FULL V027 matrix (all rows, all 100 columns) ───────
    output$download_full <- downloadHandler(
      filename = function() { "RCDome_full_matrix.csv" },
      content = function(file) {
        df <- get_genes()
        write.csv(df, file, row.names = FALSE)
      }
    )

  })
}
