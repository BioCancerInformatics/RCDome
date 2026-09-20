# -*- coding: utf-8 -*-
"""Ocean-deep pré-sal audit — every approved change + horizontal/vertical spread, item by item."""
import csv, io, os, sys, hashlib, openpyxl, docx
csv.field_size_limit(10**9)
sys.stdout.reconfigure(encoding='utf-8')

ROOT = "D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
GH   = "D:/RCDome_github"
res=[]
def ok(m): res.append(("PASS",m)); print(f"  [PASS] {m}")
def bad(m): res.append(("FAIL",m)); print(f"  [FAIL] {m}")
def md5(p):
    try: return hashlib.md5(open(p,'rb').read()).hexdigest()[:10]
    except: return 'MISS'

drows = list(csv.DictReader(io.open(os.path.join(ROOT,"RCDome Decoder/RCDome_Decoder_53.csv"), encoding='utf-8-sig')))
dec = {r['rcd_form']: r for r in drows}
with io.open(os.path.join(ROOT,"output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv"), encoding='utf-8-sig') as f:
    mrows = list(csv.DictReader(f))
wb = openpyxl.load_workbook(os.path.join(ROOT,"manuscript_V026/RCDome_manuscript_V026_supplementary_tables.xlsx"))
s3 = {r[1]: r[2] for r in wb["Table S3"].iter_rows(min_row=3, values_only=True)}
s11 = wb["Table S11"]; h11=[c.value for c in s11[1]]; j11={x:i for i,x in enumerate(h11)}
s12 = wb["Table S12"]; h12=[c.value for c in s12[1]]; j12={x:i for i,x in enumerate(h12)}
s12rows = {r[0]: r for r in s12.iter_rows(min_row=2, values_only=True)}
md = docx.Document(os.path.join(ROOT,"manuscript_V026/RCDome_manuscript_governance_V026.docx"))
mtxt = "\n".join(p.text for p in md.paragraphs)

print("="*78); print("A. ENTITY RE-DERIVATIONS (§8–§10) — decoder / matrix / S3 / S12"); print("="*78)
EXP = {
  'Lysoptosis':('SUBTYPE','L2'), 'Lysozincrosis':('SUBTYPE','L2'),
  'Mitoptosis':('CELLULAR_PROCESS','L5'), 'Aponecrosis':('UMBRELLA','L5'),
  'Pyronecrosis':('SYNONYM','L5'), 'Floatptosis':('CELL_TYPE','L4'), 'Spectosis':('CELL_TYPE','L4'),
  'NECSO':('CORE_PENDING','L1'), 'Mitoxyperilysis':('CORE_PENDING','L1'), 'Triaptosis':('CORE_PENDING','L1'),
}
for e,(cat,lv) in EXP.items():
    d = dec.get(e); m = [r for r in mrows if r['rcd_form_canonical']==e]
    ok(f"{e}: decoder={d['category']}, matrix={lv}") if d and d['category']==cat and m and all(r['rcdome_level']==lv for r in m) else bad(f"{e}: {d['category'] if d else '?'}/{set(r['rcdome_level'] for r in m) if m else '?'}")
    ok(f"{e}: S3={s3.get(e)}") if s3.get(e) in ('L1 Modalities','L2 Subtypes','L3 Triggers','L4 Functional/contextual','L5 Generic/umbrella/taxon') else bad(f"{e} S3={s3.get(e)}")
    if e in s12rows:
        ok(f"{e}: S12 level={s12rows[e][j12['adjudicated_level']]}") if s12rows[e][j12['adjudicated_level']]==lv else bad(f"{e} S12")
ok("no EMERGING/LEGACY categories remain") if not any(r['category'] in ('EMERGING','LEGACY') for r in drows) else bad("EMERGING/LEGACY remain")

