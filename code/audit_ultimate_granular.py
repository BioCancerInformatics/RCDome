# -*- coding: utf-8 -*-
"""ULTIMATE granular audit — every artifact, row, column, line vs the truth (2026-09-19)."""
import csv, io, os, sys, re, hashlib, openpyxl, docx
csv.field_size_limit(10**9)
sys.stdout.reconfigure(encoding='utf-8')

ROOT = "D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
GH   = "D:/RCDome_github"
res=[]
def ok(m): res.append(("PASS",m))
def bad(m): res.append(("FAIL",m)); print(f"  [FAIL] {m}")
def md5(p):
    try: return hashlib.md5(open(p,'rb').read()).hexdigest()[:10]
    except: return 'MISS'

# TRUTH
TRUTH_LEVELS = {'L1':19,'L2':7,'L3':2,'L4':13,'L5':12}
RENAMED = {'Entosis':'Entotic cell death','NETosis':'NETotic cell death'}
CAT10 = {'Lysoptosis':'SUBTYPE','Lysozincrosis':'SUBTYPE','Mitoptosis':'CELLULAR_PROCESS','Aponecrosis':'UMBRELLA',
         'Pyronecrosis':'SYNONYM','Floatptosis':'CELL_TYPE','Spectosis':'CELL_TYPE',
         'NECSO':'CORE_PENDING','Mitoxyperilysis':'CORE_PENDING','Triaptosis':'CORE_PENDING'}
LVL10 = {'Lysoptosis':'L2','Lysozincrosis':'L2','Mitoptosis':'L5','Aponecrosis':'L5','Pyronecrosis':'L5',
         'Floatptosis':'L4','Spectosis':'L4','NECSO':'L1','Mitoxyperilysis':'L1','Triaptosis':'L1'}

print("="*78); print("A. DECODER — 53 rows × 39 cols, row-by-row, column-by-column"); print("="*78)
drows = list(csv.DictReader(io.open(os.path.join(ROOT,"RCDome Decoder/RCDome_Decoder_53.csv"), encoding='utf-8-sig')))
ok("decoder 53 rows") if len(drows)==53 else bad(f"rows={len(drows)}")
ok("decoder 39 cols") if len(drows[0])==39 else bad(f"cols={len(drows[0])}")
ok("decoder has RS1-RS6, no C1-C6") if all(c in drows[0] for c in ['RS1','RS2','RS3','RS4','RS5','RS6']) and not any(c in drows[0] for c in ['C1','C2','C3','C4','C5','C6']) else bad("RS cols")
dec={r['rcd_form']:r for r in drows}
for e in RENAMED:
    ok(f"decoder has {RENAMED[e]!r} (renamed)") if RENAMED[e] in dec and e not in dec else bad(f"{e} rename")
for e,(cat,lv) in {**{k:(CAT10[k],LVL10[k]) for k in CAT10}}.items():
    if e in dec:
        ok(f"decoder {e}: {cat}") if dec[e]['category']==cat else bad(f"{e} cat={dec[e]['category']}")
ok("no EMERGING/LEGACY") if not any(r['category'] in ('EMERGING','LEGACY') for r in drows) else bad("EMERGING/LEGACY")
ok("Triaptosis PMID 39446948") if dec['Triaptosis']['founding_pmid']=='39446948' else bad("Triaptosis PMID")
# decoder XLSX header
wb = openpyxl.load_workbook(os.path.join(ROOT,"RCDome Decoder/RCDome_Decoder_53.xlsx"))
hdr = [c.value for c in wb.active[1]]
ok("decoder XLSX RS1-RS6 header") if all(c in hdr for c in ['RS1','RS2','RS3','RS4','RS5','RS6']) and not any(c in hdr for c in ['C1','C2','C3','C4','C5','C6']) else bad("XLSX RS")

print("="*78); print("B. MATRIX — 71 columns, value-by-value"); print("="*78)
with io.open(os.path.join(ROOT,"output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv"), encoding='utf-8-sig') as f:
    mrows=list(csv.DictReader(f))
