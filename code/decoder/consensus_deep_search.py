"""
Consensus DEEP SEARCH — corroborate each of the 28 pending ODs against:
  (a) coinage: the founding abstract actually COINS the entity (verb + name)
  (b) mechanism: the founding abstract mentions the draft key molecules
  (c) PubMed consensus: a fresh esearch for the entity returns the founding PMID
Score 0-3 per entity. >=2 = CONSENSUS, 1 = PARTIAL, 0 = WEAK.
"""
import pandas as pd, re, json, urllib.request, urllib.parse, time, csv, sys

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder"
df = pd.read_csv(BASE + "/RCDome_Decoder_53.csv")

ABS = ""
try:
    ABS += open(BASE + "/founding_abstracts_SOLID.txt", encoding="utf-8").read().lower()
except Exception:
    pass
try:
    ABS += " " + open(BASE + "/founding_abstracts_CANDIDATE.txt", encoding="utf-8").read().lower()
except Exception:
    pass

TOKEN = {
    "Programmed cell death": "programmed cell death", "Mitotic death": "mitotic death",
    "Aponecrosis": "aponecrosis", "Phagoptosis": "phagoptosis", "PANoptosis": "pan-optosis",
    "Lysoptosis": "lysoptosis", "Floatptosis": "floatptosis",
    "Ammonia-induced cell death": "ammonia", "Oncosis": "oncosis",
    "Mitoxyperilysis": "mitoxyperi", "Linker cell-type death": "linker cell",
    "Cornification": "cornification", "Triaptosis": "triaptosis", "Spectosis": "spectosis",
    "Pyronecrosis": "pyronecrosis", "Apoptosis (intrinsic)": "intrinsic apoptosis",
    "Apoptosis (extrinsic)": "extrinsic apoptosis",
    "Autophagy-dependent cell death": "autophagy-dependent", "Regulated Necrosis": "regulated necrosis",
    "MPT-driven necrosis": "mpt-driven necrosis", "Lysosomal cell death": "lysosomal cell death",
    "Metalloptosis": "metalloptosis", "Lysozincrosis": "lysozincrosis", "NECSO": "necro",
    "Vacuolar cell death": "vacuolar", "Eryptosis": "eryptosis",
    "Hypersensitive response": "hypersensitive",
}
COINAGE = r"(term|termed|coined|dubbed|designated|we call|referred to as|we propose|the name|is proposed)"


def esearch(term, retmax=20):
    u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json"
         "&retmax=%d&sort=relevance&term=" % retmax + urllib.parse.quote(term))
    try:
        with urllib.request.urlopen(u, timeout=25) as r:
            d = json.loads(r.read().decode())
        return d.get("esearchresult", {}).get("idlist", [])
    except Exception:
        return []


def pmid_str(p):
    try:
        return str(int(float(p)))
    except Exception:
        return ""


rows = []
pending = df[df["definition_status"].isin(["DRAFT_SOLID", "DRAFT_CANDIDATE", "PRE_PUBMED"])]
for _, r in pending.iterrows():
    ent = r["rcd_form"]
    token = TOKEN.get(ent, "").lower()
    p = pmid_str(r["founding_pmid"])
    mols = [m.strip().lower() for m in re.split(r"[;,]", str(r["key_molecules"])) if m.strip()]

    # (a) coinage: token + coinage verb nearby in the combined abstracts
    coinage = 0
    if token:
        for m in re.finditer(re.escape(token), ABS):
            ctx = ABS[max(0, m.start() - 90):m.end() + 90]
            if re.search(COINAGE, ctx):
                coinage = 1
                break

    # (b) mechanism: any key molecule token appears in abstracts
    mech = 0
    for mol in mols:
        mol_short = re.sub(r"[^a-z0-9]", "", mol)
        if mol_short and mol_short in ABS:
            mech = 1
            break

    # (c) PubMed consensus: fresh esearch for the entity returns the founding PMID
    consensus = 0
    if token:
        hits = esearch(f'"{token}"[Title/Abstract]')
        consensus = 1 if p in hits else 0

    score = coinage + mech + consensus
    verdict = "CONSENSUS" if score >= 2 else ("PARTIAL" if score == 1 else "WEAK")
    rows.append({
        "entity": ent, "coinage": coinage, "mechanism": mech,
        "pubmed_consensus": consensus, "score": score, "verdict": verdict,
        "founding_pmid": p,
    })
    print(f"[{score}/3 {verdict:9s}] {ent:34s} coinage={coinage} mech={mech} pubmed={consensus}")
    time.sleep(0.35)

out = pd.DataFrame(rows)
out.to_csv(BASE + "/consensus_deep_search_report.csv", index=False)
print("\nSAVED consensus_deep_search_report.csv")
print("verdict summary:", out["verdict"].value_counts().to_dict())