print("="*78); print("B. RENAMES (§3/§4) — Entotic cell death / NETotic cell death"); print("="*78)
for e in ['Entotic cell death','NETotic cell death']:
    ok(f"decoder has {e!r}") if e in dec else bad(f"{e}")
    m = [r for r in mrows if r['rcd_form_canonical']==e]
    ok(f"matrix {e} ({len(m)} rows)") if m else bad(f"{e}")
ok("old 'Entosis'/'NETosis' not canonical") if not any(r['rcd_form_canonical'] in ('Entosis','NETosis') for r in mrows) else bad("old names remain")
ok("S3 renamed") if ('Entotic cell death' in s3 and 'NETotic cell death' in s3) else bad("S3 rename")

print("="*78); print("C. ONTOLOGY DISTRIBUTION (19/7/2/13/12)"); print("="*78)
from collections import Counter
ent={}
for r in mrows: ent.setdefault(r['rcd_form_canonical'], r['rcdome_level'])
prop = dict(Counter(ent.values()))
ok(f"distribution = {prop}") if prop=={'L1':19,'L2':7,'L3':2,'L4':13,'L5':12} else bad(f"dist={prop}")
ok("manuscript 19/7/2/13/12 + 19/53") if ('19 RCD modalities' in mtxt and '7 subtypes' in mtxt and '2 triggers' in mtxt and '13 functional/contextual' in mtxt and '12 generic/umbrella/taxon' in mtxt and '19/53' in mtxt and '16/53' not in mtxt and 'only 16' not in mtxt) else bad("manuscript counts")

print("="*78); print("D. NOMENCLATURE (MC/RS/QG/ET/CT)"); print("="*78)
ok("decoder RS1-RS6, no C1-C6") if all(c in drows[0] for c in ['RS1','RS2','RS3','RS4','RS5','RS6']) and not any(c in drows[0] for c in ['C1','C2','C3','C4','C5','C6']) else bad("decoder RS")
ok("S11 RS1-RS6") if all(f'RS{i}' in h11 for i in range(1,7)) and not any(f'C{i}' in h11 for i in range(1,7)) else bad("S11 RS")
ok("S12 MC1-MC5") if all(f'MC{i}' in h12 for i in range(1,6)) and not any(f'C{i}' in h12 for i in range(1,6)) else bad("S12 MC")
s8 = [str(x) for r in wb["Table S8"].iter_rows(min_row=3, values_only=True) for x in r if x]
ok("S8 QG1-QG5") if any('QG1:' in x for x in s8) and not any('Q1:' in x for x in s8) else bad("S8 QG")
et = Counter(r['evidence_tier'] for r in mrows); ct = Counter(r['confidence_tier'] for r in mrows)
ok("matrix ET1-ET4") if any(k.startswith('ET') for k in et) and not any(k.startswith('T') for k in et) else bad("ET")
ok("matrix CT1-CT4") if any(k.startswith('CT') for k in ct) and not any(k.startswith('T') for k in ct) else bad("CT")
ok("manuscript MC/RS/ET/CT") if ('(MC1) possession' in mtxt and 'RS1 extent of research' in mtxt and 'evidence tier (ET1' in mtxt and 'confidence tier (CT1' in mtxt) else bad("ms nomenclature")

print("="*78); print("E. REFERENCE DISCIPLINE"); print("="*78)
tri = dec['Triaptosis']
ok("Triaptosis founding=39446948") if tri['founding_pmid']=='39446948' and tri['primary_refs_pmids']=='39446948;39638924' else bad("Triaptosis PMID")
vcd = dec['Vacuolar cell death']
ok("VCD citation Dictyostelium+plant") if 'Dictyostelium' in vcd['reference_citation'] and '24344187' in vcd['reference_citation'] else bad("VCD")

