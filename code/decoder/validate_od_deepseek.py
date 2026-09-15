"""
DeepSeek + RAG validation of the 28 pending ODs (consensus deep search).
For each entity:
  - deep PubMed search (2 query variants) -> candidate PMIDs + titles
  - prompt DeepSeek to (1) validate each OD claim, (2) recommend the BEST defining
    consensus reference, (3) flag hallucinations
  - cross-reference current founding PMID vs recommended
Output: od_validation_deepseek.csv
"""
import os, json, urllib.request, urllib.parse, re, time, sys
import pandas as pd

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder"
key = ""
for line in open(r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/extraction code snippets/.env", encoding="utf-8"):
    if line.startswith("DEEPSEEK_KEY="):
        key = line.split("=", 1)[1].strip()

def deepseek(messages, model="deepseek-chat", max_tokens=1200):
    req = urllib.request.Request("https://api.deepseek.com/chat/completions",
        data=json.dumps({"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0}).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read().decode())
            return d["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt == 2:
                return f"ERROR: {type(e).__name__}: {str(e)[:150]}"
            time.sleep(3 + attempt * 3)

def esearch(term, retmax=6):
    u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json"
         "&retmax=%d&sort=relevance&term=" % retmax + urllib.parse.quote(term))
    try:
        with urllib.request.urlopen(u, timeout=25) as r:
            return json.loads(r.read().decode())["esearchresult"].get("idlist", [])
    except Exception:
        return []

def esummary(ids):
    if not ids:
        return {}
    u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id="
         + ",".join(ids))
    try:
        with urllib.request.urlopen(u, timeout=30) as r:
            return json.loads(r.read().decode()).get("result", {})
    except Exception:
        return {}

df = pd.read_csv(BASE + "/RCDome_Decoder_53.csv")
pend = df[df["definition_status"] != "DEFINED_RODRIGUES"]

# abstract map (per PMID) from the saved files
absmap = {}
txt = ""
for f in ["founding_abstracts_SOLID.txt", "founding_abstracts_CANDIDATE.txt"]:
    try:
        txt += open(BASE + "/" + f, encoding="utf-8").read()
    except Exception:
        pass
pos = [(m.end(), m.group(1)) for m in re.finditer(r"PMID:\s*(\d{7,8})", txt)]
for i, (end, pid) in enumerate(pos):
    start = pos[i - 1][0] if i > 0 else 0
    absmap[pid] = re.sub(r"\s+", " ", txt[start:end]).strip()[:2500]

TOKEN = {
    "Programmed cell death": "programmed cell death", "Mitotic death": "mitotic death",
    "Aponecrosis": "aponecrosis", "Phagoptosis": "phagoptosis", "PANoptosis": "panoptosis",
    "Lysoptosis": "lysoptosis", "Floatptosis": "floatptosis", "Oncosis": "oncosis",
    "Mitoxyperilysis": "mitoxyperilysis", "Linker cell-type death": "linker cell death",
    "Cornification": "cornification", "Triaptosis": "triaptosis", "Spectosis": "spectosis",
    "Pyronecrosis": "pyronecrosis", "Apoptosis (intrinsic)": "intrinsic apoptosis",
    "Apoptosis (extrinsic)": "extrinsic apoptosis", "Autophagy-dependent cell death": "autophagy-dependent cell death",
    "Regulated Necrosis": "regulated necrosis", "MPT-driven necrosis": "MPT-driven necrosis",
    "Lysosomal cell death": "lysosomal cell death", "Metalloptosis": "metalloptosis",
    "Lysozincrosis": "lysozincrosis", "NECSO": "necrosis by sodium overload",
    "Vacuolar cell death": "vacuolar cell death", "Eryptosis": "eryptosis",
    "Hypersensitive response": "hypersensitive response", "Ammonia-induced cell death": "ammonia-induced cell death",
}

results = []
sys.stdout.reconfigure(encoding="utf-8")
for idx, (_, r) in enumerate(pend.iterrows()):
    ent = r["rcd_form"]
    od = str(r["operational_definition"])
    mol = str(r["key_molecules"])
    pmid = str(r["founding_pmid"]).replace(".0", "")
    tok = TOKEN.get(ent, ent)

    # deep search: 2 query variants
    cands = []
    for q in [f'"{tok}"[Title/Abstract]', f'{tok} cell death[Title/Abstract]']:
        for p in esearch(q, 6):
            if p not in cands:
                cands.append(p)
    titles = esummary(cands[:8])
    cand_list = "\n".join(f"- PMID {p}: {titles.get(p, {}).get('title', '')}" for p in cands[:8] if p in titles)

    prompt = f"""You are a cell-death nomenclature auditor. Validate the operational definition (OD) below for the RCD entity "{ent}".

OD: {od}
Key molecules: {mol}
Current founding reference: PMID {pmid}
Current abstract excerpt: {absmap.get(pmid, '(not available)')[:1800]}

Candidate references from a deep PubMed search (titles only):
{cand_list}

Tasks (answer in STRICT JSON, no markdown):
1. "claims": for each OD claim (mechanism, trigger, key molecules, morphology) state SUPPORTED / PARTIAL / NOT_SUPPORTED with a 5-word note.
2. "best_reference_pmid": the single BEST defining/coining reference among the candidates (or the current PMID if it is best).
3. "hallucinations": list any unsupported or invented claims (empty list if none).
4. "verdict": VALIDATED / MINOR_ISSUE / MAJOR_ISSUE.
Return ONLY the JSON object."""

    resp = deepseek([{"role": "user", "content": prompt}])
    results.append({"entity": ent, "current_pmid": pmid, "response": resp})
    print(f"[{idx+1}/{len(pend)}] {ent} -> {resp[:110]}")
    time.sleep(1.2)

out = pd.DataFrame(results)
out.to_csv(BASE + "/od_validation_deepseek.csv", index=False)
print("\nSAVED od_validation_deepseek.csv | rows:", len(out))
