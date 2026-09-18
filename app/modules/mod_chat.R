# ─── Module: chat ────────────────────────────────────────────────────────────
# Chat interface that discusses gene x RCD literature findings with DeepSeek.
# Layout inspired by ChatGPT (centered column, avatar-less user bubbles,
# borderless assistant text, pill composer, typing dots, auto-scroll,
# Enter-to-send) — RAG / "clean context" logic unchanged.

mod_chat_ui <- function(id) {
  ns <- NS(id)

  tagList(
    div(
      class = "rcdchat-shell",

      # ── Top bar ──────────────────────────────────────────────────────
      div(
        class = "rcdchat-topbar",
        div(
          class = "rcdchat-title-group",
          div(class = "rcdchat-mark", "RC"),
          div(
            div(class = "rcdchat-title", "RCDchat"),
            uiOutput(ns("context_badge"))
          )
        ),
        actionButton(ns("chat_clear"), HTML("+&nbsp;New chat"),
                     class = "rcdchat-newchat-btn")
      ),

      # ── Messages ─────────────────────────────────────────────────────
      div(
        id = ns("rcdchat_scroll"),
        class = "rcdchat-scroll",
        uiOutput(ns("chat_ui"))
      ),

      # ── Composer ─────────────────────────────────────────────────────
      div(
        class = "rcdchat-composer",
        div(
          class = "rcdchat-input-shell",
          tags$textarea(
            id = ns("chat_input"),
            class = "form-control rcdchat-textarea",
            rows = "1",
            placeholder = "Ask about the findings..."
          ),
          actionButton(ns("chat_send"), HTML("&#8593;"),
                       class = "rcdchat-send-btn")
        ),
        div(class = "rcdchat-hint", "RCDchat answers based only on loaded articles. Enter to send, Shift+Enter for new line.")
      )
    ),

    # ── Client-side behavior (Enter-to-send, auto-grow, auto-scroll) ────
    tags$script(HTML(sprintf("
      (function() {
        var inputId  = '%s';
        var sendId   = '%s';
        var scrollId = '%s';
        var outputId = '%s';

        function growTextarea(el) {
          el.style.height = 'auto';
          el.style.height = Math.min(el.scrollHeight, 160) + 'px';
        }

        $(document).on('input', '#' + inputId, function() { growTextarea(this); });

        $(document).on('keydown', '#' + inputId, function(e) {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            $('#' + sendId).trigger('click');
          }
        });

        function scrollToBottom() {
          var el = document.getElementById(scrollId);
          if (el) el.scrollTop = el.scrollHeight;
        }

        $(document).on('shiny:value', function(ev) {
          if (ev.name === outputId) {
            setTimeout(scrollToBottom, 30);
            var ta = document.getElementById(inputId);
            if (ta) { ta.value = ''; ta.style.height = 'auto'; }
          }
        });
      })();
    ", ns("chat_input"), ns("chat_send"), ns("rcdchat_scroll"), ns("chat_ui"))))
  )
}

mod_chat_server <- function(id, context_reactive) {
  moduleServer(id, function(input, output, session) {
    ns <- session$ns

    messages <- reactiveVal(list())
    free_mode <- reactiveVal(FALSE)

    # Auto-enter free mode if no gene context (user came directly to RCDchat)
    observe({
      ctx <- context_reactive()
      if (is.null(ctx) || length(ctx) == 0) {
        free_mode(TRUE)
        all <- load_all_papers()
        n_papers <- length(all)
        welcome <- paste0(
          "RCDchat — Global mode\n",
          "I can answer questions about Regulated Cell Death based on ", n_papers,
          " articles in our database. For gene-specific evidence in a particular RCD pathway, ",
          "first search a gene in the Evidence tab, then click Open in RCDchat."
        )
        messages(list(list(role = "assistant", content = welcome)))
      }
    })

    # When gene context arrives from Evidence -> switch to gene mode
    observeEvent(context_reactive(), {
      ctx <- context_reactive()
      if (is.null(ctx) || length(ctx) == 0) return()
      free_mode(FALSE)
      gene <- ctx$gene %||% "unknown"
      n_claims <- ctx$n_claims %||% 0
      n_pathways <- ctx$n_pathways %||% 0
      welcome <- sprintf(
        "%s: %d verified claims across %d RCD pathways. Ask about evidence, mechanisms, or therapeutic implications.",
        gene, n_claims, n_pathways
      )
      messages(list(list(role = "assistant", content = welcome)))
    })

    # Clear button ("+ Novo chat") — switch to free mode (all downloaded papers)
    observeEvent(input$chat_clear, {
      free_mode(TRUE)
      all <- load_all_papers()
      n_papers <- length(all)
      welcome <- sprintf(
        "Free mode: %d articles available across all genes and pathways. Ask anything about RCD literature.",
        n_papers
      )
      messages(list(list(role = "assistant", content = welcome)))
    })

    # Context badge (mode indicator, top bar)
    output$context_badge <- renderUI({
      ctx <- context_reactive()
      if (isTRUE(free_mode()) || is.null(ctx) || length(ctx) == 0) {
        tags$div(class = "rcdchat-badge", "Free mode \u00b7 all articles")
      } else {
        gene <- ctx$gene %||% "?"
        tags$div(class = "rcdchat-badge rcdchat-badge-gene", paste0("Context: ", gene))
      }
    })

    observeEvent(input$chat_send, {
      txt <- trimws(input$chat_input)
      if (is.null(txt) || txt == "") return()
      if (!isTRUE(free_mode()) && (is.null(context_reactive()) || length(context_reactive()) == 0)) return()

      ctx <- context_reactive()
      api_key <- Sys.getenv("DEEPSEEK_API_KEY", unset = "")

      msgs <- messages()
      msgs[[length(msgs) + 1]] <- list(role = "user", content = txt)
      messages(msgs)

      # Build context
      if (isTRUE(free_mode())) {
        papers <- load_all_papers()
      } else {
        papers <- load_papers_for_gene(ctx$gene)
      }

      if (length(papers) > 0) {
        n_full <- sum(sapply(papers, function(p) isTRUE(p$is_full)))
        papers_txt <- paste(lapply(papers, function(p) {
          content <- if (nchar(p$content) > 8000) paste0(substr(p$content, 1, 8000), "...[truncated]") else p$content
          label <- if (isTRUE(p$is_full)) "FULL TEXT" else "ABSTRACT ONLY"
          paste0("## ", p$pathway, " — PMID:", p$pmid, " [", label, "]\n", content)
        }), collapse = "\n\n---\n\n")
        context_msg <- paste0(
          "CONTEXT (", n_full, " full-text, ", length(papers) - n_full, " abstract-only):\n", papers_txt
        )
      } else {
        # Fallback: use claims
        claims_txt <- paste(lapply(names(ctx$pathways), function(pw) {
          entry <- ctx$pathways[[pw]]
          if (length(entry$claims) == 0) return("")
          header <- paste0("## ", pw)
          body <- paste(lapply(entry$claims, function(cl) {
            ref <- if (!is.na(cl$pmid) && cl$pmid != "") paste0("PMID:", cl$pmid)
                   else if (!is.na(cl$doi) && cl$doi != "") paste0("DOI:", cl$doi)
                   else paste0("Title: ", substr(cl$title, 1, 60))
            paste0("- ", cl$claim, " [", cl$evidence_type %||% "unspecified", "] (", ref, ")")
          }), collapse = "\n")
          synth <- if (!is.null(entry$synthesis) && nzchar(entry$synthesis))
            paste0("Synthesis: ", entry$synthesis) else ""
          paste(header, body, synth, sep = "\n")
        }), collapse = "\n\n")
        context_msg <- paste0(
          "CONTEXT (article abstracts from literature search):\n", claims_txt
        )
      }

      prompt <- list(
        list(role = "system", content = paste0(
          "You are a scientific assistant specialized in oncology and regulated cell death. ",
          "You are discussing findings about gene ", ctx$gene, " with a researcher.\n\n",
          context_msg, "\n\n",
          "RULES:\n",
          "- Answer ONLY based on the context provided above. Do not use external knowledge.\n",
          "- If the question cannot be answered from the context, say so honestly.\n",
          "- Cite PMIDs when referencing specific claims.\n",
          "- Be concise and precise. Use bullet points with dashes for multiple findings.\n",
          "- Never use markdown formatting (no **bold**, no *italic*). Use plain text only.\n",
          "- Never make clinical recommendations."
        )),
        list(role = "user", content = txt)
      )

      # Show typing indicator (rendered as animated dots, see chat_ui below)
      msgs <- messages()
      msgs[[length(msgs) + 1]] <- list(role = "assistant", content = "__typing__")
      messages(msgs)

      # Call DeepSeek using the same wrapper as Evidence (no JSON mode — free text)
      reply <- tryCatch({
        resp <- httr::POST(
          "https://api.deepseek.com/v1/chat/completions",
          httr::add_headers(
            Authorization = paste("Bearer", api_key),
            "Content-Type" = "application/json"
          ),
          body = jsonlite::toJSON(list(
            model = "deepseek-chat", messages = prompt, temperature = 0.3
          ), auto_unbox = TRUE),
          encode = "raw"
        )
        status <- httr::status_code(resp)
        body   <- httr::content(resp, "text", encoding = "UTF-8")
        if (status != 200) {
          paste0("Error: DeepSeek HTTP ", status)
        } else {
          parsed <- jsonlite::fromJSON(body)
          parsed$choices$message$content[1]
        }
      }, error = function(e) paste0("Error: ", conditionMessage(e)))

      # Replace typing indicator with real reply
      msgs <- messages()
      # Strip markdown bold and convert to HTML
      reply <- gsub("\\*\\*(.+?)\\*\\*", "<strong>\\1</strong>", reply, perl = TRUE)
      # Make PMIDs clickable
      reply <- gsub("PMID:(\\d+)", "<a href='https://pubmed.ncbi.nlm.nih.gov/\\1' target='_blank'>PMID:\\1</a>", reply, perl = TRUE)
      # Make DOIs clickable — exclude trailing punctuation
      reply <- gsub("DOI:([^\\s]+[^\\s.,;:!?)\"'])", "<a href='https://doi.org/\\1' target='_blank'>DOI:\\1</a>", reply, perl = TRUE)
      msgs[[length(msgs)]] <- list(role = "assistant", content = reply)
      messages(msgs)
    })

    # Render chat messages
    output$chat_ui <- renderUI({
      msgs <- messages()
      if (length(msgs) == 0) {
        return(tags$div(
          class = "rcdchat-empty",
          "Search a gene in Evidence and click 'Open in RCDchat', or click '+ New chat' to chat freely about all downloaded papers."
        ))
      }

      lapply(msgs, function(m) {
        is_user <- m$role == "user"
        is_typing <- identical(m$content, "__typing__")

        if (is_user) {
          tags$div(
            class = "rcdchat-row rcdchat-row-user",
            tags$div(class = "rcdchat-bubble-user", HTML(gsub("\n", "<br>", htmltools::htmlEscape(m$content))))
          )
        } else {
          tags$div(
            class = "rcdchat-row rcdchat-row-assistant",
            tags$div(class = "rcdchat-avatar", "RC"),
            if (is_typing) {
              tags$div(
                class = "rcdchat-typing",
                tags$span(class = "dot"), tags$span(class = "dot"), tags$span(class = "dot")
              )
            } else {
              tags$div(class = "rcdchat-assistant-text", HTML(gsub("\n", "<br>", htmltools::htmlEscape(m$content))))
            }
          )
        }
      })
    })

  })
}
