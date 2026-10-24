# -*- coding: utf-8 -*-
import math, random, subprocess, sys

random.seed(42)

# ---- generate SVG dome constellation (panel A) ----
dome_svg = []
# dome outline arc (semicircle, center 300,360 radius 235)
dome_svg.append('<path d="M 65 360 A 235 235 0 0 1 535 360" fill="none" stroke="#FFD700" stroke-width="3" opacity="0.35"/>')
dome_svg.append('<path d="M 65 360 A 235 235 0 0 1 535 360" fill="url(#domegrad)" stroke="none" opacity="0.12"/>')
# 53 entity nodes along the arc
for i in range(53):
    a = math.pi + (i / 52) * math.pi
    x = 300 + 235 * math.cos(a)
    y = 360 + 235 * math.sin(a)
    r = 5 if (i % 7 != 0) else 8
    c = '#FFD700' if (i % 7 != 0) else '#FF9800'
    dome_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c}"/>')
# executor core highlighted (inner ring)
for i in range(8):
    a = math.pi + (i / 7) * math.pi
    x = 300 + 150 * math.cos(a)
    y = 360 + 150 * math.sin(a)
    dome_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="#FF9800" stroke="#FFD700" stroke-width="1.5"/>')
# gene dots scattered inside
for _ in range(120):
    x = random.uniform(80, 520)
    y = random.uniform(150, 355)
    dome_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" fill="#5b8dd9" opacity="0.7"/>')
dome_svg = '\n'.join(dome_svg)

# ---- module cards (panel B) ----
modules = [
    ('Compendium Browser', '◈'), ('Gene-Centric Explorer', '◎'), ('Pathway Diagrams', '↗'),
    ('Literature Consultation', '❝'), ('Definition Comparator', '⇄'), ('Discovery Timeline', '◷'),
    ('Integration Toolkit', '⛃'),
]
cards = ''.join(
    f'<div class="card"><div class="cic">{ic}</div><div class="cn">{n}</div></div>'
    for n, ic in modules
)

HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:#ffffff; font-family:Arial,Helvetica,sans-serif; padding:22px; }}
  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:18px 18px; }}
  .cell {{ }}
  .panel {{ position:relative; background:#0b1020; border-radius:12px; overflow:hidden; height:520px; border:1px solid #1e293b; }}
  .letter {{ position:absolute; top:12px; left:14px; background:#0b1020; color:#FFD700; font-weight:800; font-size:26px; padding:1px 13px; border:2px solid #FFD700; border-radius:7px; z-index:10; }}
  .caption {{ color:#1f2937; font-size:21px; margin:9px 3px 0; font-weight:600; }}
  .capgold {{ color:#b45309; }}
  .head {{ text-align:center; padding:18px 0 6px; }}
  .head h1 {{ margin:0; font-size:40px; font-weight:800; letter-spacing:0.04em; color:#e7e5e4; }}
  .head h1 .gold {{ color:#FF9800; }}
  .head p {{ margin:4px 0 0; font-size:19px; color:#d6d3d1; }}
  .stats {{ text-align:center; font-size:19px; color:#FFD700; margin-top:4px; }}
  .stats b {{ color:#FFD700; }}
  svg {{ display:block; margin:0 auto; }}

  /* panel B */
  .cards {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; padding:16px 22px; }}
  .card {{ background:#111a2e; border:1px solid #223; border-radius:9px; padding:14px 8px; text-align:center; }}
  .cic {{ font-size:22px; color:#FF9800; }}
  .cn {{ color:#e7e5e4; font-size:13px; margin-top:6px; line-height:1.2; }}
  .bench {{ padding:6px 22px 14px; display:flex; gap:10px; flex-wrap:wrap; }}
  .chip {{ background:#0f1a2e; border:1px solid #334155; color:#FFD700; font-size:14px; border-radius:16px; padding:5px 12px; }}

  /* panel C */
  .ban {{ background:linear-gradient(90deg,#0b1020,#1c2a52); padding:16px 20px; }}
  .ban h2 {{ margin:0; font-size:26px; color:#e7e5e4; }}
  .ban .gold {{ color:#FFD700; font-weight:700; }}
  .ban .orange {{ color:#FF9800; font-weight:700; }}
  .ban .muted {{ color:#a8a29e; }}
  .selrow {{ display:flex; align-items:center; gap:14px; padding:12px 20px; color:#e7e5e4; font-size:15px; flex-wrap:wrap; }}
  .selrow .lab {{ color:#cbd5e1; font-weight:600; }}
  .btn {{ background:#0b1020; color:#FFD700; border:1.5px solid #FFD700; border-radius:6px; padding:7px 13px; font-size:13px; font-weight:700; }}
  table {{ width:calc(100% - 40px); margin:0 20px; border-collapse:collapse; font-size:13.5px; }}
  th {{ background:#0b1020; color:#e7e5e4; padding:8px 9px; text-align:left; }}
  td {{ padding:7px 9px; color:#e7e5e4; border-bottom:1px solid #1e293b; }}
  .pill {{ border-radius:10px; padding:1px 8px; font-size:11px; font-weight:700; }}
  .exec {{ background:#78350f; color:#FDE68A; }}
  .reg {{ background:#7c2d12; color:#FED7AA; }}

  /* panel D */
  .dhead {{ padding:16px 20px; }}
  .dhead h2 {{ margin:0; font-size:28px; color:#e7e5e4; }}
  .dhead .ent {{ color:#FFD700; font-size:17px; }}
  .dhead .lv {{ display:inline-block; background:#1c2a52; color:#a5b4fc; border-radius:10px; padding:2px 10px; font-size:13px; margin-left:8px; }}
  .jump {{ margin:4px 20px 10px; background:#111a2e; border:1px solid #334155; border-radius:7px; color:#e7e5e4; padding:8px 12px; font-size:15px; }}
  .cot {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; padding:0 20px; }}
  .cot .k {{ background:#111a2e; border-radius:8px; padding:11px 12px; }}
  .cot .lbl {{ color:#a8a29e; font-size:12px; }}
  .cot .val {{ color:#FFD700; font-size:17px; font-weight:700; margin-top:3px; }}
  .pmid {{ padding:12px 20px; color:#a8a29e; font-size:13px; line-height:1.6; }}
  .pmid b {{ color:#e7e5e4; }}
</style></head>
<body>
<div class="grid">

  <!-- A: Home dome -->
  <div class="cell">
    <div class="panel">
      <div class="letter">A</div>
      <div class="head">
        <h1>RCD<span class="gold">ome</span></h1>
        <p>multi-database human gene atlas of regulated cell death</p>
        <div class="stats"><b>9,265</b> genes &nbsp;·&nbsp; <b>53</b> entities &nbsp;·&nbsp; <b>21,569</b> pairs</div>
      </div>
      <svg width="600" height="430" viewBox="0 0 600 430">
        <defs>
          <linearGradient id="domegrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#FFD700"/><stop offset="100%" stop-color="#0b1020"/>
          </linearGradient>
        </defs>
        {dome_svg}
      </svg>
    </div>
    <div class="caption">Home dome — the 53 entities as a constellation around the executor core</div>
  </div>

  <!-- B: Explore RCDome -->
  <div class="cell">
    <div class="panel">
      <div class="letter">B</div>
      <div class="head">
        <h1>Explore RCD<span class="gold">ome</span></h1>
        <p>modules, benchmarks and governance</p>
      </div>
      <div class="cards">{cards}</div>
      <div class="bench">
        <span class="chip">DeepSeek CoT · 100%</span>
        <span class="chip">Consensus neutral · 100%</span>
        <span class="chip">Elicit governance · 5/5 gates</span>
        <span class="chip">10,141 PMIDs verified</span>
      </div>
    </div>
    <div class="caption">Explore RCDome — seven modules with the benchmark and governance principles</div>
  </div>

  <!-- C: Gene Catalog -->
  <div class="cell">
    <div class="panel">
      <div class="letter">C</div>
      <div class="ban">
        <h2>Gene Catalog</h2>
        <div style="margin-top:5px;font-size:15px;">
          <span class="gold">9,265 genes</span> · <span class="gold">53 entities</span> · <span class="gold">21,569 associations</span><br>
          <span class="muted">DeepSeek:</span> <span class="orange">10,016 mechanistic</span> · <span class="orange">469 executors</span> · <span class="orange">9,489 regulators</span>
        </div>
      </div>
      <div class="selrow">
        <span class="lab">Direction/Role source:</span>
        <span>◉ DeepSeek</span><span>○ Elicit</span>
        <span style="flex:1"></span>
        <span class="btn">Death core (executors)</span><span class="btn">Download CSV</span>
      </div>
      <table>
        <tr><th>Gene</th><th>RCD entity</th><th>Role</th><th>Direction</th><th>Mech.</th><th>Tier</th></tr>
        <tr><td><b>BAX</b></td><td>Apoptosis</td><td><span class="pill exec">EXECUTOR</span></td><td>PROMOTES</td><td>YES</td><td>T1</td></tr>
        <tr><td><b>CASP3</b></td><td>Apoptosis</td><td><span class="pill exec">EXECUTOR</span></td><td>PROMOTES</td><td>YES</td><td>T1</td></tr>
        <tr><td><b>MLKL</b></td><td>Necroptosis</td><td><span class="pill exec">EXECUTOR</span></td><td>PROMOTES</td><td>YES</td><td>T1</td></tr>
        <tr><td><b>GPX4</b></td><td>Ferroptosis</td><td><span class="pill reg">REGULATOR</span></td><td>PROTECTS</td><td>YES</td><td>T1</td></tr>
        <tr><td><b>TP53</b></td><td>Apoptosis</td><td><span class="pill reg">REGULATOR</span></td><td>PROMOTES</td><td>YES</td><td>T1</td></tr>
      </table>
    </div>
    <div class="caption">Gene Catalog — DeepSeek/Elicit source selector and Death-core filter (469 executors)</div>
  </div>

  <!-- D: Detail page -->
  <div class="cell">
    <div class="panel">
      <div class="letter">D</div>
      <div class="dhead">
        <h2>BAX <span class="ent">Apoptosis</span><span class="lv">L1 Modalities</span></h2>
      </div>
      <div class="jump">Jump to entity: <b style="color:#FFD700;">Apoptosis</b> ▾ &nbsp;&nbsp;|&nbsp;&nbsp; BAX — EXECUTOR</div>
      <div class="cot">
        <div class="k"><div class="lbl">cot_role</div><div class="val">EXECUTOR</div></div>
        <div class="k"><div class="lbl">cot_direction</div><div class="val">PROMOTES</div></div>
        <div class="k"><div class="lbl">cot_mechanistic</div><div class="val">YES</div></div>
        <div class="k"><div class="lbl">Required-for-death</div><div class="val">YES</div></div>
      </div>
      <div class="pmid">
        <b>Verified publications</b><br>
        1. PMID 11420677 — BAX and apoptosis (title verified)<br>
        2. PMID 14623868 — BCL2 family regulation (title verified)<br>
        3. PMID 17562483 — intrinsic apoptosis machinery (title verified)
      </div>
    </div>
    <div class="caption">Gene detail page — entity jump, chain-of-thought columns and verified PMID titles</div>
  </div>

</div>
</body></html>"""

out = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Shiny app/figure4_panels.html'
open(out, 'w', encoding='utf-8').write(HTML)
print('HTML written:', out)

# screenshot
chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
png = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures/Figure4_assets/figure4_flat.png'
subprocess.run([chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                '--virtual-time-budget=4000', '--window-size=1700,1250',
                f'--screenshot={png}', 'file:///' + out.replace('\\', '/')],
               capture_output=True)
print('screenshot saved:', png)
