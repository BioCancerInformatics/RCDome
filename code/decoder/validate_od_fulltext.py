"""
DeepSeek + RAG FULL-TEXT validation (FIXED) — 40 entities.
Always includes the ABSTRACT; adds full-text excerpts where PMC is available.
"""
import os, json, time, urllib.request, urllib.parse, re, sys
import pandas as pd

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder"
KEY = ""
for line in open(r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/extraction code snippets/.env", encoding="utf-8"):
    if line.startswith("DEEPSEEK_KEY="):
        KEY = line.split("=", 1)[1].strip()

def deepseek(messages, model="deepseek-chat", max_tokens=1400):
    req = urllib.request.Request("https://api.deepseek.com/chat/completions",
        data=json.dumps({"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0}).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + KEY})
    for a in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode())["choices"][0]["message"]["content"]
        except Exception as e:
            if a == 2:
                return f"ERROR: {type(e).__name__}: {str(e)[:120]}"
            time.sleep(5 + a * 5)

df = pd.read_csv(BASE + "/RCDome_Decoder_53.csv")
targets = df[(df["definition_status"] == "DEFINED_RODRIGUES") &
             (df["galluzzi_nccd_status"] != "NCCD_2018_INVARIANT") |
             (df["definition_status"] != "DEFINED_RODRIGUES")]

pmids = [str(r["founding_pmid"]).replace(".0", "") for _, r in targets.iterrows()
         if str(r["founding_pmid"]).replace(".0", "").isdigit()]

# abstracts (batch efetch text)
absmap = {}
u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id="
     + ",".join(pmids) + "&rettype=abstract&retmode=text")
try:
    with urllib.request.urlopen(u, timeout=120) as r:
        txt = r.read().decode("utf-8", "replace")
    pos = [(m.end(), m.group(1)) for m in re.finditer(r"PMID:\s*(\d{7,8})", txt)]
    for i, (end, pid) in enumerate(pos):
        start = pos[i-1][0] if i > 0 else 0
        absmap[pid] = re.sub(r"\s+", " ", txt[start:end]).strip()[:2200]
except Exception:
    pass

# PMC ids
def esummary(ids):
    u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(ids))
    with urllib.request.urlopen(u, timeout=40) as r:
        return json.loads(r.read().decode()).get("result", {})
summ = esummary(pmids)
pmc_of = {}
for p in pmids:
    for a in summ.get(p, {}).get("articleids", []):
        if a["idtype"] == "pmc":
            pmc_of[p] = a["value"]

def fetch_pmc(pmcid):
    u = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=" + pmcid
    try:
        with urllib.request.urlopen(u, timeout=120) as r:
            xml = r.read().decode("utf-8", "replace")
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml))
    except Exception:
        return ""

def excerpts(full, ent, mols):
    if not full:
        return ""
    ft = full.lower()
    out = []
    for m in mols:
        m2 = re.sub(r"[^a-z0-9]", "", m.lower())
        if m2:
            mm = re.search(re.escape(m2), ft)
            if mm:
                s = max(0, mm.start() - 250)
                out.append(full[s:mm.end() + 250])
    en = re.sub(r"[^a-z0-9]", "", ent.lower())
    for mm in list(re.finditer(re.escape(en), ft))[:2]:
        s = max(0, mm.start() - 200)
        out.append(full[s:mm.end() + 200])
    seen = []
    for e in out:
        if e not in seen:
            seen.append(e)
    return " ... ".join(seen)[:5000]

rows = []
sys.stdout.reconfigure(encoding="utf-8")
for i, (_, r) in enumerate(targets.iterrows()):
    ent = r["rcd_form"]
    od = str(r["operational_definition"])
    mol = str(r["key_molecules"])
    pmid = str(r["founding_pmid"]).replace(".0", "")
    ab = absmap.get(pmid, "(no abstract)")
    pmc = pmc_of.get(pmid, "")
    full = fetch_pmc(pmc) if pmc else ""
    mols = [m.strip() for m in re.split(r"[;,]", mol) if m.strip() and m.strip().lower() not in ("not specified", "nan")]
    ex = excerpts(full, ent, mols)
    evidence = "ABSTRACT"
    if full:
        evidence = "FULL TEXT + ABSTRACT"

    prompt = f"""You are a cell-death nomenclature auditor. Validate the operational definition (OD) for the RCD entity "{ent}" against the {evidence} provided.

OD: {od}
Key molecules: {mol}
Founding reference: PMID {pmid}

ABSTRACT:
{ab}

FULL-TEXT EXCERPTS (around key molecules):
{ex if ex else '(none)'}

Tasks (STRICT JSON only):
1. "claims": mechanism / trigger / key_molecules / morphology each = SUPPORTED / PARTIAL / NOT_SUPPORTED + 6-word note.
2. "best_reference_pmid": the single best defining/coining PMID (the current one if best).
3. "hallucinations": list unsupported or invented claims ([] if none).
4. "verdict": VALIDATED / MINOR_ISSUE / MAJOR_ISSUE."""

    resp = deepseek([{"role": "user", "content": prompt}])
    rows.append({"entity": ent, "evidence": evidence, "current_pmid": pmid, "response": resp})
    print(f"[{i+1}/{len(targets)}] {ent:34s} [{evidence:18s}] {resp[:80]}")
    time.sleep(1.3)

out = pd.DataFrame(rows)
out.to_csv(BASE + "/od_validation_deepseek_fulltext.csv", index=False)
print("\nSAVED od_validation_deepseek_fulltext.csv | rows:", len(out))
