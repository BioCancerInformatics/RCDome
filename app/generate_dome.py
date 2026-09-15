#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the RCDome dome (standalone) + integrated landing page with REAL V026 data.
Outputs:
  - Shiny app/dome_prototype.html   (standalone full-screen dome)
  - Shiny app/landing_page.html     (integrated: header + hero dome + legend + 7 modules + footer)
"""
import pandas as pd, json
from collections import Counter

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
v23 = pd.read_csv(BASE + "/output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv",
                  dtype=str, keep_default_na=False)

def short(l):
    return {'L1 Modalities':'L1','L2 Subtypes':'L2','L3 Triggers':'L3',
            'L4 Functional/conceptual':'L4','L5 Generic/composite':'L5'}.get(l,'L5')

LEVEL_COLORS = {'L1':'#FFD700','L2':'#00B0FF','L3':'#00E676','L4':'#E040FB','L5':'#FF6D00'}

lvl_map = {r['rcd_form_canonical']: short(r['rcdome_level_name'])
           for _, r in v23.drop_duplicates('rcd_form_canonical').iterrows()}

entities = []
for form, grp in v23.groupby('rcd_form_canonical'):
    entities.append({'name': form, 'level': lvl_map.get(form,'L5'), 'n': int(grp.gene_symbol.nunique())})
entities.sort(key=lambda e: (-e['n'], e['name']))

gene_ents = v23.groupby('gene_symbol')['rcd_form_canonical'].nunique()
top_genes = gene_ents.nlargest(400).index.tolist()
genes = []
for g in top_genes:
    forms = sorted(v23[v23.gene_symbol==g]['rcd_form_canonical'].unique())
    genes.append({'symbol': g, 'forms': forms})

DATA = {'entities': entities, 'genes': genes}
counts = dict(Counter(e['level'] for e in entities))

# ============================================================
# Shared JS (dome drawing + interactivity) — used by both pages
# ============================================================
JS = """<script>
const DATA = __DATA__;
const LEVEL_COUNTS = __COUNTS__;
const LEVEL_COLORS = {L1:"#FFD700", L2:"#00B0FF", L3:"#00E676", L4:"#E040FB", L5:"#FF6D00"};
const LEVEL_NAMES = {L1:"L1 modalities", L2:"L2 subtypes", L3:"L3 triggers", L4:"L4 Functional/contextual", L5:"L5 Generic/umbrella/legacy/taxon/emerging"};

// legend
document.getElementById("legend").innerHTML = Object.entries(LEVEL_NAMES).map(([k,v]) =>
  `<span class="lg" data-level="${k}"><i style="background:${LEVEL_COLORS[k]}"></i>${v} (${LEVEL_COUNTS[k]})</span>`).join("");

// flattened dome: semi-ellipse, wide (RX) and short (RY)
const W=1200, H=420, CX=600, CY=400, RX=580, RY=380;

const svg = d3.select("#dome").append("svg")
  .attr("viewBox", `0 0 ${W} ${H}`).attr("preserveAspectRatio","xMidYMax meet");

const pt = (theta) => ({ x: CX + RX*Math.cos(theta), y: CY - RY*Math.sin(theta) });
const arcPath = (rx, ry) => {
  return `M ${CX - rx} ${CY} A ${rx} ${ry} 0 0 1 ${CX + rx} ${CY}`;
};

// girded: rings (inner ellipses) + ribs
[0.33, 0.66].forEach(f => svg.append("path").attr("d", arcPath(RX*f, RY*f))
  .attr("fill","none").attr("stroke","#b45309").attr("stroke-width",1).attr("opacity",0.5));
const N_RIBS = 18;
for (let k=1;k<N_RIBS;k++){
  const th = Math.PI*(1-k/N_RIBS), p = pt(th), top = pt(Math.PI/2);
  svg.append("line").attr("x1",top.x).attr("y1",top.y).attr("x2",p.x).attr("y2",p.y)
     .attr("stroke","#b45309").attr("stroke-width",0.8).attr("opacity",0.4);
}
// outer shell
svg.append("path").attr("d", arcPath(RX, RY))
   .attr("fill","none").attr("stroke","#FFD700").attr("stroke-width",3);
// base
svg.append("line").attr("x1",CX-RX).attr("y1",CY).attr("x2",CX+RX).attr("y2",CY)
   .attr("stroke","#57534e").attr("stroke-width",1.5).attr("opacity",0.7);

