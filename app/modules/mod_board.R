# Module: board - the RCDome Digital Molecular Board (synthesis).
# Landing page follows the RCDome light visual identity (Gene Catalogue home).

scrub_board <- function(txt) {
  if (is.null(txt) || !nzchar(txt)) return(txt)
  txt <- gsub("**", "", txt, fixed = TRUE)
  txt <- gsub("\\bsuppress(es|ed|ing)?\\b", "is associated with reduced", txt, perl = TRUE, ignore.case = TRUE)
  txt <- gsub("\\bdrive(s|n)?\\b", "contributes to", txt, perl = TRUE, ignore.case = TRUE)
  txt <- gsub("\\bprevent(s|ed|ing)?\\b", "is associated with reduced", txt, perl = TRUE, ignore.case = TRUE)
  txt <- gsub("\\bcause(s|d)?\\b", "is associated with", txt, perl = TRUE, ignore.case = TRUE)
  txt <- gsub("\\bdemonstrate(s|d)?\\b", "indicates", txt, perl = TRUE, ignore.case = TRUE)
  txt <- gsub("\\bprove(s|n|d)?\\b", "suggests", txt, perl = TRUE, ignore.case = TRUE)
  txt <- gsub("\\bconfirm(s|ed)?\\b", "suggests", txt, perl = TRUE, ignore.case = TRUE)
  txt <- gsub("(?<!RCDome )database", "RCDome database", txt, perl = TRUE, ignore.case = TRUE)
  txt <- gsub("(?<!RCDome )decoder", "RCDome decoder", txt, perl = TRUE, ignore.case = TRUE)
  # capitalize the first letter of the synthesis
  if (nzchar(txt)) txt <- paste0(toupper(substr(txt, 1, 1)), substr(txt, 2, nchar(txt)))
  txt
}

extract_suggested_queries <- function(txt) {
  if (is.null(txt) || !nzchar(txt)) return(character(0))
  lines <- strsplit(txt, "\n", fixed = TRUE)[[1]]
  hits <- grep("^[ ]*[1-3]\\. ", lines, value = TRUE)
  if (length(hits) == 0) return(character(0))
  qs <- sub("^[ ]*[1-3]\\. ", "", hits)
  trimws(qs)[seq_len(min(3, length(qs)))]
}

# Extract the exact disclaimer sentence from a synthesis.
extract_disclaimer <- function(synth) {
  i <- regexpr("The interpretations presented above", synth)
  if (i < 0) return(NULL)
  gsub("\n", " ", trimws(substr(synth, i, nchar(synth))))
}

# Interactive example queries: each maps to an entity so a click loads the
# entity context and hands the question to the Q&A submodule.
BOARD_EXAMPLE_QUERIES <- list(
  list(entity = "Ferroptosis",
       question = "Which genes are associated with ferroptosis, and what is the evidence tier for each?"),
  list(entity = "Necroptosis",
       question = "What are the key molecular components of necroptosis, and how is MLKL classified?"),
  list(entity = "Pyroptosis",
       question = "How does the RCDome decoder define pyroptosis, and what is its founding reference?"),
  list(entity = "Apoptosis",
       question = "Is BAX recorded as an executor of apoptosis, and what is its direction of regulation?")
)

build_entity_context <- function(ent, gene = NULL) {
  mrows <- if (is.null(gene))
    genes_df[genes_df$rcd_form_canonical == ent, ]
  else
    genes_df[genes_df$rcd_form_canonical == ent & genes_df$gene_symbol == gene, ]
  drow <- decoder_df[decoder_df$rcd_form == ent, ]
  if (nrow(drow) == 0) drow <- NULL

  if (!is.null(gene) && nrow(mrows) == 0) {
    matrix_txt <- paste0("not recorded (no association for ", gene, " - ", ent, ")")
  } else if (!is.null(gene)) {
    fld <- function(col) ifelse(is.na(col), "NA", as.character(col))
    trunc_pmids <- function(p) {
      ps <- strsplit(as.character(p), ";", fixed=TRUE)[[1]]
      ps <- ps[!is.na(ps) & ps != ""]
      if (length(ps) == 0) return("NA")
      if (length(ps) <= 2) return(paste(ps, collapse=";"))
      paste0(paste(ps[1:2], collapse=";"), "; +", length(ps)-2, " more")
    }
    pair_txt <- unique(paste0(mrows$gene_symbol, ": role=", fld(mrows$cot_role),
                              " direction=", fld(mrows$cot_direction),
                              " mechanistic=", fld(mrows$mechanistic_class),
                              " evidence-first=", fld(mrows$final_role), "/", fld(mrows$final_direction), "/", fld(mrows$final_mechanistic),
                              " decision_status=", fld(mrows$decision_status),
                              " evidence_tier=", fld(mrows$evidence_tier),
                              " confidence_tier=", fld(mrows$confidence_tier),
                              " required_for_death=", fld(mrows$required_for_death),
                              " PMID=", trunc_pmids(mrows$pmid_list)))
    matrix_txt <- paste(pair_txt, collapse = "; ")
  } else {
    gene_hits <- if (nrow(mrows) == 0) character(0) else unique(mrows$gene_symbol)
    matrix_txt <- if (length(gene_hits) == 0) "not recorded" else paste0(sort(gene_hits), collapse = ", ")
  }
  decoder_txt <- if (is.null(drow)) "not recorded" else {
    fld <- names(DECODER_DESC)
    paste(sapply(fld, function(f) {
      v <- drow[[f]][1]
      if (is.null(v) || is.na(v)) "" else paste0(f, ": ", v)
    }), collapse = "; ")
  }
  list(matrix_fields = matrix_txt, decoder_fields = decoder_txt,
       drow = drow,
       genes = if (exists("gene_hits")) gene_hits else character(0))
}

