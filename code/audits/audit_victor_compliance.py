# -*- coding: utf-8 -*-
"""Ocean-deep compliance audit — Victor app-report fixes (2026-09-19)."""
import csv, io, os, sys, hashlib, subprocess
sys.stdout.reconfigure(encoding='utf-8')
csv.field_size_limit(10**9)

ROOT = "D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
GH   = "D:/RCDome_github"
res = []
def ok(m): res.append(("PASS", m)); print(f"  [PASS] {m}")
def bad(m): res.append(("FAIL", m)); print(f"  [FAIL] {m}")
def md5(p):
    try: return hashlib.md5(open(p,'rb').read()).hexdigest()
    except Exception: return None

print("="*80); print("A. DECODER DATA INTEGRITY + CORRECTNESS"); print("="*80)
src = os.path.join(ROOT, "RCDome Decoder/RCDome_Decoder_53.csv")
rows = list(csv.DictReader(io.open(src, encoding='utf-8-sig')))
ok(f"decoder rows = {len(rows)} (expect 53)") if len(rows)==53 else bad(f"rows={len(rows)}")
ok(f"decoder cols = {len(rows[0])} (expect 39)") if len(rows[0])==39 else bad(f"cols={len(rows[0])}")
by = {r['rcd_form']: r for r in rows}

DROP = {"Apoptosis","Autophagy","Methuosis","Mitochondrial permeability transition","Mitoptosis","Necrosis","Oxeiptosis","Paraptosis"}
for e in DROP:
    v = by[e].get('primary_refs_pmids','')
    ok(f"{e}: primary_refs={v} (no 29362479)") if "29362479" not in v else bad(f"{e}: still has 29362479 -> {v}")

c = by.get("Senescence and Autophagy in Cancer", {})
for k, exp in [("category","COMPOSITE"),("definition_status","COMPOSITE"),("galluzzi_nccd_status","COMPOSITE")]:
    (ok if c.get(k)==exp else bad)(f"composite {k}={c.get(k)!r} (expect {exp})")
ok("composite founding_pmid='composite'") if c.get('founding_pmid')=='composite' else bad("composite founding")
ok("composite reference_pmid=29362479;36864290") if c.get('reference_pmid')=='29362479;36864290' else bad(f"composite ref_pmid={c.get('reference_pmid')}")
ok("composite citation has 'NCCD_2018' + 'not a distinct NCCD entity'") if ('NCCD_2018' in c.get('reference_citation','') and 'not a distinct NCCD entity' in c.get('reference_citation','')) else bad(f"composite citation={c.get('reference_citation')}")

v = by.get("Vacuolar cell death", {})
ok("VCD category=TAXON") if v.get('category')=='TAXON' else bad(f"VCD category={v.get('category')}")
ok("VCD founding_pmid=15358773") if v.get('founding_pmid')=='15358773' else bad(f"VCD founding={v.get('founding_pmid')}")
ok("VCD secondary=24344187;35390283") if v.get('secondary_refs_pmids')=='24344187;35390283' else bad(f"VCD secondary={v.get('secondary_refs_pmids')}")
ok("VCD citation has Dictyostelium + plant context + both plant PMIDs") if ('Dictyostelium' in v.get('reference_citation','') and '24344187' in v.get('reference_citation','') and '35390283' in v.get('reference_citation','')) else bad(f"VCD citation={v.get('reference_citation')}")

# no other entity has COMPOSITE status
comp_others = [r['rcd_form'] for r in rows if r['galluzzi_nccd_status']=='COMPOSITE']
ok(f"COMPOSITE status only on composite entity ({comp_others})") if comp_others==["Senescence and Autophagy in Cancer"] else bad(f"COMPOSITE on: {comp_others}")

