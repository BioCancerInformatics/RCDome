# RCDome pipeline flowchart — grViz, matching the Figure-1 example style
# with stri_wrap text wrapping (same as the example's wrap_text helper)
library(DiagrammeR)
library(DiagrammeRsvg)
library(rsvg)
library(magick)
library(stringi)

wrap_text <- function(text, width = 35) {
  stri_wrap(text, width = width) |> paste(collapse = "\n")
}

# ── Read the truth matrix so the consolidation counts never go stale ──
mat <- read.csv("D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_distribution/data/unified_gene_rcd_matrix_V027.csv", check.names = FALSE, encoding = "UTF-8")
n_rows <- nrow(mat)
n_genes <- length(unique(mat$gene_symbol))
n_entities <- length(unique(mat$rcd_form_canonical))
n_cols <- ncol(mat)

labels <- list(
  sources       = wrap_text("20 source databases (FerrDB v3, RCDdb, iPCD, LncRCD, iLIR, HADb, HAMdb, ATD, AMT-DB, ncFO, KEGG, Reactome, GO, MSigDB, WikiPathways, NCBI Gene, Rodrigues 2025, XDeathDB, Elicit Phase 3, Elicit Alert)"),
  channels      = wrap_text("Five evidence channels (A-D at compile, E at validation): A PubMed Boolean (recall), B curated databases (precision), C AI-assisted screening, D manual curation (arbiter), E Elicit Phase 3 systematic review"),
  consolidation = wrap_text(paste0("Consolidation: ", n_entities, " canonicalized RCD-related entities (62 name strings), ", format(n_rows, big.mark = ","), " rows, ", format(n_genes, big.mark = ","), " genes")),
  validation    = wrap_text("INDEPENDENT VALIDATION"),
  deepseek      = wrap_text("DeepSeek (Phases 2A/D, 2B, 2C, 2D/2E, 2F): two-call validation, deep RAG, recovery, CoT full-matrix (cot_role, cot_direction, cot_mechanistic, cot_evidence)"),
  elicit        = wrap_text("Elicit (Phase 3): AI-assisted extraction, role + direction"),
  consensus     = wrap_text("Consensus (Phase 2G): evidence-channel classification, neutral query"),
  matrix        = wrap_text(paste0("Consolidated matrix: ", format(n_rows, big.mark = ","), " rows × ", n_cols, " columns")),
  app           = wrap_text("RCDome web application (Home dome, Explore RCDome, Operational Definitions, Compare Definitions, RCD entities, Gene Catalog, Discrepancy Radar, Discovery Timeline, 3D RCDome, Digital Molecular RCD Board, Network)")
)

diagram <- grViz("
digraph workflow {
  graph [layout = dot, rankdir = TB, ranksep = 0.8, nodesep = 0.6]
  node [shape = rectangle, style = 'rounded,filled', width = 2.8, height = 0.9, fontsize = 10, fontname = 'Helvetica', color = '#8DB0C9', fontcolor = '#1F3143', penwidth = 1.5]
  edge [color = '#7998AF', penwidth = 2, arrowsize = 0.7]

  sources       [label = '@@1', fillcolor = '#AED6F1']
  channels      [label = '@@2', fillcolor = '#48C9B0']
  consolidation [label = '@@3', fillcolor = '#F9E79F']
  validation    [label = '@@4', fillcolor = '#EBDEF0', fontcolor = '#D32F2F']
  deepseek      [label = '@@5', fillcolor = '#ABEBC6']
  elicit        [label = '@@6', fillcolor = '#F1948A']
  consensus     [label = '@@7', fillcolor = '#EB984E']
  matrix        [label = '@@8', fillcolor = '#FCBB18']
  app           [label = '@@9', fillcolor = '#D32F2F', fontcolor = 'white']

  sources -> channels -> consolidation -> validation
  validation -> {deepseek elicit consensus}
  {deepseek elicit consensus} -> matrix -> app
}

[1]: labels$sources
[2]: labels$channels
[3]: labels$consolidation
[4]: labels$validation
[5]: labels$deepseek
[6]: labels$elicit
[7]: labels$consensus
[8]: labels$matrix
[9]: labels$app
")

svg_code <- DiagrammeRsvg::export_svg(diagram)
svg_raw <- charToRaw(svg_code)

png_file <- "workflow_rcdome_tmp.png"
rsvg_png(svg_raw, file = png_file, width = 4961, height = 7016)  # A4 portrait @ 600 DPI

out <- "D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures/Figure_1_pipeline"
img <- image_read(png_file, density = "600x600")
image_write(img, path = paste0(out, ".tiff"), format = "tiff", compression = "lzw")
rsvg_pdf(svg_raw, file = paste0(out, ".pdf"), width = 8.27, height = 11.69)

# PNG for quick view
image_write(image_convert(img, format = "png"), path = paste0(out, ".png"))

cat("saved Figure_1_pipeline.tiff/.pdf/.png (text wrapped)\n")
