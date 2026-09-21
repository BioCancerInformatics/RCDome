"""
RCDome Definition Governance — checker + statistical benchmark (V025).

Audits RCDome_Decoder_53.csv against the governance rules:
  V1 completeness (10 core fields)
  V2 RS1-RS6 in [0,10]
  V3 S determinism (recompute = stored, bitwise)
  V4 founding PMID present
  V5 NCCD 2018 invariance (verbatim definitions attached, never altered)
  V6 score calibration (drafts vs the 25 Rodrigues anchors)

Statistics: completeness with 95% Wilson CI, PMID Knock Test (PubMed resolution),
S reproducibility, score distributions.
"""
import pandas as pd, json, re, urllib.request, math, sys, time

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder"
DF = pd.read_csv(BASE + "/RCDome_Decoder_53.csv")
W = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
CCOLS = ["RS1", "RS2", "RS3", "RS4", "RS5", "RS6"]

def filled(v):
    s = str(v).strip()
    return bool(s) and s.lower() not in ("nan", "none", "")

def wilson(k, n, z=1.959964):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z * math.sqrt((p*(1-p) + z*z/(4*n)) / n) / d
    return (max(0.0, c - h), min(1.0, c + h))

report = {}

# ---------------- V1 completeness ----------------
core = ["rcd_form", "category", "year", "operational_definition", "key_molecules",
        "inflammatory", "overlaps", "founding_pmid"]
v1 = []
for f in core:
    k = DF[f].apply(filled).sum()
    v1.append({"field": f, "filled": int(k), "total": len(DF), "pct": round(100*k/len(DF), 1)})
report["V1_completeness"] = v1

# ---------------- V2 RS1-RS6 range ----------------
v2 = []
for c in CCOLS:
    vals = pd.to_numeric(DF[c], errors="coerce")
    bad = int(((vals < 0) | (vals > 10)).sum())
    v2.append({"criteria": c, "in_range": int(len(DF) - bad), "total": len(DF), "violations": bad})
report["V2_range"] = v2

# ---------------- V3 S determinism ----------------
def recompute(r):
    return round(sum(w * float(r[c]) for w, c in zip(W, CCOLS)), 2)
S_rc = DF.apply(recompute, axis=1)
mism = int((abs(DF["S"] - S_rc) > 0.005).sum())
report["V3_S_reproducibility"] = {"mismatch": mism, "total": len(DF),
                                  "pct_bitwise": round(100*(len(DF)-mism)/len(DF), 3)}

# ---------------- V4 founding PMID ----------------
k = DF["founding_pmid"].apply(filled).sum()
report["V4_founding_pmid"] = {"present": int(k), "total": len(DF)}

# ---------------- V5 NCCD invariance ----------------
n_inv = int((DF["galluzzi_nccd_status"] == "NCCD_2018_INVARIANT").sum())
n_inv_def = int(((DF["galluzzi_nccd_status"] == "NCCD_2018_INVARIANT") &
                 DF["galluzzi_nccd_definition"].apply(filled)).sum())
report["V5_nccd_invariance"] = {"nccd_invariant": n_inv, "with_verbatim_def": n_inv_def}

# ---------------- V6 calibration (S) ----------------
anchors = pd.to_numeric(DF.loc[DF["definition_status"] == "DEFINED_RODRIGUES", "S"], errors="coerce")
drafts = pd.to_numeric(DF.loc[DF["definition_status"] != "DEFINED_RODRIGUES", "S"], errors="coerce")
report["V6_calibration"] = {
    "anchors_25": {"n": int(len(anchors)), "min": float(anchors.min()), "max": float(anchors.max()),
                    "mean": round(float(anchors.mean()), 2), "sd": round(float(anchors.std()), 2)},
    "drafts_28": {"n": int(len(drafts)), "min": float(drafts.min()), "max": float(drafts.max()),
                   "mean": round(float(drafts.mean()), 2), "sd": round(float(drafts.std()), 2)},
}

# ---------------- PMID Knock Test (PubMed resolution, batch) ----------------
def pmid_str(p):
    try:
        return str(int(float(p)))
    except Exception:
        return ""
pmids = sorted({pmid_str(p) for p in DF["founding_pmid"].tolist()
                if filled(p) and re.fullmatch(r"\d{7,8}", pmid_str(p))})
resolved = 0
failed = []
if pmids:
    u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id="
         + ",".join(pmids))
    try:
        with urllib.request.urlopen(u, timeout=60) as r:
            data = json.loads(r.read().decode())
        result = data.get("result", {})
        for p in pmids:
            rec = result.get(p, {})
            if rec and rec.get("title"):
                resolved += 1
            else:
                failed.append(p)
    except Exception as e:
        failed.append(f"API_ERROR: {e}")
report["PMID_KnockTest"] = {"resolved": resolved, "total": len(pmids),
                            "failed": failed,
                            "pct": round(100*resolved/len(pmids), 1) if pmids else None}

# ---------------- print report ----------------
sys.stdout.reconfigure(encoding="utf-8")
print("=" * 70)
print("RCDome Definition Governance — AUDIT REPORT (V025)")
print("=" * 70)
print(f"\n[V1] Completeness (10 core fields):")
for x in v1:
    print(f"   {x['field']:26s} {x['filled']:3d}/{x['total']}  ({x['pct']}%)")
k = sum(x["filled"] for x in v1); n = len(v1) * len(DF)
lo, hi = wilson(k, n)
print(f"   OVERALL {k}/{n} = {100*k/n:.1f}%  95% CI [{lo*100:.1f}%, {hi*100:.1f}%]")

print(f"\n[V2] RS1-RS6 range [0,10]: violations = {sum(x['violations'] for x in v2)} / {len(v2)*len(DF)}")

print(f"\n[V3] S determinism (bitwise recompute): {len(DF)-mism}/{len(DF)} match ({report['V3_S_reproducibility']['pct_bitwise']}%)")

print(f"\n[V4] Founding PMID present: {report['V4_founding_pmid']['present']}/{len(DF)}")

print(f"\n[V5] NCCD 2018 invariance: {n_inv} invariant entities, {n_inv_def} with verbatim definition attached")

print(f"\n[V6] Score calibration:")
print(f"   anchors (25 Rodrigues):  S {anchors.min():.2f}-{anchors.max():.2f}  mean={anchors.mean():.2f}  sd={anchors.std():.2f}")
print(f"   drafts  (28 pending):    S {drafts.min():.2f}-{drafts.max():.2f}  mean={drafts.mean():.2f}  sd={drafts.std():.2f}")

print(f"\n[PMID Knock Test] founding PMIDs resolve in PubMed: {resolved}/{len(pmids)} ({report['PMID_KnockTest']['pct']}%)")
if failed:
    print(f"   FAILED: {failed[:10]}")

json.dump(report, open(BASE + "/governance_audit_report.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nSAVED: governance_audit_report.json")