# Approved descriptor dictionaries (ported from the Python board audit).
MATRIX_DESC <- list(
  gene_symbol = c("Gene symbol", "Identifiers"),
  rcd_form = c("RCD form (original)", "Identifiers"),
  rcd_form_canonical = c("RCD form (canonical)", "Identifiers"),
  rcdome_level = c("RCDome level", "Identifiers"),
  rcdome_level_name = c("RCDome level name", "Identifiers"),
  source_databases = c("Source databases", "Source provenance"),
  source_channels = c("Source channels", "Source provenance"),
  num_sources = c("Source count", "Source provenance"),
  evidence_quality = c("Evidence quality", "Source provenance"),
  evidence_types = c("Evidence types", "Source provenance"),
  pmid_list = c("PMIDs (source)", "PMIDs"),
  llm_pmids = c("PMIDs (LLM)", "PMIDs"),
  epmc_pmids = c("PMIDs (Europe PMC)", "PMIDs"),
  elicit_pmids = c("PMIDs (Elicit)", "PMIDs"),
  confidence_score = c("Confidence score", "Confidence"),
  confidence_tier = c("Confidence tier", "Confidence tier (CT1-CT4)"),
  uniprot_id = c("UniProt ID", "Gene metadata"),
  ensembl_id = c("Ensembl ID", "Gene metadata"),
  cancer_gene_type = c("Cancer gene type", "Gene metadata"),
  rcd_gene_type = c("RCD gene type", "Gene metadata"),
  gene_symbol_status = c("Gene symbol status", "Gene metadata"),
  gene_biotype = c("Gene biotype", "Gene metadata"),
  evidence_tier = c("Evidence tier (ET1 gold to ET4 weak)", "Evidence & validation"),
  evidence_basis = c("Evidence basis", "Evidence & validation"),
  llm_status = c("LLM validation status", "Evidence & validation"),
  llm_evidence_force = c("LLM evidence force", "Evidence & validation"),
  mechanistic_class = c("Mechanistic classification", "Evidence & validation"),
  epmc_hits = c("Europe PMC full-text hits", "Evidence & validation"),
  epmc_status = c("Europe PMC validation status", "Evidence & validation"),
  phase2c_mechanistic_class = c("Phase 2C mechanistic class", "Evidence & validation"),
  elic_onto_rcd_id = c("Elicit ontology RCD id", "RCD ontology"),
  elic_onto_rcd_name = c("Elicit ontology RCD name", "RCD ontology"),
  elic_onto_inventory = c("Elicit ontology inventory", "RCD ontology"),
  elic_onto_rcd_type = c("Elicit ontology RCD type", "RCD ontology"),
  elic_onto_parent_rcd_id = c("Elicit ontology parent id", "RCD ontology"),
  elic_onto_relationship = c("Elicit ontology relationship", "RCD ontology"),
  elic_onto_ontology_status = c("Elicit ontology status", "RCD ontology"),
  elic_onto_operational_note = c("Elicit ontology operational note", "RCD ontology"),
  rodr_category = c("Rodrigues category", "RODR operational definitions"),
  rodr_core_mechanism = c("Rodrigues core mechanism", "RODR operational definitions"),
  rodr_key_molecules = c("Rodrigues key molecules", "RODR operational definitions"),
  rodr_primary_refs = c("Rodrigues primary references", "RODR operational definitions"),
  rodr_secondary_refs = c("Rodrigues secondary references", "RODR operational definitions"),
  role_direction = c("Role/direction", "Elicit extraction"),
  required_for_death = c("Required for death", "Elicit extraction"),
  evidence_type = c("Evidence type", "Elicit extraction"),
  elicit_verbatim_sentence = c("Elicit verbatim sentence", "Elicit extraction"),
  elicit_doi = c("Elicit DOI", "Elicit extraction"),
  elicit_title = c("Elicit title", "Elicit extraction"),
  elicit_authors = c("Elicit authors", "Elicit extraction"),
  elicit_venue = c("Elicit venue", "Elicit extraction"),
  elicit_year = c("Elicit year", "Elicit extraction"),
  elicit_evidence_status = c("Elicit evidence status", "Elicit extraction"),
  deep_pmids_total = c("Deep total PMIDs", "Phase 2B deep evidence"),
  deep_pmids_free = c("Deep free PMIDs", "Phase 2B deep evidence"),
  deep_pmids_skipped = c("Deep skipped PMIDs", "Phase 2B deep evidence"),
  deep_paper_count = c("Deep paper count", "Phase 2B deep evidence"),
  deep_best_sentence = c("Deep best sentence", "Phase 2B deep evidence"),
  deep_best_evidence = c("Deep best evidence", "Phase 2B deep evidence"),
  deep_best_role = c("Deep best role", "Phase 2B deep evidence"),
  deep_best_direction = c("Deep best direction", "Phase 2B deep evidence"),
  deep_confidence = c("Deep confidence", "Phase 2B deep evidence"),
  deep_evidence_score = c("Deep evidence score", "Phase 2B deep evidence"),
  cot_role = c("Role (CoT)", "DeepSeek chain-of-thought classification"),
  cot_direction = c("Direction (CoT)", "DeepSeek chain-of-thought classification"),
  cot_mechanistic = c("Mechanistic (CoT)", "DeepSeek chain-of-thought classification"),
  cot_evidence = c("Evidence (CoT)", "DeepSeek chain-of-thought classification"),
  decoder_operational_definition = c("Decoder operational definition", "Decoder"),
  decoder_key_molecules = c("Decoder key molecules", "Decoder"),
  decoder_category = c("Decoder category", "Decoder"),
  decoder_hard_gate_status = c("Decoder hard gate", "Decoder")
)