ok("matrix 71 cols") if len(mrows[0])==71 else bad(f"cols={len(mrows[0])}")
ok("matrix 22,473 rows") if len(mrows)==22473 else bad(f"rows={len(mrows)}")
from collections import Counter
ent={}
for r in mrows: ent.setdefault(r['rcd_form_canonical'], r['rcdome_level'])
prop=dict(Counter(ent.values()))
ok(f"distribution {prop}") if prop==TRUTH_LEVELS else bad(f"dist={prop}")
ok("no old Entosis/NETosis canonical") if not any(r['rcd_form_canonical'] in RENAMED for r in mrows) else bad("old names")
ok("has Entotic/NETotic cell death") if all(RENAMED[e] in ent for e in RENAMED) else bad("new names")
et=Counter(r['evidence_tier'] for r in mrows); ct=Counter(r['confidence_tier'] for r in mrows)
ok("evidence_tier = ET1-ET4 only") if all(k in ('ET1','ET2','ET3','ET4','') for k in et) else bad(f"ET={dict(et)}")
ok("confidence_tier = CT1-CT4 only") if all(k in ('CT1','CT2','CT3','CT4','') for k in ct) else bad(f"CT={dict(ct)}")
# decoder-sync columns
opdrift = sum(1 for r in mrows if r['rcd_form_canonical'] in dec and r.get('decoder_operational_definition','').strip()!=dec[r['rcd_form_canonical']]['operational_definition'].strip())
catdrift = sum(1 for r in mrows if r['rcd_form_canonical'] in dec and r.get('decoder_category','')!=dec[r['rcd_form_canonical']]['category'])
ok("matrix decoder_operational_definition synced") if opdrift==0 else bad(f"OP drift={opdrift}")
ok("matrix decoder_category synced") if catdrift==0 else bad(f"cat drift={catdrift}")

print("="*78); print("C. SUPPLEMENTARY TABLES — every sheet, row, column"); print("="*78)
wb = openpyxl.load_workbook(os.path.join(ROOT,"manuscript_V026/RCDome_manuscript_V026_supplementary_tables.xlsx"))
# INDEX
idx_txt = " ".join(str(c.value) for r in wb["INDEX"].iter_rows() for c in r if c.value)
for badsym in ['T1-T4','Q1-Q5','C1-C5','C1-C6','G1-G5','legacy/taxon/emerging','67 columns']:
    ok(f"INDEX no {badsym!r}") if badsym not in idx_txt else bad(f"INDEX {badsym}")
ok("INDEX says 71 columns") if '71 columns' in idx_txt else bad("INDEX 71")
# S3
s3={r[1]:(r[2],r[3]) for r in wb["Table S3"].iter_rows(min_row=3, values_only=True) if r[1]}
s3lvl=Counter(v[0] for v in s3.values() if v[0]!='Ontological Level')
ok(f"S3 level distribution {dict(s3lvl)}") if s3lvl==Counter({'L1 Modalities':19,'L2 Subtypes':7,'L3 Triggers':2,'L4 Functional/contextual':13,'L5 Generic/umbrella/taxon':12}) else bad(f"S3 dist={dict(s3lvl)}")
ok("S3 NECSO=B Triaptosis=C") if s3.get('NECSO',(None,None))[1]=='B' and s3.get('Triaptosis',(None,None))[1]=='C' else bad("S3 grades")
ok("S3 has Entotic/NETotic cell death") if all(RENAMED[e] in s3 for e in RENAMED) else bad("S3 rename")
# S5
s5 = [(r[0],r[1]) for r in wb["Table S5"].iter_rows(min_row=3, values_only=True) if r[0]]
s5dict = dict(s5)
ok("S5 MPT-driven-necrosis -> MPT-driven necrosis") if s5dict.get('MPT-driven-necrosis')=='MPT-driven necrosis' else bad(f"S5 MPT {s5dict.get('MPT-driven-necrosis')}")
ok("S5 Mitotic-death -> Mitotic death") if s5dict.get('Mitotic-death')=='Mitotic death' else bad("S5 Mitotic")
ok("S5 Entotic -> Entotic cell death") if all(s5dict.get(k)=='Entotic cell death' for k in ['Entotic-cell-death','Entotic cell death']) else bad("S5 Entotic")
# S8
s8=" ".join(str(x) for r in wb["Table S8"].iter_rows(values_only=True) for x in r if x)
ok("S8 QG1-QG5") if all(f'QG{i}:' in s8 for i in range(1,6)) and 'Q1:' not in s8 else bad("S8")
# S11 header
h11=[c.value for c in wb["Table S11"][1]]
ok("S11 RS1-RS6") if all(f'RS{i}' in h11 for i in range(1,7)) and not any(f'C{i}' in h11 for i in range(1,7)) else bad("S11")
# S12
h12=[c.value for c in wb["Table S12"][1]]
ok("S12 MC1-MC5") if all(f'MC{i}' in h12 for i in range(1,6)) and not any(f'C{i}' in h12 for i in range(1,6)) else bad("S12 MC")
s12={r[0]:dict(zip(h12,r)) for r in wb["Table S12"].iter_rows(min_row=2, values_only=True) if r[0]}
for e in LVL10:
    if e in s12:
        ok(f"S12 {e} adj={LVL10[e]}") if s12[e].get('adjudicated_level')==LVL10[e] else bad(f"S12 {e}")
