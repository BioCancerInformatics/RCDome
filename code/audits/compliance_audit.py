# -*- coding: utf-8 -*-
import os, re, sys, io
import pandas as pd, docx, openpyxl
sys.stdout.reconfigure(encoding='utf-8')

BASE = "D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
os.chdir(BASE)

results = []  # (artifact, check, status, detail)

def check(artifact, name, ok, detail=""):
    results.append((artifact, name, "PASS" if ok else "FAIL", detail))

def read_text(p):
    return io.open(p, encoding="utf-8", errors="replace").read()

def docx_text(p):
    d = docx.Document(p)
    t = "\n".join(x.text for x in d.paragraphs)
    for tb in d.tables:
        for r in tb.rows:
            for c in r.cells:
                t += "\n" + c.text
    return t

# ============ 1. MANUSCRIPT (governance docx) ============
mt = docx_text("manuscript_V027/RCDome_manuscript_governance_V026.docx")
ml = mt.lower()
A = "Manuscript"
check(A, "11 functional/contextual present", "11 functional/contextual" in mt)
check(A, "12 functional/contextual absent", "12 functional/contextual" not in mt)
check(A, "19 generic/umbrella present", "19 generic/umbrella/legacy/taxon/emerging" in mt)
check(A, "18 generic/umbrella absent", "18 generic/umbrella/legacy/taxon/emerging" not in mt)
check(A, "canonicalized RCD-related entity present", "canonicalized rcd-related entit" in ml)
check(A, "canonical RCD form vocabulary absent", "canonical rcd form vocabulary" not in ml)
check(A, "53 canonical RCD entities absent", "53 canonical rcd entities" not in ml)
check(A, "VCD L1->L5 sentence absent", "vacuolar cell death was reclassified from L1 to L5" not in mt)
check(A, "VCD cross-species category absent", "vacuolar cell death was reclassified from L4 to L5 as a taxon-specific" in mt)

# ============ 2. SUPPLEMENTARY INFO ============
st = docx_text("manuscript_V027/RCDome_manuscript_V027_supplementary_information.docx")
B = "Supplementary info"
check(B, "normalized name present", "by normalized name or its" in st)
check(B, "canonical name absent", "by canonical name or its" not in st)

# ============ 3. SUPPLEMENTARY TABLES (all sheets) ============
x = pd.ExcelFile("manuscript_V027/RCDome_manuscript_V027_supplementary_tables.xlsx")
C = "Supp tables"
idx = x.parse("INDEX", dtype=str).astype(str).apply(lambda c: c.fillna(""))
check(C, "INDEX canonicalized vocab", idx.apply(lambda c:c.str.contains("Canonicalized RCD-Related Entity Vocabulary", na=False)).any().any())
check(C, "INDEX old vocab absent", not idx.apply(lambda c:c.str.contains("Canonical RCD Form Vocabulary", na=False)).any().any())
vd = x.parse("Variable Descriptor", dtype=str).astype(str).apply(lambda c: c.fillna(""))
check(C, "VarDesc Canonicalized entity name", vd.apply(lambda c:c.str.contains("Canonicalized RCD-related entity name", na=False)).any().any())
check(C, "VarDesc no 'Canonical RCD form name'", not vd.apply(lambda c:c.str.contains("Canonical RCD form name", na=False)).any().any())
check(C, "VarDesc no 'Canonical name'", not vd.apply(lambda c:c.str.contains("^Canonical name$|Canonical name", na=False)).any().any())
t11 = x.parse("Table S11", dtype=str)
v11 = t11[t11.rcd_form=="Vacuolar cell death"].iloc[0]
check(C, "S11 VCD category=TAXON", v11["category"]=="TAXON")
check(C, "S11 VCD species plant+protist", "Arabidopsis" in str(v11["species_scope"]) and "Dictyostelium" in str(v11["species_scope"]) and "not human" in str(v11["species_scope"]))
check(C, "S11 VCD maturity provisional", v11["evidence_maturity"]=="provisional")
e11 = t11[t11.rcd_form=="Erebosis"].iloc[0]
check(C, "S11 Erebosis Drosophila", e11["species_scope"]=="Drosophila (invertebrate model)")
check(C, "S11 Erebosis emerging", e11["evidence_maturity"]=="emerging")

