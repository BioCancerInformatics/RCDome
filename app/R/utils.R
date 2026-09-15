# ─── Helpers ─────────────────────────────────────────────────────────────────
`%||%` <- function(x, y) if (is.null(x)) y else x

# Standardized RCDome wordmark: RCD (black, inherits) + ome (orange/gold).
# Use everywhere in titles and subtitles for a consistent conceptual color.
rcdome_span <- function() 'RCD<span style="color:#FF9800;">ome</span>'

# Selectize create callback: a typed value that matches no option triggers a
# global not-found event and returns false, so the value is NEVER added.
rcdome_create_js <- I("function(input) { if (window.Shiny) Shiny.setInputValue('rcdome_not_found', input, {priority:'event'}); return false; }")

# Resolve a gene search term to its canonical symbol, accepting aliases.
# Returns list(name, alias, term) or NULL if not found.
resolve_gene_alias <- function(term, genes_df) {
  t <- toupper(trimws(term))
  if (!nzchar(t)) return(NULL)

  # 1) exact canonical symbol (case-insensitive)
  hit <- which(toupper(genes_df$name) == t)
  if (length(hit)) return(list(name = genes_df$name[hit[1]], alias = FALSE, term = term))

  # 2) alias lookup (otheraliases is comma/semicolon-separated)
  aliases <- toupper(as.character(genes_df$otheraliases))
  for (i in seq_len(nrow(genes_df))) {
    a <- aliases[i]
    if (is.na(a) || !nzchar(a)) next
    parts <- trimws(strsplit(a, "[,;]")[[1]])
    if (t %in% parts) return(list(name = genes_df$name[i], alias = TRUE, term = term))
  }
  NULL
}
