# ─── mod_bodymap.R ─────────────────────────────────────────────────────────
# Anatograma interativo: hover mostra o órgão; clique abre os grupos de doença.
#
# Dependências:
# install.packages(c("shiny", "plotly", "ggplot2", "ggpolypath"))
# remotes::install_github("jespermaag/gganatogram")

mod_bodymap_ui <- function(id) {
  ns <- shiny::NS(id)

  shiny::div(
    id = ns("bodymap_wrap"),
    class = "bodymap-wrap",

    shiny::tags$style(shiny::HTML(sprintf(
      "#%s .plotly .cursor-crosshair,
       #%s .plotly .cursor-pointer { cursor: pointer !important; }
       #%s .bodymap-info-card {
         max-width: 720px;
         margin: 10px auto 0 auto;
         padding: 12px 14px;
         border: 1px solid rgba(31, 58, 95, 0.14);
         border-radius: 12px;
         background: rgba(255,255,255,0.92);
         box-shadow: 0 4px 18px rgba(31, 58, 95, 0.06);
       }
       #%s .bodymap-organ-button {
         background: #f5f5f4;
         border: 1px solid #e7e5e4;
         padding: 4px 10px;
         border-radius: 14px;
         font-size: 11px;
         cursor: pointer;
         color: #0b1020;
       }
       #%s .bodymap-organ-button.is-selected {
         background: #0b1020;
         color: #ffffff;
         border-color: #0b1020;
       }",
      ns("bodymap_wrap"), ns("bodymap_wrap"), ns("bodymap_wrap"),
      ns("bodymap_wrap"), ns("bodymap_wrap")
    ))),

    plotly::plotlyOutput(ns("body_plot"), height = "500px"),
    shiny::uiOutput(ns("organ_buttons")),
    shiny::uiOutput(ns("disease_chips")),

    shiny::tags$p(
      style = paste0(
        "font-size:12px;color:var(--grey);text-align:center;",
        "margin-top:8px;"
      ),
      "Move the mouse over an organ to identify it. Click the organ to view its disease groups."
    )
  )
}


# Adiciona aos polígonos criados pelo gganatogram os metadados que o Plotly
# precisa para hover e clique. O nome real do órgão vem da coluna `id` das
# coordenadas anatômicas, e não da posição do mouse ou do número da camada.
add_bodymap_plotly_metadata <- function(gg, plot_df) {
  lookup <- plot_df[, c(
    "organ", "organ_label", "value", "group_label", "hover_text"
  )]

  lookup$organ <- normalize_organ(lookup$organ)

  for (i in seq_along(gg$layers)) {
    layer_data <- gg$layers[[i]]$data

    if (
      is.null(layer_data) ||
      !is.data.frame(layer_data) ||
      !("id" %in% names(layer_data))
    ) {
      next
    }

    organ_id <- normalize_organ(layer_data$id)
    matched <- match(organ_id, lookup$organ)

    # Camadas do contorno corporal também podem possuir `id`; elas não devem
    # disparar seleção de órgão.
    if (all(is.na(matched))) {
      next
    }

    layer_data$organ <- organ_id
    layer_data$organ_label <- lookup$organ_label[matched]
    layer_data$value <- lookup$value[matched]
    layer_data$group_label <- lookup$group_label[matched]
    layer_data$hover_text <- lookup$hover_text[matched]

    # Segurança para eventuais vértices sem correspondência.
    missing_label <- is.na(layer_data$organ_label)
    layer_data$organ_label[missing_label] <- format_organ_label(
      layer_data$organ[missing_label]
    )
    layer_data$value[is.na(layer_data$value)] <- 0
    layer_data$group_label[is.na(layer_data$group_label)] <- ""
    layer_data$hover_text[is.na(layer_data$hover_text)] <- paste0(
      "<b>", layer_data$organ_label[is.na(layer_data$hover_text)], "</b>"
    )

    gg$layers[[i]]$data <- layer_data

    extra_mapping <- ggplot2::aes(
      text = hover_text,
      key = organ,
      customdata = organ
    )

    gg$layers[[i]]$mapping[names(extra_mapping)] <- extra_mapping
  }

  gg
}


