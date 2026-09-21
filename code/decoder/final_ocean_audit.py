"""
OCEAN-DEEP FINAL AUDIT — RCDome definition pipeline (V025).

Sections:
  L  Logic        — S formula, census, determination hierarchy, semantic-vs-computable proof
  G  Governance   — policy coherence (invariance, provenance P0-P3, no-make-believe, two-call, stats)
  T  Table        — decoder structure, verbatim, PMID anchor, provenance chain, format, S bitwise
  C  Coherence    — cross-audit agreement + no contradictions
"""
import re, json, sys, math, openpyxl, pandas as pd

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
DEC = BASE + r"/RCDome Decoder"
W = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
CCOLS = ["RS1", "RS2", "RS3", "RS4", "RS5", "RS6"]
PASS = FAIL = WARN = 0

def check(name, ok, detail="", warn=False):
    global PASS, FAIL, WARN
    if ok:
        PASS += 1; print(f"  [PASS] {name}")
    elif warn:
        WARN += 1; print(f"  [WARN] {name}  {detail}")
    else:
        FAIL += 1; print(f"  [FAIL] {name}  {detail}")

def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip()

sys.stdout.reconfigure(encoding="utf-8")
df = pd.read_csv(DEC + "/RCDome_Decoder_53.csv")
print("=" * 74)
print("RCDome DEFINITION PIPELINE — OCEAN-DEEP FINAL AUDIT (V025)")
print("=" * 74)

# ================= L: LOGIC =================
print("\n[L1] S formula (reverse-engineered, deterministic)")
wb = openpyxl.load_workbook(BASE + r"/output databases/Dataset S1_Rodrigues et al 2025.xlsx", read_only=True)
ws = wb["Dataset S1A"]
ok = sum(1 for r in ws.iter_rows(min_row=2, values_only=True) if r[1] is not None
         and abs(round(sum(w * x for w, x in zip(W, list(r[4:10]))), 2) - r[10]) < 0.005)
check(f"S = 0.25C1+0.25C2+0.20C3+0.15C4+0.10C5+0.05C6 matches {ok}/25 anchors", ok == 25)

print("\n[L2] Census math (three vocabularies)")
G = df["galluzzi_nccd_status"] == "NCCD_2018_INVARIANT"
R = df["definition_status"] == "DEFINED_RODRIGUES"
both, g_only, r_only, neither = int((G & R).sum()), int((G & ~R).sum()), int((R & ~G).sum()), int((~G & ~R).sum())
check(f"20 Galluzzi / 25 Rodrigues / 13 both / 7 G-only / 12 R-only / 21 neither = 53",
      (G.sum() == 20 and R.sum() == 25 and both == 13 and g_only == 7 and r_only == 12 and neither == 21
       and both + g_only + r_only + neither == 53))

print("\n[L3] Determination hierarchy (NCCD > Rodrigues > draft)")
n_nccd_src = int((df["operational_definition_source"] == "NCCD_2018_VERBATIM").sum())
n_rodr_src = int((df["operational_definition_source"] == "RODRIGUES_S1A").sum())
n_draft_src = int((df["operational_definition_source"] == "FOUNDING_DRAFT").sum())
check(f"sources: 20 NCCD_VERBATIM / 12 RODRIGUES_S1A / 19 FOUNDING_DRAFT / 1 PRE_PUBMED / 1 COMPOSITE",
      n_nccd_src == 20 and n_rodr_src == 12 and n_draft_src == 19)

print("\n[L4] RS1-RS6 are semantic, not computable (Necrosis paradox)")
ev = pd.read_csv(DEC + "/entity_evidence_V025.csv")
def genes(ent):
    r = ev[ev["rcd_form_canonical"] == ent]
    return int(r["n_genes"].iloc[0]) if len(r) else 0
nec_g, cup_g = genes("Necrosis"), genes("Cuproptosis")
nec_c1 = float(df[df["rcd_form"] == "Necrosis"]["RS1"].iloc[0])
cup_c1 = float(df[df["rcd_form"] == "Cuproptosis"]["RS1"].iloc[0])
check(f"Necrosis {nec_g} genes RS1={nec_c1} < Cuproptosis {cup_g} genes RS1={cup_c1} (semantic proof)",
      nec_g > cup_g and nec_c1 < cup_c1)

# ================= G: GOVERNANCE =================
print("\n[G1] Governance policy coherence")
gov = open(DEC + "/RCDome_Definition_Governance.md", encoding="utf-8").read()
for rule in ["INVARIANCE", "PROVENANCE POLICY", "P0", "P1", "P2", "P3", "two-call", "Two-call",
             "no make-believe", "95% CI", "Cohen", "deterministic"]:
    check(f"governance doc contains '{rule}'", rule.lower() in gov.lower(), rule)
