#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate detail_page_wireframe.html with REAL V026 data.
Entity view: definition + real gene table (mechanistic class, DBs, PMIDs).
Gene view: real metadata + associated entities.
The data is embedded inline so the page works from file://.
"""
import pandas as pd, json, csv

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
v23 = pd.read_csv(BASE + "/output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv",
                  dtype=str, keep_default_na=False)

decoder_df = pd.read_csv(BASE + "/RCDome Decoder/RCDome_Decoder_53.csv", dtype=str, keep_default_na=False)
decoder_map = {r["rcd_form"]: r for _, r in decoder_df.iterrows()}
def _first(s):
    s = str(s).strip()
    return "" if (not s or s in ("nan", "NOT_AVAILABLE")) else s

def short(l):
    return {'L1 Modalities':'L1','L2 Subtypes':'L2','L3 Triggers':'L3',
            'L4 Functional/contextual':'L4','L5 Generic/umbrella/legacy/taxon/emerging':'L5'}.get(l,'L5')

# HGNC + Entrez lookup (for external gene links)
hgnc_map = {}
try:
    with open(BASE + '/analysis/Victor_analysis/V022_fixes/hgnc_complete_set.txt', encoding='utf-8', errors='ignore') as _f:
        for _row in csv.DictReader(_f, delimiter='\t'):
            _sym = (_row.get('symbol') or '').strip()
            if _sym:
                hgnc_map[_sym] = {'hgnc': (_row.get('hgnc_id') or '').strip(),
                                  'entrez': (_row.get('entrez_id') or '').strip()}
except Exception as _e:
    print('WARN: HGNC lookup failed:', _e)

# manual aliases (symbols not matching the HGNC file)
hgnc_map['CBSL'] = {'hgnc': 'HGNC:55459', 'entrez': '124904470'}  # CBS-like readthrough (HGNC symbol: CBSLR)

# NCBI Gene summaries + HGNC fields for the Gene information block
gene_info_map = {}
try:
    with open(BASE + '/RCDome_distribution/data/gene_info_lookup.json', encoding='utf-8') as _f:
        gene_info_map = json.load(_f)
except Exception as _e:
    print('WARN: gene info lookup failed:', _e)

# ---- entity data ----
entities = {}
for form, grp in v23.groupby('rcd_form_canonical'):
    level = short(grp['rcdome_level_name'].iloc[0])
    n = int(grp.gene_symbol.nunique())
    dr = decoder_map.get(form)
    defn = _first(dr['operational_definition']) if dr is not None else ''
    if not defn:
        defn = next((str(x) for x in grp['rodr_core_mechanism'] if str(x) not in ('', 'NOT_AVAILABLE')), '')
    keymol = _first(dr['key_molecules']) if dr is not None else ''
    if not keymol:
        keymol = next((str(x) for x in grp['rodr_key_molecules'] if str(x) not in ('', 'NOT_AVAILABLE')), '')
    g = grp.drop_duplicates('gene_symbol').copy()
    g['_ns'] = pd.to_numeric(g['num_sources'], errors='coerce').fillna(0).astype(int)
    g['_mech'] = (g['mechanistic_class'] == 'MECHANISTIC').astype(int)
    g = g.sort_values(['_mech', '_ns'], ascending=[False, False])
    genes = []
    for _, r in g.iterrows():
        pmid = ''
        for _col in ('pmid_list', 'elicit_pmids'):
            if r[_col]:
                for _p in r[_col].split(';'):
                    _p = _p.strip()
                    if _p.isdigit():
                        pmid = _p
                        break
                if pmid:
                    break
        genes.append({'symbol': r['gene_symbol'], 'direction': r['role_direction'],
                      'role': r['rcd_gene_type'], 'mech': r['mechanistic_class'],
                      'direction_ds': r['cot_direction'], 'role_ds': r['cot_role'],
                      'n_db': int(r['_ns']), 'pmid': pmid, 'dbs': r['source_databases']})
    pmids = []
    for col in ('pmid_list', 'elicit_pmids'):
        for v in grp[col]:
            for p in str(v).split(';'):
                p = p.strip()
                if p.isdigit() and p not in pmids:
                    pmids.append(p)
    force = set()
    for col in ('llm_pmids', 'epmc_pmids'):
        for v in grp[col]:
            for p in str(v).split(';'):
                p = p.strip()
                if p.isdigit():
                    force.add(p)
    entities[form] = {'level': level, 'n': n, 'definition': defn, 'key': keymol,
                      'genes': genes, 'pmids': pmids, 'force': len(force), 'force_pmids': ','.join(sorted(force))}

# ---- gene data (ALL genes) ----
gene_data = {}
for sym, grp in v23.groupby('gene_symbol'):
    ents = []
    for form, fg in grp.groupby('rcd_form_canonical'):
        ents.append({'name': form, 'level': short(fg['rcdome_level_name'].iloc[0]),
                     'direction': fg['role_direction'].iloc[0], 'direction_ds': fg['cot_direction'].iloc[0],
                     'role_ds': fg['cot_role'].iloc[0], 'mech': fg['mechanistic_class'].iloc[0]})
    ents.sort(key=lambda e: (-(e['mech'] == 'MECHANISTIC'), e['name']))
    h = hgnc_map.get(sym, {})
    info = gene_info_map.get(sym, {})
    gene_data[sym] = {'ensembl': grp['ensembl_id'].iloc[0], 'biotype': grp['gene_biotype'].iloc[0],
                      'n_entities': len(ents), 'entities': ents,
                      'hgnc': h.get('hgnc', ''), 'entrez': h.get('entrez', ''),
                      'info': {'name': info.get('name', ''), 'alias': info.get('alias', ''),
                               'type': info.get('locus_type', ''), 'location': info.get('location', ''),
                               'summary': info.get('summary', '')}}

DATA = {'entities': entities, 'genes': gene_data}
DATA_JSON = json.dumps(DATA, ensure_ascii=False)

# verified PMID -> title lookup (for hover tooltips)
with open('RCDome_Atlas/APP/data/pmid_title_lookup.json', encoding='utf-8') as _f:
    PMID_TITLES = json.load(_f)
PMID_TITLES_JSON = json.dumps(PMID_TITLES, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<title>RCDome — Detail</title>
<style>
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:'Segoe UI',system-ui,sans-serif; background:#f5f5f4; color:#1c1917; }
  .frame { max-width:1100px; margin:0 auto; padding:20px; }
  .header { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;
            padding:14px 20px; background:#fff; border:1px solid #e7e5e4; border-radius:10px; }
  .jumpbar { display:flex; gap:8px; align-items:center; flex-wrap:wrap;
             margin:12px 0 14px; padding:10px 14px; background:#0b1020; border-radius:10px; }
  #geneJump::placeholder, #entityJump::placeholder { color:#d6d3d1; opacity:1; }
  .back { color:#c2410c; text-decoration:none; font-size:0.9rem; font-weight:600; cursor:pointer; }
  .logo { font-size:1.4rem; font-weight:800; }
  .logo .rust { color:#c2410c; }
  .crumb { font-size:0.85rem; color:#78716c; }
  .tabs { margin:18px 0 14px; }
  .tabs button { padding:9px 18px; margin-right:8px; border:1px solid #d6d3d1; background:#fff;
                 border-radius:8px; cursor:pointer; font-size:0.95rem; font-weight:600; }
  .tabs button.active { background:#1c1917; color:#fff; border-color:#1c1917; }
  .hero { background:#0b1020; color:#e7e5e4; border-radius:12px; padding:28px 26px; }
  .hero h1 { font-size:2.2rem; }
  .hero .meta { margin-top:6px; font-size:0.95rem; color:#d6d3d1; }
  .hero .meta a { color:#FF9800; text-decoration:none; }
  .hero .meta a:hover { text-decoration:underline; }
  .hero .def { margin-top:12px; font-size:0.9rem; color:#a8a29e; line-height:1.5; max-width:800px; }
  .hero .key { margin-top:8px; font-size:0.85rem; color:#94a3b8; }
  .section { margin-top:18px; background:#fff; border:1px solid #e7e5e4; border-radius:10px; padding:16px; }
  .section h2 { font-size:1.05rem; margin-bottom:10px; }
  table { width:100%; border-collapse:collapse; font-size:0.85rem; }
  th, td { text-align:left; padding:8px 10px; border-bottom:1px solid #f0efed; }
  th { color:#57534e; font-size:0.78rem; text-transform:uppercase; letter-spacing:0.05em; }
  .pill { display:inline-block; padding:2px 8px; border-radius:10px; font-size:0.75rem; font-weight:600; }
  .p-promote { background:#dcfce7; color:#166534; }
  .p-protect { background:#dbeafe; color:#1e40af; }
  .p-mech { background:#dcfce7; color:#166534; }
  .p-context { background:#ffedd5; color:#9a3412; }
  .p-coocc { background:#e0f2fe; color:#075985; }
  .p-litgap { background:#fef9c3; color:#854d0e; }
  .p-insuf { background:#f1f5f9; color:#475569; }
  .p-dbonly { background:#f3e8ff; color:#6b21a8; }
  .literature { font-size:0.82rem; color:#44403c; }
  .literature a { color:#1d4ed8; text-decoration:none; }
  .literature p { margin:4px 0; }
  .modlinks { display:flex; gap:10px; flex-wrap:wrap; }
  .modlinks a { padding:8px 14px; background:#ffedd5; color:#c2410c; border-radius:8px;
                text-decoration:none; font-size:0.85rem; font-weight:600; }
  .note { font-size:0.75rem; color:#a8a29e; margin-top:8px; }
  .search { flex:1; min-width:180px; padding:8px 12px; border:1px solid #d6d3d1; border-radius:8px; font-size:0.9rem; }
  .filters { display:flex; gap:10px; margin-bottom:10px; flex-wrap:wrap; align-items:center; }
  .filters select { padding:7px 10px; border:1px solid #d6d3d1; border-radius:8px; font-size:0.85rem; }
  .filters button { padding:7px 14px; border:1px solid #d6d3d1; background:#fff; border-radius:8px; cursor:pointer; font-size:0.85rem; }
  .filters button:hover { background:#f5f5f4; }
  .pager { display:flex; align-items:center; gap:10px; margin-top:10px; }
  .pager button { padding:5px 12px; border:1px solid #d6d3d1; background:#fff; border-radius:6px; cursor:pointer; }
  .pager button:disabled { opacity:0.4; cursor:default; }
  .litbar { display:flex; align-items:center; gap:12px; font-size:0.85rem; flex-wrap:wrap; }
  .litbar button { padding:6px 14px; border:1px solid #d6d3d1; background:#fff; border-radius:6px; cursor:pointer; font-size:0.85rem; }
  .litbar button:hover { background:#f5f5f4; }
  .has-tip { cursor:help; border-bottom:1px dotted #a8a29e; }
  .tip { position:fixed; background:#1c1917; color:#e7e5e4; padding:8px 12px; border-radius:8px; font-size:0.8rem; max-width:340px; pointer-events:none; opacity:0; transition:opacity .15s; z-index:100; }
  .modal { position:fixed; inset:0; background:rgba(0,0,0,0.5); display:flex; align-items:center; justify-content:center; z-index:100; }
  .modal-box { background:#fff; border-radius:10px; width:min(700px, 90vw); max-height:80vh; display:flex; flex-direction:column; }
  .modal-head { display:flex; justify-content:space-between; align-items:center; padding:12px 16px; border-bottom:1px solid #e7e5e4; font-weight:700; }
  .modal-head button { border:none; background:none; font-size:1.4rem; cursor:pointer; color:#57534e; }
  .modal-body { padding:12px 16px; overflow:auto; font-size:0.85rem; }
  .modal-body a { color:#1d4ed8; text-decoration:none; display:inline-block; margin:2px 8px 2px 0; }
</style>
</head>
<body>
<div class="frame">

  <div class="header">
    <a class="back" href="landing_page.html">← Back to the dome</a>
    <div class="logo">RCD<span class="rust">ome</span></div>
    <div class="crumb">Home / <span id="crumbName">…</span></div>
  </div>

  <div class="jumpbar">
    <span style="color:#a8a29e; font-size:13px; font-weight:600;">Jump to:</span>
    <input id="geneJump" list="geneList" placeholder="type a gene, press Enter…" style="width:240px; padding:8px 10px; border:2px solid #FF9800; border-radius:8px; font-size:14px; color:#FF9800; background:#0b1020; font-weight:700;">
    <datalist id="geneList"></datalist>
    <input id="entityJump" list="entityList" placeholder="type an RCD entity, press Enter…" style="width:280px; padding:8px 10px; border:2px solid #FFD700; border-radius:8px; font-size:14px; color:#FFD700; background:#0b1020; font-weight:700;">
    <datalist id="entityList"></datalist>
  </div>

  <!-- navigation: clickable rows (entity <-> gene) -->

  <!-- ============ ENTITY VIEW ============ -->
  <div id="entityView">
    <div class="hero">
      <h1 id="entityTitle">…</h1>
      <p class="meta" id="entityMeta"></p>
      <p class="def" id="entityDef"></p>
      <p class="key" id="entityKey"></p>
    </div>
    <div class="section">
      <h2>Associated genes</h2>
      <div style="margin: 8px 0 12px; font-size: 14px; color: #1c1917;">
        <span style="font-weight:600;">Direction/Role source:</span>
        <label style="margin-left:14px;"><input type="radio" name="dirSrc" value="deepseek" checked> DeepSeek</label>
        <label style="margin-left:14px;"><input type="radio" name="dirSrc" value="elicit"> Elicit</label>
      </div>
      <div class="filters">
        <input id="entitySearch" class="search" placeholder="Search genes…">
        <select id="fDirection"><option value="">All directions</option></select>
        <select id="fRole"><option value="">All roles</option></select>
        <select id="fMech"><option value="">All mechanistic classes</option></select>
        <select id="fDb"><option value="">All evidence DBs</option></select>
        <select id="fPmid"><option value="">All PMIDs</option><option value="has">Has PMID</option><option value="none">No PMID</option></select>
        <button id="entityDownloadCsv">Download .csv</button>
      </div>
      <span id="entityCount" class="note"></span>
      <table>
        <thead><tr>
          <th class="has-tip" data-tip="Official HGNC gene symbol (italicized). Click to open the gene detail page.">Gene</th>
          <th id="thDirection" class="has-tip" data-tip="Direction of the gene's effect on this RCD entity (PROMOTES/PROTECTS/UNCLEAR), from the selected analysis (DeepSeek = complete; Elicit = original).">Direction (DeepSeek)</th>
          <th id="thRole" class="has-tip" data-tip="Functional role (EXECUTOR/REGULATOR/MARKER/UNCERTAIN), from the selected analysis (DeepSeek = complete; Elicit = original).">Role (DeepSeek)</th>
          <th class="has-tip" data-tip="Seven-class mechanistic classification: MECHANISTIC = validated by both LLM knowledge and PubMed abstracts; LITERATURE_GAP = LLM training recognizes but abstracts lack explicit statements; CONTEXT_GAP = PubMed confirms but LLM training does not recognize; CO_OCCURRENCE = high paper counts but no mechanistic evidence; INSUFFICIENT_DATA = few papers, LLM cannot determine involvement; DATABASE_ONLY = gene and RCD term never co-occur in PubMed; TECHNICAL_FAILURE = API failure (0 in final run).">Mechanistic class</th>
          <th class="has-tip" data-tip="Number of independent source databases supporting this gene-RCD association.">Evidence DBs</th>
          <th class="has-tip" data-tip="First curated PMID (from pmid_list + elicit_pmids) that directly supports the association. One representative PMID per gene — the full list is under Literature evidence.">Association evidence PMID</th>
        </tr></thead>
        <tbody id="entityGenes"></tbody>
      </table>
      <div class="pager">
        <button id="entityPrev">&larr; Prev</button>
        <span id="entityPage"></span>
        <button id="entityNext">Next &rarr;</button>
      </div>
      <p class="note">Direction/Role source: DeepSeek (complete) vs Elicit (original, ~20% populated). Switch above.</p>
    </div>
    <div class="section">
      <h2>Literature evidence</h2>
      <div class="litbar">
        <b class="has-tip" data-tip="PMIDs that directly support the gene-RCD association (from source databases + Elicit AI extraction). Association evidence — not a mechanistic classification.">Association evidence:</b> <span id="entityLitCount"></span>
        <button id="entityViewPmids">View all PMIDs</button>
        <button id="entityDownloadPmids">Download .txt</button>
      </div>
      <div class="litbar" style="margin-top:6px;">
        <b class="has-tip" data-tip="Raw PMIDs where the gene and RCD term merely co-occur (llm_pmids + epmc_pmids) — literature volume, not direct association evidence.">Co-occurrence force:</b> <span id="entityForceCount"></span>
        <button id="entityDownloadForce">Download .txt</button>
      </div>
    </div>
    <div class="section">
      <h2>Jump to modules</h2>
      <div class="modlinks">
        <a href="module_placeholder.html?m=3">Pathway diagram</a>
        <a href="module_placeholder.html?m=6">Discovery timeline</a>
        <a href="module_placeholder.html?m=5">Operational comparator</a>
        <a href="module_placeholder.html?m=7">Export .csv</a>
      </div>
    </div>
  </div>

  <!-- ============ GENE VIEW ============ -->
  <div id="geneView" style="display:none;">
    <div class="hero">
      <h1 id="geneTitle" style="font-style:italic;">…</h1>
      <p class="meta" id="geneMeta"></p>
    </div>
    <div id="geneInfo"></div>
    <div class="section">
      <h2>Associated RCD entities</h2>
      <table>
        <thead><tr>
          <th class="has-tip" data-tip="Canonical RCD form name. Click to open the entity detail page.">RCD entity</th>
          <th class="has-tip" data-tip="Ontological level of the RCD entity: L1 modality, L2 subtype, L3 trigger, L4 Functional/contextual, L5 Generic/umbrella/legacy/taxon/emerging.">Level</th>
          <th id="thGeneDirection" class="has-tip" data-tip="Direction of the gene's effect on this RCD entity, from the selected analysis (DeepSeek = complete; Elicit = original).">Direction (DeepSeek)</th>
          <th class="has-tip" data-tip="Seven-class mechanistic classification: MECHANISTIC = validated by both LLM knowledge and PubMed abstracts; LITERATURE_GAP = LLM training recognizes but abstracts lack explicit statements; CONTEXT_GAP = PubMed confirms but LLM training does not recognize; CO_OCCURRENCE = high paper counts but no mechanistic evidence; INSUFFICIENT_DATA = few papers, LLM cannot determine involvement; DATABASE_ONLY = gene and RCD term never co-occur in PubMed; TECHNICAL_FAILURE = API failure (0 in final run).">Mechanistic class</th>
        </tr></thead>
        <tbody id="geneEntities"></tbody>
      </table>
      <p class="note">Direction source: DeepSeek (complete) vs Elicit (original).</p>
    </div>
    <div class="section">
      <h2>Jump to modules</h2>
      <div class="modlinks">
        <a href="module_placeholder.html?m=2">Gene-centric explorer (omic layers)</a>
        <a href="module_placeholder.html?m=3">Pathway diagram</a>
        <a href="module_placeholder.html?m=7">Export .csv</a>
      </div>
    </div>
  </div>

  <div class="tip" id="tip"></div>

  <!-- PMID modal -->
  <div id="pmidModal" class="modal" style="display:none;">
    <div class="modal-box">
      <div class="modal-head"><span id="pmidModalTitle"></span><button id="pmidModalClose">×</button></div>
      <div class="modal-body" id="pmidModalBody"></div>
    </div>
  </div>

</div>

<script>
const DATA = __DATA__;
const PMID_TITLES = __PMID_TITLES__;
const LEVEL_COLORS = {L1:"#FFD700", L2:"#00B0FF", L3:"#00E676", L4:"#E040FB", L5:"#FF6D00"};
const LEVEL_TEXT_COLORS = {L1:"#8a6d00", L2:"#006f9e", L3:"#007a4d", L4:"#7b1fa2", L5:"#c2410c"};
const LEVEL_NAMES = {L1:"L1 modality", L2:"L2 subtype", L3:"L3 trigger", L4:"L4 Functional/contextual", L5:"L5 Generic/umbrella/legacy/taxon/emerging"};
const MECH_PILL = {MECHANISTIC:"p-mech", CONTEXT_GAP:"p-context", CO_OCCURRENCE:"p-coocc",
                   LITERATURE_GAP:"p-litgap", INSUFFICIENT_DATA:"p-insuf", DATABASE_ONLY:"p-dbonly"};

const entityView = document.getElementById("entityView");
const geneView = document.getElementById("geneView");
const crumb = document.getElementById("crumbName");

const dirPill = d => d.toLowerCase().startsWith("promote") ? "p-promote"
                 : d.toLowerCase().startsWith("protect") ? "p-protect" : "";
const uniq = arr => [...new Set(arr.filter(Boolean))];
let dirSrc = "deepseek";
const DIR = g => dirSrc === "elicit" ? (g.direction || "") : (g.direction_ds || "");
const ROLE = g => dirSrc === "elicit" ? (g.role || "") : (g.role_ds || "");
function updateHeaders() {
  const lbl = dirSrc === "elicit" ? "Elicit" : "DeepSeek";
  const td = document.getElementById("thDirection");
  const tr = document.getElementById("thRole");
  const tg = document.getElementById("thGeneDirection");
  if (td) td.textContent = "Direction (" + lbl + ")";
  if (tr) tr.textContent = "Role (" + lbl + ")";
  if (tg) tg.textContent = "Direction (" + lbl + ")";
}
const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const pmLink = p => {
  const t = PMID_TITLES[p] || '';
  return `<a href="https://pubmed.ncbi.nlm.nih.gov/${p}/" target="_blank" class="has-tip" data-tip="${esc(t)}">PMID ${p}</a>`;
};

const PAGE = 25;
let curGenes = [], curFiltered = [], curPage = 0, curPmids = [], curForce = [], curMeta = {name:"", level:"", n:0, def:""};
const rowHtml = g => `
  <tr>
    <td class="gene-link" data-symbol="${g.symbol}" style="cursor:pointer;"><b style="color:#1d4ed8;font-style:italic;">${g.symbol}</b></td>
    <td>${DIR(g) ? `<span class="pill ${dirPill(DIR(g))}">${DIR(g)}</span>` : "—"}</td>
    <td>${ROLE(g) || "—"}</td>
    <td><span class="pill ${MECH_PILL[g.mech] || "p-insuf"}">${g.mech || "—"}</span></td>
    <td class="has-tip" data-tip="${g.dbs.replace(/;/g, ', ')}">${g.n_db}</td>
    <td>${g.pmid ? pmLink(g.pmid) : "—"}</td>
  </tr>`;
function renderGenes() {
  const start = curPage * PAGE;
  const slice = curFiltered.slice(start, start + PAGE);
  document.getElementById("entityGenes").innerHTML = slice.map(rowHtml).join("");
  document.getElementById("entityCount").textContent = `${curFiltered.length.toLocaleString('en-US')} genes`;
  document.getElementById("entityPage").textContent = `Page ${curPage + 1} / ${Math.max(1, Math.ceil(curFiltered.length / PAGE))}`;
  document.getElementById("entityPrev").disabled = curPage === 0;
  document.getElementById("entityNext").disabled = (curPage + 1) * PAGE >= curFiltered.length;
}
function applyFilters() {
  const q = document.getElementById("entitySearch").value.toLowerCase();
  const fd = document.getElementById("fDirection").value;
  const fr = document.getElementById("fRole").value;
  const fm = document.getElementById("fMech").value;
  const fdb = document.getElementById("fDb").value;
  const fpm = document.getElementById("fPmid").value;
  curFiltered = curGenes.filter(g =>
    (!q || g.symbol.toLowerCase().includes(q)) &&
    (!fd || DIR(g) === fd) &&
    (!fr || ROLE(g) === fr) &&
    (!fm || g.mech === fm) &&
    (!fdb || String(g.n_db) === fdb) &&
    (!fpm || (fpm === "has" ? g.pmid : !g.pmid)));
  curPage = 0;
  renderGenes();
}
document.getElementById("entitySearch").addEventListener("input", applyFilters);
document.getElementById("entitySearch").addEventListener("keydown", ev => {
  if (ev.key !== "Enter") return;
  const raw = document.getElementById("entitySearch").value.trim();
  if (!raw) return;
  const key = raw.toUpperCase();
  const inEntity = curGenes.some(g => String(g.symbol).toUpperCase() === key);
  if (inEntity) return;
  const body = document.getElementById("pmidModalBody");
  const title = document.getElementById("pmidModalTitle");
  if (DATA.genes[key]) {
    title.textContent = "Gene not associated";
    body.innerHTML =
      `<p><b>${esc(raw)}</b> is in the RCDome database but is not associated with <b>${esc(crumb.textContent)}</b>.</p>` +
      `<p><a href="#" onclick="event.preventDefault(); document.getElementById('pmidModal').style.display='none'; showGene('${esc(key)}');">Open ${esc(raw)} gene page</a></p>`;
  } else {
    title.textContent = "Gene not found";
    body.innerHTML = `<p>Sorry, <b>${esc(raw)}</b> is not in the RCDome database (9,265 HGNC-validated genes).</p>`;
  }
  document.getElementById("pmidModal").style.display = "flex";
});
document.getElementById("fDirection").addEventListener("change", applyFilters);
document.getElementById("fRole").addEventListener("change", applyFilters);
document.getElementById("fMech").addEventListener("change", applyFilters);
document.getElementById("fDb").addEventListener("change", applyFilters);
document.getElementById("fPmid").addEventListener("change", applyFilters);
document.getElementById("entityGenes").addEventListener("click", ev => {
  const td = ev.target.closest("td.gene-link");
  if (td) showGene(td.dataset.symbol);
});
document.getElementById("geneEntities").addEventListener("click", ev => {
  const td = ev.target.closest("td.ent-link");
  if (td) showEntity(td.dataset.name);
});
document.getElementById("entityPrev").addEventListener("click", () => { if (curPage > 0) { curPage--; renderGenes(); } });
document.getElementById("entityNext").addEventListener("click", () => { if ((curPage + 1) * PAGE < curFiltered.length) { curPage++; renderGenes(); } });
document.getElementById("entityViewPmids").addEventListener("click", () => {
  document.getElementById("pmidModalTitle").textContent = (crumb.textContent || "entity") + " — " + curPmids.length.toLocaleString('en-US') + " PMIDs";
  document.getElementById("pmidModalBody").innerHTML = curPmids.length ? curPmids.map(pmLink).join("") : "<p>No PMIDs.</p>";
  document.getElementById("pmidModal").style.display = "flex";
});
document.getElementById("pmidModalClose").addEventListener("click", () => {
  document.getElementById("pmidModal").style.display = "none";
});
document.getElementById("pmidModal").addEventListener("click", ev => {
  if (ev.target.id === "pmidModal") document.getElementById("pmidModal").style.display = "none";
});
document.getElementById("entityDownloadPmids").addEventListener("click", () => {
  const NL = String.fromCharCode(10);
  const defLine = curMeta.def || "No operational definition recorded in the matrix.";
  const head = [
    curMeta.name || "entity",
    (curMeta.level ? curMeta.level + " · " : "") + curMeta.n.toLocaleString('en-US') + " associated genes",
    defLine,
    curMeta.key ? ("Key molecules: " + curMeta.key) : "",
    "",
    "PMIDs (" + curPmids.length + "):"
  ].filter(Boolean).join(NL);
  const blob = new Blob([head + NL + curPmids.join(NL)], {type: "text/plain"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "RCDome_" + (curMeta.name || "entity") + "_pmids.txt";
  a.click();
  URL.revokeObjectURL(url);
});
document.getElementById("entityDownloadCsv").addEventListener("click", () => {
  const NL = String.fromCharCode(10);
  const defLine = curMeta.def || "No operational definition recorded in the matrix.";
  const meta = [
    "# RCDome — " + (curMeta.name || "entity"),
    "# " + (curMeta.level ? curMeta.level + " · " : "") + curMeta.n.toLocaleString('en-US') + " associated genes",
    "# " + defLine,
    curMeta.key ? ("# Key molecules: " + curMeta.key) : "",
    ""
  ].filter(Boolean).join(NL);
  const head = "gene,direction,role,mechanistic_class,evidence_DBs,pmid";
  const rows = curGenes.map(g => [g.symbol, DIR(g), ROLE(g), g.mech, g.n_db, g.pmid].join(","));
  const blob = new Blob([meta + head + NL + rows.join(NL)], {type: "text/csv"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "RCDome_" + (curMeta.name || "entity") + "_genes.csv";
  a.click();
  URL.revokeObjectURL(url);
});
document.getElementById("entityDownloadForce").addEventListener("click", () => {
  const NL = String.fromCharCode(10);
  const head = [
    curMeta.name || "entity",
    (curMeta.level ? curMeta.level + " · " : "") + curMeta.n.toLocaleString('en-US') + " associated genes",
    "Co-occurrence force (llm_pmids + epmc_pmids): " + curForce.length.toLocaleString('en-US') + " PMIDs",
    ""
  ].join(NL);
  const blob = new Blob([head + curForce.join(NL)], {type: "text/plain"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "RCDome_" + (curMeta.name || "entity") + "_cooccurrence_pmids.txt";
  a.click();
  URL.revokeObjectURL(url);
});

document.querySelectorAll('input[name="dirSrc"]').forEach(r => {
  r.addEventListener("change", () => {
    dirSrc = r.value;
    updateHeaders();
    const e = DATA.entities[crumb.textContent];
    if (!e) return;
    document.getElementById("fDirection").innerHTML = '<option value="">All directions</option>' + uniq(e.genes.map(g => DIR(g))).map(d => `<option>${d}</option>`).join("");
    document.getElementById("fRole").innerHTML = '<option value="">All roles</option>' + uniq(e.genes.map(g => ROLE(g))).map(r => `<option>${r}</option>`).join("");
    applyFilters();
  });
});

function showEntity(name) {
  entityView.style.display = "block"; geneView.style.display = "none";
  crumb.textContent = name;
  if (entityJump) entityJump.value = name;
  const e = DATA.entities[name];
  document.getElementById("entityTitle").textContent = name;
  if (!e) {
    document.getElementById("entityMeta").textContent = "No matrix data for this entity.";
    document.getElementById("entityDef").textContent = "";
    document.getElementById("entityKey").textContent = "";
    document.getElementById("entityGenes").innerHTML = "";
    document.getElementById("entityLitCount").textContent = "No matrix data.";
    document.getElementById("entityForceCount").textContent = "";
    return;
  }
  const nExec = e.genes.filter(g => g.role_ds === "EXECUTOR").length;
  const nReg = e.genes.filter(g => g.role_ds === "REGULATOR").length;
  const dsStats = (nExec + nReg > 0) ? ` · <b style="color:#FF9800;">${nExec}</b> <span style="color:#FF9800;">executors</span> · <b style="color:#FF9800;">${nReg}</b> <span style="color:#FF9800;">regulators</span> <span style="color:#a8a29e;">(DeepSeek)</span>` : "";
  document.getElementById("entityMeta").innerHTML =
    `<span class="pill" style="background:${LEVEL_COLORS[e.level]}33;color:${LEVEL_TEXT_COLORS[e.level]}">${LEVEL_NAMES[e.level]}</span> · <b style="color:#FFD700;">${e.n.toLocaleString('en-US')}</b> <span style="color:#FFD700;">associated genes</span>${dsStats}`;
  document.getElementById("entityDef").textContent = e.definition || "No operational definition recorded in the matrix.";
  document.getElementById("entityKey").textContent = e.key ? ("Key molecules: " + e.key) : "";
  curGenes = e.genes;
  curFiltered = e.genes;
  curPage = 0;
  document.getElementById("entitySearch").value = "";
  document.getElementById("fDirection").innerHTML = '<option value="">All directions</option>' + uniq(e.genes.map(g => DIR(g))).map(d => `<option>${d}</option>`).join("");
  document.getElementById("fRole").innerHTML = '<option value="">All roles</option>' + uniq(e.genes.map(g => ROLE(g))).map(r => `<option>${r}</option>`).join("");
  document.getElementById("fMech").innerHTML = '<option value="">All mechanistic classes</option>' + uniq(e.genes.map(g => g.mech)).map(m => `<option>${m}</option>`).join("");
  const dbs = [...new Set(e.genes.map(g => String(g.n_db)))].sort((a, b) => Number(a) - Number(b));
  document.getElementById("fDb").innerHTML = '<option value="">All evidence DBs</option>' + dbs.map(d => `<option>${d}</option>`).join("");
  renderGenes();
  curPmids = e.pmids;
  curForce = e.force_pmids ? e.force_pmids.split(',') : [];
  curMeta = {name: name, level: LEVEL_NAMES[e.level] || e.level, n: e.n, def: e.definition, key: e.key};
  document.getElementById("entityLitCount").textContent = e.pmids.length
    ? `${e.pmids.length.toLocaleString('en-US')} PMIDs recorded`
    : "No PMIDs yet — they populate as the AI extraction (DeepSeek/Consensus) completes.";
  document.getElementById("entityForceCount").textContent = e.force
    ? `${e.force.toLocaleString('en-US')} co-occurrence PMIDs (llm + epmc)`
    : "—";
}

function showGene(name) {
  geneView.style.display = "block"; entityView.style.display = "none";
  crumb.textContent = name;
  const g = DATA.genes[name];
  document.getElementById("geneTitle").textContent = name;
  if (!g) {
    document.getElementById("geneMeta").textContent = "No matrix data for this gene.";
    document.getElementById("geneEntities").innerHTML = "";
    return;
  }
  const ext = [];
  ext.push(g.hgnc
    ? `<a href="https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/${g.hgnc}" target="_blank">HGNC ↗</a>`
    : `<a href="https://www.genenames.org/tools/search/#!/all?query=${encodeURIComponent(name)}" target="_blank">HGNC ↗</a>`);
  if (g.ensembl) ext.push(`<a href="https://www.ensembl.org/Homo_sapiens/Gene/Summary?g=${g.ensembl}" target="_blank">Ensembl ↗</a>`);
  if (g.entrez) ext.push(`<a href="https://www.ncbi.nlm.nih.gov/gene/${g.entrez}" target="_blank">NCBI Gene ↗</a>`);
  document.getElementById("geneMeta").innerHTML =
    `${g.ensembl ? "<b>" + g.ensembl + "</b> · " : ""}${g.biotype || "—"} · <b>${g.n_entities}</b> RCD entities · ${ext.join(" · ")}`;
  const gi = g.info || {};
  let infoBlock = "";
  if (gi.name || gi.alias || gi.type || gi.location || gi.summary) {
    infoBlock = `<div style="background:#f8fafc; border:1px solid #e7e5e4; border-radius:10px; padding:12px 14px; margin:12px 0; font-size:13.5px; line-height:1.55; color:#1c1917;">
      <div style="font-size:12px; letter-spacing:0.06em; color:#c2410c; margin-bottom:6px; font-weight:600;">Gene information</div>
      ${gi.name ? `<div style="font-weight:600;">${gi.name}</div>` : ""}
      ${gi.alias ? `<div>Aliases: ${gi.alias}</div>` : ""}
      ${gi.type ? `<div>Type: ${gi.type}</div>` : ""}
      ${gi.location ? `<div>Location: ${gi.location}</div>` : ""}
      ${gi.summary ? `<div style="margin-top:6px;">${gi.summary}</div>` : ""}
      ${g.entrez ? `<div style="margin-top:6px;"><a href="https://www.ncbi.nlm.nih.gov/gene/${g.entrez}" target="_blank">NCBI Gene ↗</a></div>` : ""}
    </div>`;
  }
  document.getElementById("geneInfo").innerHTML = infoBlock;
  document.getElementById("geneEntities").innerHTML = g.entities.map(en => `
    <tr>
      <td class="ent-link" data-name="${en.name}" style="cursor:pointer;"><b style="color:#1d4ed8;">${en.name}</b></td>
      <td><span class="pill" style="background:${LEVEL_COLORS[en.level]}33;color:${LEVEL_TEXT_COLORS[en.level]}">${en.level}</span></td>
      <td>${DIR(en) ? `<span class="pill ${dirPill(DIR(en))}">${DIR(en)}</span>` : "—"}</td>
      <td><span class="pill ${MECH_PILL[en.mech] || "p-insuf"}">${en.mech || "—"}</span></td>
    </tr>`).join("");
}

// custom tooltips (immediate, styled, delegated for dynamic cells)
const tipEl = document.getElementById("tip");
document.addEventListener("mouseover", ev => {
  const el = ev.target.closest(".has-tip");
  if (!el) return;
  tipEl.textContent = el.dataset.tip || "";
  tipEl.style.opacity = 1;
  tipEl.style.left = (ev.clientX + 12) + "px";
  tipEl.style.top = (ev.clientY - 10) + "px";
});
document.addEventListener("mousemove", ev => {
  const el = ev.target.closest(".has-tip");
  if (!el) return;
  tipEl.style.left = (ev.clientX + 12) + "px";
  tipEl.style.top = (ev.clientY - 10) + "px";
});
document.addEventListener("mouseout", ev => {
  const el = ev.target.closest(".has-tip");
  if (el && !el.contains(ev.relatedTarget)) tipEl.style.opacity = 0;
});

// entity jump dropdown (native select, scrollable, all 53 entities)
const entityJump = document.getElementById("entityJump");
if (entityJump) {
  const entityNames = Object.keys(DATA.entities).sort();
  const entityList = document.getElementById("entityList");
  if (entityList) entityList.innerHTML = entityNames.map(n => `<option value="${n}">`).join("");
  entityJump.addEventListener("keydown", ev => {
    if (ev.key !== "Enter") return;
    const raw = entityJump.value.trim();
    const match = entityNames.find(n => n.toLowerCase() === raw.toLowerCase());
    if (match) {
      showEntity(match);
    } else if (raw) {
      document.getElementById("pmidModalTitle").textContent = "RCD entity not found";
      document.getElementById("pmidModalBody").innerHTML =
        `<p>Sorry, <b>${esc(raw)}</b> is not in the RCDome database (${entityNames.length} canonicalized RCD-related entities).</p>`;
      document.getElementById("pmidModal").style.display = "flex";
    }
  });
}

// gene jump (free text; type a gene + Enter; not-found -> pop-up)
const geneJump = document.getElementById("geneJump");
if (geneJump) {
  const geneNames = Object.keys(DATA.genes).sort();
  const geneList = document.getElementById("geneList");
  if (geneList) geneList.innerHTML = geneNames.map(n => `<option value="${n}">`).join("");
  geneJump.addEventListener("keydown", ev => {
    if (ev.key !== "Enter") return;
    const raw = geneJump.value.trim();
    const key = raw.toUpperCase();
    if (DATA.genes[key]) {
      showGene(key);
      geneJump.value = "";
    } else if (raw) {
      document.getElementById("pmidModalTitle").textContent = "Gene not found";
      document.getElementById("pmidModalBody").innerHTML =
        `<p>Sorry, <b>${esc(raw)}</b> is not in the RCDome database (${geneNames.length.toLocaleString('en-US')} HGNC-validated genes).</p>`;
      document.getElementById("pmidModal").style.display = "flex";
    }
  });
}

// read URL params (from the dome click)
const params = new URLSearchParams(window.location.search);
const type = params.get("type");
const name = params.get("name");
if (type === "gene" && name) showGene(name);
else if (type === "entity" && name) showEntity(name);
else showEntity("Apoptosis");
</script>
</body>
</html>
"""

html = html.replace("__DATA__", DATA_JSON).replace("__PMID_TITLES__", PMID_TITLES_JSON)
open(BASE + "/Shiny app/detail_page_wireframe.html", "w", encoding="utf-8").write(html)
print("generated detail_page_wireframe.html with", len(entities), "entities and", len(gene_data), "genes")
print("sample entity Apoptosis:", entities.get('Apoptosis', {}).get('definition', '')[:80])
print("sample gene BAX:", gene_data.get('BAX', {}))
