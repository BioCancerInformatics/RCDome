"""
Recover full texts for abstract-only entities via Europe PMC, then re-validate
with DeepSeek RAG (full text, not abstract).
"""
import json, time, urllib.request, urllib.parse, re, sys
import pandas as pd

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder"
KEY = ""
for line in open(r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/extraction code snippets/.env", encoding="utf-8"):
    if line.startswith("DEEPSEEK_KEY="):
        KEY = line.split("=", 1)[1].strip()

def epmc_search(pmid):
    u = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:"
         + pmid + "&format=json&pageSize=5&resultType=core")
    try:
        with urllib.request.urlopen(u, timeout=30) as r:
            d = json.loads(r.read().decode())
        for res in d.get("resultList", {}).get("result", []):
            pmcid = res.get("pmcid")
            has_full = res.get("hasTextMinedTerms") or res.get("isOpenAccess") == "Y"
            if pmcid and res.get("isOpenAccess") == "Y":
                return pmcid, res.get("title", "")
        # fallback: any pmcid
        for res in d.get("resultList", {}).get("result", []):
            if res.get("pmcid"):
                return res["pmcid"], res.get("title", "")
    except Exception as e:
        return None, f"ERR {e}"
    return None, ""

def epmc_fulltext(pmcid):
    u = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    try:
        with urllib.request.urlopen(u, timeout=60) as r:
            xml = r.read().decode("utf-8", "replace")
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml))
    except Exception as e:
        return ""

targets = {
    "Cornification": "23792051",
    "NECSO": "39915626",
    "Phagoptosis": "22682109",
    "Vacuolar cell death": "15358773",
}

sys.stdout.reconfigure(encoding="utf-8")
print("=== Europe PMC full-text recovery ===")
recovered = {}
for ent, pmid in targets.items():
    pmcid, title = epmc_search(pmid)
    if pmcid:
        full = epmc_fulltext(pmcid)
        n = len(full)
        recovered[ent] = (pmid, pmcid, full)
        print(f"  {ent:24s} PMID {pmid} -> {pmcid} fulltext {n} chars  {title[:50]}")
    else:
        print(f"  {ent:24s} PMID {pmid} -> NO PMCID {title}")
    time.sleep(1)

json.dump({k: {"pmid": v[0], "pmcid": v[1], "fulltext": v[2]} for k, v in recovered.items()},
          open(BASE + "/recovered_fulltexts.json", "w", encoding="utf-8"), ensure_ascii=False)
print("\nsaved recovered_fulltexts.json | recovered:", len(recovered), "/4")
