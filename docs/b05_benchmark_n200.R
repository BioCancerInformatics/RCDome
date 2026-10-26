# B05 full benchmark — n=200 random pairs × 7 layers (accuracy, CI, substitution)
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
uniq <- uniq[nzchar(uniq$final_role) & nzchar(uniq$cot_role), ]
div <- uniq[uniq$div, ]; agr <- uniq[!uniq$div, ]
set.seed(7)
n_div <- round(200 * nrow(div) / nrow(uniq)); n_agr <- 200 - n_div
pairs <- rbind(div[sample(nrow(div), n_div), ], agr[sample(nrow(agr), n_agr), ])
pairs <- pairs[sample(nrow(pairs)), ]
cat(sprintf("sampled %d pairs: %d divergent + %d agree\n", nrow(pairs), n_div, n_agr))

layers <- c(EF="Evidence-first", DS="DeepSeek", CM="Compiled gene role",
            CN="Consensus", GP="GPT", C1="Curator 1", C2="Curator 2")

ask <- function(sys, q) {
  for (attempt in 1:3) {
    resp <- tryCatch(
      httr::POST("https://api.deepseek.com/v1/chat/completions",
        httr::add_headers(Authorization=paste("Bearer",api_key), "Content-Type"="application/json"),
        body=jsonlite::toJSON(list(model="deepseek-chat",
          messages=list(list(role="system", content=sys), list(role="user", content=q)),
          temperature=0.3, max_tokens=500), auto_unbox=TRUE), encode="raw", httr::timeout(300)),
      error = function(e) NULL)
    if (!is.null(resp) && httr::status_code(resp) == 200) {
      b <- httr::content(resp, "text", encoding="UTF-8")
      return(jsonlite::fromJSON(b)$choices$message$content[1])
    }
    cat(sprintf("  (retry %d/3)\n", attempt)); Sys.sleep(8)
  }
  "HTTP_ERROR"
}

get_exp <- function(r) {
  c(EF=paste0(r$final_role[1],"/",r$final_direction[1]),
    DS=paste0(r$cot_role[1],"/",r$cot_direction[1]),
    CM=paste0(r$rcd_gene_type[1],"/",r$role_direction[1]),
    CN=paste0(r$consensus_role[1],"/",r$consensus_direction[1]),
    GP=paste0(r$gpt_mapped_role[1],"/",r$gpt_mapped_dir[1]),
    C1=paste0(r$curator_1_mapped_role[1],"/",r$curator_1_mapped_dir[1]),
    C2=paste0(r$curator_2_mapped_role[1],"/",r$curator_2_mapped_dir[1]))
}

score <- function(ans, exp) {
  parts <- strsplit(exp, "/", fixed=TRUE)[[1]]
  parts <- trimws(parts[parts != "" & parts != "NA"])
  if (length(parts) == 0) return(NA)
  all(vapply(parts, function(p) grepl(p, ans, fixed=TRUE), logical(1)))
}

wilson <- function(x, n, z=1.96) {
  if (n == 0) return(c(NA, NA))
  p <- x/n
  den <- 1 + z^2/n
  ctr <- p + z^2/(2*n)
  m <- z * sqrt(p*(1-p)/n + z^2/(4*n^2))
  c((ctr - m)/den, (ctr + m)/den)
}

outfile <- "analysis/b05_benchmark_results_n200.csv"
done <- if (file.exists(outfile)) read.csv(outfile, stringsAsFactors=FALSE) else NULL
started <- if (!is.null(done)) unique(done$pair) else character(0)

for (i in seq_len(nrow(pairs))) {
  g <- pairs$gene_symbol[i]; e <- pairs$rcd_form_canonical[i]
  pid <- paste0(g, " x ", e)
  if (pid %in% started) { cat("skip", pid, "\n"); next }
  b <- list(entity=e, gene=g, decoder_fields="not recorded")
  exp <- get_exp(pairs[i, ])
  rows <- list()
  for (L in names(layers)) {
    q <- paste0("What is the ", layers[[L]], " role and direction of ", g, " in ", e, "? Give only the role and direction.")
    ans <- ask(build_board_qa_prompt(b, q), q)
    ok <- score(ans, exp[[L]])
    rows[[length(rows)+1]] <- data.frame(pair=pid, layer=L, expected=exp[[L]],
      got=gsub("[\r\n\"]+", " ", substr(ans,1,80)), pass=ok, stringsAsFactors=FALSE)
    cat(sprintf("%s %s: %s\n", L, pid, ifelse(isTRUE(ok),"PASS", ifelse(is.na(ok),"NA","FAIL"))))
    Sys.sleep(0.3)
  }
  chunk <- do.call(rbind, rows)
  write.table(chunk, outfile, sep=",", row.names=FALSE, col.names=!file.exists(outfile), append=TRUE, quote=TRUE)
  cat(sprintf("--- saved %d/%d pairs ---\n", i, nrow(pairs)))
}

out <- read.csv(outfile, stringsAsFactors=FALSE)
out$pass <- as.logical(out$pass)
valid <- out[!is.na(out$pass), ]
acc <- sum(valid$pass) / nrow(valid)
ci <- wilson(sum(valid$pass), nrow(valid))
cat(sprintf("\n=== N=200 BENCHMARK ===\nN=%d pairs, %d scored questions\n", length(unique(out$pair)), nrow(valid)))
cat(sprintf("OVERALL Accuracy: %.1f%% (%d/%d)  [95%% Wilson CI: %.1f%% - %.1f%%]\n\n",
    acc*100, sum(valid$pass), nrow(valid), ci[1]*100, ci[2]*100))
cat("=== PER-LAYER (stratified) ===\n")
for (L in names(layers)) {
  sub <- out[out$layer == L, ]
  v <- sub[!is.na(sub$pass), ]
  if (nrow(v) == 0) { cat(sprintf("%-20s: no data\n", layers[[L]])); next }
  a <- sum(v$pass) / nrow(v)
  c2 <- wilson(sum(v$pass), nrow(v))
  cat(sprintf("%-20s: %.1f%% (%d/%d) [95%% CI %.1f%%-%.1f%%]\n", layers[[L]], a*100, sum(v$pass), nrow(v), c2[1]*100, c2[2]*100))
}