# ============ 4. MATRIX CSV ============
m = pd.read_csv("output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv", dtype=str, low_memory=False)
D = "Matrix CSV"
v = m[m.rcd_form_canonical=="Vacuolar cell death"]
check(D, "VCD 24 rows L5", len(v)==24 and (v.rcdome_level=="L5").all())
check(D, "VCD category TAXON", (v.decoder_category=="TAXON").all())
check(D, "VCD note Dictyostelium", v.elic_onto_operational_note.str.contains("Dictyostelium", na=False).all())
lv = m.drop_duplicates('rcd_form_canonical').rcdome_level.value_counts().to_dict()
check(D, "levels 16/5/2/11/19", lv=={'L1':16,'L2':5,'L3':2,'L4':11,'L5':19}, str(lv))

# ============ 5. DECODER CSV ============
dec = pd.read_csv("RCDome Decoder/RCDome_Decoder_53.csv", dtype=str)
E = "Decoder CSV"
vc = dec[dec.rcd_form=="Vacuolar cell death"].iloc[0]
check(E, "VCD TAXON", vc["category"]=="TAXON")
check(E, "VCD plant+protist", "Arabidopsis" in str(vc["species_scope"]) and "Dictyostelium" in str(vc["species_scope"]) and "not human" in str(vc["species_scope"]))
check(E, "VCD provisional", vc["evidence_maturity"]=="provisional")
check(E, "VCD def reworded", "taxon-specific pattern" in vc["operational_definition"])
er = dec[dec.rcd_form=="Erebosis"].iloc[0]
check(E, "Erebosis Drosophila", er["species_scope"]=="Drosophila (invertebrate model)")
check(E, "Erebosis emerging", er["evidence_maturity"]=="emerging")
nonl1 = dec[dec.hard_gate_status!="L1-ELIGIBLE"]
check(E, "no modality in non-L1 defs", not nonl1.operational_definition.str.lower().str.contains("modality", na=False).any())
check(E, "maturity lowercase", dec.evidence_maturity.str.islower().all())
rod = dec[dec.reference_citation.str.contains("Rodrigues", na=False)]
check(E, "Rodrigues 2025 + 41048343", (rod.reference_citation=="Rodrigues et al. 2025 (Dataset S1A)").all() and (rod.reference_pmid=="41048343").all())
check(E, "VCD def: Dictyostelium (not yeast)", "Dictyostelium discoideum (protist) study" in vc["operational_definition"] and "yeast" not in vc["operational_definition"].lower())

# ============ 6. APP ============
F = "App"
for f, old in [("Shiny app/RCDome_Atlas/APP/modules/mod_omic.R","53 canonical entities"),
               ("Shiny app/RCDome_Atlas/APP/modules/mod_board.R","53 canonical entities"),
               ("Shiny app/RCDome_Atlas/APP/modules/mod_rcd_grid.R","53 canonical entities"),
               ("Shiny app/RCDome_Atlas/APP/www/landing_page.html","53 canonical entities"),
               ("Shiny app/RCDome_Atlas/APP/www/dome_prototype.html","53 canonical entities")]:
    s = read_text(f)
    check(F, f"{os.path.basename(f)}: '{old}' absent", old not in s)
s = read_text("Shiny app/RCDome_Atlas/APP/modules/mod_od.R")
check(F, "mod_od: canonicalized + bona fide", "53 canonicalized RCD-related entities" in s and "bona fide cell-death modalities" in s)
s = read_text("Shiny app/RCDome_Atlas/APP/modules/mod_network.R")
check(F, "mod_network: normalized entity", "normalized entity" in s)
appd = pd.read_csv("Shiny app/RCDome_Atlas/APP/data/RCDome_Decoder_53.csv", dtype=str)
check(F, "app decoder == source", appd.equals(dec))

# ============ 7. DECODER DOCS + CODE ============
G = "Decoder docs/code"
s = read_text("RCDome Decoder/MandM_operational_definitions.md")
check(G, "MandM: canonicalized", "53 canonicalized RCD-related entities" in s)
s = read_text("RCDome Decoder/Results_OD_census.md")
check(G, "Results_OD_census: canonicalized", "53 canonicalized RCD-related entities" in s)
s = read_text("RCDome Decoder/build_variable_descriptor.py")
check(G, "build_variable_descriptor: Canonicalized", "Canonicalized RCD-related entity name" in s)
check(G, "build_variable_descriptor: Normalized name", "Normalized name" in s)

# ============ 8. DOCS ============
H = "docs"
s = read_text("docs/RCDome_Traceability_Contract.md")
check(H, "Traceability: Canonicalized RCD-related entities", "Canonicalized RCD-related entities | 53" in s)
check(H, "Traceability: 11/19 (not 12/18)", "11 functional/contextual · 19 generic" in s and "12 functional/contextual · 18 generic" not in s)
s = read_text("docs/RCDome_Gene_Traceability_Spec.md")
check(H, "Gene_Traceability_Spec: CANONICALIZED", "CANONICALIZED RCD-RELATED ENTITY NAMES" in s)