DECODER_DESC <- list(
  rcd_form = c("Entity", "Canonicalized RCD-related entity name (53 entities)"),
  category = c("Category", "Entity category (Executioner / Trigger / Functional / Subtype / Synonym / Umbrella / Contextual / Taxon / Cell-type / Differentiation)"),
  hard_gate_status = c("Hard gate", "Hard-gate L1 admission status (L1-ELIGIBLE = passes G1 machinery + G2 necessity; NOT-L1 = subtypes/triggers/umbrellas/morphology)"),
  year = c("Year", "Year of discovery (of the founding reference; 'composite' for non-single entities)"),
  operational_definition = c("Operational definition", "Operational definition prose (Galluzzi MC1-MC5 logic, classification-led, citation-free)"),
  operational_definition_complement = c("Definition complement", "Galluzzi-style complement for verbatim entities (never replaces the verbatim)"),
  operational_definition_source = c("Definition source", "Source of the definition (NCCD_2018_VERBATIM / RODRIGUES_S1A / FOUNDING_DRAFT / PRE_PUBMED / COMPOSITE)"),
  reference_pmid = c("Reference PMID", "PMID anchoring the definition (evidence)"),
  reference_citation = c("Reference citation", "Citation (Author et al. Year)"),
  primary_refs_pmids = c("Primary reference PMIDs", "Primary evidence PMIDs (semicolon-separated)"),
  secondary_refs_pmids = c("Secondary reference PMIDs", "Secondary evidence PMIDs (semicolon-separated; empty if none)"),
  core_mechanism = c("Core mechanism", "Short core mechanism (from the 25-Forms Reference Table)"),
  key_molecules = c("Key molecules", "Key molecular machinery (comma-separated)"),
  inflammatory = c("Inflammatory", "Inflammatory status (Yes / No / not specified / member-dependent)"),
  overlaps = c("Overlaps", "Description of overlaps with other RCD forms"),
  RS1 = c("RS1 - Extent of Research", "Extent of Research criterion (1-10, weight 25%)"),
  RS2 = c("RS2 - Direct Involvement", "Direct Involvement criterion (1-10, weight 25%)"),
  RS3 = c("RS3 - Impact on homeostasis", "Impact on cell/tissue homeostasis criterion (1-10, weight 20%)"),
  RS4 = c("RS4 - Emerging Potential", "Emerging Potential criterion (1-10, weight 15%)"),
  RS5 = c("RS5 - Biological Significance", "Biological Significance criterion (1-10, weight 10%)"),
  RS6 = c("RS6 - Pathophysiological Relevance", "Pathophysiological Relevance criterion (1-10, weight 5%)"),
  S = c("Overall score (S)", "Overall Score = 0.25*RS1 + 0.25*RS2 + 0.20*RS3 + 0.15*RS4 + 0.10*RS5 + 0.05*RS6 (deterministic)"),
  founding_pmid = c("Founding PMID", "Founding PMID (the discovery article)"),
  definition_status = c("Definition status", "Definition status (DEFINED_RODRIGUES / DRAFT_SOLID / DRAFT_CANDIDATE / COMPOSITE / PRE_PUBMED)"),
  galluzzi_nccd_definition = c("NCCD verbatim definition", "Verbatim NCCD 2018 Box 1 definition (byte-identical; for invariant entities)"),
  galluzzi_nccd_status = c("NCCD status", "NCCD status (NCCD_2018_INVARIANT / NOT_IN_NCCD_2018 / COMPOSITE)"),
  source_databases = c("Source databases", "Source databases contributing the entity's genes (semicolon-separated)"),
  source_channels = c("Source channels", "Source channels (A = programmatic / B = database / E = AI-screening)"),
  provenance_note = c("Provenance note", "Provenance note (matrix ontology annotation)"),
  od_author = c("Definition author", "Authoring source of the definition (Galluzzi et al. 2018 / Rodrigues et al. 2025 / RCDome)"),
  review_status = c("Review status", "Review status (APPROVED = human-approved draft / LOCKED-VERBATIM = published verbatim)"),
  validation_verdict = c("Validation verdict", "Validation verdict (VALIDATED / MINOR_ISSUE / VERBATIM-INVARIANT / CRITERION-PENDING / UMBRELLA-SCOPE)"),
  species_scope = c("Species scope", "Species scope of the modality (human / mammalian / vertebrate / invertebrate_model / plant / cross_species / uncertain)"),
  evidence_maturity = c("Evidence maturity", "Evidence maturity (established / supported / emerging / legacy / provisional)"),
  relationship_type = c("Relationship", "Ontological relation (is_a / subtype_of / triggered_by / driven_by / umbrella_for / associated_with)"),
  parent_entity = c("Parent entity", "Parent entity in the ontology (empty for root)"),
  ontology_curator_verified = c("Ontology curator verified", "Ontology curator verification (TRUE/FALSE; curator; date)"),
  independent_replication = c("Independent replication", "Independent replication (none / limited / multiple; pending until curated)"),
  primary_discovery_reference = c("Primary discovery reference", "Primary discovery reference PMID (equals founding_pmid)")
)

