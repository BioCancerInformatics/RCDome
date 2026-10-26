# B05 precision pass — 100 divergent pairs × EF/DS (accuracy + substitution + precision)
suppressPackageStartupMessages({library(jsonlite); library(httr)})
`%||%` <- function(a, b) if (is.null(a) || length(a) == 0 || is.na(a)) b else a
src <- readLines("RCDome_distribution/modules/mod_board_qa.R", warn = FALSE)
cut <- grep("mod_board_qa_server", src)[1]
eval(parse(text = paste(src[1:(cut - 1)], collapse = "\n")))
genes_df <- readRDS("RCDome_distribution/data/unified_gene_rcd_matrix_V027.rds")
api_key <- Sys.getenv("DEEPSEEK_API_KEY", unset = "")
stopifnot(nzchar(api_key))

uniq <- genes_df[!duplicated(paste(genes_df$gene_symbol, genes_df$rcd_form_canonical)), ]
uniq$div <- (paste(uniq$final_role, uniq$final_direction) != paste(uniq$cot_role, uniq$cot_direction))
div <- uniq[uniq$div & nzchar(uniq$final_role) & nzchar(uniq$cot_role), ]
set.seed(42)
pairs <- div[sample(nrow(div), 100), ]

ask <- function(sys, q) {
  for (attempt in 1:3) {
    resp <- tryCatch(httr::POST("https://api.deepseek.com/v1/chat/completions",
      httr::add_headers(Authorization=paste("Bearer",api_key), "Content-Type"="application/json"),
      body=jsonlite::toJSON(list(model="deepseek-chat",
        messages=list(list(role="system", content=sys), list(role="user", content=q)),
        temperature=0.3, max_tokens=500), auto_unbox=TRUE), encode="raw", httr::timeout(300)),
      error = function(e) NULL)
    if (!is.null(resp) && httr::status_code(resp) == 200) {
      b <- httr::content(resp, "text", encoding="UTF-8")
      return(jsonlite::fromJSON(b)$choices$message$content[1])
    }
    Sys.sleep(8)
  }
  "HTTP_ERROR"
}

has <- function(ans, s) { parts <- strsplit(s, "/", fixed=TRUE)[[1]]; parts <- trimws(parts[parts != "" & parts != "NA"]); length(parts) > 0 && all(vapply(parts, function(p) grepl(p, ans, fixed=TRUE), logical(1))) }

res <- list()
for (i in seq_len(nrow(pairs))) {
  g <- pairs$gene_symbol[i]; e <- pairs$rcd_form_canonical[i]
  ef <- paste0(pairs$final_role[i], "/", pairs$final_direction[i])
  ds <- paste0(pairs$cot_role[i], "/", pairs$cot_direction[i])
  b <- list(entity=e, gene=g, decoder_fields="not recorded")
  aEF <- ask(build_board_qa_prompt(b, paste0("What is the Evidence-first role and direction of ", g, " in ", e, "? Give only the role and direction.")), paste0("What is the Evidence-first role and direction of ", g, " in ", e, "? Give only the role and direction."))
  aDS <- ask(build_board_qa_prompt(b, paste0("What is the DeepSeek role and direction of ", g, " in ", e, "? Give only the role and direction.")), paste0("What is the DeepSeek role and direction of ", g, " in ", e, "? Give only the role and direction."))
  res[[length(res)+1]] <- data.frame(pair=paste0(g," x ",e),
    EF_acc=has(aEF, ef), EF_subst=has(aEF, ds),
    DS_acc=has(aDS, ds), DS_subst=has(aDS, ef),
    stringsAsFactors=FALSE)
  Sys.sleep(0.3)
}
out <- do.call(rbind, res)
cat("\n=== PRECISION PASS (100 divergent pairs) ===\n")
for (L in c("EF","DS")) {
  acc <- mean(out[[paste0(L,"_acc")]], na.rm=TRUE)
  subst <- mean(out[[paste0(L,"_subst")]], na.rm=TRUE)
  prec <- 1 - subst
  ci <- function(x, n) { p<-x; z<-1.96; den<-1+z^2/n; ctr<-p+z^2/(2*n); m<-z*sqrt(p*(1-p)/n+z^2/(4*n^2)); c((ctr-m)/den,(ctr+m)/den) }
  aci <- ci(acc, 100); pci <- ci(prec, 100)
  cat(sprintf("%s: accuracy %.0f%% (CI %.0f-%.0f) | substitution %.0f%% | precision %.0f%% (CI %.0f-%.0f)\n",
    L, acc*100, aci[1]*100, aci[2]*100, subst*100, prec*100, pci[1]*100, pci[2]*100))
}
write.csv(out, "analysis/b05_precision_pass.csv", row.names=FALSE)
