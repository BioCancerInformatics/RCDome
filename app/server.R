# ─── Server ──────────────────────────────────────────────────────────────────
if (!exists("genes_df", inherits = TRUE) || !exists("fingerprint_df", inherits = TRUE)) source("global.R")

server <- function(input, output, session) {

  # Per-session Evidence Trail state (fixes the cross-session leak)
  evidence_trail_rv <- shiny::reactiveVal(NULL)
  gene_catalog_entity_rv <- shiny::reactiveVal(NULL)

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

  # ── Home tab: reload the landing page iframe only when the user RETURNS to
  #    Home (skip the initial load — the iframe already has its src in the UI).
  #    This removes the startup reload that made the page flicker. ────────────
  home_tab_seen <- FALSE
  observeEvent(input$main_nav, {
    if (isTRUE(input$main_nav == "Home")) {
      if (home_tab_seen) {
        shinyjs::runjs('document.getElementById("home_iframe").src = "landing_page.html";')
      } else {
        home_tab_seen <<- TRUE
      }
    }
  }, ignoreNULL = TRUE)

  # ── Network module (Aba Network) ────────────────────────────────────
  mod_network_server("network", genes_df, evidence_trail_rv)

  # ── RCD Entity Definitions (separate sub-module) ─────────────────
  mod_rcd_entities_server("rcd_entities", gene_catalog_entity_rv)

  # ── Operational Definitions module ──────────────────────────────
  mod_od_server("od")

  # ── Operational Definition Comparator module ──────────────────────
  mod_od_compare_server("od_compare")

  # ── Omic module (Aba Omic) ──────────────────────────────────────
  mod_gene_catalog_server("gene_catalog", evidence_trail_rv, gene_catalog_entity_rv)

  # ── Discrepancy Radar (classifier-conflict knowledge frontier) ────
  mod_discrepancy_server("discrepancy", evidence_trail_rv)

  # ── Discovery Timeline (founding year + ontological level) ────────
  mod_timeline_server("timeline")

  # ── Reader Mode (first-visit guided tour) ──────────────────────────
  mod_tour_server("tour")

  # ── 3D Dome gene click → Evidence Trail drawer ───────────────────────
  observeEvent(input$dome3d_gene, {
    req(input$dome3d_gene)
    message("[TRAIL] dome3d_gene fired: ", input$dome3d_gene)
    parts <- strsplit(input$dome3d_gene, "|", fixed = TRUE)[[1]]
    if (length(parts) != 2) return()
    evidence_trail_rv(list(gene = parts[1], entity = parts[2]))
    shinyjs::runjs("document.getElementById('evidence_drawer').style.display='block';")
  })

  # ── Chat module (RCDchat tab) — standalone (context wired to V027 later) ──
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


  # ── Evidence Trail drawer (global, direct HTML injection) ───────────
  build_evidence_trail_html <- function(g, e, extra = NULL) {
    r <- genes_df[genes_df$name == g & genes_df$Pathway_Categorization == e, , drop = FALSE]
    if (nrow(r) == 0) return("<p style='color:#1c1917;'>No matrix row for this pair.</p>")
    r <- r[1, , drop = FALSE]
    f <- function(x) { x <- as.character(x); if (length(x) == 0 || is.na(x) || !nzchar(trimws(x))) "—" else trimws(x) }

    ds_sent <- f(r$deep_best_sentence)
    el_verb <- f(r$elicit_verbatim_sentence)
    el_status <- f(r$elicit_evidence_status)
    # Suppress only explicit no-evidence (Not mentioned / status none)
    el_sent <- el_verb
    if (grepl("not mentioned", el_verb, ignore.case = TRUE) ||
        tolower(el_status) %in% c("none", "")) {
      el_sent <- "—"
    }
    pm <- unique(unlist(strsplit(paste(f(r$pmid_list), f(r$llm_pmids), f(r$epmc_pmids), f(r$elicit_pmids), sep = ";"), ";", fixed = TRUE)))
    pm <- pm[grepl("^\\d+$", pm)]
    pm_links <- if (length(pm) > 0) {
      paste(vapply(pm, function(x) paste0("<a href='https://pubmed.ncbi.nlm.nih.gov/", x, "/' target='_blank' style='color:#1d4ed8;'>PMID ", x, "</a>"), character(1)), collapse = " · ")
    } else "—"

    badge <- function(txt, col) sprintf("<span style='display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:600;color:#fff;background:%s;margin-right:4px;'>%s</span>", col, txt)

    verdict_row <- function(lbl, role, dir, mech, role_col, dir_col, tip = NULL, empty_label = NULL) {
      role_col2 <- if (role %in% names(role_col)) role_col[[role]] else "#9E9E9E"
      dir_col2  <- if (dir %in% names(dir_col)) dir_col[[dir]] else "#757575"
      role_b <- if (role != "—") badge(role, role_col2) else "<span style='color:#a8a29e;'>—</span>"
      dir_b  <- if (dir != "—") badge(dir, dir_col2) else "<span style='color:#a8a29e;'>—</span>"
      mech_b <- if (mech != "—") badge(mech, if (mech == "YES") "#2E7D32" else "#9E9E9E") else "<span style='color:#a8a29e;'>—</span>"
      tip_html <- if (!is.null(tip) && nzchar(tip)) {
        sprintf("<span class='claim-info' tabindex='0' aria-label='About this row' data-tip='%s'>&#9432;</span>", htmltools::htmlEscape(tip))
      } else ""
      body <- if (!is.null(empty_label) && role == "—" && dir == "—" && mech == "—") {
        sprintf("<span style='color:#a8a29e;font-size:12px;font-weight:500;'>%s</span>", empty_label)
      } else {
        paste0(role_b, dir_b, mech_b)
      }
      sprintf("<div style='display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid #f0efed;'><span style='width:88px;font-weight:700;color:#57534e;font-size:13px;'>%s</span>%s%s</div>", lbl, tip_html, body)
    }

    role_col <- c(EXECUTOR = "#E53935", REGULATOR = "#3949AB", MARKER = "#00897B", UNCERTAIN = "#9E9E9E")
    dir_col  <- c(PROMOTES = "#2E7D32", PROTECTS = "#1565C0", UNCLEAR = "#757575")

    ds_p <- if (ds_sent != "—") sprintf("<p style='margin:0 0 6px;'><b>DeepSeek:</b> %s</p>", ds_sent) else ""
    el_badge <- if (tolower(f(r$elicit_multi_gene)) == "true") {
      "<style>.mg-badge{position:relative;display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600;color:#92400e;background:#fef3c7;margin-right:4px;cursor:help;}.mg-badge::before{content:\"\";position:absolute;left:0;right:0;bottom:100%;height:14px;}.mg-badge:hover::after{content:attr(data-tip);position:absolute;bottom:calc(100% + 10px);left:0;width:260px;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;padding:7px 10px;border-radius:6px;font-size:12px;line-height:1.4;white-space:normal;z-index:1000;box-shadow:0 2px 8px rgba(0,0,0,.15);pointer-events:none;}</style><span class='mg-badge' data-tip='Supporting paper indexed under multiple genes; the verbatim may not be gene-specific.'>multi-gene</span>"
    } else ""
    el_p <- if (el_sent != "—") sprintf("<p style='margin:0;'><b>Elicit:</b> %s%s</p>", el_badge, el_sent) else ""

    verbatim_body <- if (ds_sent == "—" && el_sent == "—") {
      "<span style='color:#a8a29e;font-style:italic;'>Verbatim not available \u2014 no exact supporting sentence was retrieved for this pair. This is expected: the role, direction, and mechanistic class below are produced independently by the classification pipeline (LLM knowledge + PubMed abstracts) and do not require a verbatim sentence. Exact-sentence retrieval covers only ~6% of pairs (DeepSeek) and ~11% (Elicit).</span>"
    } else {
      paste0(ds_p, el_p)
    }

    logo_file_d <- file.path("data/RCD modulo/logo RCDs", paste0(e, ".png"))
    logo_url_d <- if (file.exists(logo_file_d)) paste0("rcd_logos/", URLencode(paste0(e, ".png"), reserved = TRUE)) else ""
    logo_html_d <- if (nzchar(logo_url_d)) sprintf("<img src='%s' style='width:30px;height:30px;object-fit:contain;margin-right:10px;vertical-align:middle;'>", logo_url_d) else ""

    base <- sprintf(
      "<div><style>.claim-info{position:relative;display:inline-block;cursor:help;color:#92400e;font-size:13px;margin-left:5px;vertical-align:middle;outline:none;}.claim-info::after{content:attr(data-tip);position:absolute;bottom:calc(100%% + 8px);left:0;transform:none;width:280px;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;padding:8px 10px;border-radius:6px;font-size:12px;font-weight:400;line-height:1.4;white-space:normal;z-index:1000;box-shadow:0 2px 8px rgba(0,0,0,.15);text-align:left;opacity:0;visibility:hidden;transition:opacity .15s,visibility .15s;pointer-events:none;}.claim-info:hover::after,.claim-info:focus::after{opacity:1;visibility:visible;}</style><div style='background:#0b1020;color:#e7e5e4;border-radius:10px;padding:14px 16px;margin-bottom:16px;'><h4 style='margin:0;color:#fff;'>%s<i>%s</i> × %s</h4><div style='color:#d6d3d1;font-size:12px;margin-top:4px;'>Evidence tier: %s · sources: %s</div></div><p style='margin:0 0 6px;'><strong style='color:#92400e;'>Claim (verbatim)</strong> <span class='claim-info' tabindex='0' aria-label='About verbatim claims' data-tip='Verbatim claims are displayed only when an exact supporting sentence has been retrieved. Evidence classifications (mechanistic role, regulatory direction, mechanistic classification) are populated independently and do not necessarily indicate that verbatim supporting evidence was retrieved. Coverage: ~6%% DeepSeek, ~11%% Elicit.'>&#9432;</span></p><div style='background:#fafaf9;border:1px solid #e7e5e4;border-radius:8px;padding:10px 12px;margin-bottom:14px;font-size:13px;color:#1c1917;'>%s</div><p style='margin:0 0 6px;color:#1c1917;'><strong>Source</strong></p><div style='font-size:13px;margin-bottom:14px;'>%s</div><p style='margin:0 0 6px;color:#1c1917;'><strong>Classifiers</strong></p>%s%s%s</div>",
      logo_html_d, g, e, f(r$evidence_tier), f(r$num_sources), verbatim_body, pm_links,
      verdict_row("DeepSeek", f(r$cot_role), f(r$cot_direction), f(r$cot_mechanistic), role_col, dir_col),
      verdict_row("Compiled gene role", f(r$rcd_gene_type), f(r$role_direction), "—", role_col, dir_col,
                  tip = "Source-compiled role/direction from the extraction channels (A–D), before the independent validations. Empty = the source databases made no pre-evaluation claim for this pair.",
                  empty_label = "NO_SOURCE_ANNOTATION"),
      verdict_row("Consensus", f(r$consensus_role), f(r$consensus_direction), f(r$consensus_mechanistic), role_col, dir_col)
    )

    # ── Status-aware adjudication block (all rows) ──────────────────────
    status <- f(r$decision_status)
    has_axis <- !is.null(extra) && !is.null(extra$axis) && nzchar(extra$axis)
    axis_label <- if (has_axis) {
      switch(extra$axis, direction = "Direction", role = "Role", mechanistic = "Mechanistic", extra$axis)
    } else "Mechanistic"
    axis_key <- if (has_axis) extra$axis else "mechanistic"

    ext_lab <- function(concat) {
      concat <- trimws(as.character(concat))
      if (length(concat) == 0 || is.na(concat) || !nzchar(concat)) return(NA_character_)
      parts <- strsplit(concat, "|", fixed = TRUE)[[1]]
      idx <- match(axis_key, c("mechanistic", "role", "direction"))
      if (is.na(idx) || length(parts) < idx) return(NA_character_)
      trimws(parts[idx])
    }

    vbadge <- function(txt, col) {
      txt <- trimws(as.character(txt))
      if (length(txt) == 0 || is.na(txt) || !nzchar(txt)) return("<span style='color:#a8a29e;'>—</span>")
      sprintf("<span style='display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:600;color:#fff;background:%s;margin-right:6px;'>%s</span>", col, txt)
    }

    fin_val <- switch(axis_key, role = f(r$final_role), direction = f(r$final_direction), f(r$final_mechanistic))
    fin_map <- switch(axis_key,
      role = c(EXECUTOR = "#E53935", REGULATOR = "#3949AB", MARKER = "#00897B", UNCERTAIN = "#9E9E9E"),
      direction = c(PROMOTES = "#2E7D32", PROTECTS = "#1565C0", UNCLEAR = "#757575"),
      c(YES = "#2E7D32", NO = "#9E9E9E", OUT_OF_CONTEXT = "#F59E0B"))
    fin_col <- if (fin_val %in% names(fin_map)) fin_map[[fin_val]] else "#9E9E9E"

    cur1 <- ext_lab(r$curator_1_verdict)
    cur2 <- ext_lab(r$curator_2_verdict)

    ev_txt <- f(r$deciding_evidence)
    if (ev_txt != "—" && nchar(ev_txt) > 380) ev_txt <- paste0(substr(ev_txt, 1, 380), "…")

    adj_html <- ""
    if (!has_axis) {
      # Full 3-dimension resolution + the seven decisions (Gene Catalog / Network / 3D Dome)
      mech_map3 <- c(YES = "#2E7D32", NO = "#9E9E9E", OUT_OF_CONTEXT = "#F59E0B")
      fcol <- function(v, map) if (v %in% names(map)) map[[v]] else "#9E9E9E"
      votes_html <- ""
      if (status == "UNIFORM_PIPELINE") {
        vote_line <- function(lbl, concat) {
          concat <- trimws(as.character(concat))
          if (length(concat) == 0 || is.na(concat) || !nzchar(concat)) {
            return(paste0("<div style='margin-top:8px;padding:10px 12px;background:#fafaf9;border:1px solid #e7e5e4;border-radius:8px;font-size:13px;color:#1c1917;'><strong>", lbl, ":</strong> <span style='color:#a8a29e;'>—</span></div>"))
          }
          parts <- strsplit(concat, "|", fixed = TRUE)[[1]]
          ok <- which(nzchar(trimws(parts)))
          if (length(ok) == 0) {
            return(paste0("<div style='margin-top:8px;padding:10px 12px;background:#fafaf9;border:1px solid #e7e5e4;border-radius:8px;font-size:13px;color:#1c1917;'><strong>", lbl, ":</strong> <span style='color:#a8a29e;'>—</span></div>"))
          }
          axis <- c("mechanistic", "role", "direction")[ok[1]]
          src <- trimws(parts[ok[1]])
          val <- src
          if (src == "DEEPSEEK") val <- switch(axis, role = f(r$cot_role), direction = f(r$cot_direction), f(r$cot_mechanistic))
          else if (src == "CONSENSUS") val <- switch(axis, role = f(r$consensus_role), direction = f(r$consensus_direction), f(r$consensus_mechanistic))
          cmap <- switch(axis, role = role_col, direction = dir_col, c(YES = "#2E7D32", NO = "#9E9E9E", OUT_OF_CONTEXT = "#F59E0B"))
          col <- if (val %in% names(cmap)) cmap[[val]] else "#9E9E9E"
          paste0("<div style='margin-top:8px;padding:10px 12px;background:#fafaf9;border:1px solid #e7e5e4;border-radius:8px;font-size:13px;color:#1c1917;'><strong>", lbl, " (voted with ", htmltools::htmlEscape(src), "):</strong> ", vbadge(val, col), "</div>")
        }
        votes_html <- paste0(
          "<p style='margin:14px 0 6px;color:#1c1917;'><strong>Votes</strong></p>",
          vote_line("GPT", r$gpt4o_verdict),
          vote_line("Curator 1", r$curator_1_verdict),
          vote_line("Curator 2", r$curator_2_verdict)
        )
      }
      adj_html <- paste0(
        votes_html,
        "<div style='margin-top:14px;padding:12px 14px;background:#0b1020;border-radius:8px;font-size:13px;color:#fff;'><strong style='color:#fbbf24;'>Human adjudication (evidence-first):</strong> ",
        vbadge(f(r$final_mechanistic), fcol(f(r$final_mechanistic), mech_map3)), " <span style='color:#78716c;'>\u00b7</span> ",
        vbadge(f(r$final_role), fcol(f(r$final_role), role_col)), " <span style='color:#78716c;'>\u00b7</span> ",
        vbadge(f(r$final_direction), fcol(f(r$final_direction), dir_col)),
        "<div style='color:#d6d3d1;margin-top:6px;font-size:12px;'>", htmltools::htmlEscape(ev_txt), "</div>",
        "<div style='color:#a8a29e;margin-top:4px;font-size:11px;'>decision_status: ", htmltools::htmlEscape(status),
        " · evidence_source: ", htmltools::htmlEscape(f(r$evidence_source)),
        if (status == "AGREED_LABEL_ABSTRACT") paste0(" · abstract_check: ", htmltools::htmlEscape(f(r$abstract_check))) else "",
        "</div></div>"
      )
    } else if (status == "PENDING_DELTA") {
      adj_html <- "<div style='margin-top:14px;padding:10px 12px;background:#f5f5f4;border-radius:8px;font-size:13px;color:#57534e;'><strong>Adjudication:</strong> Pending (curator review — all complete)</div>"
    } else if (status == "AGREED_LABEL_ABSTRACT") {
      adj_html <- paste0(
        "<div style='margin-top:14px;padding:10px 12px;background:#ecfdf5;border:1px solid #6ee7b7;border-radius:8px;font-size:13px;color:#1c1917;'><strong>Human adjudication (evidence-first, agreement stands):</strong>",
        vbadge(fin_val, fin_col),
        " <span style='color:#78716c;'>· abstract check: ", htmltools::htmlEscape(f(r$abstract_check)), "</span></div>"
      )
    } else {
      gpt_line <- ""
      if (!is.null(extra) && !is.null(extra$gpt_verdict) && nzchar(extra$gpt_verdict)) {
        gpt_v <- trimws(extra$gpt_verdict)
        gpt_v2 <- gpt_v
        if (gpt_v == "DEEPSEEK") {
          gpt_v2 <- switch(axis_key, role = f(r$cot_role), direction = f(r$cot_direction), f(r$cot_mechanistic))
        } else if (gpt_v == "CONSENSUS") {
          gpt_v2 <- switch(axis_key, role = f(r$consensus_role), direction = f(r$consensus_direction), f(r$consensus_mechanistic))
        }
        gpt_map <- switch(axis_key, role = role_col, direction = dir_col, c(YES = "#2E7D32", NO = "#9E9E9E", OUT_OF_CONTEXT = "#F59E0B"))
        gpt_bg <- if (gpt_v2 %in% names(gpt_map)) gpt_map[[gpt_v2]] else "#9E9E9E"
        gpt_line <- paste0(
          "<div style='margin-top:14px;padding:10px 12px;background:#fffbeb;border:1px solid #fde68a;border-radius:8px;font-size:13px;color:#1c1917;'><strong>GPT arbitration (",
          axis_label, " — sided with ", htmltools::htmlEscape(gpt_v), "):</strong> ",
          sprintf("<span style='display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:600;color:#fff;background:%s;margin-left:4px;'>%s</span>", gpt_bg, gpt_v2),
          "<div style='color:#57534e;margin-top:6px;'>", htmltools::htmlEscape(trimws(extra$gpt_reason %||% "")), "</div></div>"
        )
      }
      cur_line <- function(lbl, v) {
        vv <- trimws(as.character(v))
        if (length(vv) == 0 || is.na(vv) || !nzchar(vv)) {
          return(paste0("<div style='margin-top:8px;padding:10px 12px;background:#f5f5f4;border-radius:8px;font-size:13px;color:#57534e;'><strong>", lbl, ":</strong> Pending (curator review — all complete)</div>"))
        }
        # map the source-side vote -> the vocabulary value that source declared
        v2 <- vv
        if (vv == "DEEPSEEK") {
          v2 <- switch(axis_key, role = f(r$cot_role), direction = f(r$cot_direction), f(r$cot_mechanistic))
        } else if (vv == "CONSENSUS") {
          v2 <- switch(axis_key, role = f(r$consensus_role), direction = f(r$consensus_direction), f(r$consensus_mechanistic))
        }
        cmap <- switch(axis_key, role = role_col, direction = dir_col, c(YES = "#2E7D32", NO = "#9E9E9E", OUT_OF_CONTEXT = "#F59E0B"))
        col <- if (v2 %in% names(cmap)) cmap[[v2]] else "#9E9E9E"
        paste0("<div style='margin-top:8px;padding:10px 12px;background:#fafaf9;border:1px solid #e7e5e4;border-radius:8px;font-size:13px;color:#1c1917;'><strong>", lbl, " (voted with ", htmltools::htmlEscape(vv), "):</strong> ", vbadge(v2, col), "</div>")
      }
      fin_line <- paste0(
        "<div style='margin-top:10px;padding:12px 14px;background:#0b1020;border-radius:8px;font-size:13px;color:#fff;'><strong style='color:#fbbf24;'>Human adjudication (evidence-first, the resolution):</strong>",
        vbadge(fin_val, fin_col),
        "<div style='color:#d6d3d1;margin-top:6px;font-size:12px;'>", htmltools::htmlEscape(ev_txt), "</div>",
        "<div style='color:#a8a29e;margin-top:4px;font-size:11px;'>decision_status: ", htmltools::htmlEscape(status), " · evidence_source: ", htmltools::htmlEscape(f(r$evidence_source)), "</div></div>"
      )
      adj_html <- paste0(gpt_line, cur_line("Curator 1", cur1), cur_line("Curator 2", cur2), fin_line)
    }

    paste0(base, adj_html)
  }

  observeEvent(evidence_trail_rv(), {
    req(evidence_trail_rv())
    message("[TRAIL] evidence_trail_rv fired: gene=", evidence_trail_rv()$gene, " entity=", evidence_trail_rv()$entity)
    g <- evidence_trail_rv()$gene
    e <- evidence_trail_rv()$entity
    extra <- evidence_trail_rv()$extra
    html <- tryCatch(
      build_evidence_trail_html(g, e, extra),
      error = function(err) {
        paste0("<p style='color:#c0392b;'>Evidence Trail error: ", htmltools::htmlEscape(conditionMessage(err)), "</p>")
      }
    )
    shinyjs::runjs(sprintf(
      "document.getElementById('evidence_trail_body').innerHTML = %s; document.getElementById('evidence_drawer').style.display='block';",
      jsonlite::toJSON(html)
    ))
  }, ignoreInit = TRUE)

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
        textInput("contact_email_confirm", "Confirm your email:", placeholder = "e.g. john@example.com"),
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
    email <- trimws(input$contact_email %||% "")
    email_confirm <- trimws(input$contact_email_confirm %||% "")
    if (email != email_confirm) {
      showNotification("Email addresses do not match. Please re-enter them.", type = "warning")
      return()
    }
    name  <- trimws(input$contact_name %||% "")
    reply <- isTRUE(input$contact_reply)
    body  <- paste0(
      "Name: ", if (name != "") name else "Anonymous", "\n",
      "Email: ", if (email != "") email else "Not provided", "\n",
      "Reply requested: ", if (reply) "Yes" else "No", "\n\n",
      msg
    )
    smtp_user <- Sys.getenv("SMTP_USER")
    sendgrid_key <- Sys.getenv("SENDGRID_API_KEY")
    if (smtp_user == "" || sendgrid_key == "") {
      showNotification("Email not configured. Set SMTP_USER and SENDGRID_API_KEY in .Renviron.",
                       type = "error", duration = 8)
      return()
    }
    subject <- if (name != "") paste0("New comment from ", name, " (RCDome)") else "New comment from RCDome"
    result <- tryCatch({
      resp <- httr::POST(
        "https://api.sendgrid.com/v3/mail/send",
        httr::add_headers(
          Authorization = paste("Bearer", sendgrid_key),
          "Content-Type" = "application/json"
        ),
        body = jsonlite::toJSON(list(
          personalizations = list(list(to = list(list(email = "quique@uenf.br")))),
          from = list(email = smtp_user),
          subject = subject,
          content = list(list(type = "text/plain", value = body))
        ), auto_unbox = TRUE),
        encode = "raw"
      )
      if (httr::status_code(resp) %in% c(200, 201, 202)) {
        TRUE
      } else {
        showNotification(paste0("Failed to send (HTTP ", httr::status_code(resp), ")"),
                         type = "error", duration = 8)
        FALSE
      }
    }, error = function(e) {
      showNotification(paste0("Failed to send: ", conditionMessage(e)),
                       type = "error", duration = 8)
      FALSE
    })
    if (isTRUE(result)) {
      updateTextAreaInput(session, "contact_msg", value = "")
      updateTextInput(session, "contact_name", value = "")
      updateTextInput(session, "contact_email", value = "")
      updateTextInput(session, "contact_email_confirm", value = "")
      showNotification("Message sent!", type = "message")
      removeModal()
    }
  })

  # ── Multimedia description modals ────────────────────────────────────
  observeEvent(input$btn_audio_desc, {
    showModal(modalDialog(
      title = "Podcast Description",
      p("This audio explores how fragmented, heterogeneous, and sometimes contradictory scientific evidence can be transformed into a reliable, traceable atlas of human genes associated with regulated cell death. In a 45-minute two-host conversation, it moves from the expanding landscape of apoptosis, ferroptosis, pyroptosis, necroptosis, and cuproptosis through multi-database harmonization, the complementary AI-assisted research of DeepSeek, Consensus, and Elicit, and the human expert verification and adjudication that distinguish direct mechanistic roles from indirect associations. The discussion emphasizes that provenance matters as much as association counts — AI agreement is not mechanistic proof, and expert adjudication is not experimental validation — and closes with the interactive RCDome Shiny application as an evidence-governed framework for studying regulated cell death."),
      easyClose = TRUE,
      footer = modalButton("Close")
    ))
  })

  observeEvent(input$btn_video_desc, {
    showModal(modalDialog(
      title = "Video Description",
      p("This video presents the scientific architecture of RCDome, a multi-database human gene atlas of regulated cell death. Opening with the biological landscape of apoptosis, necroptosis, pyroptosis, ferroptosis, and cuproptosis, it explains why fragmented, heterogeneous evidence across 20 databases and resources required a harmonized, evidence-governed framework. It shows how complementary AI-assisted research through DeepSeek, Consensus, and Elicit scaled evidence analysis, why human expert verification and adjudication remained essential, and how the result — 22,473 gene–RCD associations across 53 RCD-related entities, every claim traceable to its source — became an interactive Shiny application. The documentary closes with the message that RCDome is not merely a gene atlas but a framework linking computational discovery, scientific verification, expert judgment, and interactive exploration."),
      easyClose = TRUE,
      footer = modalButton("Close")
    ))
  })


}