mod_bodymap_server <- function(
  id,
  counts_by_group = NULL,
  sex = "male",
  parent_session = NULL,
  disease_filter_input_id = "disease_filter"
) {
  shiny::moduleServer(id, function(input, output, session) {

    source_id <- session$ns("bodymap_plotly_source")
    selected_organ <- shiny::reactiveVal(NULL)

    anatogram_key <- if (identical(sex, "female")) {
      gganatogram::hgFemale_key
    } else {
      gganatogram::hgMale_key
    }

    default_counts <- shiny::reactive({
      tsv <- tryCatch(
        read.delim(
          "data/disease_terms.tsv",
          sep = "\t",
          stringsAsFactors = FALSE
        ),
        error = function(e) NULL
      )

      if (is.null(tsv) || !("group" %in% names(tsv))) {
        return(NULL)
      }

      tab <- table(tsv$group)
      stats::setNames(as.numeric(tab), names(tab))
    })

    counts_reactive <- shiny::reactive({
      if (!is.null(counts_by_group)) {
        vals <- counts_by_group()
        if (!is.null(vals) && length(vals) > 0) {
          return(vals)
        }
      }

      default_counts()
    })

    plot_data <- shiny::reactive({
      vals <- counts_reactive()
      shiny::req(vals, length(vals) > 0)
      build_bodymap_data(vals, anatogram_key)
    })

    output$body_plot <- plotly::renderPlotly({
      df <- plot_data()
      shiny::req(nrow(df) > 0)

      gg <- gganatogram::gganatogram(
        data = df,
        organism = "human",
        sex = sex,
        fill = "value",
        outline = TRUE,
        fillOutline = "#f5f5f4",

        # geom_polygon é convertido pelo ggplotly com maior previsibilidade do
        # que geom_polypath. Isso é essencial para hover e clique.
        ggplot2_only = TRUE
      ) +
        ggplot2::theme_void() +
        ggplot2::scale_fill_gradient(
          low = "#f7ede2",
          high = "#c2410c",
          name = "Evidence",
          guide = "none"
        ) +
        ggplot2::coord_fixed()

      gg <- add_bodymap_plotly_metadata(gg, df)

      widget <- plotly::ggplotly(
        gg,
        tooltip = "text",
        source = source_id,
        dynamicTicks = FALSE
      )

      # Faz o hover responder à área preenchida do órgão inteiro, e não apenas
      # aos vértices do polígono. Também remove o nome técnico da trace.
      for (i in seq_along(widget$x$data)) {
        trace <- widget$x$data[[i]]

        has_organ_key <- !is.null(trace$key) || !is.null(trace$customdata)
        is_filled_polygon <- !is.null(trace$fill) && !identical(trace$fill, "none")

        if (has_organ_key && is_filled_polygon) {
          trace$hoveron <- "fills"
          trace$hovertemplate <- "%{text}<extra></extra>"

          if (is.null(trace$customdata) && !is.null(trace$key)) {
            trace$customdata <- trace$key
          }
        } else {
          trace$hoverinfo <- "skip"
        }

        widget$x$data[[i]] <- trace
      }

      widget <- plotly::layout(
        widget,
        hovermode = "closest",
        dragmode = FALSE,
        showlegend = FALSE,
        margin = list(l = 0, r = 0, t = 4, b = 0),
        xaxis = list(
          visible = FALSE,
          fixedrange = TRUE,
          zeroline = FALSE,
          showgrid = FALSE
        ),
        yaxis = list(
          visible = FALSE,
          fixedrange = TRUE,
          zeroline = FALSE,
          showgrid = FALSE,
          scaleanchor = "x",
          scaleratio = 1
        ),
        hoverlabel = list(
          bgcolor = "#0b1020",
          bordercolor = "#0b1020",
          font = list(color = "#FFFFFF", size = 12)
        )
      )

      plotly::config(
        widget,
        displayModeBar = FALSE,
        responsive = TRUE,
        scrollZoom = FALSE
      )
    })

    # Clique direto sobre um órgão do anatograma.
    shiny::observeEvent(
      plotly::event_data("plotly_click", source = source_id),
      {
        event <- plotly::event_data("plotly_click", source = source_id)
        shiny::req(event)

        candidate <- NULL

        if (!is.null(event$customdata)) {
          candidate <- unlist(event$customdata, use.names = FALSE)
        }

        if ((is.null(candidate) || length(candidate) == 0) && !is.null(event$key)) {
          candidate <- unlist(event$key, use.names = FALSE)
        }

        candidate <- normalize_organ(candidate)
        candidate <- candidate[nzchar(candidate)]

        if (length(candidate) > 0) {
          selected_organ(candidate[[1]])
        }
      },
      ignoreInit = TRUE
    )

    # Botões mantidos como navegação alternativa e também para acessibilidade.
    output$organ_buttons <- shiny::renderUI({
      df <- plot_data()
      shiny::req(nrow(df) > 0)

      organs <- unique(df$organ[df$group_label != ""])
      if (length(organs) == 0) {
        return(NULL)
      }

      current <- selected_organ()

      shiny::div(
        style = paste0(
          "display:flex;gap:6px;justify-content:center;",
          "flex-wrap:wrap;margin-top:12px;"
        ),
        lapply(sort(organs), function(org) {
          selected_class <- if (identical(current, org)) " is-selected" else ""

          shiny::tags$button(
            type = "button",
            class = paste0("bodymap-organ-button", selected_class),
            onclick = sprintf(
              "Shiny.setInputValue('%s', '%s', {priority: 'event'})",
              session$ns("organ_click"),
              org
            ),
            format_organ_label(org)
          )
        })
      )
    })

    shiny::observeEvent(input$organ_click, {
      shiny::req(input$organ_click)
      selected_organ(normalize_organ(input$organ_click))
    })

    output$disease_chips <- shiny::renderUI({
      organ <- selected_organ()

      if (is.null(organ)) {
        return(shiny::tags$p(
          "Click an organ in the anatomical map.",
          style = paste0(
            "text-align:center;color:var(--grey);",
            "font-size:13px;margin-top:8px;"
          )
        ))
      }

      df <- plot_data()
      row <- df[df$organ == organ, , drop = FALSE]
      groups <- groups_for_organ(organ)

      organ_label <- if (nrow(row) > 0) {
        row$organ_label[[1]]
      } else {
        format_organ_label(organ)
      }

      evidence_value <- if (nrow(row) > 0) {
        row$value[[1]]
      } else {
        0
      }

      chip_ui <- if (length(groups) == 0) {
        shiny::tags$p(
          "No disease group is mapped to this organ.",
          style = "margin:6px 0 0 0;color:var(--grey);font-size:13px;"
        )
      } else {
        shiny::div(
          style = paste0(
            "display:flex;gap:6px;justify-content:center;",
            "flex-wrap:wrap;margin-top:8px;"
          ),
          lapply(groups, function(group_name) {
            shiny::tags$button(
              type = "button",
              onclick = sprintf(
                "Shiny.setInputValue('%s', '%s', {priority: 'event'})",
                session$ns("chip_click"),
                group_name
              ),
              style = paste0(
                "background:#0b1020;color:white;padding:5px 12px;",
                "border-radius:20px;font-size:12px;border:none;",
                "cursor:pointer;"
              ),
              group_name
            )
          })
        )
      }

      shiny::div(
        class = "bodymap-info-card",
        style = "text-align:center;",
        shiny::tags$div(
          style = "font-size:16px;font-weight:700;color:#0b1020;",
          organ_label
        ),
        shiny::tags$div(
          style = "font-size:12px;color:var(--grey);margin-top:2px;",
          paste0("Evidence: ", format(
            evidence_value,
            trim = TRUE,
            scientific = FALSE
          ))
        ),
        chip_ui
      )
    })

    shiny::observeEvent(input$chip_click, {
      group_name <- input$chip_click

      if (
        !is.null(parent_session) &&
        !is.null(group_name) &&
        nzchar(group_name)
      ) {
        shiny::updateSelectizeInput(
          parent_session,
          disease_filter_input_id,
          selected = group_name
        )

        shiny::updateNavbarPage(
          parent_session,
          "main_nav",
          selected = "Evidence"
        )
      }
    })
  })
}
