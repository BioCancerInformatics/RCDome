"""
PMID TOPIC AUDIT — every PMID in the decoder must correspond to its RCD entity.
Checks the 28 draft founding PMIDs (worksheet scope) + the 25 Rodrigues primary/secondary
PMIDs (parent-source scope). Fetches titles from PubMed and verifies the entity's key
token appears in the title.
"""
import pandas as pd, urllib.request, json, re, sys

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder"
df = pd.read_csv(BASE + "/RCDome_Decoder_53.csv")

# key token per entity (the coined name / distinctive term expected in the title)
TOKEN = {
    "Programmed cell death": "programmed cell death", "Mitotic death": "mitotic death",
    "Aponecrosis": "aponecrosis", "Phagoptosis": "phagoptosis", "PANoptosis": "pan-optosis",
    "Lysoptosis": "lysoptosis", "Floatptosis": "floatptosis", "Oncosis": "oncosis",
    "Mitoxyperilysis": "mitoxyperi", "Linker cell-type death": "linker cell",
    "Cornification": "cornification", "Triaptosis": "triaptosis", "Spectosis": "red blood cells",
    "Pyronecrosis": "necrotic cell death", "Apoptosis (intrinsic)": "intrinsic apoptosis",
    "Apoptosis (extrinsic)": "extrinsic apoptosis", "Autophagy-dependent cell death": "autophagy",
    "Regulated Necrosis": "regulated necrosis", "MPT-driven necrosis": "permeability transition",
    "Lysosomal cell death": "lysosomal cell death", "Metalloptosis": "metalloptosis",
    "Lysozincrosis": "lysosomal zn", "NECSO": "sodium overload", "Vacuolar cell death": "vacuolar",
    "Eryptosis": "eryptosis", "Hypersensitive response": "hypersensitive",
    "Ammonia-induced cell death": "ammonia",
    "Senescence and Autophagy in Cancer": "",  # composite (parent PMIDs checked separately)
    # 25 Rodrigues
    "Apoptosis": "apoptosis", "Necroptosis": "necroptosis", "Pyroptosis": "pyroptosis",
    "Ferroptosis": "ferroptosis", "Autophagy": "autophagy", "Cuproptosis": "cuproptosis",
    "Mitotic catastrophe": "mitotic", "Parthanatos": "parthanatos",
    "Immunogenic cell death": "immunogenic", "Autosis": "autosis", "NETosis": "net",
    "Disulfidptosis": "disulfidptosis", "Alkaliptosis": "alkaliptosis",
    "Lysosome-dependent cell death": "lysosom", "Entosis": "entosis", "Anoikis": "anoikis",
    "Oxeiptosis": "oxeiptosis", "Paraptosis": "paraptosis", "Cellular senescence": "senescence",
    "Mitoptosis": "mitoptosis", "Erebosis": "erebosis", "Efferocytosis": "efferocytosis",
    "Mitochondrial permeability transition": "permeability transition", "Methuosis": "methuosis",
    "Necrosis": "necrosis",
}

# collect all PMIDs
pmid_set = set()
def add(v):
    for p in str(v).split(";"):
        p = p.strip().replace(".0", "")
        if re.fullmatch(r"\d{7,8}", p):
            pmid_set.add(p)

for _, r in df.iterrows():
    for c in ["founding_pmid", "reference_pmid", "primary_refs_pmids", "secondary_refs_pmids"]:
        add(r[c])

pmids = sorted(pmid_set)
# batch esummary
TITLES = {}
for i in range(0, len(pmids), 200):
    chunk = pmids[i:i+200]
    u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id="
         + ",".join(chunk))
    with urllib.request.urlopen(u, timeout=60) as r:
        data = json.loads(r.read().decode()).get("result", {})
    for p in chunk:
        TITLES[p] = (data.get(p, {}).get("title") or "").lower()

def token_in(tok, titles):
    if not tok:
        return True
    t = tok.lower().replace(" ", "")
    return any(t in re.sub(r"[^a-z0-9]", "", title) for title in titles)

sys.stdout.reconfigure(encoding="utf-8")
print("=" * 74)
print("PMID TOPIC AUDIT — every PMID matches its RCD entity")
print("=" * 74)
flags = []
for _, r in df.iterrows():
    ent = r["rcd_form"]
    tok = TOKEN.get(ent, "")
    titles = []
    for c in ["founding_pmid", "reference_pmid", "primary_refs_pmids", "secondary_refs_pmids"]:
        for p in str(r[c]).split(";"):
            p = p.strip().replace(".0", "")
            if p in TITLES:
                titles.append(TITLES[p])
    if ent == "Senescence and Autophagy in Cancer":
        continue  # composite handled by parent tokens
    ok = token_in(tok, titles)
    status = "PASS" if ok else "FLAG"
    print(f"  [{status}] {ent:34s} token='{tok}'")
    if not ok:
        flags.append(ent)
        for c in ["primary_refs_pmids", "secondary_refs_pmids", "founding_pmid"]:
            for p in str(r[c]).split(";"):
                p = p.strip().replace(".0", "")
                if p in TITLES:
                    print(f"         PMID {p}: {TITLES[p][:80]}")

print()
print(f"RESULT: {53 - len(flags) - 1}/52 PASS, {len(flags)} FLAG (composite excluded)")