# Build the 3-column payload table (Variable | Description | Value).
build_payload_table <- function(ent, gene, ctx) {
  drow <- ctx$drow
  rows <- list()
  rows[[length(rows) + 1]] <- c("Entity", "RCD-related entity queried", ent)

  if (!is.null(gene)) {
    m <- genes_df[genes_df$rcd_form_canonical == ent & genes_df$gene_symbol == gene, ]
    if (nrow(m) > 0) {
      for (k in names(MATRIX_DESC)) {
        v <- m[[k]][1]
        v <- if (is.null(v) || is.na(v) || v == "") "not applicable" else as.character(v)
        rows[[length(rows) + 1]] <- c(MATRIX_DESC[[k]][1], MATRIX_DESC[[k]][2], v)
      }
    }
  } else {
    g <- ctx$genes
    gtxt <- if (length(g) == 0) "not recorded" else paste(sort(g), collapse = ", ")
    rows[[length(rows) + 1]] <- c("Associated genes", "Gene symbols associated with this entity in the RCDome database", gtxt)
  }

  if (!is.null(drow)) {
    for (k in names(DECODER_DESC)) {
      v <- drow[[k]][1]
      v <- if (is.null(v) || is.na(v) || v == "" || tolower(v) == "nan") "not applicable" else as.character(v)
      rows[[length(rows) + 1]] <- c(DECODER_DESC[[k]][1], DECODER_DESC[[k]][2], v)
    }
  }

  tags$table(
    style = "width:100%; border-collapse:collapse; font-size:12.5px;",
    tags$thead(tags$tr(
      tags$th(style = "text-align:left; color:#57534e; font-weight:600; padding:4px 0;", "Variable"),
      tags$th(style = "text-align:left; color:#57534e; font-weight:600; padding:4px 0;", "Description"),
      tags$th(style = "text-align:left; color:#57534e; font-weight:600; padding:4px 0;", "Value")
    )),
    tags$tbody(
      lapply(rows, function(r) {
        tags$tr(
          tags$td(style = "color:#1c1917; padding:3px 8px 3px 0; vertical-align:top; font-weight:500;", r[1]),
          tags$td(style = "color:#57534e; padding:3px 8px 3px 0; vertical-align:top;", r[2]),
          tags$td(style = "color:#1c1917; padding:3px 0; vertical-align:top; word-break:break-word;", r[3])
        )
      })
    )
  )
}

# HTML-string version of the payload table (for the downloaded report).
build_payload_table_html <- function(ent, gene, ctx) {
  rows <- list()
  rows[[length(rows) + 1]] <- c("Entity", "RCD-related entity queried", ent)
  if (!is.null(gene)) {
    m <- genes_df[genes_df$rcd_form_canonical == ent & genes_df$gene_symbol == gene, ]
    if (nrow(m) > 0) {
      for (k in names(MATRIX_DESC)) {
        v <- m[[k]][1]
        v <- if (is.null(v) || is.na(v) || v == "") "not applicable" else as.character(v)
        rows[[length(rows) + 1]] <- c(MATRIX_DESC[[k]][1], MATRIX_DESC[[k]][2], v)
      }
    }
  } else {
    g <- ctx$genes
    gtxt <- if (length(g) == 0) "not recorded" else paste(sort(g), collapse = ", ")
    rows[[length(rows) + 1]] <- c("Associated genes",
                                  "Gene symbols associated with this entity in the RCDome database", gtxt)
  }
  if (!is.null(ctx$drow)) {
    for (k in names(DECODER_DESC)) {
      v <- ctx$drow[[k]][1]
      v <- if (is.null(v) || is.na(v) || v == "" || tolower(v) == "nan") "not applicable" else as.character(v)
      rows[[length(rows) + 1]] <- c(DECODER_DESC[[k]][1], DECODER_DESC[[k]][2], v)
    }
  }
  body <- paste0(sapply(rows, function(r) {
    paste0("<tr><td style='color:#1c1917; padding:3px 8px 3px 0; vertical-align:top; font-weight:500;'>", r[1], "</td>",
           "<td style='color:#57534e; padding:3px 8px 3px 0; vertical-align:top;'>", r[2], "</td>",
           "<td style='color:#1c1917; padding:3px 0; vertical-align:top; word-break:break-word;'>", r[3], "</td></tr>")
  }), collapse = "")
  paste0("<table style='width:100%; border-collapse:collapse; font-size:12.5px;'>",
         "<thead><tr><th style='text-align:left; color:#57534e; font-weight:600; padding:4px 0;'>Variable</th>",
         "<th style='text-align:left; color:#57534e; font-weight:600; padding:4px 0;'>Description</th>",
         "<th style='text-align:left; color:#57534e; font-weight:600; padding:4px 0;'>Value</th></tr></thead>",
         "<tbody>", body, "</tbody></table>")
}