// stars = real genes, placed inside the flattened dome
const genes = DATA.genes;
let seed = 7; const rand = () => (seed=(seed*16807)%2147483647)/2147483647;
const starData = genes.map(g => {
  const u = rand(), th = rand()*Math.PI;
  return { ...g, x: CX + RX*Math.sqrt(u)*Math.cos(th), y: CY - RY*Math.sqrt(u)*Math.sin(th), s: 1.5+rand()*1.6 };
});
const star = svg.selectAll("circle.star").data(starData).join("circle")
  .attr("cx",d=>d.x).attr("cy",d=>d.y).attr("r",d=>d.s)
  .attr("fill","#cbd5e1").attr("opacity",0.5).style("cursor","pointer");

// nodes = 53 entities on the ellipse surface (L1 golden + larger)
const nodeData = DATA.entities.map((e,i) => {
  const th = Math.PI*(1 - i/(DATA.entities.length-1));
  const p = pt(th);
  return { ...e, x:p.x, y:p.y, color:LEVEL_COLORS[e.level] };
});
const glow = svg.append("defs").append("filter").attr("id","glow")
  .attr("x","-60%").attr("y","-60%").attr("width","220%").attr("height","220%");
glow.append("feGaussianBlur").attr("stdDeviation","3").attr("result","blur");
glow.append("feMerge").selectAll("feMergeNode")
  .data(["blur","SourceGraphic"]).join("feMergeNode").attr("in", d=>d);
const node = svg.selectAll("g.node").data(nodeData).join("g")
  .attr("transform",d=>`translate(${d.x},${d.y})`).style("cursor","pointer");
node.append("circle")
  .attr("r", d => d.level==="L1" ? 9 : 6.5)
  .attr("fill", d=>d.color).attr("stroke","#fff").attr("stroke-width",1.5)
  .attr("filter","url(#glow)");

// threads: connect each gene to its REAL entities (top 2)
const threads = [];
starData.forEach((g, gi) => {
  g.forms.slice(0, 2).forEach(f => {
    const e = nodeData.find(n => n.name === f);
    if (e) threads.push({ gi, entity: f, level: e.level, x1:g.x, y1:g.y, x2:e.x, y2:e.y });
  });
});
const line = svg.selectAll("line.thread").data(threads).join("line")
  .attr("x1",d=>d.x1).attr("y1",d=>d.y1).attr("x2",d=>d.x2).attr("y2",d=>d.y2)
  .attr("stroke","#FFD700").attr("stroke-width",0.7).attr("opacity",0.18);

// interactivity
const tip = d3.select("body").append("div").attr("class","tip");
let activeLevel = null;

const nodeOpacity = d => !activeLevel ? 1 : (d.level === activeLevel ? 1 : 0.12);
const starOpacity = d => {
  if (!activeLevel) return 0.5;
  const hit = d.forms.some(f => { const e = nodeData.find(n => n.name === f); return e && e.level === activeLevel; });
  return hit ? 0.85 : 0.04;
};
const threadOpacity = t => !activeLevel ? 0.18 : (t.level === activeLevel ? 0.7 : 0.015);

function applyFilter(){
  node.select("circle").attr("opacity", nodeOpacity);
  star.attr("opacity", starOpacity);
  line.attr("opacity", threadOpacity);
  d3.selectAll("#legend span.lg").each(function(){
    const on = this.dataset.level === activeLevel;
    this.style.opacity = (!activeLevel || on) ? 1 : 0.35;
    this.style.background = on ? "rgba(255,255,255,0.15)" : "transparent";
  });
}

d3.select("#legend").on("click", ev => {
  const el = ev.target.closest("span.lg");
  if (!el) return;
  activeLevel = (activeLevel === el.dataset.level) ? null : el.dataset.level;
  applyFilter();
});

node.on("mouseenter", function(ev,d){
  line.attr("opacity", t => t.entity === d.name ? 0.9 : 0.02);
  d3.select(this).select("circle").attr("r", d.level==="L1"?12:8.5);
  tip.html(`<b>${d.name}</b><br><span style='color:${d.color}'>${LEVEL_NAMES[d.level]}</span><br>${d.n} genes`)
     .style("opacity",1).style("left",(ev.clientX+12)+"px").style("top",(ev.clientY-10)+"px");
}).on("mousemove", ev => tip.style("left",(ev.clientX+12)+"px").style("top",(ev.clientY-10)+"px"))
  .on("mouseleave", function(ev,d){
    applyFilter();
    d3.select(this).select("circle").attr("r", d.level==="L1"?9:6.5);
    tip.style("opacity",0);
  });