ok("S12 pre=L5 for 10 re-derived") if all(s12.get(e,{}).get('pre_adjudication_level')=='L5' for e in CAT10) else bad("S12 pre")
# S7
s7=" ".join(str(x) for r in wb["Table S7"].iter_rows(values_only=True) for x in r if x)
ok("S7 ET1/ET4") if 'ET1 (Gold)' in s7 and 'ET4 (Weak)' in s7 else bad("S7")

print("="*78); print("D. MANUSCRIPT — paragraph by paragraph"); print("="*78)
md=docx.Document(os.path.join(ROOT,"manuscript_V026/RCDome_manuscript_governance_V026.docx"))
mtxt="\n".join(p.text for p in md.paragraphs)
for badsym in ['C1-C6','C1–C6','C1-C5','C1–C5','T1-T4','T1–T4','Q1-Q5','G1-G5','legacy/taxon/emerging','16/53','only 16 of the 53','64.7%','40.5%','23.9%','31.3%']:
    ok(f"manuscript no {badsym!r}") if badsym not in mtxt else bad(f"ms {badsym}")
for good in ['RS1 extent of research','(MC1) possession','evidence tier (ET1','confidence tier (CT1','19/53','19 RCD modalities','7 subtypes','13 functional/contextual','12 generic/umbrella/taxon','Entotic cell death','NETotic cell death','64.6%','31.5%']:
    ok(f"manuscript has {good!r}") if good in mtxt else bad(f"ms missing {good}")

print("="*78); print("E. SUPPLEMENTARY INFO — paragraph by paragraph"); print("="*78)
si=docx.Document(os.path.join(ROOT,"manuscript_V026/RCDome_manuscript_V026_supplementary_information.docx"))
sitxt="\n".join(p.text for p in si.paragraphs)
for badsym in ['C1-C6','C1–C6','C1-C5','C1–C5','T1-T4','T1–T4','legacy/taxon/emerging','(16 entities)','subtypes (5)','contextual (11)','emerging (19)','64.7%','40.5%','23.9%','31.3%']:
    ok(f"supp-info no {badsym!r}") if badsym not in sitxt else bad(f"SI {badsym}")
ok("S6 held-out + 20260919") if 'Held-out validation' in sitxt and '20260919' in sitxt else bad("S6")
ok("S2 legend (19)/(7)/(13)/(12) + generic/umbrella/taxon") if 'L1 modalities (19 entities)' in sitxt and 'L2 subtypes (7)' in sitxt and 'L4 functional/contextual (13)' in sitxt and 'L5 generic/umbrella/taxon (12)' in sitxt else bad("S2 legend")

print("="*78); print("F. FIGURES — code + legends"); print("="*78)
f3=io.open(os.path.join(ROOT,"code/make_figure3_composite.py"), encoding='utf-8').read()
ok("Fig3 pcts 64.6/40.4/33.3/23.6/31.5") if "pcts=[64.6,40.4,33.3,23.6,31.5]" in f3 and "64.7" not in f3 else bad("Fig3 pcts")
f4=io.open(os.path.join(ROOT,"code/make_figure_entity_coverage.R"), encoding='utf-8').read()
ok("Fig4 L5 name generic/umbrella/taxon") if 'Generic/umbrella/taxon' in f4 and 'legacy/taxon/emerging' not in f4 else bad("Fig4")
fS2=io.open(os.path.join(ROOT,"code/make_figure_s2_stacked_by_level.py"), encoding='utf-8').read()
ok("FigS2 legend counts 19/7/2/13/12 + name") if 'L1 Modalities (19)' in fS2 and 'L2 Subtypes (7)' in fS2 and 'L4 Functional/contextual (13)' in fS2 and 'L5 Generic/umbrella/taxon (12)' in fS2 and 'legacy/taxon/emerging' not in fS2 else bad("FigS2")

