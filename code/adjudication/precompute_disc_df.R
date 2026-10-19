t0 <- Sys.time()
g <- readRDS("RCDome_distribution/data/unified_gene_rcd_matrix_V027.rds")
g$name <- as.character(g$gene_symbol)
g$pc <- trimws(as.character(g$rcd_form_canonical))
files <- list.files("RCDome_distribution/data/adjudication", pattern = "xlsx$", full.names = TRUE)
sheets <- lapply(files, function(f) {
  raw <- tryCatch(readxl::read_excel(f), error = function(e) NULL)
  if (is.null(raw) || nrow(raw) == 0) return(NULL)
  get <- function(nm) if (nm %in% names(raw)) trimws(as.character(raw[[nm]])) else rep(NA_character_, nrow(raw))
  data.frame(
    gene_symbol = get("gene_symbol"),
    rcd_form_canonical = get("rcd_form_canonical"),
    label = tolower(get("label")),
    ds_val = get("deepseek"),
    cs_val = get("consensus"),
    gpt4o_verdict = get("gpt4o_verdict"),
    gpt4o_reason = get("gpt4o_reason"),
    cur1_val = get("curator_1_verdict"),
    cur2_val = get("curator_2_verdict"),
    final_val = get("final_verdict"),
    decision_status = if ("decision_status" %in% names(raw)) get("decision_status") else rep("PENDING_DELTA", nrow(raw)),
    deciding_evidence = get("deciding_evidence"),
    stringsAsFactors = FALSE
  )
})
raw <- do.call(rbind, Filter(Negate(is.null), sheets))
raw <- raw[raw$label %in% c("mechanistic", "role", "direction"), , drop = FALSE]
key <- paste(raw$gene_symbol, raw$rcd_form_canonical, sep = "\r")
mkey <- paste(g$name, g$pc, sep = "\r")
idx <- match(key, mkey)
raw$el_val <- ifelse(raw$label == "direction" & !is.na(idx), as.character(g$role_direction[idx]), NA_character_)
raw$compiled_role <- ifelse(!is.na(idx), as.character(g$rcd_gene_type[idx]), NA_character_)
raw$compiled_dir <- ifelse(!is.na(idx), as.character(g$role_direction[idx]), NA_character_)
saveRDS(raw, "RCDome_distribution/data/adjudication/disc_df.rds")
cat("saved disc_df.rds:", nrow(raw), "rows in", round(difftime(Sys.time(), t0, units = "secs"), 1), "s\n")