star.on("mouseenter", function(ev,d){
  d3.select(this).attr("r", d.s*2).attr("fill","#fff").attr("opacity",1);
  tip.html(`<b>${d.symbol}</b><br>${d.forms.length} RCD entities:<br>${d.forms.slice(0,8).join(", ")}${d.forms.length>8?"…":""}`)
     .style("opacity",1).style("left",(ev.clientX+12)+"px").style("top",(ev.clientY-10)+"px");
}).on("mousemove", ev => tip.style("left",(ev.clientX+12)+"px").style("top",(ev.clientY-10)+"px"))
  .on("mouseleave", function(ev,d){
    d3.select(this).attr("r", d.s).attr("fill","#cbd5e1").attr("opacity", starOpacity(d));
    tip.style("opacity",0);
  });

node.on("click", (ev, d) => {
  window.location.href = "detail_page_wireframe.html?type=entity&name=" + encodeURIComponent(d.name);
});
star.on("click", (ev, d) => {
  window.location.href = "detail_page_wireframe.html?type=gene&name=" + encodeURIComponent(d.symbol);
});

svg.attr("opacity",0).transition().duration(1200).attr("opacity",1);
</script>
"""

# ============================================================
# 1) STANDALONE dome (full-screen)
# ============================================================
standalone = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RCDome</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  * { box-sizing:border-box; }
  body { margin:0; background:#0b1020; color:#e7e5e4; font-family:'Segoe UI',system-ui,sans-serif; overflow:hidden; }
  .wrap { width:100vw; height:100vh; display:flex; flex-direction:column; }
  .title { text-align:center; padding:0.8vh 0 0.2vh; pointer-events:none; flex-shrink:0; }
  .title h1 { margin:0; font-size:5.1rem; font-weight:800; letter-spacing:0.04em; line-height:1; }
  .title h1 .gold { color:#FF9800; }
  .title p { margin:0.35rem 0 0; font-size:2.025rem; color:#d6d3d1; }
  .title .stats { font-size:1.575rem; color:#a8a29e; }
  .title .hint { font-size:0.85rem; color:#94a3b8; font-style:italic; margin-top:0.2rem; }
  .stage { flex:1; min-height:0; }
  #dome { width:100%; height:100%; }
  svg { display:block; width:100%; height:100%; }
  .legend { text-align:center; padding:0.5vh 0 2vh; font-size:1.4rem; color:#d6d3d1; flex-shrink:0; }
  .legend span { margin:0 12px; white-space:nowrap; cursor:pointer; padding:4px 8px; border-radius:8px; transition:opacity .15s; }
  .legend i { display:inline-block; width:16px; height:16px; border-radius:50%; margin-right:6px; }
  .tip { position:fixed; background:#1c1917; color:#e7e5e4; padding:7px 12px; border-radius:8px;
         font-size:0.95rem; pointer-events:none; opacity:0; transition:opacity .15s; z-index:10; max-width:340px; }
</style>
</head>
<body>
<div class="wrap">
  <div class="title">
    <h1>RCD<span class="gold">ome</span></h1>
    <p>A multi-database human gene atlas of regulated cell death</p>
    <p class="stats">9,265 HGNC-validated genes &middot; 53 canonicalized RCD-related entities &middot; 21,568 associations &middot; 20 resources</p>
    <p class="hint">Hover an entity node on the dome border to reveal its genes &middot; hover a gene dot in the constellation beneath to reveal its RCD entities &middot; click a legend level to highlight</p>
  </div>
  <div class="stage"><div id="dome"></div></div>
  <div class="legend" id="legend"></div>
</div>
__JS__
</body>
</html>
"""

