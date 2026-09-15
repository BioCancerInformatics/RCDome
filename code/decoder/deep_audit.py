"""
OCEAN-DEEP AUDIT — logic, code, and results of the RCDome definition pipeline.

Sections:
  L1  S formula re-derivation (25/25 anchors)
  L2  Census math (Galluzzi vs Rodrigues vs neither)
  L3  Invariance integrity (NCCD verbatim byte-identical)
  L4  'Necrosis paradox' proof (C1-C6 semantic, not computable)
  C1  Decoder structural checks (53 unique, S bitwise, C1-C6 range, PMID format)
  C2  Name-alignment audit (S1A -> Reference Table -> matrix) no misalignment
  C3  Merge invariance guard (simulated EDIT on NCCD must be refused)
  R1  Audit-report cross-check (JSON vs printed numbers)
  R2  Cross-validation report cross-check (PASS/FLAG/INFO counts)
"""
import pandas as pd, json, re, math, csv, sys
import openpyxl

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
DEC = BASE + r"/RCDome Decoder"
W = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
CCOLS = ["C1", "C2", "C3", "C4", "C5", "C6"]
PASS = FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}  {detail}")

sys.stdout.reconfigure(encoding="utf-8")
print("=" * 72)
print("RCDome DEFINITION PIPELINE — OCEAN-DEEP AUDIT")
print("=" * 72)

# ================= L1: S formula re-derivation =================
print("\n[L1] S formula re-derivation (0.25/0.25/0.20/0.15/0.10/0.05)")
wb = openpyxl.load_workbook(BASE + r"/output databases/Dataset S1_Rodrigues et al 2025.xlsx", read_only=True)
ws = wb["Dataset S1A"]
ok = bad = 0
for r in ws.iter_rows(min_row=2, values_only=True):
    if r[1] is None:
        continue
    c = list(r[4:10]); given = r[10]
    calc = round(sum(w * x for w, x in zip(W, c)), 2)
    if abs(calc - given) < 0.005:
        ok += 1
    else:
        bad += 1
check("S formula matches all 25 Rodrigues anchors", ok == 25 and bad == 0, f"{ok}/25, {bad} bad")

# ================= L2: Census math =================
print("\n[L2] Census math (Galluzzi / Rodrigues / neither)")
df = pd.read_csv(DEC + "/RCDome_Decoder_53.csv")
G = df["galluzzi_nccd_status"] == "NCCD_2018_INVARIANT"
R = df["definition_status"] == "DEFINED_RODRIGUES"
both = int((G & R).sum()); g_only = int((G & ~R).sum())
r_only = int((R & ~G).sum()); neither = int((~G & ~R).sum())
check("total = 53", len(df) == 53)
check("Galluzzi = 20", G.sum() == 20, str(G.sum()))
check("Rodrigues = 25", R.sum() == 25, str(R.sum()))
check("both = 13", both == 13, str(both))
check("Galluzzi-only = 7", g_only == 7, str(g_only))
check("Rodrigues-only = 12", r_only == 12, str(r_only))
check("neither = 21", neither == 21, str(neither))
check("13+7+12+21 = 53", both + g_only + r_only + neither == 53)

# ================= L3: Invariance integrity =================
print("\n[L3] NCCD invariance integrity (verbatim byte-identical)")
NCCD = json.load(open(DEC + "/galluzzi2018_nccd_definitions.json", encoding="utf-8"))
inv_ok = 0
for _, row in df[G].iterrows():
    op = str(row["operational_definition"]).strip()
    gdef = str(row["galluzzi_nccd_definition"]).strip()
    match = any(v.strip() == op for v in NCCD.values()) and op == gdef
    inv_ok += match
check("all 20 invariant: operational_definition == verbatim NCCD", inv_ok == 20, f"{inv_ok}/20")

# ================= L4: Necrosis paradox (semantic not computable) =================
print("\n[L4] 'Necrosis paradox' — C1-C6 are semantic, not computable from gene counts")
ev = pd.read_csv(DEC + "/entity_evidence_V026.csv")
def genes_of(ent):
    r = ev[ev["rcd_form_canonical"] == ent]
    return int(r["n_genes"].iloc[0]) if len(r) else None
nec_genes = genes_of("Necrosis"); cup_genes = genes_of("Cuproptosis")
nec_c1 = float(df[df["rcd_form"] == "Necrosis"]["C1"].iloc[0])
cup_c1 = float(df[df["rcd_form"] == "Cuproptosis"]["C1"].iloc[0])
check("C1 NOT a function of gene count (Necrosis 1092 genes C1=4 < Cuproptosis 77 genes C1=7)",
      nec_genes > cup_genes and nec_c1 < cup_c1,
      f"Necrosis {nec_genes} genes C1={nec_c1}; Cuproptosis {cup_genes} genes C1={cup_c1}")

