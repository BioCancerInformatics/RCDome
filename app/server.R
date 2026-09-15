# ─── Server ──────────────────────────────────────────────────────────────────
if (!exists("genes_df", inherits = TRUE) || !exists("fingerprint_df", inherits = TRUE)) source("global.R")

server <- function(input, output, session) {

  # ── Global not-found pop-up: a value typed into any scroll-down that matches
  #    no option triggers this centered pop-up (value is never added). ──
  observeEvent(input$rcdome_not_found, {
    v <- input$rcdome_not_found
    if (is.null(v) || !nzchar(v)) return()
    showModal(modalDialog(
      title = "Not in the RCDome compilation",
      tags$p(paste0("RCD ", htmltools::htmlEscape(v), " is not present in the RCDome compilation.")),
      size = "m", easyClose = TRUE,
      footer = modalButton("Close")
    ))
  }, ignoreNULL = TRUE)

  # ── Home tab: always reload the landing page iframe ─────────────────
  observeEvent(input$main_nav, {
    if (isTRUE(input$main_nav == "Home")) {
      shinyjs::runjs('document.getElementById("home_iframe").src = "landing_page.html";')
    }
  })

  # ── Network module (Aba Network) ────────────────────────────────────
  mod_network_server("network", genes_df, signatures_df)

  # ── RCD Grid module (Aba RCD Pathways) ──────────────────────────────
  mod_rcd_grid_server("rcd_grid")

  # ── Operational Definitions module ──────────────────────────────
  mod_od_server("od")

  # ── Operational Definition Comparator module ──────────────────────
  mod_od_compare_server("od_compare")

  # ── Omic module (Aba Omic) ──────────────────────────────────────
  mod_gene_catalog_server("gene_catalog")

  # ── Chat module (RCDchat tab) — standalone (context wired to V026 later) ──
  # ── Digital Molecular RCD Board (synthesis) + nested RCDome Q&A AI submodule ──
  board_reactive <- reactiveVal(NULL)
  mod_board_server("board", board_reactive)

  # ── Pathway Fingerprint ─────────────────────────────────────────────
  output$fingerprint_plot <- renderPlotly({
    df <- fingerprint_df

    shiny::validate(shiny::need(nrow(df) > 0, "No RCD entity data available."))

    df <- df[order(df$total, df$pathway), , drop = FALSE]

    custom_data <- lapply(seq_len(nrow(df)), function(i) {
      as.numeric(c(
        df$total[i], df$Exclusive[i], df$Shared[i],
        df$databases[i], df$references[i]
      ))
    })

    p <- plot_ly(
      data = df,
      x = ~Exclusive,
      y = ~pathway,
      type = "bar",
      orientation = "h",
      name = "Exclusive",
      customdata = custom_data,
      marker = list(color = "#0b1020", line = list(width = 0)),
      textposition = "none",
      hovertemplate = paste0(
        "<b>%{y}</b><br>",
        "Exclusive genes: %{x}<br>",
        "Total genes: %{customdata[0]}<br>",
        "Databases: %{customdata[3]}<br>",
        "References: %{customdata[4]}",
        "<extra></extra>"
      ),
      source = "fingerprint"
    ) %>%
      add_trace(
        x = ~Shared,
        y = ~pathway,
        customdata = custom_data,
        name = "Shared",
        marker = list(color = "#e7e5e4", line = list(width = 0)),
        textposition = "none",
        hovertemplate = paste0(
          "<b>%{y}</b><br>",
          "Shared genes: %{x}<br>",
          "Total genes: %{customdata[0]}<br>",
          "Databases: %{customdata[3]}<br>",
          "References: %{customdata[4]}",
          "<extra></extra>"
        )
      ) %>%
      layout(
        barmode = "stack",
        bargap = 0.24,
        transition = list(duration = 380, easing = "cubic-in-out"),
        xaxis = list(
          title = "",
          showgrid = TRUE,
          gridcolor = "#e7e5e4",
          zeroline = FALSE,
          rangemode = "tozero",
          fixedrange = TRUE
        ),
        yaxis = list(
          title = "",
          showgrid = FALSE,
          automargin = TRUE,
          fixedrange = TRUE,
          categoryorder = "array",
          categoryarray = df$pathway,
          tickfont = list(size = 10)
        ),
        margin = list(l = 205, r = 24, t = 14, b = 72),
        legend = list(
          orientation = "h",
          x = 0.5, y = -0.16,
          xanchor = "center", yanchor = "top"
        ),
        font = list(family = "Segoe UI", color = "#1c1917", size = 12),
        hoverlabel = list(font = list(family = "Segoe UI", size = 13)),
        hovermode = "closest",
        paper_bgcolor = "#FFFFFF",
        plot_bgcolor = "#FFFFFF",
        uirevision = "fingerprint-v2"
      ) %>%
      config(
        displayModeBar = FALSE,
        responsive = TRUE,
        doubleClick = FALSE
      )

    p <- htmlwidgets::onRender(p, "
      function(el, x) {
        var gd = el;
        if (!gd || !gd.data || gd.data.length < 2) return;

        if (gd._fingerprintInitialized) return;
        gd._fingerprintInitialized = true;

        if (!document.getElementById('fingerprint-click-style')) {
          var style = document.createElement('style');
          style.id = 'fingerprint-click-style';
          style.textContent = [
            '#fingerprint_plot .ytick, #fingerprint_plot .ytick text, #fingerprint_plot .ytick tspan {',
            '  cursor: pointer !important;',
            '  pointer-events: all !important;',
            '}',
            '#fingerprint_plot .ytick text {',
            '  stroke: rgba(0,0,0,0);',
            '  stroke-width: 10px;',
            '  paint-order: stroke fill;',
            '  transition: fill .15s ease, font-weight .15s ease;',
            '}',
            '#fingerprint_plot .ytick text:hover {',
            '  fill: #0b1020 !important;',
            '  font-weight: 600 !important;',
            '}',
            '#fingerprint_plot {',
            '  overflow: visible !important;',
            '  transition: height .36s cubic-bezier(.4,0,.2,1);',
            '}',
            '#fingerprint_plot > .plot-container, #fingerprint_plot .svg-container {',
            '  transition: height .36s cubic-bezier(.4,0,.2,1);',
            '}'
          ].join('\\n');
          document.head.appendChild(style);
        }

        var base = [];
        var n = gd.data[0].y.length;

        for (var i = 0; i < n; i++) {
          var cd = gd.data[0].customdata && gd.data[0].customdata[i]
            ? gd.data[0].customdata[i]
            : [Number(gd.data[0].x[i]) + Number(gd.data[1].x[i]), Number(gd.data[0].x[i]), Number(gd.data[1].x[i]), 0, 0];

          base.push({
            pathway: String(gd.data[0].y[i]),
            Exclusive: Number(gd.data[0].x[i]) || 0,
            Shared: Number(gd.data[1].x[i]) || 0,
            total: Number(cd[0]) || 0,
            databases: Number(cd[3]) || 0,
            references: Number(cd[4]) || 0
          });
        }

        var state = {
          showExclusive: true,
          showShared: true,
          focus: null
        };

        var axisClickGuardUntil = 0;
        var renderRevision = 0;

        function eligible(row) {
          if (state.showExclusive && state.showShared) return true;
          if (state.showExclusive) return row.Exclusive > 0;
          if (state.showShared) return row.Shared > 0;
          return false;
        }

        function visibleRows() {
          var sortKey;
          if (state.showExclusive && state.showShared) {
            sortKey = function(r) { return r.total; };
          } else if (state.showExclusive) {
            sortKey = function(r) { return r.Exclusive; };
          } else {
            sortKey = function(r) { return r.Shared; };
          }

          if (state.focus !== null) {
            var focused = base.filter(function(r) { return r.pathway === state.focus; });
            if (!focused.length || !eligible(focused[0])) state.focus = null;
          }

          var rows = base.filter(eligible);
          rows.sort(function(a, b) { return sortKey(a) - sortKey(b); });

          if (state.focus !== null) {
            rows = rows.filter(function(r) { return r.pathway === state.focus; });
          }
          return rows;
        }

        function custom(rows) {
          return rows.map(function(r) {
            return [r.total, r.Exclusive, r.Shared, r.databases, r.references];
          });
        }

        function maxVisibleValue(rows) {
          if (!rows.length) return 1;
          var values = rows.map(function(r) {
            if (state.showExclusive && state.showShared) return r.Exclusive + r.Shared;
            if (state.showExclusive) return r.Exclusive;
            return r.Shared;
          });
          var m = Math.max.apply(null, values.concat([1]));
          return Math.max(1, m * 1.08);
        }

        function targetHeight(count) {
          if (count <= 1) return 230;
          if (count <= 4) return 270;
          return Math.max(320, Math.min(1380, 126 + count * 22));
        }

        function setContainerHeight(h) {
          gd.style.height = h + 'px';
          gd.style.minHeight = h + 'px';

          var parent = gd.parentElement;
          if (parent) {
            parent.style.height = h + 'px';
            parent.style.minHeight = h + 'px';
            parent.style.overflow = 'visible';
          }
        }

        function makeTrace(traceIndex, rows) {
          var isExclusive = traceIndex === 0;
          var isShown = isExclusive ? state.showExclusive : state.showShared;
          return {
            x: rows.map(function(r) {
              if (!isShown) return 0;
              return isExclusive ? r.Exclusive : r.Shared;
            }),
            y: rows.map(function(r) { return r.pathway; }),
            customdata: custom(rows),
            visible: true,
            opacity: isShown ? 1 : 0.035,
            width: rows.length === 1 ? 0.34 : 0.62
          };
        }

        function updateLegendAppearance() {
          var items = gd.querySelectorAll('.legend .traces');
          if (items.length > 0) items[0].style.opacity = state.showExclusive ? '1' : '0.30';
          if (items.length > 1) items[1].style.opacity = state.showShared ? '1' : '0.30';
        }

        function markFocusedTick() {
          var ticks = gd.querySelectorAll('.ytick text');
          ticks.forEach(function(t) {
            var isFocus = state.focus !== null && t.textContent.trim() === state.focus;
            t.style.fontWeight = isFocus ? '600' : '';
            t.style.fill = isFocus ? '#0b1020' : '';
          });
        }

        function layoutFor(rows) {
          var labels = rows.map(function(r) { return r.pathway; });
          var h = targetHeight(rows.length);
          setContainerHeight(h);

          return {
            height: h,
            autosize: false,
            barmode: 'stack',
            bargap: rows.length === 1 ? 0.58 : 0.24,
            margin: {l: 205, r: 24, t: 14, b: 72},
            legend: {
              orientation: 'h',
              x: 0.5,
              y: -0.16,
              xanchor: 'center',
              yanchor: 'top'
            },
            xaxis: {
              range: [0, maxVisibleValue(rows)],
              autorange: false,
              fixedrange: true,
              title: '',
              showgrid: true,
              gridcolor: '#e7e5e4',
              zeroline: false,
              rangemode: 'tozero'
            },
            yaxis: {
              categoryorder: 'array',
              categoryarray: labels,
              autorange: false,
              range: rows.length > 0 ? [-0.5, rows.length - 0.5] : [-0.5, 0.5],
              fixedrange: true,
              title: '',
              showgrid: false,
              automargin: true,
              tickfont: {size: rows.length === 1 ? 11 : 10}
            }
          };
        }

        function finishUpdate() {
          updateLegendAppearance();
          markFocusedTick();
          requestAnimationFrame(function() {
            Plotly.Plots.resize(gd);
          });
        }

        function forceVisibleAxes(nextLayout) {
          return Plotly.relayout(gd, {
            'height': nextLayout.height,
            'xaxis.autorange': false,
            'xaxis.range': nextLayout.xaxis.range,
            'yaxis.autorange': false,
            'yaxis.range': nextLayout.yaxis.range,
            'yaxis.categoryorder': 'array',
            'yaxis.categoryarray': nextLayout.yaxis.categoryarray
          });
        }

        function reactFallback(rows, nextLayout) {
          var mergedLayout = Object.assign({}, gd.layout || {}, nextLayout);
          mergedLayout.margin = Object.assign({}, (gd.layout || {}).margin || {}, nextLayout.margin || {});
          mergedLayout.legend = Object.assign({}, (gd.layout || {}).legend || {}, nextLayout.legend || {});
          mergedLayout.xaxis = Object.assign({}, (gd.layout || {}).xaxis || {}, nextLayout.xaxis || {});
          mergedLayout.yaxis = Object.assign({}, (gd.layout || {}).yaxis || {}, nextLayout.yaxis || {});

          renderRevision += 1;
          mergedLayout.uirevision = 'fingerprint-state-' + renderRevision;
          mergedLayout.datarevision = renderRevision;

          return Plotly.react(
            gd,
            [
              Object.assign({}, gd.data[0], makeTrace(0, rows)),
              Object.assign({}, gd.data[1], makeTrace(1, rows))
            ],
            mergedLayout,
            gd._context || {}
          ).then(function() {
            return forceVisibleAxes(nextLayout);
          }).then(finishUpdate);
        }

        function applyState(animate) {
          var rows = visibleRows();
          var nextLayout = layoutFor(rows);

          var currentCount = gd.data[0] && gd.data[0].y ? gd.data[0].y.length : 0;
          var sameCount = currentCount === rows.length;

          if (animate && sameCount) {
            var frame = {
              data: [makeTrace(0, rows), makeTrace(1, rows)],
              layout: nextLayout
            };

            Plotly.animate(gd, frame, {
              transition: {duration: 360, easing: 'cubic-in-out'},
              frame: {duration: 360, redraw: true},
              mode: 'immediate'
            }).then(function() {
              return forceVisibleAxes(nextLayout);
            }).then(finishUpdate).catch(function() {
              reactFallback(rows, nextLayout);
            });
          } else {
            reactFallback(rows, nextLayout);
          }
        }

        function toggleFocus(pathway) {
          if (!pathway) return;
          var exists = base.some(function(r) { return r.pathway === pathway; });
          if (!exists) return;

          var restoringAll = state.focus === pathway;
          state.focus = restoringAll ? null : pathway;

          applyState(!restoringAll);
        }

        gd.on('plotly_legendclick', function(ev) {
          var idx = ev.curveNumber;
          if (idx === 0) {
            if (state.showExclusive && !state.showShared) return false;
            state.showExclusive = !state.showExclusive;
          } else if (idx === 1) {
            if (state.showShared && !state.showExclusive) return false;
            state.showShared = !state.showShared;
          } else {
            return false;
          }

          applyState(true);
          return false;
        });

        gd.on('plotly_legenddoubleclick', function() {
          return false;
        });

        gd.on('plotly_click', function(ev) {
          if (Date.now() < axisClickGuardUntil) return;

          if (ev && ev.points && ev.points.length) {
            toggleFocus(String(ev.points[0].y));
          }
        });

        gd.addEventListener('mousedown', function(ev) {
          var target = ev.target;
          if (!target || !target.closest) return;

          var tick = target.closest('.ytick');
          if (!tick || !gd.contains(tick)) return;

          var pathway = (tick.textContent || '').trim();
          if (!pathway) return;

          axisClickGuardUntil = Date.now() + 650;

          ev.preventDefault();
          ev.stopPropagation();
          if (typeof ev.stopImmediatePropagation === 'function') {
            ev.stopImmediatePropagation();
          }

          toggleFocus(pathway);
        }, true);

        var initialRows = visibleRows();
        var initialLayout = layoutFor(initialRows);
        Plotly.relayout(gd, initialLayout).then(finishUpdate);
      }
    ")

    p
  })

  # ── Developer cards (About tab) ────────────────────────────────────
  output$dev_cards <- renderUI({
    dev_dir <- "data/about/Desenvolvedores"
    devs <- list.dirs(dev_dir, full.names = FALSE, recursive = FALSE)
    dev_order <- c("Emanuell Rodrigues de Souza", "Victor dos Santos Lopes",
                   "Higor Almeida Cordeiro Nogueira", "Enrique Medina-Acosta")
    devs <- dev_order[dev_order %in% devs]
    if (length(devs) == 0) return(tags$p("No developers found."))

    cards <- lapply(devs, function(dev_name) {
      dev_path <- file.path(dev_dir, dev_name)
      photo_files <- list.files(dev_path, pattern = "foto", ignore.case = TRUE)
      photo_src <- if (length(photo_files) > 0) paste0("devs/", dev_name, "/", photo_files[1]) else NULL
      read_link <- function(file) {
        p <- file.path(dev_path, file)
        if (file.exists(p)) trimws(readLines(p, warn = FALSE)[1]) else NULL
      }
      email   <- read_link("Email.txt")
      github  <- read_link("Github.txt")
      lattes  <- read_link("Lattes.txt")
      linkedin <- read_link("Linkedin.txt")
      researchgate <- read_link("ResearchGate.txt")
      role <- if (dev_name == "Enrique Medina-Acosta") "Group leader" else NULL

      tags$div(class = "dev-card",
        if (!is.null(photo_src)) tags$img(src = photo_src, class = "dev-photo"),
        tags$h4(dev_name),
        tags$p("LBTGenomica/UENF", class = "dev-affiliation"),
        if (!is.null(role)) tags$p(role, class = "dev-role"),
        if (!is.null(email)) tags$p(tags$a(href = paste0("mailto:", email), email, class = "dev-link")),
        tags$div(class = "dev-links",
          if (!is.null(github))  tags$a(href = github,  target = "_blank", "GitHub",  class = "dev-link"),
          if (!is.null(lattes))  tags$a(href = lattes,  target = "_blank", "Lattes",  class = "dev-link"),
          if (!is.null(linkedin)) tags$a(href = linkedin, target = "_blank", "LinkedIn", class = "dev-link"),
          if (!is.null(researchgate)) tags$a(href = researchgate, target = "_blank", "ResearchGate", class = "dev-link")
        )
      )
    })

    tagList(
      tags$div(class = "dev-grid", cards),
      tags$style(HTML('
        .dev-grid { display: flex; flex-wrap: wrap; gap: 16px; width: 100%; }
        .dev-card {
          width: calc(25% - 12px);
          background: #FFFFFF; border: 1px solid var(--line);
          border-radius: 8px; padding: 20px; min-height: 300px;
          box-sizing: border-box; overflow: hidden;
          text-align: center;
        }
        .dev-photo { width: 110px; height: 110px; border-radius: 50%; object-fit: cover; margin-bottom: 12px; }
        .dev-card h4 { font-family: "Segoe UI", system-ui, sans-serif; margin: 0 0 8px; word-break: break-word; font-weight: 700; font-size: 16px; color: #1c1917; }
        .dev-role { font-size: 12px; color: #c2410c; font-weight: 600; margin: 0 0 8px; }
        .dev-affiliation { font-size: 12px; color: #a8a29e; margin: 0 0 8px; }
        .dev-link {
          display: inline-block; margin: 3px 6px;
          font-family: "Segoe UI", system-ui, sans-serif; font-size: 12px;
          color: #1d4ed8; text-decoration: none;
          border-bottom: none;
        }
        .dev-link:hover { color: #c2410c; }
      '))
    )
  })

  # ── Data sources (About tab) ────────────────────────────────────
  output$data_sources <- renderUI({
    ds <- tryCatch(
      readxl::read_excel("data/about/Data sources/data_sources.xlsx"),
      error = function(e) NULL
    )
    if (is.null(ds) || nrow(ds) == 0) return(tags$p("No data sources found."))

    items <- lapply(seq_len(nrow(ds)), function(i) {
      abbr <- ds$abbreviation[i]
      name <- ds$full_name[i]
      link <- ds$link[i]
      label <- tags$span(tags$strong(abbr), " — ", name)
      if (!is.na(link) && nzchar(trimws(link))) {
        label <- tags$a(href = link, target = "_blank", rel = "noopener", label)
      }
      tags$li(label)
    })

    tagList(
      tags$div(class = "ds-sections",
        tags$ul(class = "ds-list", items)
      ),
      tags$style(HTML('
        .ds-sections { margin-top: 8px; }
        .ds-list {
          list-style: none; padding: 0; margin: 0;
          display: grid;
          grid-template-columns: 1fr 1fr;
          column-gap: 48px;
        }
        .ds-list li {
          min-height: 44px;
          padding: 8px 0;
          border-bottom: 1px solid var(--line);
          font-size: 14px; line-height: 1.5; color: var(--ink);
          display: flex; align-items: center;
        }
        .ds-list a { color: var(--navy); text-decoration: none; }
        .ds-list a:hover { color: var(--rust); text-decoration: underline; }
        @media (max-width: 700px) { .ds-list { grid-template-columns: 1fr; } }
      '))
    )
  })

  # ── Contact form ────────────────────────────────────────────────────
  observeEvent(input$open_contact, {
    showModal(modalDialog(
        title = "Contact the developers",
        size = "m", easyClose = TRUE,
        footer = tagList(
          div(style = "display: flex; gap: 10px; justify-content: flex-end;",
            modalButton("Cancel"),
            actionButton("contact_send", "Send message", class = "search-evidence-btn",
                         style = "margin-top: 0;")
          )
        ),
        textInput("contact_name", "Your name:", placeholder = "e.g. John Doe"),
        textInput("contact_email", "Your email:", placeholder = "e.g. john@example.com"),
        checkboxInput("contact_reply", "I'd like a reply", value = FALSE),
        textAreaInput("contact_msg", "Your message:", rows = 6,
                      placeholder = "Write your feedback, bug report, or suggestion here...")
      ))
  })

  observeEvent(input$contact_send, {
    msg <- trimws(input$contact_msg)
    if (msg == "") {
      showNotification("Please write a message first.", type = "warning")
      return()
    }
    name  <- trimws(input$contact_name %||% "")
    email <- trimws(input$contact_email %||% "")
    reply <- isTRUE(input$contact_reply)
    body  <- paste0(
      "Name: ", if (name != "") name else "Anonymous", "\n",
      "Email: ", if (email != "") email else "Not provided", "\n",
      "Reply requested: ", if (reply) "Yes" else "No", "\n\n",
      msg
    )
    creds <- tryCatch(readLines("data/email_creds.txt", warn = FALSE),
                      error = function(e) NULL)
    if (is.null(creds) || length(creds) < 2 || creds[2] == "REPLACE_WITH_APP_PASSWORD") {
      showNotification("Email not configured. Set your Gmail App Password in data/email_creds.txt",
                       type = "error", duration = 8)
      return()
    }
    from_addr <- trimws(creds[1])
    app_pwd   <- trimws(creds[2])
    result <- tryCatch({
      email <- emayili::envelope() %>%
        emayili::from(from_addr) %>%
        emayili::to("souza.ers00@gmail.com") %>%
        emayili::subject("NEW RCDome") %>%
        emayili::text(body)
      smtp <- emayili::server(host = "smtp.gmail.com", port = 587,
                     username = from_addr, password = app_pwd)
      smtp(email, verbose = FALSE)
      TRUE
    }, error = function(e) {
      showNotification(paste0("Failed to send: ", conditionMessage(e)),
                       type = "error", duration = 8)
      FALSE
    })
    if (isTRUE(result)) {
      updateTextAreaInput(session, "contact_msg", value = "")
      updateTextInput(session, "contact_name", value = "")
      updateTextInput(session, "contact_email", value = "")
      showNotification("Message sent!", type = "message")
    }
  })


}
