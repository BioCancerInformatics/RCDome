# ─── UI ──────────────────────────────────────────────────────────────────────
if (!exists("genes_df", inherits = TRUE) || !exists("fingerprint_df", inherits = TRUE)) source("global.R")

ui <- tagList(
  # ── Reader Mode (first-visit guided tour trigger) ───────────────────
  mod_tour_ui("tour"),
  tags$button(
    "Start tour",
    id = "start_tour_btn",
    onclick = "Shiny.setInputValue('tour-first_visit', Math.random(), {priority:'event'});",
    style = "display:none; position:fixed; top:100px; right:24px; z-index:9998; background:#FF9800; color:#0b1020; border:none; border-radius:999px; padding:10px 22px; font-size:14px; font-weight:700; cursor:pointer; box-shadow:0 4px 14px rgba(0,0,0,.35);"
  ),
  tags$script(HTML("
    function toggleStartTourBtn() {
      var btn = document.getElementById('start_tour_btn');
      if (!btn) return;
      var homeTab = document.querySelector('a[data-toggle=\"tab\"][data-value=\"Home\"]');
      var active = homeTab && homeTab.parentElement.classList.contains('active');
      btn.style.display = active ? 'block' : 'none';
    }
    $(document).ready(function(){ setTimeout(toggleStartTourBtn, 400); });
    $(document).on('shown.bs.tab', 'a[data-toggle=\"tab\"]', function(){ setTimeout(toggleStartTourBtn, 60); });
  ")),
  # ── Evidence Trail drawer (global, shared) ──────────────────────────
  tags$div(
    id = "evidence_drawer",
    style = "display:none; position:fixed; top:0; right:0; width:40%; min-width:360px; height:100vh; background:#ffffff; box-shadow:-6px 0 24px rgba(0,0,0,0.22); z-index:9999; overflow-y:auto; padding:20px 22px;",
    tags$div(
      style = "display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;",
      tags$h3("Evidence Trail", style = "margin:0; color:#1c1917; font-weight:700;"),
      tags$button(
        "✕",
        onclick = "document.getElementById('evidence_drawer').style.display='none';",
        style = "border:none; background:none; font-size:20px; cursor:pointer; color:#78716c;"
      )
    ),
    tags$div(id = "evidence_trail_body")
  ),
  tags$div(
    id = "busy_overlay",
    style = "position:fixed; top:0; left:0; width:100%; height:100%; display:none; align-items:center; justify-content:center; background:rgba(255,255,255,0.88); z-index:9999;",
    tags$div(
      style = "text-align:center;",
      tags$div(class = "spinner-border", role = "status",
               style = "width:3rem; height:3rem; color:#FF9800;"),
      tags$p("Retrieving and rendering RCDome data…",
             style = "margin-top:12px; color:#1c1917; font-size:14px;")
    )
  ),
  tags$script(HTML("
    $(function() {
      var rcd_busy_timer = null;
      $(document).on('shiny:busy', function() {
        rcd_busy_timer = setTimeout(function() {
          var o = document.getElementById('busy_overlay');
          if (o) o.style.display = 'flex';
        }, 500);
      });
      $(document).on('shiny:idle', function() {
        if (rcd_busy_timer) clearTimeout(rcd_busy_timer);
        var o = document.getElementById('busy_overlay');
        if (o) o.style.display = 'none';
      });
    });
  ")),
  navbarPage(
  title = HTML(rcdome_span()),
  id    = "main_nav",

  # ── Home = FRONT PAGE ─────────────────────────────────────────────────
  # The first tab in navbarPage() is selected by default on app launch.
  # It embeds landing_page.html (the interactive dome + 7 module cards),
  # which self-navigates to detail_page_wireframe.html on node/gene click.
  tabPanel(
    title = "Home",
    tags$div(
      style = "position:relative; width:100%; height:calc(100vh - 100px);",
      tags$iframe(
        id = "home_iframe",
        src = "landing_page.html?v=5",
        style = "width:100%; height:100%; border:none; display:block;",
        scrolling = "auto"
      ),
      tags$div(
        id = "home_loading_overlay",
        style = "position:absolute; top:0; left:0; width:100%; height:100%; display:none; align-items:center; justify-content:center; background:#ffffff; z-index:20;",
        tags$div(
          style = "text-align:center;",
          tags$div(class = "spinner-border", role = "status",
                   style = "width:3rem; height:3rem; color:#FF9800;"),
          tags$p("Retrieving and rendering RCDome data…", style = "margin-top:12px; color:#1c1917; font-size:14px;")
        )
      )
    )
  ),

  # ── Explore RCDome (educational/exploratory guide) ─────────────────
  tabPanel(
    title = HTML(paste0("Explore ", rcdome_span())),
    tags$iframe(
      id = "explore_iframe",
      src = "explore.html?v=20261017",
      style = "width:100%; height:calc(100vh - 100px); border:none; display:block;",
      scrolling = "auto"
    )
  ),

  # ── Operational Definitions ─────────────────────────────────────────
  tabPanel(
    title = "Operational Definitions",
    div(class = "wrap",
      style = "max-width: 1160px; margin: 0 auto; padding: 20px;",
      mod_od_ui("od")
    )
  ),

  # ── Compare Definitions ─────────────────────────────────────────
  tabPanel(
    title = "Compare Definitions",
    div(class = "wrap",
      style = "max-width: 1200px; margin: 0 auto; padding: 20px;",
      mod_od_compare_ui("od_compare")
    )
  ),

  # ── RCD entities ───────────────────────────────────────────────────
  tabPanel(
    title = "RCD entities",
    div(class = "wrap",
      style = "max-width: 1100px; margin: 0 auto; padding: 20px;",
      mod_rcd_entities_ui("rcd_entities")
    )
  ),

  # ── Gene Catalog ──────────────────────────────────────────────────
  tabPanel(
    title = "Gene Catalog",
    div(class = "wrap",
      style = "max-width: 1100px; margin: 0 auto; padding: 20px;",
      mod_gene_catalog_ui("gene_catalog")
    )
  ),

  # ── Discrepancy Radar ─────────────────────────────────────────────
  tabPanel(
    title = "Discrepancy Radar",
    div(class = "wrap",
      style = "max-width: 1200px; margin: 0 auto; padding: 20px;",
      mod_discrepancy_ui("discrepancy")
    )
  ),

  # ── Discovery Timeline ────────────────────────────────────────────
  tabPanel(
    title = "Discovery Timeline",
    div(class = "wrap",
      style = "max-width: 1200px; margin: 0 auto; padding: 20px;",
      mod_timeline_ui("timeline")
    )
  ),

  tabPanel(
    title = HTML(paste0(rcdome_span(), " Board")),
    div(class = "wrap",
      style = "max-width: 1160px; margin: 0 auto; padding: 24px 20px 40px;",
      mod_board_ui("board")
    )
  ),

  # ── Network ───────────────────────────────────────────────────────────
  tabPanel(
    title = "Network",
    div(class = "wrap",
      style = "max-width: 1200px; margin: 0 auto; padding: 20px;",
      mod_network_ui("network")
    )
  ),

  # ── 3D RCDome ────────────────────────────────────────────────────────
  tabPanel(
    title = HTML(paste0("3D ", rcdome_span())),
    tags$iframe(
      id = "dome3d_iframe",
      src = "dome_3d.html",
      style = "width:100%; height:calc(100vh - 100px); border:none; display:block;",
      scrolling = "no"
    )
  ),

  # ── Multimedia ─────────────────────────────────────────────────────────
  tabPanel(
    title = "Multimedia",
    div(
      style = "background:#0b1020; min-height:calc(100vh - 100px); padding: 28px 20px;",
      div(style = "max-width: 1200px; margin: 0 auto;",
        tags$div(style = "margin-bottom:24px;",
          tags$h1("Multimedia", style = "font-size:35px; margin:0; color:#ffffff;"),
          tags$p("Video and audio presentations covering the core concepts and findings of RCDome.",
                 style = "color:#a8a29e; margin:6px 0 0; font-size:15px;")
        ),
        fluidRow(
          column(6,
            tags$div(style = "background:#131a2e; border:1px solid #1e293b; border-radius:12px; padding:20px; height:100%;",
              tags$div(style = "display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;",
                tags$h4(style = "color:#60a5fa; margin:0;", "🎧 Podcast"),
                actionButton("btn_audio_desc", "Description", icon = icon("info-circle"),
                             class = "btn btn-sm", style = "color:#60a5fa; border:1px solid #60a5fa; background:transparent;")
              ),
              tags$h5("RCDome: How AI Audited Cell Death Databases",
                      style = "color:#cbd5e1; margin-bottom:16px; font-weight:600;"),
              tags$audio(controls = NA, style = "width:100%; outline:none;",
                tags$source(src = "media/002_Media_Potscat_How_AI_Audited_Cell_Death_Databases.m4a", type = "audio/mp4")
              )
            )
          ),
          column(6,
            tags$div(style = "background:#131a2e; border:1px solid #1e293b; border-radius:12px; padding:20px; height:100%;",
              tags$div(style = "display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;",
                tags$h4(style = "color:#f87171; margin:0;", "🎬 Video Presentation"),
                actionButton("btn_video_desc", "Description", icon = icon("info-circle"),
                             class = "btn btn-sm", style = "color:#f87171; border:1px solid #f87171; background:transparent;")
              ),
              tags$h5("RCDome: A Multi-Database Human Gene Atlas of Regulated Cell Death",
                      style = "color:#cbd5e1; margin-bottom:16px; font-weight:600;"),
              tags$video(controls = NA, style = "width:100%; border-radius:8px;",
                tags$source(src = "media/001_Media_Video_RCDome.mp4", type = "video/mp4")
              )
            )
          )
        )
      )
    )
  ),

  # ── Evidence ─────────────────────────────────────────────────────────────
  # ── RCDchat ───────────────────────────────────────────────────────────
  # ── Infographics ─────────────────────────────────────────────────────────
  tabPanel(
    title = "Infographics",
    div(
      style = "background:#0b1020; min-height:calc(100vh - 100px); padding: 28px 20px;",
      div(style = "max-width: 1400px; margin: 0 auto;",
        tags$div(style = "display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:12px;",
          tags$div(
            tags$h1("Infographics", style = "font-size:35px; margin:0; color:#ffffff;"),
            tags$p("Regulated Cell Death Atlas — overview of the information sources behind the RCDome scientific podcast.",
                   style = "color:#a8a29e; margin:6px 0 0; font-size:15px;")
          ),
          tags$button("⛶ Full screen",
            onclick = "var el = document.getElementById('infograph_img'); if (el.requestFullscreen) { el.requestFullscreen(); } else if (el.webkitRequestFullscreen) { el.webkitRequestFullscreen(); } else if (el.msRequestFullscreen) { el.msRequestFullscreen(); }",
            style = "background:#FF9800; color:#0b1020; border:none; border-radius:8px; padding:8px 18px; font-size:14px; font-weight:700; cursor:pointer;")
        ),
        tags$div(style = "background:#131a2e; border:1px solid #1e293b; border-radius:12px; padding:20px;",
          tags$img(id = "infograph_img", src = "infographics/003_Infograph_Regulated_Cell_Death_Atlas_Overview.png",
                   alt = "Regulated Cell Death Atlas Overview infographic",
                   style = "width:100%; height:auto; display:block; border-radius:8px;")
        )
      )
    )
  ),

  # ── About ─────────────────────────────────────────────────────────────
  tabPanel(
    title = "About",
    div(class = "wrap", style = "max-width: 1100px; margin: 0 auto; padding: 20px;",
      tags$div(style = "background:#0b1020; color:#e7e5e4; border-radius:12px; padding:28px 26px; margin-bottom:24px;",
        tags$h1("About", style = "font-size:35px; margin:0;"),
        tags$p(HTML(paste0("The ", rcdome_span(), " Atlas — a multi-database human gene atlas of regulated cell death.")),
               style = "color:#d6d3d1; margin:6px 0 0; font-size:15px;"),
        tags$button("Replay tour",
          onclick = "localStorage.removeItem('rcdome_tour_seen'); Shiny.setInputValue('tour-first_visit', Math.random(), {priority:'event'});",
          style = "margin-top:14px; background:#FF9800; color:#0b1020; border:none; border-radius:8px; padding:6px 16px; font-size:13px; font-weight:700; cursor:pointer;")
      ),
      h3(HTML(paste0("Who built ", rcdome_span()))),
      uiOutput("dev_cards"),

      h3("Related platforms", style = "margin-top: 56px;"),
      p(class = "lede", "Other tools from LBTGenomica/UENF"),
      div(class = "see-also",
        a(href = "https://cancerrcdshiny.shinyapps.io/cancerrcdshiny/", target = "_blank", rel = "noopener",
          img(src = "see_also/CancerRCDShiny.png", class = "sa-logo", alt = "CancerRCDShiny logo"),
          span(class = "sa-text",
            span(class = "sa-name", "CancerRCDShiny"),
            span(class = "sa-url", "cancerrcdshiny.shinyapps.io"))),
        a(href = "https://oncometabolismgps.be/", target = "_blank", rel = "noopener",
          img(src = "see_also/Cancer_metabolism_GPS.png", class = "sa-logo", alt = "OncometabolismGPS logo"),
          span(class = "sa-text",
            span(class = "sa-name", "OncometabolismGPS"),
            span(class = "sa-url", "oncometabolismgps.be"))),
        a(href = "https://sigpolytope.shinyapps.io/geometricatlas/", target = "_blank", rel = "noopener",
          img(src = "see_also/sigpolytope.svg", class = "sa-logo", alt = "SigPolytope logo"),
          span(class = "sa-text",
            span(class = "sa-name", "SigPolytope"),
            span(class = "sa-url", "sigpolytope.shinyapps.io/geometricatlas"))),
        a(href = "https://lbtgenomica.uenf.br/cancerrcdpredictor/", target = "_blank", rel = "noopener",
          img(src = "see_also/CancerRCDPredictor.png", class = "sa-logo", alt = "CancerRCDPredictor logo"),
          span(class = "sa-text",
            span(class = "sa-name", "CancerRCDPredictor"),
            span(class = "sa-url", "lbtgenomica.uenf.br")))
      ),

      h3("Data provenance", style = "margin-top: 56px;"),
      p(class = "lede", "Where each gene–RCD association comes from"),
      uiOutput("data_sources")
    )
  ),

  # ── CSS + Fonts ────────────────────────────────────────────────────────
  header = tags$head(
    shinyjs::useShinyjs(),
    tags$link(rel = "icon", type = "image/svg+xml", href = "rcdome_logo.svg"),
    tags$script(src = "contact_intercept.js"),
    tags$style(HTML("
      :root {
        --ink: #1c1917;
        --paper: #f5f5f4;
        --paper-raised: #ffffff;
        --navy: #0b1020;
        --rust: #c2410c;
        --gold: #FFD700;
        --orange: #FF9800;
        --grey: #a8a29e;
        --line: #e7e5e4;
      }
      body {
        background: #f5f5f4;
        font-family: 'Segoe UI', system-ui, sans-serif;
        -webkit-font-smoothing: antialiased;
      }

      .navbar {
        background: #ffffff;
        border-bottom: 1px solid var(--line);
        font-family: 'Segoe UI', system-ui, sans-serif;
        margin-bottom: 0 !important;
      }
      .navbar-brand, .navbar-nav > li > a {
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 15px;
        letter-spacing: 0.03em;
        font-weight: 700;
      }
      .navbar-brand { color: #1c1917 !important; }
      .navbar-nav > li > a { color: #374151 !important; }
      .navbar-nav > li > a:hover { color: #c2410c !important; }
      .navbar-nav > li.active > a { color: #FF9800 !important; border-bottom: 2px solid #FF9800 !important; }
      #infograph_img:fullscreen { width:100%; height:100%; object-fit:contain; background:#0b1020; }
      #infograph_img:-webkit-full-screen { width:100%; height:100%; object-fit:contain; background:#0b1020; }
      h3, h4 { font-family: 'Segoe UI', system-ui, sans-serif; color: var(--ink); }
      .rc-pill { display:inline-block; padding:2px 8px; border-radius:10px; font-size:12px; font-weight:600; }
      .pill-gold   { background:#fef3c7; color:#92400e; }
      .pill-blue   { background:#dbeafe; color:#1e40af; }
      .pill-green  { background:#dcfce7; color:#166534; }
      .pill-purple { background:#f3e8ff; color:#6b21a8; }
      .pill-orange { background:#ffedd5; color:#9a3412; }
      .pill-red    { background:#fee2e2; color:#991b1b; }
      .pill-gray   { background:#f1f5f9; color:#475569; }
      .pill-teal   { background:#ccfbf1; color:#115e59; }
      .pill-amber  { background:#fef9c3; color:#854d0e; }
      /* DT tables — match the RCDome detail-page typography */
      table.dataTable { font-size: 13.6px !important; font-family: 'Segoe UI', system-ui, sans-serif !important; }
      table.dataTable thead th { font-size: 12.5px !important; text-transform: uppercase; letter-spacing: 0.05em; color: #57534e !important; }
      table.dataTable tbody td { font-size: 13.6px !important; }
      table.dataTable th, table.dataTable td { padding: 8px 10px !important; border-bottom: 1px solid #f0efed !important; }
      .wrap { max-width: 1100px; margin: 0 auto; padding: 0 32px; }
      .about-content {
        width: 100%;
        max-width: 1160px;
        margin: 0 auto;
        padding: 40px 20px;
        box-sizing: border-box;
      }

      /* Hero */
      .hero {
        display: grid;
        grid-template-columns: 1.1fr 0.9fr;
        gap: 56px;
        padding: 18px 0 40px;
        border-bottom: 1px solid var(--line);
        align-items: center;
      }
      .eyebrow {
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 12px; letter-spacing: 0.08em;
        color: var(--rust); text-transform: uppercase;
        margin-bottom: 18px;
      }
      h1 {
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-weight: 500; font-size: 44px;
        line-height: 1.12; margin: 0 0 22px;
      }
      h1 i { color: var(--navy); font-style: italic; }
      .lede {
        font-size: 16px; line-height: 1.65;
        color: #57534e; max-width: 46ch;
        margin: 0 0 26px;
      }
      .lede b { color: var(--ink); font-weight: 600; }
      .hero-actions { display: flex; gap: 14px; }
      .btn {
        font-size: 13px; font-weight: 500; letter-spacing: 0.02em;
        padding: 11px 20px; cursor: pointer;
        border: 1px solid var(--ink);
        text-decoration: none; color: var(--ink);
        transition: background .15s ease, color .15s ease;
      }
      .btn.primary { background: var(--rust); border-color: var(--rust); color: var(--paper); }
      .btn.primary:hover { background: var(--ink); border-color: var(--ink); }
      .btn:not(.primary):hover { background: var(--ink); color: var(--paper); }
      .shiny-progress-notification {
        position: fixed !important; top: 50% !important; left: 50% !important;
        transform: translate(-50%, -50%) !important; right: auto !important; bottom: auto !important;
        width: 340px !important; max-width: 86vw;
        background: #fff7ed !important; border: 2px solid #FF9800 !important; border-radius: 12px !important;
        padding: 18px 22px !important; z-index: 9999 !important;
        box-shadow: 0 14px 40px rgba(0,0,0,0.28) !important;
      }
      .shiny-progress .bar { background: #FF9800 !important; height: 8px !important; border-radius: 6px !important; }
      .shiny-progress .progress-text { color: #c2410c !important; font-weight: 700 !important; font-size: 14px !important; font-family: 'Segoe UI', system-ui, sans-serif !important; }
      .hero-visual {
        display: flex; align-items: center; justify-content: center;
        width: 100%; overflow: hidden;
      }
      .hero-logo {
        display: block; width: 110%; max-width: 540px;
        height: auto; object-fit: contain;
      }

      /* Index */
      .index { padding: 56px 0 40px; }
      .index-head {
        display: flex; justify-content: space-between; align-items: baseline;
        margin-bottom: 8px;
      }
      .index-title {
        font-family: 'Segoe UI', system-ui, sans-serif; font-size: 15px;
        text-transform: uppercase; letter-spacing: 0.08em; color: #57534e;
      }
      .index-count {
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 12px; color: var(--grey);
      }
      .atlas-row {
        display: grid;
        grid-template-columns: 44px minmax(100px, 160px) minmax(0, 1fr) 20px;
        align-items: center; gap: 18px;
        padding: 22px 0;
        border-top: 1px solid var(--line);
        text-decoration: none; color: inherit;
        cursor: pointer;
        transition: padding-left .15s ease;
      }
      .atlas-row:last-child { border-bottom: 1px solid var(--line); }
      .atlas-row:hover { padding-left: 8px; }
      .atlas-row:hover .row-name { color: var(--rust); }
      .atlas-row:hover .arrow { transform: translateX(4px); opacity: 1; }
      .tag {
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 13px; color: var(--navy);
        border: 1px solid var(--line);
        width: 38px; height: 38px;
        display: flex; align-items: center; justify-content: center;
      }
      .row-name {
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 19px; transition: color .15s ease;
      }
      .row-desc {
        font-size: 13.5px; color: var(--grey); line-height: 1.5;
      }
      .arrow {
        color: var(--rust); opacity: 0;
        transform: translateX(0); transition: .15s ease; font-size: 16px;
      }

      /* Footer */
      footer {
        border-top: 1px solid var(--line);
        padding: 26px 0 40px;
        display: flex; justify-content: space-between;
        font-size: 12px; color: var(--grey);
        font-family: 'Segoe UI', system-ui, sans-serif;
      }

      /* Evidence search row */
      .rcdmap-search-row {
        display: flex; align-items: flex-end; gap: 15px; flex-wrap: wrap;
      }
      .rcdmap-search-row .form-group { margin-bottom: 0; }
      .search-evidence-btn {
        height: 38px; margin: 0;
        padding: 0 24px;
        display: inline-flex; align-items: center; justify-content: center;
        background: var(--navy) !important; color: #FFFFFF !important;
        border: none; font-size: 13px; font-weight: 500;
        letter-spacing: 0.02em; cursor: pointer;
        transition: background .15s ease;
      }
      .rcdmap-search-row .search-evidence-btn { margin-top: 25px; }
      .modal-footer .btn {
        height: 38px; padding: 0 24px;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 13px; font-weight: 500;
      }
      .modal-footer .btn-default { background: #FFFFFF; border: 1px solid var(--line); }
      .rcd-download-btn {
        height: 38px; padding: 0 16px;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 13px; font-weight: 500; border-radius: 6px;
        background: transparent !important;
        border: 1px solid var(--line) !important;
        color: var(--grey) !important;
        box-shadow: none !important;
        text-decoration: none;
        transition: border-color .15s ease, color .15s ease;
      }
      .rcd-download-btn:hover {
        background: transparent !important;
        border-color: var(--navy) !important;
        color: var(--navy) !important;
      }
      .rcd-media-toggle {
        flex-shrink: 0;
        width: 38px; height: 38px;
        border-radius: 50%;
        border: 1px solid var(--line);
        background: transparent;
        color: var(--grey);
        font-size: 16px; line-height: 1;
        cursor: pointer;
        display: inline-flex; align-items: center; justify-content: center;
        transition: border-color .15s ease, color .15s ease;
      }
      .rcd-media-toggle:hover {
        border-color: var(--navy);
        color: var(--navy);
      }
      .rcd-ref-toggle {
        height: 34px; padding: 0 14px;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 12.5px; font-weight: 500; letter-spacing: 0.02em;
        background: transparent !important;
        border: 1px solid var(--line) !important;
        border-radius: 999px;
        color: var(--grey) !important;
        cursor: pointer;
        box-shadow: none !important;
        transition: border-color .15s ease, color .15s ease;
      }
      .rcd-ref-toggle:hover {
        background: transparent !important;
        border-color: var(--navy) !important;
        color: var(--navy) !important;
      }
      .rcd-view-toggle {
        height: 32px; padding: 0 14px;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 12.5px; font-weight: 500; letter-spacing: 0.02em;
        background: transparent !important;
        border: 1px solid var(--line) !important;
        border-radius: 999px;
        color: var(--grey) !important;
        cursor: pointer;
        box-shadow: none !important;
        transition: border-color .15s ease, color .15s ease, background .15s ease;
      }
      .rcd-view-toggle:hover {
        border-color: var(--navy) !important;
        color: var(--navy) !important;
      }
      .rcd-view-toggle.active {
        background: var(--navy) !important;
        border-color: var(--navy) !important;
        color: #FFFFFF !important;
      }
      .see-also {
        display: flex; flex-wrap: wrap; gap: 14px; margin-top: 12px;
      }
      .see-also a {
        display: inline-flex; flex-direction: row; align-items: center; gap: 14px;
        padding: 14px 18px;
        border: 1px solid var(--line); border-radius: 8px;
        text-decoration: none; color: var(--ink);
        transition: border-color .15s ease, color .15s ease;
      }
      .see-also a:hover { border-color: var(--rust); color: var(--rust); }
      .see-also .sa-logo {
        height: 44px; width: 44px; object-fit: contain; flex-shrink: 0;
      }
      .see-also .sa-text { display: flex; flex-direction: column; gap: 4px; }
      .see-also .sa-name { font-weight: 600; font-size: 14px; }
      .see-also .sa-url {
        font-family: 'Segoe UI', system-ui, sans-serif; font-size: 11px; color: var(--grey);
      }
      .search-evidence-btn:hover { background: var(--rust); }

      /* RCDchat — ChatGPT-style layout ------------------------------------ */
      .rcdchat-shell {
        display: flex; flex-direction: column;
        height: min(85vh, 950px); min-height: 600px;
        border: 1px solid var(--line); border-radius: 16px;
        background: #FFFFFF; overflow: hidden;
        box-shadow: 0 1px 2px rgba(20,23,28,0.05);
      }
      .rcdchat-topbar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 14px 20px; border-bottom: 1px solid var(--line);
        flex-shrink: 0;
      }
      .rcdchat-title-group { display: flex; align-items: center; gap: 12px; }
      .rcdchat-mark {
        width: 32px; height: 32px; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        background: var(--navy); color: #FFFFFF;
        font-family: 'Segoe UI', system-ui, sans-serif; font-size: 12px; font-weight: 500;
        border-radius: 8px;
      }
      .rcdchat-title {
        font-family: 'Segoe UI', system-ui, sans-serif; font-size: 12.5px;
        letter-spacing: 0.06em; text-transform: uppercase; color: var(--ink);
        line-height: 1.3;
      }
      .rcdchat-badge {
        font-family: 'Segoe UI', system-ui, sans-serif; font-size: 11px; color: var(--grey);
        border: 1px solid var(--line); border-radius: 999px;
        padding: 2px 10px; display: inline-block; margin-top: 4px;
      }
      .rcdchat-badge-gene { color: var(--rust); border-color: var(--rust); }
      .rcdchat-newchat-btn {
        background: #FFFFFF !important; color: var(--ink) !important;
        border: 1px solid var(--line) !important; border-radius: 999px !important;
        padding: 7px 16px !important; font-size: 12.5px !important;
        font-weight: 500; box-shadow: none !important;
      }
      .rcdchat-newchat-btn:hover { border-color: var(--rust) !important; color: var(--rust) !important; }
      .rcdchat-scroll {
        flex: 1 1 auto; overflow-y: auto; background: #FFFFFF;
        padding: 22px 0 10px;
      }
      .rcdchat-empty {
        color: #57534e; font-style: italic; text-align: center;
        max-width: 420px; margin: 90px auto 0; font-size: 13.5px; line-height: 1.6;
      }
      .rcdchat-row {
        max-width: 720px; margin: 0 auto; padding: 8px 24px;
      }
      .rcdchat-row-user { display: flex; justify-content: flex-end; }
      .rcdchat-row-assistant { display: flex; align-items: flex-start; gap: 12px; }
      .rcdchat-bubble-user {
        background: var(--paper-raised); color: var(--ink);
        border-radius: 18px; padding: 10px 16px;
        font-size: 14.5px; line-height: 1.55; max-width: 78%;
        white-space: pre-wrap; word-break: break-word;
      }
      .rcdchat-avatar {
        width: 28px; height: 28px; flex-shrink: 0; margin-top: 2px;
        border-radius: 8px; background: var(--rust); color: #FFFFFF;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Segoe UI', system-ui, sans-serif; font-size: 10.5px; font-weight: 500;
      }
      .rcdchat-assistant-text {
        font-size: 14.5px; line-height: 1.65; color: var(--ink);
        max-width: 82%; white-space: pre-wrap; word-break: break-word;
        padding-top: 3px;
      }
      .rcdchat-assistant-text a { color: var(--navy); }
      .rcdchat-assistant-text a:hover { color: var(--rust); }
      .rcdchat-typing {
        display: flex; align-items: center; gap: 4px; padding: 9px 0 0 0;
      }
      .rcdchat-typing .dot {
        width: 6px; height: 6px; border-radius: 50%; background: var(--grey);
        animation: rcdchat-bounce 1.2s infinite ease-in-out;
      }
      .rcdchat-typing .dot:nth-child(2) { animation-delay: 0.15s; }
      .rcdchat-typing .dot:nth-child(3) { animation-delay: 0.3s; }
      @keyframes rcdchat-bounce {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
        30% { transform: translateY(-4px); opacity: 1; }
      }
      .rcdchat-suggested {
        flex-shrink: 0; padding: 14px 20px 6px;
        border-bottom: 1px solid var(--line); background: #FFFFFF;
        display: flex; flex-direction: column; gap: 8px;
      }
      .rcdchat-chip {
        display: block !important;
        width: 100% !important;
        text-align: left !important;
        background: #f5f5f4 !important;
        color: #1c1917 !important;
        border: 1px solid #e7e5e4 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        line-height: 1.45 !important;
        min-height: 46px !important;
        box-shadow: none !important;
        white-space: normal !important;
        word-break: break-word !important;
      }
      .rcdchat-chip:hover {
        border-color: var(--rust) !important;
        color: var(--rust) !important;
        background: #ffffff !important;
      }
      .rcdchat-composer {
        flex-shrink: 0; border-top: 1px solid var(--line);
        padding: 14px 24px 16px; background: #FFFFFF;
      }
      .rcdchat-input-shell {
        max-width: 720px; margin: 0 auto;
        display: flex; align-items: flex-end; gap: 8px;
        border: 1px solid var(--line); border-radius: 24px;
        padding: 7px 7px 7px 18px; background: #FFFFFF;
        transition: border-color .15s ease;
      }
      .rcdchat-input-shell:focus-within { border-color: var(--navy); }
      .rcdchat-textarea {
        flex: 1 1 auto; border: none !important; outline: none !important;
        box-shadow: none !important; resize: none; background: transparent;
        font-size: 14.5px; line-height: 1.5; padding: 7px 0 !important;
        max-height: 160px; min-height: 24px; font-family: 'Segoe UI', system-ui, sans-serif;
      }
      .rcdchat-textarea::placeholder {
        color: #57534e; opacity: 1;
      }
      .rcdchat-send-btn {
        flex-shrink: 0; width: 34px; height: 34px; min-height: 34px;
        border-radius: 50% !important; background: var(--ink) !important;
        color: #FFFFFF !important; border: none !important;
        display: flex; align-items: center; justify-content: center;
        padding: 0 !important; font-size: 15px; line-height: 1;
        box-shadow: none !important;
      }
      .rcdchat-send-btn:hover { background: var(--rust) !important; }
      .rcdchat-hint {
        max-width: 720px; margin: 8px auto 0; text-align: center;
        font-size: 11px; color: #57534e;
      }
      .rcdchat-copy-btn {
        display: inline-block;
        margin-top: 6px;
        padding: 3px 10px;
        font-size: 11px;
        font-weight: 500;
        color: #57534e;
        background: #ffffff;
        border: 1px solid #e7e5e4;
        border-radius: 999px;
        cursor: pointer;
      }
      .rcdchat-copy-btn:hover { border-color: var(--rust); color: var(--rust); }

      /* Pathway Fingerprint interactions */
      #fingerprint_plot { transition: height .42s cubic-bezier(.4,0,.2,1); }
      #fingerprint_plot .ytick text {
        cursor: pointer;
        transition: fill .15s ease, font-weight .15s ease;
      }
      #fingerprint_plot .ytick text:hover {
        fill: var(--navy) !important;
        font-weight: 600;
      }
      #fingerprint_plot .legendtoggle { cursor: pointer !important; }

      .landscape-section { padding: 40px 0; border-top: 1px solid var(--line); }

      @media (max-width: 800px) {
        .hero { grid-template-columns: 1fr; padding: 44px 0; }
        h1 { font-size: 32px; }
        .atlas-row { grid-template-columns: 44px 1fr; row-gap: 8px; }
        .row-desc { grid-column: 1/-1; }
        .rcdmap-search-row { flex-direction: column; align-items: stretch; }
        .rcdmap-search-row .form-group { width: 100%; }
        .search-evidence-btn { width: 100%; }
      }
    "))
  )
)
)
