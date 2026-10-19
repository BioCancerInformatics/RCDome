# -*- coding: utf-8 -*-
import os, io, sys
import pandas as pd, docx
sys.stdout.reconfigure(encoding='utf-8')

BASE = "D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
os.chdir(BASE)

res = []
def chk(scope, name, ok, detail=""):
    res.append((scope, name, "PASS" if ok else "FAIL", detail))

# ---- 1. MANUSCRIPT ----
d = docx.Document("manuscript_V027/RCDome_manuscript_governance_V026.docx")
mt = "\n".join(p.text for p in d.paragraphs)
for t in d.tables:
    for r in t.rows:
        for c in r.cells: mt += "\n" + c.text
M = "Manuscript"
chk(M, "Europe PMC 12.3M (not 40M)", "12.3 million full-text articles" in mt and "40 million biomedical" not in mt)
chk(M, "T1 2,864 (not 2,862)", "2,864 pairs (12.7%)" in mt and "2,862 pairs" not in mt)
chk(M, "T3 8,212 (not 8,213)", "8,212 pairs (36.5%)" in mt and "8,213 pairs" not in mt)
chk(M, "EXECUTOR precision reworded", "No unsupported EXECUTOR classification remained" in mt and "EXECUTOR precision was 100%" not in mt)
chk(M, "19 of 20 NCCD (not 19/19)", "19 of 20 NCCD terms" in mt and "19/19 NCCD" not in mt)
chk(M, "33 non-NCCD (not 40)", "33 non-NCCD entities" in mt and "40 non-NCCD" not in mt)
chk(M, "'for the first time' removed", "for the first time" not in mt)
chk(M, "28-entities reworded", "de novo definitions anchored to a founding PMID" in mt)
chk(M, "direction scope clarified", "across all role-resolved associations" in mt)
chk(M, "T1-T4 pointer added", "as defined in Methods, Evidence Tier Assignment" in mt)

# ---- 2. MATRIX ----
m = pd.read_csv("output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv", dtype=str, low_memory=False)
u = m.drop_duplicates(['gene_symbol','rcd_form_canonical'])
Mx = "Matrix"
tier = m.evidence_tier.value_counts().to_dict()
chk(Mx, "tier T1=2864 T3=8212 (rows)", tier.get("T1")==2864 and tier.get("T3")==8212)
chk(Mx, "tier sum 22473", sum(tier.values())==22473)
role = u.cot_role.value_counts().to_dict()
chk(Mx, "role (unique pairs) 9489/469/5/11605", role.get("REGULATOR")==9489 and role.get("EXECUTOR")==469 and role.get("MARKER")==5 and role.get("UNCERTAIN")==11605)
dirn = u.cot_direction.value_counts().to_dict()
chk(Mx, "direction (unique pairs) 5070/4755/11743", dirn.get("PROMOTES")==5070 and dirn.get("PROTECTS")==4755 and dirn.get("UNCLEAR")==11743)

# ---- 3. DECODER ----
dec = pd.read_csv("RCDome Decoder/RCDome_Decoder_53.csv", dtype=str)
Dc = "Decoder"
chk(Dc, "NCCD 20 / non-NCCD 33", (dec.galluzzi_nccd_status=="NCCD_2018_INVARIANT").sum()==20 and (dec.galluzzi_nccd_status=="NOT_IN_NCCD_2018").sum()==33)
chk(Dc, "definition sources 20/12/19/1/1", dec.operational_definition_source.value_counts().to_dict()=={'NCCD_2018_VERBATIM':20,'RODRIGUES_S1A':12,'FOUNDING_DRAFT':19,'PRE_PUBMED':1,'COMPOSITE':1})

# ---- 4. SUPPLEMENTARY + APP ----
S = "Supplementary/app"
sup = docx.Document("manuscript_V027/RCDome_manuscript_V027_supplementary_information.docx")
st = "\n".join(p.text for p in sup.paragraphs)
for t in sup.tables:
    for r in t.rows:
        for c in r.cells: st += "\n" + c.text
for k in ["2,862","8,213","40 million","40 non-NCCD","19/19 NCCD","EXECUTOR precision was 100%"]:
    chk(S, f"no stale '{k}' in supplementary", k not in st)

# app: any stale tier/role numbers in modules
import glob
stale = ["2,862 pairs","8,213 pairs","9,489 regulators, 469 executors, 5 markers, and 11,605"]
for f in glob.glob("Shiny app/RCDome_Atlas/APP/modules/*.R") + glob.glob("Shiny app/RCDome_Atlas/APP/www/*.html"):
    s = io.open(f, encoding="utf-8", errors="replace").read()
    for k in stale:
        if k in s:
            chk(S, f"no stale '{k[:30]}' in {os.path.basename(f)}", False)
chk(S, "app checked for stale numbers", True)

# ---- output ----
out = pd.DataFrame(res, columns=["scope","check","status","detail"])
out.to_excel("Expert Nomenclature and Ontological Adjudication Audit/HIGOR_COMPLIANCE_AUDIT.xlsx", index=False)
md = io.StringIO()
md.write("# Higor corrections — compliance audit (manuscript + parts)\n\n")
md.write(f"**Total:** {len(out)} · **PASS:** {(out.status=='PASS').sum()} · **FAIL:** {(out.status=='FAIL').sum()}\n\n")
for scope in out.scope.unique():
    sub = out[out.scope==scope]
    md.write(f"## {scope}\n\n")
    for _,r in sub.iterrows():
        md.write(f"- [{'✓' if r.status=='PASS' else '✗'}] {r['check']}\n")
    md.write("\n")
fails = out[out.status=='FAIL']
md.write("## Failures\n\n")
if len(fails):
    for _,r in fails.iterrows(): md.write(f"- **{r['scope']}** — {r['check']}\n")
else:
    md.write("None.\n")
io.open("Expert Nomenclature and Ontological Adjudication Audit/HIGOR_COMPLIANCE_AUDIT.md","w",encoding="utf-8").write(md.getvalue())
print(f"checks={len(out)} pass={(out.status=='PASS').sum()} fail={(out.status=='FAIL').sum()}")
for _,r in out[out.status=='FAIL'].iterrows():
    print("FAIL:", r['scope'], "|", r['check'])
