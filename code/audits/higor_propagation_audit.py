# -*- coding: utf-8 -*-
import os, io, sys, glob
import pandas as pd, docx, openpyxl
sys.stdout.reconfigure(encoding='utf-8')

BASE = "D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
os.chdir(BASE)

STALE = ["40 million biomedical", "12.3 million full-text", "2,862 pairs", "8,213 pairs",
         "EXECUTOR precision was 100%", "executor precision from 47% to 100%",
         "EXECUTOR precision 100.0%", "19/19 NCCD", "19 of 20 NCCD", "40 non-NCCD",
         "19 were drafted de novo", "for the first time",
         "without a PMID-referenced definition"]
GOOD = {
 "167,868 open-access full-text articles": None,
 "2,864 pairs (12.7%)": None,
 "8,212 pairs (36.5%)": None,
 "No unsupported EXECUTOR classification remained": None,
 "Unsupported EXECUTOR claims remaining: 0": None,
 "20/20 NCCD terms": None,
 "33 non-NCCD entities": None,
 "20 were drafted de novo": None,
 "across all role-resolved associations": None,
 "confidence tier": None,
}

res = []
def chk(scope, name, ok):
    res.append((scope, name, "PASS" if ok else "FAIL"))

def scan_text(scope, txt):
    for s in STALE:
        if s in txt:
            chk(scope, f"stale '{s[:40]}' absent", False)
    for g in GOOD:
        if g in txt:
            GOOD[g] = scope

# 1. manuscript
d = docx.Document("manuscript_V027/RCDome_manuscript_governance_V026.docx")
mt = "\n".join(p.text for p in d.paragraphs)
for t in d.tables:
    for r in t.rows:
        for c in r.cells: mt += "\n"+c.text
scan_text("Manuscript", mt)

# 2. supplementary info
d2 = docx.Document("manuscript_V027/RCDome_manuscript_V027_supplementary_information.docx")
st = "\n".join(p.text for p in d2.paragraphs)
for t in d2.tables:
    for r in t.rows:
        for c in r.cells: st += "\n"+c.text
scan_text("Supplementary info", st)

# 3. supplementary tables (all sheets)
x = pd.ExcelFile("manuscript_V027/RCDome_manuscript_V027_supplementary_tables.xlsx")
allx = ""
for sh in x.sheet_names:
    df = x.parse(sh, dtype=str).astype(str)
    allx += "\n".join(" ".join(map(str,row)) for row in df.values)
scan_text("Supp tables (all sheets)", allx)

# 4. matrix CSV
m = pd.read_csv("output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv", dtype=str, low_memory=False, nrows=5).fillna("")
chk("Matrix", "columns include evidence_tier + confidence_tier", "evidence_tier" in m.columns and "confidence_tier" in m.columns)

# 5. decoder CSV
dec = pd.read_csv("RCDome Decoder/RCDome_Decoder_53.csv", dtype=str).fillna("")
dectxt = " ".join(dec.columns) + " " + " ".join(dec.astype(str).values.ravel().tolist())
scan_text("Decoder CSV", dectxt)

# 6. app modules + www + board + data + html
appfiles = (glob.glob("Shiny app/RCDome_Atlas/APP/modules/*.R") +
            glob.glob("Shiny app/RCDome_Atlas/APP/R/*.R") +
            glob.glob("Shiny app/RCDome_Atlas/APP/www/*.html") +
            glob.glob("Shiny app/RCDome_Atlas/APP/board/*.md") +
            ["Shiny app/RCDome_Atlas/APP/global.R","Shiny app/RCDome_Atlas/APP/server.R","Shiny app/RCDome_Atlas/APP/ui.R"])
apptxt = ""
for f in appfiles:
    try: apptxt += "\n" + io.open(f, encoding="utf-8", errors="replace").read()
    except: pass
scan_text("App (R/html/board)", apptxt)

# 7. decoder docs + descriptors + code
codefiles = (glob.glob("RCDome Decoder/*.md") + glob.glob("RCDome Decoder/*.py") +
             glob.glob("docs/*.md"))
codetxt = ""
for f in codefiles:
    try: codetxt += "\n" + io.open(f, encoding="utf-8", errors="replace").read()
    except: pass
scan_text("Decoder docs + code", codetxt)

# output
out = pd.DataFrame(res, columns=["scope","check","status"])
out.to_excel("Expert Nomenclature and Ontological Adjudication Audit/HIGOR_PROPAGATION_AUDIT.xlsx", index=False)
md = io.StringIO()
md.write("# Higor corrections — project-wide propagation audit\n\n")
md.write(f"**Total checks:** {len(out)} · **PASS:** {(out.status=='PASS').sum()} · **FAIL:** {(out.status=='FAIL').sum()}\n\n")
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
io.open("Expert Nomenclature and Ontological Adjudication Audit/HIGOR_PROPAGATION_AUDIT.md","w",encoding="utf-8").write(md.getvalue())
print(f"checks={len(out)} pass={(out.status=='PASS').sum()} fail={(out.status=='FAIL').sum()}")
for _,r in out[out.status=='FAIL'].iterrows():
    print("FAIL:", r['scope'], "|", r['check'])
