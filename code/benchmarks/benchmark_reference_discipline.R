# RCDome — Reference-discipline benchmark (reproducible)
# Purpose: verify that the Board/Q&A separate gene-specific PMID (association)
# from entity founding PMID (definition). Real DeepSeek calls.
# Result (run 2026-09-18): n=50, 50/50 PASS, 100% (95% CI 92.9–100%).

renv <- readLines("RCDome_distribution/.Renviron", warn = FALSE)
api_key <- sub("^DEEPSEEK_API_KEY=", "", renv[grep("DEEPSEEK_API_KEY", renv)][1])

m <- readRDS("RCDome_distribution/data/unified_gene_rcd_matrix_V026.rds")
dec <- read.csv("RCDome_distribution/data/RCDome_Decoder_53.csv", stringsAsFactors = FALSE)
sys_prompt <- paste(readLines("RCDome_distribution/board/RCD_Board_DeepSeek_Prompt.md", warn = FALSE), collapse = "\n")

# Show the first two PMIDs only, so a long list does not overwhelm the model.
trunc_pmids <- function(p) {
  ps <- strsplit(as.character(p), ";", fixed = TRUE)[[1]]
  ps <- ps[!is.na(ps) & ps != ""]
  if (length(ps) == 0) return("NA")
  if (length(ps) <= 2) return(paste(ps, collapse = ";"))
  paste0(paste(ps[1:2], collapse = ";"), "; +", length(ps) - 2, " more")
}
first_pmid <- function(p) strsplit(as.character(p), ";", fixed = TRUE)[[1]][1]

# Population: gene–entity pairs whose pmid_list is a REAL PMID (starts with a digit).
pop <- m[grepl("^[0-9]", m$pmid_list),
         c("gene_symbol", "rcd_form_canonical", "pmid_list", "cot_role",
           "cot_direction", "mechanistic_class", "evidence_tier")]
pop <- pop[!duplicated(paste(pop$gene_symbol, pop$rcd_form_canonical)), ]

set.seed(2026)
idx <- sample(seq_len(nrow(pop)), 50)
pass <- 0; total <- 0
failures <- character(0)

for (i in seq_along(idx)) {
  gr <- pop[idx[i], ]; g <- gr$gene_symbol; e <- gr$rcd_form_canonical
  dr <- dec[dec$rcd_form == e, ][1, ]
  if (nrow(dr) == 0) next
  gpmid <- first_pmid(gr$pmid_list); epmid <- dr$founding_pmid
  user_msg <- paste0(
    "Gene: ", g, "\nEntity: ", e, "\n",
    "RCDome database (", g, "-", e, "): role=", gr$cot_role,
    " direction=", gr$cot_direction, " mechanistic=", gr$mechanistic_class,
    " evidence_tier=", gr$evidence_tier, " PMID=", trunc_pmids(gr$pmid_list), "\n",
    "RCDome decoder (", e, "): operational_definition=", dr$operational_definition,
    "; founding_pmid=", epmid, "; category=", dr$category)

  body <- jsonlite::toJSON(list(model = "deepseek-chat", temperature = 0.7,
    messages = list(list(role = "system", content = sys_prompt),
                    list(role = "user", content = user_msg))), auto_unbox = TRUE)
  resp <- httr::POST("https://api.deepseek.com/v1/chat/completions",
    httr::add_headers(Authorization = paste("Bearer", api_key),
                      "Content-Type" = "application/json"),
    body = body, encode = "raw", httr::timeout(120))
  out <- jsonlite::fromJSON(httr::content(resp, "text", encoding = "UTF-8"))$choices$message$content[1]

  ok <- grepl(gpmid, out, fixed = TRUE) && grepl(epmid, out, fixed = TRUE)
  total <- total + 1
  if (ok) pass <- pass + 1 else failures <- c(failures, paste0(g, "-", e))
}

cat("n =", total, "| PASS =", pass, "| FAIL =", total - pass, "\n")
cat("success rate =", round(100 * pass / total, 1), "%\n")
bt <- binom.test(pass, total)
cat("exact binomial 95% CI =", round(100 * bt$conf.int[1], 1), "-", round(100 * bt$conf.int[2], 1), "%\n")
w <- prop.test(pass, total)
cat("Wilson 95% CI =", round(100 * w$conf.int[1], 1), "-", round(100 * w$conf.int[2], 1), "%\n")
if (length(failures)) cat("failures:", paste(failures, collapse = ", "), "\n")