# ============ 9. LEVEL-DISTRIBUTION PROPAGATION (every UI copy) ============
I = "Level counts"
for f in ["Shiny app/RCDome_Atlas/APP/www/explore.html",
          "Shiny app/explore.html"]:
    s = read_text(f)
    base = os.path.basename(os.path.dirname(f)) + "/" + os.path.basename(f)
    check(I, f"{base}: 11/19 present", "11 functional/contextual · 19 generic" in s)
    check(I, f"{base}: 12/18 absent", "12 functional/contextual · 18 generic" not in s)
OLD_LC = '{"L1": 16, "L5": 18, "L2": 5, "L4": 12, "L3": 2}'
NEW_LC = '{"L1": 16, "L5": 19, "L2": 5, "L4": 11, "L3": 2}'
for f in ["Shiny app/RCDome_Atlas/APP/www/landing_page.html",
          "Shiny app/RCDome_Atlas/APP/www/dome_prototype.html",
          "Shiny app/landing_page.html",
          "Shiny app/dome_prototype.html"]:
    s = read_text(f)
    base = os.path.basename(f)
    check(I, f"{base}: LEVEL_COUNTS 11/19", NEW_LC in s and OLD_LC not in s)

# ============ 10. CROSS-ARTIFACT FIELD ALIGNMENT (shared fields) ============
J = "Alignment"
appd2 = pd.read_csv("Shiny app/RCDome_Atlas/APP/data/RCDome_Decoder_53.csv", dtype=str)
check(J, "decoder CSV == app CSV", dec.equals(appd2))
dxl = pd.read_excel("RCDome Decoder/RCDome_Decoder_53.xlsx", dtype=str)
cols = [c for c in dec.columns if c in dxl.columns]
check(J, "decoder CSV == XLSX", dec[cols].equals(dxl[cols]))
t11b = pd.read_excel("manuscript_V027/RCDome_manuscript_V027_supplementary_tables.xlsx", sheet_name="Table S11", dtype=str)
cols = [c for c in dec.columns if c in t11b.columns]
a = dec[cols].sort_values("rcd_form").reset_index(drop=True)
b = t11b[cols].sort_values("rcd_form").reset_index(drop=True)
def empty(x): return pd.isna(x) or str(x).strip()==""
reald = sum(1 for c in cols for i in range(len(a)) if not (empty(a.at[i,c]) and empty(b.at[i,c])) and a.at[i,c]!=b.at[i,c])
check(J, "Table S11 == decoder (non-empty)", reald==0, f"({reald} diffs)")
mc = m.drop_duplicates("rcd_form_canonical")[["rcd_form_canonical","decoder_category"]].rename(columns={"rcd_form_canonical":"rcd_form"})
mg = dec[["rcd_form","category"]].merge(mc, on="rcd_form", how="left")
check(J, "matrix decoder_category == decoder category", (mg.category==mg.decoder_category).all())

# ============ 11. HIGOR HACN + BOARD FOLLOW-UP (accepted corrections) ============
K = "Higor follow-up"
for f in ["analysis/Digital Molecular Board/RCD_Board_Governance.md",
          "Shiny app/RCDome_Atlas/APP/board/RCD_Board_Governance.md",
          "analysis/Digital Molecular Board/RCD_Board_DeepSeek_Prompt.md",
          "Shiny app/RCDome_Atlas/APP/board/RCD_Board_DeepSeek_Prompt.md"]:
    s = read_text(f)
    base = os.path.basename(f)
    check(K, f"Board {base}: 'four evidence tiers' absent", "four evidence tiers" not in s)
    check(K, f"Board {base}: 'T1 Observed' absent", "T1 Observed" not in s)
    check(K, f"Board {base}: 'EVIDENCE HIERARCHY' absent", "EVIDENCE HIERARCHY" not in s)
    check(K, f"Board {base}: 'hallucination-free' absent", "hallucination-free" not in s)
for f in ["analysis/Digital Molecular Board/RCD_Board_Governance.md",
          "Shiny app/RCDome_Atlas/APP/board/RCD_Board_Governance.md"]:
    s = read_text(f)
    base = os.path.basename(f)
    check(K, f"Board {base}: 'four provenance categories' present", "four provenance categories" in s)
    check(K, f"Board {base}: 'P1 Observed' present", "P1 Observed" in s)
    check(K, f"Board {base}: scrub runs first", "scrub runs first" in s)
    check(K, f"Board {base}: zero hallucination benchmark", "zero hallucination in the performed benchmark" in s)
