# ─── Pathways: extraído direto da tabela ─────────────────────────────────────
# Nada inventado — as RCDs vêm da coluna rcd_form (uma por linha por gene).
# A query usa o nome exato como termo de busca. Sem sinônimos, sem expansão.

#' Extrai as vias associadas a um gene a partir do data frame completo.
#' Retorna vetor de nomes (ex.: c("Apoptosis", "Necrosis")).
get_pathways_for_gene <- function(gene_row, genes_df = NULL) {
  if (nrow(gene_row) == 0) return(character(0))
  gene_name <- gene_row$name[1]

  # Se temos o data frame completo, agrega todas as linhas do gene
  if (!is.null(genes_df)) {
    all_rows <- genes_df[genes_df$name == gene_name, ]
    rcds <- unique(all_rows$Pathway_Categorization[!is.na(all_rows$Pathway_Categorization) & all_rows$Pathway_Categorization != ""])
    if (length(rcds) > 0) return(rcds)
  }

  # Fallback: linha única (compatibilidade)
  if (is.na(gene_row$Pathway_Categorization) || gene_row$Pathway_Categorization == "") {
    return(character(0))
  }
  raw <- strsplit(gene_row$Pathway_Categorization, ";")[[1]]
  trimws(raw)
}