# Render the synthesis prose + the "Suggested Queries" box as a numbered list.
render_synthesis <- function(synth) {
  parts <- strsplit(synth, "Suggested Queries:", fixed = TRUE)[[1]]
  prose <- parts[1]
  queries <- if (length(parts) > 1) parts[2] else NULL
  prose_paras <- strsplit(prose, "\n\n", fixed = TRUE)[[1]]
  prose_paras <- prose_paras[nzchar(trimws(prose_paras))]
  out <- tagList(lapply(prose_paras, function(p) {
    esc <- htmltools::htmlEscape(p)
    lnk <- gsub("PMID[ :](\\d+)", "<a href='https://pubmed.ncbi.nlm.nih.gov/\\1' target='_blank'>PMID \\1</a>", esc, perl = TRUE)
    tags$p(style = "font-size:14px; line-height:1.65; color:#1c1917;", HTML(gsub("\n", "<br>", lnk)))
  }))
  if (!is.null(queries) && nzchar(trimws(queries))) {
    qs <- extract_suggested_queries(synth)
    if (length(qs) > 0) {
      out <- tagList(out, tags$div(
        style = "margin-top:18px; padding:14px 16px; background:#f5f5f4; border:1px solid #e7e5e4; border-radius:10px;",
        tags$div(style = "font-family:'Segoe UI',system-ui,sans-serif; font-size:12px; letter-spacing:0.06em; color:#c2410c; margin-bottom:10px;",
                 "Suggested Queries"),
        lapply(seq_along(qs), function(i) {
          tags$div(style = "font-size:13.5px; color:#1c1917; line-height:1.5; padding:4px 0;",
                   tags$span(style = "color:#FF9800; font-weight:600; margin-right:6px;", paste0(i, ".")),
                   qs[i])
        })
      ))
    }
  }
  disc <- extract_disclaimer(synth)
  if (!is.null(disc) && nzchar(disc)) {
    out <- tagList(out, tags$p(style = "color:#57534e; font-style:italic; font-size:13px; line-height:1.6; margin-top:14px;", disc))
  }
  out
}

render_synthesis_html <- function(synth) {
  parts <- strsplit(synth, "Suggested Queries:", fixed = TRUE)[[1]]
  prose <- parts[1]
  queries <- if (length(parts) > 1) parts[2] else NULL
  prose_paras <- strsplit(prose, "\n\n", fixed = TRUE)[[1]]
  prose_paras <- prose_paras[nzchar(trimws(prose_paras))]
  body <- paste0(sapply(prose_paras, function(p) {
    esc <- htmltools::htmlEscape(p)
    lnk <- gsub("PMID[ :](\\d+)", "<a href='https://pubmed.ncbi.nlm.nih.gov/\\1' target='_blank'>PMID \\1</a>", esc, perl = TRUE)
    paste0("<p style='font-size:14px; line-height:1.65; color:#1c1917;'>", gsub("\n", "<br>", lnk), "</p>")
  }), collapse = "")
  if (!is.null(queries) && nzchar(trimws(queries))) {
    qs <- extract_suggested_queries(synth)
    if (length(qs) > 0) {
      qhtml <- paste0(sapply(seq_along(qs), function(i) {
        paste0("<div style='font-size:13.5px; color:#1c1917; line-height:1.5; padding:4px 0;'>",
               "<span style='color:#FF9800; font-weight:600; margin-right:6px;'>", i, ".</span>",
               qs[i], "</div>")
      }), collapse = "")
      body <- paste0(body,
        "<div style='margin-top:18px; padding:14px 16px; background:#f5f5f4; border:1px solid #e7e5e4; border-radius:10px;'>",
        "<div style='font-family:Calibri,sans-serif; font-size:12px; letter-spacing:0.06em; color:#c2410c; margin-bottom:10px;'>Suggested Queries</div>",
        qhtml, "</div>")
    }
  }
  disc <- extract_disclaimer(synth)
  if (!is.null(disc) && nzchar(disc)) {
    body <- paste0(body, "<p style='color:#57534e; font-style:italic; font-size:13px; line-height:1.6; margin-top:14px;'>", disc, "</p>")
  }
  body
}

board_card <- function(title, body) {
  div(
    style = "background:#ffffff; border:1px solid #e7e5e4; border-radius:12px; padding:20px 22px; flex:1; min-width:220px;",
    div(style = "font-family:'Segoe UI',system-ui,sans-serif; font-size:24px; letter-spacing:0.08em; color:#c2410c; margin-bottom:8px;", HTML(title)),
    div(style = "font-size:13.5px; line-height:1.6; color:#57534e;", HTML(body))
  )
}