check(K, "MS: confidence tier distinct from evidence tier", "confidence tier is a metric distinct from the evidence tier" in mt)
check(K, "MS: 167,868 Phase 2B", "167,868 open-access full-text articles" in mt)
check(K, "MS: 20 de novo", "20 were drafted de novo" in mt)
check(K, "MS: 20/20 NCCD", "20/20 NCCD terms" in mt)
check(K, "MS: 28-entities provenance", "were not covered by the previous multi-optosis operational-definition set" in mt)
t14txt = " ".join(pd.read_excel("manuscript_V027/RCDome_manuscript_V027_supplementary_tables.xlsx", sheet_name="Table S14", dtype=str).fillna("").astype(str).values.ravel())
check(K, "Table S14: 'EXECUTOR precision' absent", "EXECUTOR precision" not in t14txt)
check(K, "Table S14: unsupported EXECUTOR claims", "Unsupported EXECUTOR claims remaining: 0" in t14txt)

# ============ 12. LEVEL PROPAGATION (VCD L4->L5) ============
L = "Level propagation"
f4 = pd.read_csv("Figures/Figure_4_entity_coverage_data.csv", dtype=str).fillna("")
check(L, "Fig4 data: VCD = L5", (f4[f4.rcd_form_canonical=="Vacuolar cell death"].rcdome_level=="L5").all())
check(L, "Fig4 data: L4=11 / L5=19", (f4.rcdome_level=="L4").sum()==11 and (f4.rcdome_level=="L5").sum()==19)
s3 = read_text("code/make_figure3_composite.py")
check(L, "Fig3 script: pcts 23.9/31.3 (not 23.6/31.4)", "23.9,31.3" in s3 and "23.6,31.4" not in s3)
sp = read_text("code/make_figure_s2_stacked_by_level.py")
check(L, "FigS2 py legend: (11)/(19)", "Functional/contextual (11)" in sp and "taxon/emerging (19)" in sp)
sr = read_text("code/make_figure_source_classification.R")
check(L, "FigS2 R legend: (11)/(19)", "Functional/contextual (11)" in sr and "taxon/emerging (19)" in sr)
check(L, "MS: 23.6% absent", "23.6%" not in mt)
check(L, "MS: 31.4% absent", "31.4%" not in mt)
st2 = docx_text("manuscript_V027/RCDome_manuscript_V027_supplementary_information.docx")
check(L, "SUP legend: (12)/(18) absent", "functional/contextual (12)" not in st2 and "taxon/emerging (18)" not in st2)

# ---- output ----
out = pd.DataFrame(results, columns=["artifact","check","status","detail"])
out.to_excel("Expert Nomenclature and Ontological Adjudication Audit/COMPLIANCE_AUDIT.xlsx", index=False)

md = io.StringIO()
md.write("# RCDome change-compliance audit — per-artifact (documented)\n\n")
md.write("Every change from Pre-Audit 0 + the 53-entity adjudication, checked individually per artifact.\n\n")
md.write(f"**Total checks:** {len(out)} · **PASS:** {(out.status=='PASS').sum()} · **FAIL:** {(out.status=='FAIL').sum()}\n\n")
for art in out.artifact.unique():
    sub = out[out.artifact==art]
    md.write(f"## {art}\n\n")
    for _, r in sub.iterrows():
        md.write(f"- [{'✓' if r.status=='PASS' else '✗'}] {r['check']}" + (f" — {r['detail']}" if r['detail'] else "") + "\n")
    md.write("\n")
# list FAILs
fails = out[out.status=="FAIL"]
md.write("## FAILURES (must fix)\n\n")
if len(fails):
    for _, r in fails.iterrows():
        md.write(f"- **{r['artifact']}** — {r['check']} {r['detail']}\n")
else:
    md.write("None.\n")
io.open("Expert Nomenclature and Ontological Adjudication Audit/COMPLIANCE_AUDIT.md", "w", encoding="utf-8").write(md.getvalue())

print(f"checks={len(out)} pass={(out.status=='PASS').sum()} fail={(out.status=='FAIL').sum()}")
print("\nFAILURES:")
for _, r in out[out.status=='FAIL'].iterrows():
    print(" ", r['artifact'], "|", r['check'], "|", r['detail'])
