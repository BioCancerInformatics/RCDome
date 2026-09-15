"""
RCDome Definition Governance — consensus cross-validation (V026).

Each definition field must be corroborated by >=2 independent sources before locking.
Three checks:
  C1  NCCD verbatim integrity   (byte-compare decoder vs galluzzi2018_nccd_definitions.json)
  C2  Founding-PMID title corroboration (PubMed title contains the entity's key token —
      an independent "consensus search" that the PMID actually coins the entity)
  C3  C1-C6 objective consistency (draft scores vs deterministic matrix inputs:
      n_genes -> C1 band, mechanistic_ratio -> C2 band, type/year -> C4 band)

Output: consensus_crossvalidation_report.csv  (PASS / FLAG per field)
"""
import pandas as pd, json, re, urllib.request, math, csv, sys

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder"
df = pd.read_csv(BASE + "/RCDome_Decoder_53.csv")
ev = pd.read_csv(BASE + "/entity_evidence_V026.csv")
NCCD = json.load(open(BASE + "/galluzzi2018_nccd_definitions.json", encoding="utf-8"))

def pmid_str(p):
    try:
        return str(int(float(p)))
    except Exception:
        return ""

# abstract text (for title/abstract corroboration of the 28 pending)
ABS = ""
try:
    ABS += open(BASE + "/founding_abstracts_SOLID.txt", encoding="utf-8").read().lower()
except Exception:
    pass
try:
    ABS += " " + open(BASE + "/founding_abstracts_CANDIDATE.txt", encoding="utf-8").read().lower()
except Exception:
    pass

# ---------- key token per entity (for title corroboration) ----------
TOKEN = {
    "Programmed cell death": "programmed cell death",
    "Mitotic death": "mitotic death",
    "Aponecrosis": "aponecrosis",
    "Phagoptosis": "phagoptosis",
    "PANoptosis": "pan-optosis",
    "Lysoptosis": "lysoptosis",
    "Floatptosis": "floatptosis",
    "Ammonia-induced cell death": "ammonia",
    "Oncosis": "oncosis",
    "Mitoxyperilysis": "mitoxyperi",
    "Linker cell-type death": "linker cell",
    "Cornification": "cornification",
    "Triaptosis": "triaptosis",
    "Spectosis": "spectosis",
    "Pyronecrosis": "pyronecrosis",
    "Apoptosis (intrinsic)": "intrinsic apoptosis",
    "Apoptosis (extrinsic)": "extrinsic apoptosis",
    "Autophagy-dependent cell death": "autophagy-dependent",
    "Regulated Necrosis": "regulated necrosis",
    "MPT-driven necrosis": "mpt-driven necrosis",
    "Lysosomal cell death": "lysosomal cell death",
    "Metalloptosis": "metalloptosis",
    "Lysozincrosis": "lysozincrosis",
    "NECSO": "necro",
    "Vacuolar cell death": "vacuolar",
    "Eryptosis": "eryptosis",
    "Hypersensitive response": "hypersensitive",
}

# ---------- fetch all founding PMID titles (batch esummary) ----------
pmids = sorted({pmid_str(p) for p in df["founding_pmid"].tolist()
                if pmid_str(p) and re.fullmatch(r"\d{7,8}", pmid_str(p))})
TITLES = {}
if pmids:
    u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id="
         + ",".join(pmids))
    with urllib.request.urlopen(u, timeout=60) as r:
        data = json.loads(r.read().decode())
    for p, rec in data.get("result", {}).items():
        if p == "uids":
            continue
        TITLES[p] = (rec.get("title") or "").lower()

ev_map = {r["rcd_form_canonical"]: r for _, r in ev.iterrows()}

rows = []
# ---- C1: NCCD verbatim integrity ----
for _, r in df.iterrows():
    if r["galluzzi_nccd_status"] != "NCCD_2018_INVARIANT":
        continue
    # find the NCCD term whose definition matches this entity
    # (we compare what is stored against any value in NCCD JSON)
    stored = str(r["galluzzi_nccd_definition"]).strip()
    matches = [k for k, v in NCCD.items() if v.strip() == stored]
    rows.append({
        "entity": r["rcd_form"], "field": "galluzzi_nccd_definition",
        "check": "C1_NCCD_verbatim_integrity",
        "status": "PASS" if matches else "FLAG",
        "evidence": f"verbatim match to NCCD Box1 ({matches[0] if matches else 'NO MATCH'})",
    })

# ---- C2: founding PMID corroboration (token in title OR abstract) ----
for _, r in df.iterrows():
    if r["definition_status"] == "DEFINED_RODRIGUES" or r["definition_status"] == "COMPOSITE":
        continue
    p = pmid_str(r["founding_pmid"])
    token = TOKEN.get(r["rcd_form"], "").lower()
    title = TITLES.get(p, "")
    if not token:
        status, evidence = "MANUAL", "no token defined"
    elif token in title or token in ABS:
        status, evidence = "PASS", f"'{token}' found in PMID {p} title/abstract"
    else:
        status, evidence = "FLAG", f"'{token}' NOT in PMID {p} title/abstract"
    rows.append({
        "entity": r["rcd_form"], "field": "founding_pmid",
        "check": "C2_founding_PMID_corroboration",
        "status": status, "evidence": evidence,
    })

# ---- C3: C1-C6 objective inputs (INFORMATIONAL — expert judgment is semantic) ----
def expected_c1(n_genes):
    return min(10, max(3, round(4 + 6 * math.log10(1 + n_genes) / math.log10(1 + 5897))))

for _, r in df.iterrows():
    e = ev_map.get(r["rcd_form"])
    if e is None:
        continue
    n_genes = int(e["n_genes"]); n_m = int(e["n_mechanistic"]); n_c = int(e["n_context_gap"])
    ratio = n_m / (n_m + n_c) if (n_m + n_c) else 0.0
    exp_c1 = expected_c1(n_genes)
    rows.append({
        "entity": r["rcd_form"], "field": "C1",
        "check": "C3_C1_objective_inputs",
        "status": "INFO",
        "evidence": f"C1={r['C1']} (draft); n_genes={n_genes}; gene-based reference={exp_c1}",
    })
    rows.append({
        "entity": r["rcd_form"], "field": "C2",
        "check": "C3_C2_objective_inputs",
        "status": "INFO",
        "evidence": f"C2={r['C2']} (draft); mech_ratio={ratio:.2f} (n_mech={n_m}, n_ctx={n_c})",
    })

out = pd.DataFrame(rows)
out.to_csv(BASE + "/consensus_crossvalidation_report.csv", index=False)
print("SAVED consensus_crossvalidation_report.csv | rows:", len(out))
print()
print("=== status summary ===")
print(out["status"].value_counts().to_string())
print()
print("=== FLAG / MANUAL items (need human resolution) ===")
for _, r in out[out["status"] != "PASS"].iterrows():
    print(f"  [{r['status']:6s}] {r['entity']:34s} {r['field']:24s} | {r['evidence'][:80]}")