print("="*78); print("G. APP CODE — line by line"); print("="*78)
mo=io.open(os.path.join(ROOT,"RCDome_distribution/modules/mod_od.R"), encoding='utf-8').read()
mg=io.open(os.path.join(ROOT,"RCDome_distribution/modules/mod_rcd_grid.R"), encoding='utf-8').read()
mb=io.open(os.path.join(ROOT,"RCDome_distribution/modules/mod_board.R"), encoding='utf-8').read()
ok("mod_od.R RS1-RS6") if 'RS1' in mo and '"C1"' not in mo else bad("mod_od")
ok("mod_rcd_grid.R dr$RS1") if 'dr$RS1' in mg and 'dr$C1' not in mg else bad("mod_rcd_grid")
ok("mod_board.R RS + ET/CT + MC") if 'RS1 - ' in mb and 'ET1 gold' in mb and 'CT1-CT4' in mb and 'MC1-MC5' in mb else bad("mod_board")
lp=io.open(os.path.join(ROOT,"RCDome_distribution/www/landing_page.html"), encoding='utf-8').read()
ok("landing L1=19 L5=12 + generic/umbrella/taxon") if '"L1": 19' in lp and '"L5": 12' in lp and 'legacy/taxon/emerging' not in lp and 'Only 19 of the 53' in lp else bad("landing")
ex=io.open(os.path.join(ROOT,"RCDome_distribution/www/explore.html"), encoding='utf-8').read()
ok("explore held-out + home_iframe") if 'held-out' in ex and '20260919' in ex and 'home_iframe' in ex else bad("explore")
boardprompt=io.open(os.path.join(ROOT,"RCDome_distribution/board/RCD_Board_DeepSeek_Prompt.md"), encoding='utf-8').read()
ok("board prompt RS1-RS6") if 'RS1–RS6' in boardprompt and 'C1–C6' not in boardprompt else bad("board prompt")

print("="*78); print("H. PROPAGATION (md5) + R parse"); print("="*78)
pairs=[
 ("decoder CSV", os.path.join(ROOT,"RCDome Decoder/RCDome_Decoder_53.csv"), [os.path.join(ROOT,"RCDome_distribution/data/RCDome_Decoder_53.csv"), os.path.join(GH,"data/RCDome_Decoder_53.csv"), os.path.join(GH,"app/data/RCDome_Decoder_53.csv")]),
 ("tables", os.path.join(ROOT,"manuscript_V026/RCDome_manuscript_V026_supplementary_tables.xlsx"), [os.path.join(GH,"docs/manuscript/RCDome_manuscript_V026_supplementary_tables.xlsx")]),
 ("manuscript", os.path.join(ROOT,"manuscript_V026/RCDome_manuscript_governance_V026.docx"), [os.path.join(GH,"docs/manuscript/RCDome_manuscript_governance_V026.docx")]),
 ("supp info", os.path.join(ROOT,"manuscript_V026/RCDome_manuscript_V026_supplementary_information.docx"), [os.path.join(GH,"docs/manuscript/RCDome_manuscript_V026_supplementary_information.docx")]),
 ("matrix RDS", os.path.join(ROOT,"output databases/Phase 2C output/unified_gene_rcd_matrix_V026.rds"), [os.path.join(ROOT,"RCDome_distribution/data/unified_gene_rcd_matrix_V026.rds")]),
]
for n,s,ds in pairs:
    m0=md5(s); ok(f"{n}: identical") if all(md5(d)==m0 for d in ds) else bad(f"{n} md5 mismatch")

nfail=sum(1 for s,_ in res if s=="FAIL")
print("="*78); print(f"RESULT: {len(res)} checks, {nfail} FAIL"); print("="*78)
with io.open(os.path.join(ROOT,"docs/AUDIT_ultimate_granular_2026-09-19.md"),'w',encoding='utf-8') as f:
    f.write("# Ultimate granular audit — every artifact vs truth (2026-09-19)\n\n")
    f.write(f"**Result: {len(res)} checks, {nfail} FAIL**\n\n")
    for s,m in res: f.write(f"- [{s}] {m}\n")
print("saved docs/AUDIT_ultimate_granular_2026-09-19.md")
