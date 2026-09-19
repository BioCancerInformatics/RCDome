# RCDome — T06 context-fidelity benchmark (reproducible)
# Purpose: verify the Board synthesis does NOT contradict the structured payload
# now that role/direction/mechanistic/tier/required_for_death/PMID are fed into the context.
# Result (run 2026-09-18): n=30, 30/30 no-contradiction, 100% (95% CI 88.4–100%).

renv <- readLines("RCDome_distribution/.Renviron", warn = FALSE)
api_key <- sub("^DEEPSEEK_API_KEY=", "", renv[grep("DEEPSEEK_API_KEY", renv)][1])
m <- readRDS("RCDome_distribution/data/unified_gene_rcd_matrix_V026.rds")
dec <- read.csv("RCDome_distribution/data/RCDome_Decoder_53.csv", stringsAsFactors = FALSE)
sys_prompt <- paste(readLines("RCDome_distribution/board/RCD_Board_DeepSeek_Prompt.md", warn = FALSE), collapse = "\n")

trunc_pmids <- function(p) {
  ps <- strsplit(as.character(p), ";", fixed = TRUE)[[1]]
  ps <- ps[!is.na(ps) & ps != ""]
  if (length(ps) <= 2) return(paste(ps, collapse = ";"))
  paste0(paste(ps[1:2], collapse = ";"), "; +", length(ps) - 2, " more")
}

# Population: pairs with a REAL role + direction + PMID (a "no direction/role" phrase would be a contradiction).
pop <- m[m$cot_role %in% c("EXECUTOR", "REGULATOR", "MARKER") &
         m$cot_direction %in% c("PROMOTES", "PROTECTS") &
         grepl("^[0-9]", m$pmid_list),
         c("gene_symbol", "rcd_form_canonical", "pmid_list", "cot_role", "cot_direction",
           "mechanistic_class", "evidence_tier", "confidence_tier", "required_for_death")]
pop <- pop[!duplicated(paste(pop$gene_symbol, pop$rcd_form_canonical)), ]

set.seed(7)
idx <- sample(seq_len(nrow(pop)), 30)
pass <- 0; total <- 0

for (i in seq_along(idx)) {
  gr <- pop[idx[i], ]; g <- gr$gene_symbol; e <- gr$rcd_form_canonical
  dr <- dec[dec$rcd_form == e, ][1, ]
  if (nrow(dr) == 0) next
  user_msg <- paste0(
    "Gene: ", g, "\nEntity: ", e, "\n",
    "RCDome database (", g, "-", e, "): role=", gr$cot_role, " direction=", gr$cot_direction,
    " mechanistic=", gr$mechanistic_class, " evidence_tier=", gr$evidence_tier,
    " confidence_tier=", gr$confidence_tier, " required_for_death=", gr$required_for_death,
    " PMID=", trunc_pmids(gr$pmid_list), "\n",
    "RCDome decoder (", e, "): operational_definition=", dr$operational_definition,
    "; founding_pmid=", dr$founding_pmid)
  body <- jsonlite::toJSON(list(model = "deepseek-chat", temperature = 0.7,
    messages = list(list(role = "system", content = sys_prompt),
                    list(role = "user", content = user_msg))), auto_unbox = TRUE)
  resp <- httr::POST("https://api.deepseek.com/v1/chat/completions",
    httr::add_headers(Authorization = paste("Bearer", api_key),
                      "Content-Type" = "application/json"),
    body = body, encode = "raw", httr::timeout(120))
  out <- jsonlite::fromJSON(httr::content(resp, "text", encoding = "UTF-8"))$choices$message$content[1]
  low <- tolower(out)

  # Field-specific contradiction check (do NOT flag "mechanistic not specified" unless it IS MECHANISTIC).
  contradiction <- FALSE
  if (grepl("no direction|direction is not specified|no mechanistic direction", low) &&
      gr$cot_direction %in% c("PROMOTES", "PROTECTS")) contradiction <- TRUE
  if (grepl("no role|role is not specified|no functional role", low) &&
      gr$cot_role %in% c("EXECUTOR", "REGULATOR", "MARKER")) contradiction <- TRUE
  if (grepl("no requirement for death|not required for death", low) &&
      !is.na(gr$required_for_death) && gr$required_for_death == "YES") contradiction <- TRUE
  if (grepl("no mechanistic|mechanistic basis is not specified|not mechanistically", low) &&
      !is.na(gr$mechanistic_class) && gr$mechanistic_class == "MECHANISTIC") contradiction <- TRUE

  total <- total + 1
  if (!contradiction) pass <- pass + 1
}

cat("n =", total, "| no-contradiction =", pass, "| contradiction =", total - pass, "\n")
cat("success rate =", round(100 * pass / total, 1), "%\n")
bt <- binom.test(pass, total)
cat("exact 95% CI =", round(100 * bt$conf.int[1], 1), "-", round(100 * bt$conf.int[2], 1), "%\n")