# no non-composite NOT_IN_NCCD entity still lists 29362479
bad_ones = [r['rcd_form'] for r in rows if r['galluzzi_nccd_status']=='NOT_IN_NCCD_2018' and r['rcd_form']!='Senescence and Autophagy in Cancer' and '29362479' in r['primary_refs_pmids']]
ok("no NOT_IN_NCCD_2018 entity (non-composite) still lists 29362479 in primary_refs") if not bad_ones else bad(f"remaining: {bad_ones}")

print("="*80); print("B. APP CODE (R modules)"); print("="*80)
def has(f, s): return s in io.open(f, encoding='utf-8').read()
mo = os.path.join(ROOT, "RCDome_distribution/modules/mod_od.R")
ok("mod_od.R: composite founding branch present") if has(mo, 'f == "founding_pmid"') and has(mo, 'Composite —') else bad("mod_od.R composite branch")
ok("mod_od.R: reference_pmid uses render_pmids (multi-PMID)") if 'f %in% c("reference_pmid", "primary_discovery_reference")' in io.open(mo,encoding='utf-8').read() and 'val <- render_pmids(v)' in io.open(mo,encoding='utf-8').read() else bad("mod_od.R ref_pmid render_pmids")
ok("mod_od.R: reference_citation links first PMID") if 'first <- trimws(strsplit(pmid, ";")[[1]])[1]' in io.open(mo,encoding='utf-8').read() else bad("mod_od.R first PMID")
mg = os.path.join(ROOT, "RCDome_distribution/modules/mod_rcd_grid.R")
ok('mod_rcd_grid.R: collapse="\\n\\n" in build_decoder_desc') if 'collapse = "\\n\\n"' in io.open(mg,encoding='utf-8').read() else bad("mod_rcd_grid collapse")
mb = os.path.join(ROOT, "RCDome_distribution/modules/mod_board.R")
ok('mod_board.R: NCCD status desc includes / COMPOSITE') if 'NOT_IN_NCCD_2018 / COMPOSITE' in io.open(mb,encoding='utf-8').read() else bad("mod_board desc")

print("="*80); print("C. HTML NAVIGATION (back to the dome)"); print("="*80)
HOME = "indexOf('Home')===0"
htmls = ["RCDome_distribution/www/explore.html","RCDome_distribution/www/detail_page_wireframe.html","RCDome_distribution/www/module_placeholder.html"]
for h in htmls:
    p = os.path.join(ROOT, h); s = io.open(p, encoding='utf-8').read()
    n_back = s.count("Back to the dome"); n_onclick = s.count(HOME); n_href = s.count('href="landing_page.html"')
    ok(f"{h}: {n_back} back-links, {n_onclick} Home-clicks, {n_href} stale hrefs") if (n_onclick>=n_back and n_href==0) else bad(f"{h}: back={n_back} onclick={n_onclick} href={n_href}")
gp = os.path.join(GH, "app/generate_detail_page.py"); s = io.open(gp, encoding='utf-8').read()
ok("generate_detail_page.py: Home-click, no landing_page href") if HOME in s and 'href="landing_page.html"' not in s else bad("generate_detail_page.py")