# ============================================================
# 2) INTEGRATED landing page
# ============================================================
landing = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RCDome — Landing Page</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:'Segoe UI',system-ui,sans-serif; background:#f5f5f4; color:#1c1917; }
  .header { display:flex; justify-content:space-between; align-items:center;
            padding:14px 24px; background:#fff; border-bottom:1px solid #e7e5e4; }
  .logo { font-size:1.4rem; font-weight:800; }
  .logo .gold { color:#b45309; }
  .nav a { margin-left:18px; color:#57534e; text-decoration:none; font-size:0.95rem; }
  .nav a:hover { color:#b45309; }
  .hero { background:#0b1020; padding:26px 20px 14px; text-align:center; }
  .hero .title h1 { font-size:5.1rem; font-weight:800; letter-spacing:0.04em; line-height:1; color:#e7e5e4; }
  .hero .title h1 .gold { color:#FF9800; }
  .hero .title p { margin:0.35rem 0 0; font-size:2.025rem; color:#d6d3d1; }
  .hero .title .stats { font-size:1.575rem; color:#a8a29e; }
  .hero .title .hint { font-size:0.85rem; color:#94a3b8; font-style:italic; margin-top:0.2rem; }
  .stage { width:100%; }
  #dome { width:100%; }
  svg { display:block; width:100%; height:auto; aspect-ratio: 1200 / 420; }
  .legend { padding:0.6vh 0 1.4vh; font-size:1.4rem; color:#d6d3d1; }
  .legend span { margin:0 12px; white-space:nowrap; cursor:pointer; padding:4px 8px; border-radius:8px; transition:opacity .15s; }
  .legend i { display:inline-block; width:16px; height:16px; border-radius:50%; margin-right:6px; }
  .tip { position:fixed; background:#1c1917; color:#e7e5e4; padding:7px 12px; border-radius:8px;
         font-size:0.95rem; pointer-events:none; opacity:0; transition:opacity .15s; z-index:10; max-width:340px; }
  .modules { max-width:1100px; margin:0 auto; padding:30px 20px; }
  .modules h2 { font-size:1.5rem; margin-bottom:16px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(240px, 1fr)); gap:16px; }
  .card { display:block; background:#fff; border:1px solid #e7e5e4; border-radius:10px; padding:18px; text-decoration:none; color:inherit; }
  .card:hover { border-color:#c2410c; }
  .card .num { font-size:0.75rem; font-weight:700; color:#FF9800; letter-spacing:0.05em; }
  .card h3 { font-size:1.05rem; margin:6px 0; }
  .card p { font-size:0.85rem; color:#57534e; line-height:1.4; }
  .footer { text-align:center; font-size:0.8rem; color:#a8a29e; padding:18px; }
</style>
</head>
<body>

  <!-- header nav removed: the Shiny navbar already provides the main navigation -->

  <div class="hero">
    <div class="title">
      <h1>RCD<span class="gold">ome</span></h1>
      <p>A multi-database human gene atlas of regulated cell death</p>
      <p class="stats">9,265 HGNC-validated genes &middot; 53 canonicalized RCD-related entities &middot; 21,568 associations &middot; 20 resources</p>
      <p class="hint">Hover an entity node on the dome border to reveal its genes &middot; hover a gene dot in the constellation beneath to reveal its RCD entities &middot; click a legend level to highlight</p>
    </div>
    <div class="stage"><div id="dome"></div></div>
    <div class="legend" id="legend"></div>
  </div>

  <div class="modules">
    <h2>The 7 modules</h2>
    <div class="grid">
      <a class="card" href="module_placeholder.html?m=1"><div class="num">MODULE 1</div><h3>RCD Compendium Browser</h3><p>Interactive filtering + direct PMID hyperlinks for every gene-RCD association.</p></a>
      <a class="card" href="module_placeholder.html?m=2"><div class="num">MODULE 2</div><h3>Gene-Centric Explorer</h3><p>Omic layer toggle: mRNA, isoform, miRNA, methylation, mutation, CNV, protein.</p></a>
      <a class="card" href="module_placeholder.html?m=3"><div class="num">MODULE 3</div><h3>AI Pathway Diagrams</h3><p>AI-generated, manually curated pathway diagrams (STRING PPI &rarr; Mermaid.js).</p></a>
      <a class="card" href="module_placeholder.html?m=4"><div class="num">MODULE 4</div><h3>LLM Literature Consultation</h3><p>Retrieval-Augmented Generation over a ChromaDB vector store of RCD literature.</p></a>
      <a class="card" href="module_placeholder.html?m=5"><div class="num">MODULE 5</div><h3>Operational Definition Comparator</h3><p>Side-by-side comparison of RCD forms' operational definitions.</p></a>
      <a class="card" href="module_placeholder.html?m=6"><div class="num">MODULE 6</div><h3>Discovery Timeline &amp; Evidence Dashboard</h3><p>Timeline of RCD discovery + evidence dashboard.</p></a>
      <a class="card" href="module_placeholder.html?m=7"><div class="num">MODULE 7</div><h3>Manuscript Integration Toolkit</h3><p>Export in .docx, .csv, and .ris formats.</p></a>
    </div>
  </div>

  <div class="footer">
    RCDome &middot; https://lbtgenomica.uenf.br/rcdome/ &middot; a multi-database human gene atlas of regulated cell death
  </div>

__JS__
</body>
</html>
"""

def render(template):
    return (template.replace("__JS__", JS)
                    .replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
                    .replace("__COUNTS__", json.dumps(counts)))

open(BASE + "/Shiny app/dome_prototype.html", "w", encoding="utf-8").write(render(standalone))
open(BASE + "/Shiny app/landing_page.html", "w", encoding="utf-8").write(render(landing))
print("generated dome_prototype.html + landing_page.html with", len(entities), "entities and", len(genes), "genes")