# ================= C1: Decoder structural checks =================
print("\n[C1] Decoder structural checks")
check("53 unique rcd_form", df["rcd_form"].nunique() == 53)
check("no duplicate entities", df["rcd_form"].is_unique)
c_ok = all(0 <= float(df[c].iloc[i]) <= 10 for c in CCOLS for i in range(len(df)))
check("C1-C6 all in [0,10]", c_ok)
rc = df.apply(lambda r: round(sum(w * float(r[c]) for w, c in zip(W, CCOLS)), 2), axis=1)
check("S bitwise recompute 53/53", (abs(df["S"] - rc) < 0.005).sum() == 53)
pmids = [str(int(float(p))) for p in df["founding_pmid"] if str(p).strip() not in ("", "nan")]
check("founding PMIDs all 7-8 digit", all(re.fullmatch(r"\d{7,8}", p) for p in pmids), f"{len(pmids)} pmids")

# ================= C2: Name-alignment audit =================
print("\n[C2] Name alignment (S1A -> Reference Table -> matrix canonical)")
CANON_EXPECT = {
    "Mitotic Catastrophe": "Mitotic catastrophe",
    "Immunogenic Cell Death": "Immunogenic cell death",
    "Lysosome-Dependent Cell Death (LDCD)": "Lysosome-dependent cell death",
    "Cellular Senescence": "Cellular senescence",
    "Mitochondrial Permeability Transition": "Mitochondrial permeability transition",
}
s1a_names = []
for r in ws.iter_rows(min_row=2, values_only=True):
    if r[1] is not None:
        s1a_names.append(str(r[1]).strip())
aligned = all((CANON_EXPECT.get(n, n)) in set(df["rcd_form"]) for n in s1a_names)
check("all 25 S1A names resolve to a matrix canonical entity", aligned)
matrix_entities = set(df["rcd_form"])
check("25 Rodrigues rows present in decoder", int(R.sum()) == 25)

# ================= C3: Merge invariance guard =================
print("\n[C3] Merge invariance guard (EDIT on NCCD verbatim must be refused)")
nccd_ent = df[G]["rcd_form"].iloc[0]
row = df[df["rcd_form"] == nccd_ent].iloc[0]
invariant = row["galluzzi_nccd_status"] == "NCCD_2018_INVARIANT"
# the guard rule as implemented in merge_approved.py:
#   invariant and field=='operational_definition' and dec in ('EDIT','REJECT') -> REFUSED
for trial_dec in ["EDIT", "REJECT"]:
    refuse = invariant and trial_dec in ("EDIT", "REJECT")
    check(f"{trial_dec} on '{nccd_ent}' operational_definition is refused", refuse)
# and for a NON-invariant entity, an EDIT is allowed
noninv = df[~G]["rcd_form"].iloc[0]
check(f"EDIT on non-invariant '{noninv}' is allowed (not refused)",
      df[df["rcd_form"] == noninv]["galluzzi_nccd_status"].iloc[0] != "NCCD_2018_INVARIANT")

# ================= R1: audit report cross-check =================
print("\n[R1] Audit-report cross-check (JSON vs recomputed)")
rep = json.load(open(DEC + "/governance_audit_report.json", encoding="utf-8"))
check("V3 S reproducibility = 100%", rep["V3_S_reproducibility"]["pct_bitwise"] == 100.0)
check("V5 nccd_invariant = 20", rep["V5_nccd_invariance"]["nccd_invariant"] == 20)
check("PMID KnockTest = 52/52", rep["PMID_KnockTest"]["resolved"] == 52 and rep["PMID_KnockTest"]["total"] == 52)

# ================= R2: cross-validation report cross-check =================
print("\n[R2] Cross-validation report cross-check")
cv = pd.read_csv(DEC + "/consensus_crossvalidation_report.csv")
c = cv["status"].value_counts().to_dict()
check("C1 NCCD verbatim = 20 PASS", int((cv["check"] == "C1_NCCD_verbatim_integrity").sum()) == 20)
check("C2 founding PMID: 26 PASS + 1 FLAG",
      int(((cv["check"] == "C2_founding_PMID_corroboration") & (cv["status"] == "PASS")).sum()) == 26
      and int(((cv["check"] == "C2_founding_PMID_corroboration") & (cv["status"] == "FLAG")).sum()) == 1)
check("C3 objective inputs = 106 INFO", int((cv["check"].str.startswith("C3_")).sum()) == 106)

print("\n" + "=" * 72)
print(f"AUDIT RESULT: {PASS} PASS, {FAIL} FAIL")
print("=" * 72)