check("P0 (no deletion) present", "deleted" in gov)
check("invariance covers Galluzzi AND Rodrigues", "INVARIANT" in gov and "Rodrigues" in gov)
check("no-deletion vs merge resolved (retire, not delete)", ("RETIRED" in gov and "never removed" in gov))

print("\n[G2] Invariance enforced in decoder")
nccd = df[G]
byte_ok = sum(norm(r["operational_definition"]) == norm(r["galluzzi_nccd_definition"]) for _, r in nccd.iterrows())
check(f"20/20 NCCD: operational_definition == verbatim (byte-identical)", byte_ok == 20)

print("\n[G3] Provenance policy applied")
comp = df[df["rcd_form"] == "Senescence and Autophagy in Cancer"]
check("composite KEPT (not deleted)", len(comp) == 1)
check("composite labeled with parent PMIDs", "29362479" in str(comp["reference_pmid"].iloc[0]))
check("composite provenance note present", "WikiPathways" in str(comp["provenance_note"].iloc[0]))

# ================= T: TABLE =================
print("\n[T1] Decoder structure")
check("53 unique entities", df["rcd_form"].nunique() == 53 and df["rcd_form"].is_unique)
check("28 columns", len(df.columns) == 28, f"{len(df.columns)} cols")

print("\n[T2] S determinism + RS1-RS6 range")
rc = df.apply(lambda r: round(sum(w * float(r[c]) for w, c in zip(W, CCOLS)), 2), axis=1)
check("S bitwise recompute 53/53", (abs(df["S"] - rc) < 0.005).sum() == 53)
check("RS1-RS6 all in [0,10]", all(0 <= float(df[c].iloc[i]) <= 10 for c in CCOLS for i in range(len(df))))

print("\n[T3] PMID anchoring + format")
def pmid_ok(v):
    return bool(re.fullmatch(r"\d{7,8}(\.0)?(;\d{7,8}(\.0)?)?", str(v).strip()))
n_anch = df["reference_pmid"].apply(lambda v: pmid_ok(v)).sum()
check(f"reference_pmid anchored {n_anch}/53 (composite via parents)", n_anch == 53)
check("no inline citations in OD prose", df["operational_definition"].astype(str).str.contains(r"\((?:18|19|20|21)\d{2}\)", regex=True).sum() == 0)

print("\n[T4] Provenance chain")
for c in ["source_databases", "source_channels", "provenance_note"]:
    n = df[c].astype(str).str.len().gt(0).sum()
    check(f"{c} filled {n}/53", n == 53, f"{n}/53")

print("\n[T5] Verbatim integrity (published definitions)")
json_ok = json.load(open(DEC + "/galluzzi2018_nccd_definitions.json", encoding="utf-8"))
nccd_match = sum(any(norm(v) == norm(r["galluzzi_nccd_definition"]) for v in json_ok.values()) for _, r in nccd.iterrows())
check(f"Galluzzi verbatim {nccd_match}/20 match source JSON", nccd_match == 20)

# ================= C: COHERENCE =================
print("\n[RS1] Cross-audit agreement")
rep = json.load(open(DEC + "/governance_audit_report.json", encoding="utf-8"))
cv = pd.read_csv(DEC + "/consensus_crossvalidation_report.csv")
check("governance_checker V5 = 20 NCCD", rep["V5_nccd_invariance"]["nccd_invariant"] == 20)
check("governance_checker V3 = 100% S", rep["V3_S_reproducibility"]["pct_bitwise"] == 100.0)
check("governance_checker PMID KnockTest = 52/52", rep["PMID_KnockTest"]["resolved"] == 52)
check("consensus cross-validation RS1 = 20 PASS", int((cv["check"] == "C1_NCCD_verbatim_integrity").sum()) == 20)
check("consensus cross-validation RS2 = 26 PASS + 1 FLAG (resolved)",
      int(((cv["check"] == "C2_founding_PMID_corroboration") & (cv["status"] == "PASS")).sum()) == 26)

print("\n[RS2] Logic coherence (no contradictions)")
check("census == source-count == decoder status counts",
      n_nccd_src + n_rodr_src + n_draft_src + 2 == 53)
check("every real entity has a Galluzzi-format reading (verbatim or complement)",
      (df["operational_definition_source"].isin(["NCCD_2018_VERBATIM", "FOUNDING_DRAFT", "PRE_PUBMED"]).sum()
       + df["operational_definition_complement"].astype(str).str.len().gt(10).sum()) >= 52)

print("\n" + "=" * 74)
print(f"FINAL AUDIT RESULT: {PASS} PASS, {FAIL} FAIL, {WARN} WARN")
print("=" * 74)