print("="*78); print("F. GOVERNANCE ARTIFACTS (§23/§25/§12-13)"); print("="*78)
s6 = docx.Document(os.path.join(ROOT,"manuscript_V026/RCDome_manuscript_V026_supplementary_information.docx"))
s6txt = "\n".join(p.text for p in s6.paragraphs)
ok("S6 held-out") if 'Held-out validation' in s6txt and '20260919' in s6txt else bad("S6")
ok("§25 three curators") if 'primary curator (EM-A)' in mtxt and 'VdSL' in mtxt and 'HACN' in mtxt else bad("§25")
s1 = io.open(os.path.join(ROOT,"Expert Nomenclature and Ontological Adjudication Audit/Supplementary_Note_S1_Terminology_Ontological_Adjudication_Governance.md"), encoding='utf-8').read()
ok("S1 cautions") if 'Classification cautions' in s1 and 'phagocyte' in s1 else bad("S1")

print("="*78); print("G. HORIZONTAL + VERTICAL CONSISTENCY (md5)"); print("="*78)
pairs = [
 ("decoder CSV", os.path.join(ROOT,"RCDome Decoder/RCDome_Decoder_53.csv"), [os.path.join(ROOT,"RCDome_distribution/data/RCDome_Decoder_53.csv"), os.path.join(GH,"data/RCDome_Decoder_53.csv"), os.path.join(GH,"app/data/RCDome_Decoder_53.csv")]),
 ("decoder XLSX", os.path.join(ROOT,"RCDome Decoder/RCDome_Decoder_53.xlsx"), [os.path.join(GH,"data/RCDome_Decoder_53.xlsx"), os.path.join(ROOT,"RCDome_distribution/data/RCDome_Decoder_53.xlsx")]),
 ("matrix RDS", os.path.join(ROOT,"output databases/Phase 2C output/unified_gene_rcd_matrix_V026.rds"), [os.path.join(ROOT,"RCDome_distribution/data/unified_gene_rcd_matrix_V026.rds")]),
 ("supp tables", os.path.join(ROOT,"manuscript_V026/RCDome_manuscript_V026_supplementary_tables.xlsx"), [os.path.join(GH,"docs/manuscript/RCDome_manuscript_V026_supplementary_tables.xlsx")]),
 ("manuscript", os.path.join(ROOT,"manuscript_V026/RCDome_manuscript_governance_V026.docx"), [os.path.join(GH,"docs/manuscript/RCDome_manuscript_governance_V026.docx")]),
]
for name, src, dests in pairs:
    m0 = md5(src); allok = all(md5(d)==m0 for d in dests)
    ok(f"{name}: {len(dests)} copies identical") if allok else bad(f"{name} mismatch")

print("="*78); print("H. APP CODE"); print("="*78)
mo = io.open(os.path.join(ROOT,"RCDome_distribution/modules/mod_od.R"), encoding='utf-8').read()
mg = io.open(os.path.join(ROOT,"RCDome_distribution/modules/mod_rcd_grid.R"), encoding='utf-8').read()
mb = io.open(os.path.join(ROOT,"RCDome_distribution/modules/mod_board.R"), encoding='utf-8').read()
ok("mod_od.R RS1-RS6") if 'RS1' in mo and '"C1"' not in mo else bad("mod_od")
ok("mod_rcd_grid.R RS1-RS6") if 'dr$RS1' in mg and 'dr$C1' not in mg else bad("mod_rcd_grid")
ok("mod_board.R RS + ET/CT") if 'RS1 - ' in mb and 'ET1 gold' in mb and 'CT1-CT4' in mb else bad("mod_board")

nfail = sum(1 for s,_ in res if s=="FAIL")
print("="*78); print(f"RESULT: {len(res)} checks, {nfail} FAIL"); print("="*78)
with io.open(os.path.join(ROOT,"docs/AUDIT_ocean_deep_2026-09-19.md"),'w',encoding='utf-8') as f:
    f.write("# Ocean-deep pré-sal audit — all approved Victor changes + spread (2026-09-19)\n\n")
    f.write(f"**Result: {len(res)} checks, {nfail} FAIL**\n\n")
    for s,m in res: f.write(f"- [{s}] {m}\n")
print("saved docs/AUDIT_ocean_deep_2026-09-19.md")
