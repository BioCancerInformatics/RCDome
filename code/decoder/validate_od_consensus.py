"""
Consensus API cross-reference for the 40 entities (12 Rodrigues-only + 28 pending).
For each entity, query Consensus /v1/search and record the top papers (title, year,
abstract snippet) as an independent evidence stream for the OD's founding reference.
Output: od_crossref_consensus.csv
"""
import os, json, time, urllib.request, urllib.parse, re, sys
import pandas as pd

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder"
key = ""
for line in open(r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/extraction code snippets/.env", encoding="utf-8"):
    if line.startswith("CONSENSUS_API_KEY="):
        key = line.split("=", 1)[1].strip()

def consensus(query, page_size=5, retries=4):
    url = ("https://api.consensus.app/v1/search?query=" + urllib.parse.quote(query)
           + f"&page_size={page_size}")
    for a in range(retries):
        try:
            req = urllib.request.Request(url, headers={"x-api-key": key, "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if a == retries - 1:
                return {"error": f"{type(e).__name__}: {str(e)[:120]}"}
            time.sleep(8 + a * 8)

df = pd.read_csv(BASE + "/RCDome_Decoder_53.csv")
# 12 Rodrigues-only + 28 pending
targets = df[(df["definition_status"] == "DEFINED_RODRIGUES") &
             (df["galluzzi_nccd_status"] != "NCCD_2018_INVARIANT") |
             (df["definition_status"] != "DEFINED_RODRIGUES")]

TOKEN = {
    "Programmed cell death": "programmed cell death", "Mitotic death": "mitotic death",
    "Aponecrosis": "aponecrosis", "Phagoptosis": "phagoptosis", "PANoptosis": "panoptosis",
    "Lysoptosis": "lysoptosis", "Floatptosis": "floatptosis", "Oncosis": "oncosis",
    "Mitoxyperilysis": "mitoxyperilysis", "Linker cell-type death": "linker cell death",
    "Cornification": "cornification cell death", "Triaptosis": "triaptosis",
    "Spectosis": "spectosis red blood cell", "Pyronecrosis": "pyronecrosis",
    "Apoptosis (intrinsic)": "intrinsic apoptosis", "Apoptosis (extrinsic)": "extrinsic apoptosis",
    "Autophagy-dependent cell death": "autophagy-dependent cell death",
    "Regulated Necrosis": "regulated necrosis", "MPT-driven necrosis": "MPT-driven necrosis",
    "Lysosomal cell death": "lysosomal cell death", "Metalloptosis": "metalloptosis",
    "Lysozincrosis": "lysozincrosis", "NECSO": "necrosis sodium overload",
    "Vacuolar cell death": "vacuolar cell death", "Eryptosis": "eryptosis",
    "Hypersensitive response": "hypersensitive response plant cell death",
    "Ammonia-induced cell death": "ammonia-induced cell death",
    # 12 Rodrigues-only
    "Apoptosis": "apoptosis", "Autophagy": "autophagy", "Cuproptosis": "cuproptosis",
    "Disulfidptosis": "disulfidptosis", "Alkaliptosis": "alkaliptosis", "Oxeiptosis": "oxeiptosis",
    "Paraptosis": "paraptosis", "Mitoptosis": "mitoptosis", "Erebosis": "erebosis",
    "Methuosis": "methuosis", "Necrosis": "necrosis cell death",
    "Mitochondrial permeability transition": "mitochondrial permeability transition",
}

rows = []
sys.stdout.reconfigure(encoding="utf-8")
for i, (_, r) in enumerate(targets.iterrows()):
    ent = r["rcd_form"]
    q = TOKEN.get(ent, ent) + " cell death"
    d = consensus(q)
    top = ""
    if "results" in d and d["results"]:
        items = []
        for p in d["results"][:5]:
            title = p.get("title", "")
            year = p.get("year", p.get("publication_date", ""))
            pmid = ""
            for k in ("pmid", "id", "paper_id", "doi"):
                if p.get(k):
                    pmid = str(p[k])[:40]
                    break
            items.append(f"{title} ({year}) [{pmid}]")
        top = " || ".join(items)
    rows.append({"entity": ent, "query": q, "consensus_top": top})
    print(f"[{i+1}/{len(targets)}] {ent:34s} -> {top[:90]}")
    time.sleep(2.5)

out = pd.DataFrame(rows)
out.to_csv(BASE + "/od_crossref_consensus.csv", index=False)
print("\nSAVED od_crossref_consensus.csv | rows:", len(out))
