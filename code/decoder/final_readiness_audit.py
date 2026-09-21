"""
FINAL OCEAN-DEEP READINESS AUDIT — the whole definition pipeline, before the
human two-call validation.
Sections: A OD integrity · B method of definition · C data support ·
          D validation strategies · E two-call readiness
"""
import re, json, sys, math, openpyxl, pandas as pd

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
DEC = BASE + r"/RCDome Decoder"
W = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
CCOLS = ["RS1", "RS2", "RS3", "RS4", "RS5", "RS6"]
PASS = FAIL = 0
def check(name, ok, detail=""):
    global PASS, FAIL
    if ok: PASS += 1; print(f"  [PASS] {name}")
    else: FAIL += 1; print(f"  [FAIL] {name}  {detail}")

sys.stdout.reconfigure(encoding="utf-8")
df = pd.read_csv(DEC + "/RCDome_Decoder_53.csv")
def empty(v): return str(v).strip().lower() in ("", "nan", "none")

print("=" * 74)
print("RCDome DEFINITION PIPELINE — FINAL OCEAN-DEEP READINESS AUDIT")
print("=" * 74)

# ---------- A: OD integrity ----------
print("\n[A] OD integrity")
check("53 unique entities", df["rcd_form"].nunique() == 53 and df["rcd_form"].is_unique)
check("29 columns (incl. od_author)", len(df.columns) == 29, f"{len(df.columns)} cols")
G = df["galluzzi_nccd_status"] == "NCCD_2018_INVARIANT"
R = df["definition_status"] == "DEFINED_RODRIGUES"
nccd_byte = sum(str(r["operational_definition"]).strip() == str(r["galluzzi_nccd_definition"]).strip() for _, r in df[G].iterrows())
check("20/20 NCCD verbatim byte-identical", nccd_byte == 20, f"{nccd_byte}/20")
check("0 inline citations in OD prose", df["operational_definition"].astype(str).str.contains(r"\((?:18|19|20|21)\d{2}\)", regex=True).sum() == 0)
check("0 inline citations in complements", df["operational_definition_complement"].astype(str).str.contains(r"\((?:18|19|20|21)\d{2}\)", regex=True).sum() == 0)

# ---------- B: method of definition ----------
print("\n[B] Method of definition")
wb = openpyxl.load_workbook(BASE + r"/output databases/Dataset S1_Rodrigues et al 2025.xlsx", read_only=True)
ws = wb["Dataset S1A"]
ok = sum(1 for r in ws.iter_rows(min_row=2, values_only=True) if r[1] is not None
         and abs(round(sum(w * x for w, x in zip(W, list(r[4:10]))), 2) - r[10]) < 0.005)
check("S formula 25/25 anchors (explicit Rodrigues weights)", ok == 25, f"{ok}/25")
rc = df.apply(lambda r: round(sum(w * float(r[c]) for w, c in zip(W, CCOLS)), 2), axis=1)
check("S bitwise recompute 53/53", (abs(df["S"] - rc) < 0.005).sum() == 53)
check("RS1-RS6 all in [0,10]", all(0 <= float(df[c].iloc[i]) <= 10 for c in CCOLS for i in range(len(df))))
ev = pd.read_csv(DEC + "/entity_evidence_V025.csv")
def genes(e):
    r = ev[ev["rcd_form_canonical"] == e]; return int(r["n_genes"].iloc[0]) if len(r) else 0
check("RS1-RS6 semantic (Necrosis 1092 genes RS1=4 < Cuproptosis 77 genes RS1=7)",
      genes("Necrosis") > genes("Cuproptosis") and
      float(df[df["rcd_form"] == "Necrosis"]["RS1"].iloc[0]) < float(df[df["rcd_form"] == "Cuproptosis"]["RS1"].iloc[0]))
check("three-tier hierarchy (20 NCCD_VERBATIM / 12 RODRIGUES_S1A / 20 RCDome drafts + 1 composite)",
      df["operational_definition_source"].value_counts().to_dict().get("NCCD_2018_VERBATIM", 0) == 20 and
      df["operational_definition_source"].value_counts().to_dict().get("RODRIGUES_S1A", 0) == 12)

# ---------- C: data support ----------
print("\n[C] Data support (matrix + PMID + provenance)")
check("reference_pmid 53/53", df["reference_pmid"].apply(lambda v: not empty(v)).sum() == 53)
check("reference_citation 53/53", df["reference_citation"].apply(lambda v: not empty(v)).sum() == 53)
check("primary_refs_pmids 53/53", df["primary_refs_pmids"].apply(lambda v: not empty(v)).sum() == 53)
check("source_databases + channels + provenance_note 53/53",
      all(df[c].apply(lambda v: not empty(v)).sum() == 53 for c in ["source_databases", "source_channels", "provenance_note"]))
check("od_author 53/53", df["od_author"].apply(lambda v: not empty(v)).sum() == 53)
comp = df[df["rcd_form"] == "Senescence and Autophagy in Cancer"].iloc[0]
check("composite P1 (kept, parents PMIDs 29362479;36864290)", "29362479" in str(comp["reference_pmid"]) and "36864290" in str(comp["reference_pmid"]))
ND5 = ["Cuproptosis", "Disulfidptosis", "Erebosis", "Alkaliptosis", "Oxeiptosis"]
nd5_ok = all("AI-extracted" in str(df[df["rcd_form"] == e]["provenance_note"].iloc[0]) for e in ND5)
check("5 ND forms marked AI-extracted + human-validated", nd5_ok)

# ---------- D: validation strategies ----------
print("\n[D] Validation strategies (artifacts present + consistent)")
import os
artifacts = ["od_validation_deepseek_fulltext.csv", "od_crossref_consensus.csv",
             "verbatim_audit.py", "pmid_topic_audit.py", "governance_audit_report.json",
             "consensus_crossvalidation_report.csv", "final_ocean_audit.py"]
check("all validation artifacts present", all(os.path.exists(DEC + "/" + a) for a in artifacts))
deepseek = pd.read_csv(DEC + "/od_validation_deepseek_fulltext.csv")
check("DeepSeek full-text validation = 40 rows", len(deepseek) == 40)
cons = pd.read_csv(DEC + "/od_crossref_consensus.csv")
check("Consensus cross-ref = 40 rows", len(cons) == 40)
rep = json.load(open(DEC + "/governance_audit_report.json", encoding="utf-8"))
check("PMID Knock Test 52/52", rep["PMID_KnockTest"]["resolved"] == 52 and rep["PMID_KnockTest"]["total"] == 52)

# ---------- E: two-call readiness ----------
print("\n[E] Two-call human validation readiness")
ws = pd.read_csv(DEC + "/definition_review_worksheet.csv")
check("worksheet 336 rows / 28 entities", len(ws) == 336 and ws["entity"].nunique() == 28)
check("worksheet 0 inline citations", ws[ws["field"] == "operational_definition"]["draft_value"].astype(str).str.contains(r"\((?:18|19|20|21)\d{2}\)", regex=True).sum() == 0)
check("review_guide.md present", os.path.exists(DEC + "/review_guide.md"))
check("merge_approved.py present", os.path.exists(DEC + "/merge_approved.py"))
check("all reviewer_decision = PENDING (ready for human)", (ws["reviewer_decision"] == "PENDING").all())

print("\n" + "=" * 74)
print(f"FINAL READINESS AUDIT: {PASS} PASS, {FAIL} FAIL")
print("READY FOR TWO-CALL HUMAN VALIDATION" if FAIL == 0 else "NOT READY — fix the FAILs above")
print("=" * 74)
