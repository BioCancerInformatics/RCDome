# ─── DeepSeek API — robust scientific extraction and verification ────────────

DEEPSEEK_URL <- "https://api.deepseek.com/v1/chat/completions"

first_nonempty <- function(...) {
  values <- list(...)
  for (x in values) {
    if (is.null(x) || length(x) == 0) next
    x <- as.character(x[[1]])
    if (!is.na(x) && nzchar(trimws(x))) return(trimws(x))
  }
  ""
}

strip_json_fences <- function(x) {
  x <- trimws(as.character(x %||% ""))
  x <- sub("^```(?:json)?\\s*", "", x, perl = TRUE, ignore.case = TRUE)
  x <- sub("\\s*```$", "", x, perl = TRUE)
  trimws(x)
}

call_deepseek <- function(messages, api_key, model = "deepseek-chat") {
  if (is.null(api_key) || !nzchar(trimws(api_key))) stop("DeepSeek API key is empty.", call. = FALSE)
  resp <- httr::POST(DEEPSEEK_URL,
    httr::add_headers("Authorization" = paste("Bearer", api_key), "Content-Type" = "application/json"),
    body = jsonlite::toJSON(list(model = model, messages = messages, temperature = 0,
          response_format = list(type = "json_object")), auto_unbox = TRUE, null = "null"),
    encode = "raw", httr::timeout(60))
  status <- httr::status_code(resp)
  body <- httr::content(resp, "text", encoding = "UTF-8")
  if (status != 200) stop(sprintf("DeepSeek HTTP %d: %s", status, substr(body, 1, 500)), call. = FALSE)
  parsed <- jsonlite::fromJSON(body, simplifyVector = FALSE)
  text <- tryCatch(parsed$choices[[1]]$message$content, error = function(e) NULL)
  if (is.null(text) || !nzchar(trimws(text))) stop("DeepSeek returned an empty response.", call. = FALSE)
  json_text <- strip_json_fences(text)
  tryCatch(jsonlite::fromJSON(json_text, simplifyVector = FALSE),
    error = function(e) stop(paste0("DeepSeek invalid JSON: ", conditionMessage(e), " | ", substr(json_text, 1, 300)), call. = FALSE))
}

extract_claims <- function(article, gene, pathway_name, api_key) {
  title <- first_nonempty(article$title)
  abstract <- first_nonempty(article$abstract)
  if (!nzchar(title) && !nzchar(abstract)) return(list(claims = list()))
  pathway_terms <- if (exists("get_pathway_terms", mode = "function")) get_pathway_terms(pathway_name) else pathway_name
  schema <- '{"claims":[{"claim":"concise scientific claim","supporting_sentence":"verbatim support copied from the article","evidence_type":"functional_study_cell_line|functional_study_animal|correlation_human_tissue|clinical_study|review_mechanistic|review_hypothesis|other","relation_type":"direct|mechanistic|indirect"}]}'
  messages <- list(
    list(role = "system", content = paste0(
      "You are a rigorous biomedical evidence extractor.\n",
      "Target gene: ", gene, "\nTarget cell-death pathway: ", pathway_name, "\n",
      "Recognized pathway wording: ", paste(pathway_terms, collapse = ", "), "\n\n",
      "Extract a claim when the supplied title or abstract supports a relationship ",
      "between the target gene and the target pathway. Accept both: ",
      "(1) direct regulation and (2) a clearly described mechanistic chain in which ",
      "the gene, gene-containing complex, fusion, inhibition, activation, release, ",
      "or restoration changes the pathway outcome.\n",
      "The supporting_sentence field must be copied verbatim from the supplied text. ",
      "It may contain one to three consecutive sentences when the mechanism spans ",
      "adjacent sentences. Do not paraphrase.\n",
      "Do not use outside knowledge. Review articles are allowed, but label them.\n",
      "If there is no supported relationship, return exactly {\"claims\":[]}.\n",
      "Return JSON only, using exactly this schema: ", schema)),
    list(role = "user", content = paste0(
      "PMID: ", first_nonempty(article$pmid, "N/A"), "\nTitle: ", title, "\n\nAbstract:\n", abstract)))
  out <- call_deepseek(messages, api_key)
  if (is.null(out$claims)) out$claims <- list()
  out
}

verify_claim <- function(claim, sentence, api_key) {
  claim <- first_nonempty(claim)
  sentence <- first_nonempty(sentence)
  if (!nzchar(claim) || !nzchar(sentence)) return(list(verdict = "NOT_SUPPORTED", reason = "Missing claim or support text."))
  messages <- list(
    list(role = "system", content = paste0(
      "You are a biomedical claim verifier. Judge only the supplied claim and ",
      "supporting passage. A claim is SUPPORTED when the passage directly states it ",
      "or provides an explicit mechanistic chain that entails it.\n",
      "Use NOT_SUPPORTED when the passage contradicts or does not contain the relationship. ",
      "Use AMBIGUOUS when plausible but not established by the passage.\n",
      'Return JSON only: {"verdict":"SUPPORTED|NOT_SUPPORTED|AMBIGUOUS","reason":"brief reason"}')),
    list(role = "user", content = paste0("Claim:\n", claim, "\n\nSupporting passage:\n", sentence)))
  call_deepseek(messages, api_key)
}

synthesize_pathway <- function(gene, pathway_name, claims, api_key, disease = "All") {
  if (length(claims) == 0) return(list(summary = NULL))
  claim_text <- vapply(seq_along(claims), function(i) {
    cl <- claims[[i]]
    paste0(i, ". Claim: ", first_nonempty(cl$claim), "\nSupport: ",
           first_nonempty(cl$supporting_sentence, cl$sentence), "\n",
           "Article: ", first_nonempty(cl$title), "\nPMID: ", first_nonempty(cl$pmid, "N/A"))
  }, character(1))
  messages <- list(
    list(role = "system", content = paste0(
      "Write a concise, evidence-bounded biomedical synthesis. Use only the verified ",
      "claims supplied by the user. Distinguish direct experimental evidence from ",
      "review-level mechanistic interpretation. Do not add external facts, clinical ",
      "recommendations, or stronger causal language than the evidence supports. ",
      'Return JSON only: {"summary":"one concise paragraph"}.')),
    list(role = "user", content = paste0("Gene: ", gene, "\nCell-death pathway: ", pathway_name,
      "\nDisease context: ", disease, "\n\n", paste(claim_text, collapse = "\n\n"))))
  call_deepseek(messages, api_key)
}
