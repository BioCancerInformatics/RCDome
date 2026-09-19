# RCDome — HELD-OUT benchmark (2026-09-19) — reproducible
# Purpose: validate generalization to unseen cases (Victor §23). Fresh seed, excludes dev cases.
# Dev sets: reference-discipline seed=2026, T06 seed=7. Held-out seed = 20260919, n = 100 each.

renv <- readLines("RCDome_distribution/.Renviron", warn = FALSE)
api_key <- sub("^DEEPSEEK_API_KEY=", "", renv[grep("DEEPSEEK_API_KEY", renv)][1])
m <- readRDS("RCDome_distribution/data/unified_gene_rcd_matrix_V026.rds")
dec <- read.csv("RCDome_distribution/data/RCDome_Decoder_53.csv", stringsAsFactors = FALSE)
sys_prompt <- paste(readLines("RCDome_distribution/board/RCD_Board_DeepSeek_Prompt.md", warn = FALSE), collapse = "\n")

trunc_pmids <- function(p) {
  ps <- strsplit(as.character(p), ";", fixed = TRUE)[[1]]
  ps <- ps[!is.na(ps) & ps != ""]
  if (length(ps) == 0) return("NA")
  if (length(ps) <= 2) return(paste(ps, collapse = ";"))
  paste0(paste(ps[1:2], collapse = ";"), "; +", length(ps) - 2, " more")
}
first_pmid <- function(p) strsplit(as.character(p), ";", fixed = TRUE)[[1]][1]

call_llm <- function(user_msg) {
  body <- jsonlite::toJSON(list(model = "deepseek-chat", temperature = 0.7,
    messages = list(list(role = "system", content = sys_prompt),
                    list(role = "user", content = user_msg))), auto_unbox = TRUE)
  resp <- httr::POST("https://api.deepseek.com/v1/chat/completions",
    httr::add_headers(Authorization = paste("Bearer", api_key),
                      "Content-Type" = "application/json"),
    body = body, encode = "raw", httr::timeout(120))
  jsonlite::fromJSON(httr::content(resp, "text", encoding = "UTF-8"))$choices$message$content[1]
}

# ── held-out sampling: exclude the dev indices ──
heldout_idx <- function(pop, dev_seed, dev_n, seed = 20260919, n = 100) {
  set.seed(dev_seed)
  dev <- sample(seq_len(nrow(pop)), dev_n)
  set.seed(seed)
  cand <- sample(setdiff(seq_len(nrow(pop)), dev))
  cand[seq_len(min(n, length(cand)))]
}

cat("===== HELD-OUT 1: Reference discipline (gene PMID vs entity PMID) =====\n")
pop1 <- m[grepl("^[0-9]", m$pmid_list),
          c("gene_symbol", "rcd_form_canonical", "pmid_list", "cot_role",
            "cot_direction", "mechanistic_class", "evidence_tier")]
pop1 <- pop1[!duplicated(paste(pop1$gene_symbol, pop1$rcd_form_canonical)), ]
idx <- heldout_idx(pop1, dev_seed = 2026, dev_n = 100, seed = 20260919, n = 100)
pass <- 0; total <- 0; failures <- character(0)
for (i in idx) {
  gr <- pop1[i, ]; g <- gr$gene_symbol; e <- gr$rcd_form_canonical
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
  out <- call_llm(user_msg)
  ok <- grepl(gpmid, out, fixed = TRUE) && grepl(epmid, out, fixed = TRUE)
  total <- total + 1
  if (ok) pass <- pass + 1 else failures <- c(failures, paste0(g, "-", e))
}
cat("HELD-OUT 1: n =", total, "| PASS =", pass, "| FAIL =", total - pass, "\n")
if (total > 0) {
  bt <- binom.test(pass, total)
  cat("  rate =", round(100*pass/total,1), "% | exact binomial 95% CI =",
      round(100*bt$conf.int[1],1), "-", round(100*bt$conf.int[2],1), "%\n")
}
if (length(failures)) cat("  failures:", paste(failures, collapse=", "), "\n")

cat("\n===== HELD-OUT 2: T06 context fidelity (no payload contradiction) =====\n")
pop2 <- m[m$cot_role %in% c("EXECUTOR","REGULATOR","MARKER") &
          m$cot_direction %in% c("PROMOTES","PROTECTS") &
          grepl("^[0-9]", m$pmid_list),
          c("gene_symbol","rcd_form_canonical","pmid_list","cot_role","cot_direction",
            "mechanistic_class","evidence_tier","confidence_tier","required_for_death")]
pop2 <- pop2[!duplicated(paste(pop2$gene_symbol, pop2$rcd_form_canonical)), ]
idx2 <- heldout_idx(pop2, dev_seed = 7, dev_n = 100, seed = 20260919, n = 100)
pass2 <- 0; total2 <- 0; failures2 <- character(0)
for (i in idx2) {
  gr <- pop2[i, ]; g <- gr$gene_symbol; e <- gr$rcd_form_canonical
  dr <- dec[dec$rcd_form == e, ][1, ]
  if (nrow(dr) == 0) next
  payload <- paste0("role=", gr$cot_role, "; direction=", gr$cot_direction,
                    "; mechanistic=", gr$mechanistic_class, "; tier=", gr$evidence_tier,
                    "; required_for_death=", gr$required_for_death, "; PMID=", trunc_pmids(gr$pmid_list))
  user_msg <- paste0("Gene: ", g, "\nEntity: ", e, "\nRCDome structured payload: ", payload,
                     "\nDo NOT contradict this payload in your answer.")
  out <- call_llm(user_msg)
  low <- tolower(out)
  contradiction <- FALSE
  if (grepl("no direction|direction is not specified|no mechanistic direction", low) &&
      gr$cot_direction %in% c("PROMOTES", "PROTECTS")) contradiction <- TRUE
  if (grepl("no role|role is not specified|no functional role", low) &&
      gr$cot_role %in% c("EXECUTOR", "REGULATOR", "MARKER")) contradiction <- TRUE
  if (grepl("no requirement for death|not required for death", low) &&
      !is.na(gr$required_for_death) && gr$required_for_death == "YES") contradiction <- TRUE
  if (grepl("no mechanistic|mechanistic basis is not specified|not mechanistically", low) &&
      !is.na(gr$mechanistic_class) && gr$mechanistic_class == "MECHANISTIC") contradiction <- TRUE
  ok2 <- !contradiction
  total2 <- total2 + 1
  if (ok2) pass2 <- pass2 + 1 else failures2 <- c(failures2, paste0(g, "-", e))
}
cat("HELD-OUT 2: n =", total2, "| no-contradiction =", pass2, "| contradictions =", total2 - pass2, "\n")
if (total2 > 0) {
  bt2 <- binom.test(pass2, total2)
  cat("  rate =", round(100*pass2/total2,1), "% | exact binomial 95% CI =",
      round(100*bt2$conf.int[1],1), "-", round(100*bt2$conf.int[2],1), "%\n")
}
if (length(failures2)) cat("  contradictions:", paste(failures2, collapse=", "), "\n")