print("="*80); print("D. PROPAGATION CONSISTENCY (md5)"); print("="*80)
pairs = [
  ("decoder CSV", os.path.join(ROOT,"RCDome Decoder/RCDome_Decoder_53.csv"),
   [os.path.join(ROOT,"RCDome_distribution/data/RCDome_Decoder_53.csv"), os.path.join(GH,"data/RCDome_Decoder_53.csv"), os.path.join(GH,"app/data/RCDome_Decoder_53.csv")]),
  ("decoder XLSX", os.path.join(ROOT,"RCDome Decoder/RCDome_Decoder_53.xlsx"), [os.path.join(GH,"data/RCDome_Decoder_53.xlsx")]),
  ("mod_od.R", os.path.join(ROOT,"RCDome_distribution/modules/mod_od.R"), [os.path.join(GH,"app/modules/mod_od.R")]),
  ("mod_rcd_grid.R", os.path.join(ROOT,"RCDome_distribution/modules/mod_rcd_grid.R"), [os.path.join(GH,"app/modules/mod_rcd_grid.R")]),
  ("mod_board.R", os.path.join(ROOT,"RCDome_distribution/modules/mod_board.R"), [os.path.join(GH,"app/modules/mod_board.R")]),
  ("explore.html", os.path.join(ROOT,"RCDome_distribution/www/explore.html"), [os.path.join(GH,"app/www/explore.html"), os.path.join(GH,"app/explore.html")]),
  ("detail_page_wireframe.html", os.path.join(ROOT,"RCDome_distribution/www/detail_page_wireframe.html"), [os.path.join(GH,"app/www/detail_page_wireframe.html"), os.path.join(GH,"app/detail_page_wireframe.html")]),
  ("module_placeholder.html", os.path.join(ROOT,"RCDome_distribution/www/module_placeholder.html"), [os.path.join(GH,"app/www/module_placeholder.html")]),
]
for name, src, dests in pairs:
    m0 = md5(src)
    all_ok = all(md5(d)==m0 for d in dests)
    (ok if all_ok else bad)(f"{name}: all {len(dests)} copies identical")

print("="*80); print("E. R SYNTAX (parse)"); print("="*80)
R = r'"C:\Program Files\R\R-4.2.3\bin\Rscript.exe"'
for m in ["mod_od.R","mod_rcd_grid.R","mod_board.R"]:
    p = os.path.join(ROOT,"RCDome_distribution/modules", m)
    r = subprocess.run(f'{R} -e "invisible(parse(\\"{p}\\".replace(chr(92),chr(47))))"', shell=True, capture_output=True, text=True)
    ok(f"{m} parses") if "Error" not in r.stderr+r.stdout else bad(f"{m} parse: {r.stderr[:200]}")

print("="*80); print("F. MATRIX + PROMPT CONSISTENCY"); print("="*80)
mp = os.path.join(ROOT, "output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv")
with io.open(mp, encoding='utf-8-sig') as f:
    mh = next(csv.reader(f))
    mrows = list(csv.DictReader(io.open(mp, encoding='utf-8-sig')))
if 'decoder_category' in mh:
    vcd_cats = set(r['decoder_category'] for r in mrows if r.get('rcd_form_canonical')=='Vacuolar cell death')
    ok(f"matrix VCD decoder_category = {vcd_cats} (expect TAXON)") if vcd_cats=={'TAXON'} else bad(f"matrix VCD decoder_category={vcd_cats}")
else:
    bad("matrix has no decoder_category column")
# matrix does NOT carry decoder reference fields (different fields)
if not any('primary_refs_pmids' in c or 'reference_citation' in c or 'galluzzi_nccd_status' in c for c in mh):
    ok("matrix does not mirror decoder primary_refs/citation/nccd_status (no propagation needed)")
else:
    bad("matrix mirrors decoder reference fields — needs propagation")

prompt = io.open(os.path.join(ROOT,"RCDome_distribution/board/RCD_Board_DeepSeek_Prompt.md"), encoding='utf-8').read()
ok("board prompt has no hardcoded stale PMIDs (29362479/15358773) in decoder-reference role") if ("29362479" not in prompt and "15358773" not in prompt) else bad("board prompt hardcodes PMIDs")

# summary
nfail = sum(1 for s,_ in res if s=="FAIL")
print("="*80); print(f"RESULT: {len(res)} checks, {nfail} FAIL"); print("="*80)
with io.open(os.path.join(ROOT,"docs/AUDIT_Victor_compliance_2026-09-19.md"),'w',encoding='utf-8') as f:
    f.write("# Ocean-deep compliance audit — Victor app-report fixes (2026-09-19)\n\n")
    f.write(f"**Result: {len(res)} checks, {nfail} FAIL**\n\n")
    for s,m in res: f.write(f"- [{s}] {m}\n")
print("saved docs/AUDIT_Victor_compliance_2026-09-19.md")