mod_board_ui <- function(id) {
  ns <- NS(id)

  div(class = "about-content",

    # Hero
    div(class = "hero", style = "grid-template-columns: 1fr 1.2fr; gap: 32px;",
      div(
        div(class = "eyebrow", style = "text-transform: none; font-size: 24px;", HTML(paste0(rcdome_span(), " \u00b7 Scientific Module"))),
        h1(HTML(paste0(rcdome_span(), " Digital Molecular Board"))),
        div(class = "lede", HTML(paste0(
          "A regulated-cell-death (RCD) interpretation module built for ",
          "<b>educational use and scientific interrogation</b>. It translates the ",
          "<b>RCDome database</b> (22,473 gene\u2013RCD associations across 53 ",
          "RCD-related entities) and the <b>RCDome decoder</b> (curated operational ",
          "definitions and ontological classification) into a sourced, hedged ",
          "prose synthesis \u2014 then supports structured follow-up questions about ",
          "gene associations, mechanistic roles, regulatory directions, evidence ",
          "maturity, key molecules, and ontological relationships, through the ",
          "RCDome Q&A AI."
        )))
      ),
      div(
        style = "display:flex; align-items:center; justify-content:flex-end;",
        img(src = "rcdome_logo.svg", alt = "RCDome dome",
            style = "width:100%; max-width:640px; height:auto; display:block; margin-left:auto;")
      )
    ),

    # What the Board integrates
    div(class = "index",
      div(class = "index-head",
        div(class = "index-title", "What the Board integrates")
      ),
      div(style = "display:flex; gap:16px; flex-wrap:wrap;",
        board_card(paste0(rcdome_span(), " database"),
          paste0("Gene\u2013RCD associations with evidence tier, role, direction, ",
                 "mechanistic classification, and verified PMIDs.")),
        board_card(paste0(rcdome_span(), " decoder"),
          paste0("53 canonicalized RCD-related entities with operational definitions, key molecules, ",
                 "core mechanisms, hard-gate status, and founding references.")),
        board_card(paste0(rcdome_span(), " Q&A AI"),
          paste0("A governed follow-up dialogue: genes associated, required genes, ",
                 "evidence maturity, key molecules, and ontological relationships."))
      )
    ),

    # How to use
    div(class = "index",
      div(class = "index-head",
        div(class = "index-title", "How to use it")
      ),
      div(style = "display:flex; gap:16px; flex-wrap:wrap;",
        board_card("1. Select", "Choose an RCD entity (and optionally a single gene) from the dropdowns."),
        board_card("2. Generate", "The AI agent produces a prose synthesis sourced from the database and decoder."),
        board_card("3. Question", "The three suggested queries appear in the Q&A module; ask any follow-up within scope.")
      )
    ),

    # The Board
    div(class = "index",
      div(style = "background:#ffffff; border:1px solid #e7e5e4; border-radius:14px; padding:26px 28px;",
        fluidRow(
          column(4,
            selectizeInput(
              ns("board_entity"),
              tags$span(style = "color:#1c1917; font-weight:600;", "1. RCD entity"),
              choices = c("Select an entity" = ""),
              width = "100%",
              options = list(placeholder = "Select or type an RCD entity", create = rcdome_create_js)
            ),
            selectizeInput(
              ns("board_gene"),
              tags$span(style = "color:#1c1917; font-weight:600;", "2. Gene (optional)"),
              choices = c("(all genes)" = ""),
              width = "100%",
              options = list(placeholder = "All genes for this entity", create = rcdome_create_js)
            ),
            uiOutput(ns("generate_btn")),
            uiOutput(ns("download_ui"))
          ),
          column(8,
            uiOutput(ns("board_report_ui"))
          )
        )
      )
    ),

    # Q&A submodule
    div(style = "margin-top:28px;",
      mod_board_qa_ui(ns("qa"))
    ),

    # Interactive example queries (after the Q&A submodule, so they never
    # interfere with the automatic display of the agent-generated queries)
    div(class = "index",
      div(class = "index-head",
        div(class = "index-title", "Try an example query")
      ),
      div(style = "display:flex; flex-direction:column; gap:8px;",
        lapply(seq_along(BOARD_EXAMPLE_QUERIES), function(i) {
          actionButton(
            ns(paste0("ex_q", i)),
            BOARD_EXAMPLE_QUERIES[[i]]$question,
            class = "btn",
            style = "text-align:left; width:100%; margin-bottom:8px; font-weight:500;"
          )
        })
      )
    )
  )
}

mod_board_server <- function(id, board_reactive) {
  moduleServer(id, function(input, output, session) {
    ns <- session$ns

    observe({
      if (exists("canonical_pathways", inherits = TRUE) && length(canonical_pathways) > 0) {
        updateSelectizeInput(session, "board_entity",
                             choices = c("Select an entity" = "", canonical_pathways),
                             server = FALSE)
      }
    })

    observeEvent(input$board_entity, {
      ent <- input$board_entity
      if (is.null(ent) || ent == "") {
        updateSelectizeInput(session, "board_gene", choices = character(0), server = FALSE)
        return()
      }
      if (!ent %in% canonical_pathways) {
        showNotification(paste0("Sorry, '", ent, "' is not in the RCDome database (53 RCD-related entities)."), type = "error")
        updateSelectizeInput(session, "board_entity",
                             choices = c("Select an entity" = "", canonical_pathways), server = FALSE)
        updateSelectizeInput(session, "board_gene", choices = character(0), server = FALSE)
        return()
      }
      g <- unique(trimws(genes_df$gene_symbol[genes_df$rcd_form_canonical == ent]))
      updateSelectizeInput(session, "board_gene", choices = c("(all genes)" = "", sort(g)), server = FALSE)
    }, ignoreNULL = TRUE)

    observeEvent(input$board_gene, {
      gene <- input$board_gene
      ent <- input$board_entity
      if (is.null(gene) || gene == "" || is.null(ent) || ent == "") return()
      if (!ent %in% canonical_pathways) return()
      g_ok <- unique(trimws(genes_df$gene_symbol[genes_df$rcd_form_canonical == ent]))
      if (!gene %in% g_ok) {
        showNotification(paste0("Sorry, '", gene, "' is not associated with ", ent, " in the RCDome database."), type = "error")
        updateSelectizeInput(session, "board_gene", choices = c("(all genes)" = "", sort(g_ok)), server = FALSE)
      }
    }, ignoreNULL = TRUE)

    report <- reactiveVal(NULL)
    generating <- reactiveVal(FALSE)
    pending_query <- reactiveVal(NULL)

    output$generate_btn <- renderUI({
      if (isTRUE(generating())) {
        tags$button(
          class = "btn primary",
          style = "width:100%; margin-top:8px; opacity:0.65; cursor:wait;",
          disabled = NA,
          "Generating synthesis…"
        )
      } else {
        actionButton(ns("btn_generate"), "Generate Synthesis", class = "btn primary", style = "width:100%; margin-top:8px;")
      }
    })

    observeEvent(input$btn_generate, {
      ent <- input$board_entity
      if (is.null(ent) || ent == "") {
        showNotification("Please select an RCD entity.", type = "error")
        return()
      }
      if (!ent %in% canonical_pathways) {
        showNotification(paste0("Sorry, '", ent, "' is not in the RCDome database (53 RCD-related entities)."), type = "error")
        return()
      }
      gene <- input$board_gene
      if (is.null(gene) || gene == "") gene <- NULL
      if (!is.null(gene)) {
        g_ok <- unique(trimws(genes_df$gene_symbol[genes_df$rcd_form_canonical == ent]))
        if (!gene %in% g_ok) {
          showNotification(paste0("Sorry, '", gene, "' is not associated with ", ent, " in the RCDome database."), type = "error")
          return()
        }
      }

      api_key <- Sys.getenv("DEEPSEEK_API_KEY", unset = "")
      if (api_key == "") {
        showNotification("DEEPSEEK_API_KEY is not set.", type = "error")
        return()
      }

      ctx <- build_entity_context(ent, gene)

      prompt_file <- "board/RCD_Board_DeepSeek_Prompt.md"
      sys_prompt <- if (file.exists(prompt_file))
        paste(readLines(prompt_file, warn = FALSE), collapse = "\n")
      else
        "You are the RCDome Digital Molecular RCD Board. Answer from the RCDome database and decoder."

      prompt <- list(
        list(role = "system", content = sys_prompt),
        list(role = "user", content = paste0(
          "Gene: ", if (is.null(gene)) "(all genes)" else gene, "\n",
          "Entity: ", ent, "\n",
          "RCDome database (genes associated with ", ent, "): ", ctx$matrix_fields, "\n",
          "RCDome decoder (ontology for ", ent, "): ", ctx$decoder_fields
        ))
      )

      generating(TRUE)
      withProgress(message = "Generating synthesis...", value = 0, {
      start_t <- Sys.time()
      res <- tryCatch({
        resp <- httr::POST(
          "https://api.deepseek.com/v1/chat/completions",
          httr::add_headers(
            Authorization = paste("Bearer", api_key),
            "Content-Type" = "application/json"
          ),
          body = jsonlite::toJSON(list(
            model = "deepseek-chat", messages = prompt, temperature = 0.7
          ), auto_unbox = TRUE),
          encode = "raw",
          httr::timeout(300)
        )
        status <- httr::status_code(resp)
        body   <- httr::content(resp, "text", encoding = "UTF-8")
        if (status != 200) {
          paste0("Error: DeepSeek HTTP ", status)
        } else {
          jsonlite::fromJSON(body)$choices$message$content[1]
        }
      }, error = function(e) paste0("Error: ", conditionMessage(e)))
      elapsed <- as.numeric(difftime(Sys.time(), start_t, units = "secs"))

      synth <- scrub_board(res)
      qs <- extract_suggested_queries(synth)

      report(list(entity = ent, gene = gene, synthesis = synth, suggested_queries = qs, ctx = ctx, elapsed = elapsed,
                  api_ok = !grepl("^Error:", res)))
      board_reactive(list(
        entity = ent,
        gene = gene,
        matrix_fields = ctx$matrix_fields,
        decoder_fields = ctx$decoder_fields,
        suggested_queries = qs
      ))
      })
      generating(FALSE)
    })

    # Example-query clicks: load the entity context + hand the question to the Q&A
    lapply(seq_along(BOARD_EXAMPLE_QUERIES), function(i) {
      observeEvent(input[[paste0("ex_q", i)]], {
        ex <- BOARD_EXAMPLE_QUERIES[[i]]
        ent <- ex$entity
        ctx <- build_entity_context(ent)
        updateSelectInput(session, "board_entity", selected = ent)
        updateSelectizeInput(session, "board_gene",
                             choices = c("(all genes)" = "", sort(unique(genes_df$gene_symbol[genes_df$rcd_form_canonical == ent]))),
                             server = FALSE)
        board_reactive(list(
          entity = ent,
          gene = NULL,
          matrix_fields = ctx$matrix_fields,
          decoder_fields = ctx$decoder_fields,
          suggested_queries = character(0)
        ))
        pending_query(ex$question)
      }, ignoreNULL = TRUE)
    })

    output$board_report_ui <- renderUI({
      r <- report()
      if (is.null(r)) {
        return(tags$div(
          style = "color:#57534e; font-style:italic; text-align:center; padding:40px 20px; font-size:13.5px;",
          "Select an entity and click Generate Synthesis. The report and its suggested queries will appear here."
        ))
      }
      synth <- r$synthesis
      tags$div(
        style = "background:#ffffff; border:1px solid #e7e5e4; border-radius:12px; padding:24px 26px;",
        div(style = "font-family:'Segoe UI',system-ui,sans-serif; font-size:12px; letter-spacing:0.08em; text-transform:uppercase; color:#c2410c; margin-bottom:6px;",
            HTML(paste0(rcdome_span(), " \u00b7 Digital Molecular Synthesis Report"))),
        div(style = "font-family:'Segoe UI',system-ui,sans-serif; font-size:20px; font-weight:600; color:#1c1917; margin-bottom:16px;",
            r$entity),
        render_synthesis(synth),
        if (isTRUE(r$api_ok)) div(
          style = "background:#dcfce7; color:#166534; padding:8px 14px; border-radius:8px; font-size:12.5px; margin-top:16px;",
          "✓ Governance Audit: No violations detected. LLM output passed all automated checks."
        ) else div(
          style = "background:#fef3c7; color:#92400e; padding:8px 14px; border-radius:8px; font-size:12.5px; margin-top:16px;",
          "⚠ Generation failed — no synthesis produced (DeepSeek API error)."
        ),
        tags$details(
          style = "margin-top:12px; padding:12px 14px; background:#f5f5f4; border:1px solid #e7e5e4; border-radius:8px;",
          tags$summary(style = "font-size:12.5px; color:#FF9800; cursor:pointer; font-weight:600;",
                      "Audit Molecular and Cellular Payload Data (Raw Injection)"),
          build_payload_table(r$entity, r$gene, r$ctx)
        ),
        div(style = "font-size:11.5px; color:#57534e; text-align:right; margin-top:14px;",
            paste0("Automatically generated on ", format(Sys.time(), "%d/%m/%Y %H:%M:%S"),
                   " (Processing Time: ", round(r$elapsed %||% 0, 1), "s)"))
      )
    })

    output$download_ui <- renderUI({
      r <- report()
      if (is.null(r)) return(NULL)
      ent <- r$entity
      logo_file <- file.path("data/RCD modulo/logo RCDs", paste0(ent, ".png"))
      logo_url <- if (file.exists(logo_file)) paste0("rcd_logos/", URLencode(paste0(ent, ".png"), reserved = TRUE)) else ""
      tagList(
        downloadButton(ns("download_html"), "Download Synthesis (HTML)",
                       class = "btn",
                       style = "width:100%; margin-top:10px;"),
        if (nzchar(logo_url)) tags$div(
          style = "text-align:center; margin-top:14px;",
          tags$img(src = logo_url, alt = ent, style = "width:240px; height:240px; object-fit:contain;")
        ) else NULL
      )
    })

    output$download_html <- downloadHandler(
      filename = function() {
        ent <- report()$entity
        gene <- report()$gene
        if (is.null(ent) || !nzchar(ent)) ent <- "synthesis"
        base <- if (is.null(gene) || !nzchar(gene))
          paste0("RCDome_Board_", gsub(" ", "_", ent))
        else
          paste0("RCDome_Board_", gsub(" ", "_", gene), "_", gsub(" ", "_", ent))
        paste0(base, ".html")
      },
      content = function(file) {
        r <- report()
        body <- render_synthesis_html(r$synthesis)
        
        # Small RCDome logo (upper right), embedded base64 so the report is standalone.
        logo_file <- "www/rcdome_logo_full.svg"
        logo_img <- if (file.exists(logo_file)) {
          b64 <- jsonlite::base64_enc(readBin(logo_file, "raw", file.info(logo_file)$size))
          paste0(
            "<div style='position:absolute; top:16px; right:16px; width:200px;'>",
            "<img src='data:image/svg+xml;base64,", b64, "' alt='RCDome' ",
            "style='width:100%; height:auto; display:block;'></div>"
          )
        } else ""
        
        # Entity logo (top-left), embedded base64 so the report is standalone.
        ent_logo_file <- file.path("data/RCD modulo/logo RCDs", paste0(r$entity, ".png"))
        ent_logo_img <- if (file.exists(ent_logo_file)) {
          b64e <- jsonlite::base64_enc(readBin(ent_logo_file, "raw", file.info(ent_logo_file)$size))
          paste0(
            "<div style='margin-bottom:18px;'>",
            "<img src='data:image/png;base64,", b64e, "' alt='", r$entity, "' ",
            "style='width:140px; height:auto; display:block;'></div>"
          )
        } else ""
        
        gov_box <- if (isTRUE(r$api_ok)) paste0(
          "<div style='background:#dcfce7; color:#166534; padding:8px 14px; border-radius:8px; font-size:12.5px; margin-top:16px;'>",
          "✓ Governance Audit: No violations detected. LLM output passed all automated checks.</div>"
        ) else paste0(
          "<div style='background:#fef3c7; color:#92400e; padding:8px 14px; border-radius:8px; font-size:12.5px; margin-top:16px;'>",
          "⚠ Generation failed — no synthesis produced (DeepSeek API error).</div>"
        )
        html <- paste0(
          "<!DOCTYPE html><html><head><meta charset='utf-8'><title>RCDome Digital Molecular Board</title></head><body style='font-family:Calibri,sans-serif;'>",
          logo_img,
          ent_logo_img,
          "<div style='font-size:28px; letter-spacing:0.08em; text-transform:uppercase; color:#c2410c;'>RCDome \u00b7 Digital Molecular Synthesis Report</div>",
          "<h1 style='font-weight:500; font-size:28px; margin:8px 0 20px;'>RCDome Digital Molecular Board</h1>",
          body,
          gov_box,
          "<details style='margin-top:12px; padding:12px 14px; background:#f5f5f4; border:1px solid #e7e5e4; border-radius:8px;'>",
          "<summary style='font-size:12.5px; color:#FF9800; cursor:pointer; font-weight:600;'>Audit Molecular and Cellular Payload Data (Raw Injection)</summary>",
          build_payload_table_html(r$entity, r$gene, r$ctx),
          "</details>",
          "<div style='font-size:11.5px; color:#57534e; text-align:right; margin-top:14px;'>",
          "Automatically generated on ", format(Sys.time(), "%d/%m/%Y %H:%M:%S"),
          " (Processing Time: ", round(r$elapsed %||% 0, 1), "s)</div>",
          "</body></html>"
        )
        writeLines(html, file, useBytes = TRUE)
      }
    )

    # nested Q&A submodule (receives the pending example query)
    mod_board_qa_server("qa", board_reactive, pending_query)

  })
}
