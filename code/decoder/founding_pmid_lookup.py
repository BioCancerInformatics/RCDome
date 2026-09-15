"""
RCDome Definition Governance — founding-PMID lookup (V026).

For each of the 28 pending RCD entities, locate the ORIGINAL DISCOVERY ARTICLE
(the paper that first named/described the entity) via PubMed E-utilities.

Strategy:
  - query the coined name in [Title] (most precise for finding the coining paper),
    with [dp] date bounds for broad/historical terms;
  - esearch sort=pub date (newest-first), then fetch the OLDEST hit via retstart;
  - esummary the oldest hit.

Knock Test: the result is a CANDIDATE only; the title must actually coin/describe
the entity. Final assignment is human-verified (two-call).
"""
import json, time, urllib.request, urllib.parse, re, csv, sys

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# <entity>: esearch term (coined name in [Title]; [dp] bounds where the term is broad)
QUERIES = {
    "Programmed cell death": '"programmed cell death"[Title] AND 1950:1975[dp]',
    "Apoptosis (intrinsic)": '"intrinsic apoptosis"[Title]',
    "Apoptosis (extrinsic)": '"extrinsic apoptosis"[Title]',
    "Mitotic death": '"mitotic death"[Title]',
    "Autophagy-dependent cell death": '"autophagy-dependent cell death"[Title]',
    "Regulated Necrosis": '"regulated necrosis"[Title]',
    "Senescence and Autophagy in Cancer": '"senescence"[Title] AND "autophagy"[Title] AND 2000:2015[dp]',
    "MPT-driven necrosis": '"MPT-driven necrosis"[Title/Abstract]',
    "Phagoptosis": '"phagoptosis"[Title]',
    "Aponecrosis": '"aponecrosis"[Title]',
    "PANoptosis": '"PANoptosis"[Title]',
    "Lysosomal cell death": '"lysosomal cell death"[Title]',
    "Metalloptosis": '"metalloptosis"[Title]',
    "Lysoptosis": '"lysoptosis"[Title]',
    "Floatptosis": '"floatptosis"[Title]',
    "NECSO": '"NECSO"[Title/Abstract]',
    "Vacuolar cell death": '"vacuolar cell death"[Title]',
    "Hypersensitive response": '"hypersensitive response"[Title] AND 1900:1960[dp]',
    "Ammonia-induced cell death": '"ammonia"[Title] AND "cell death"[Title] AND 1980:2005[dp]',
    "Oncosis": '"oncosis"[Title]',
    "Mitoxyperilysis": '"mitoxyperilysis"[Title/Abstract]',
    "Lysozincrosis": '"lysozincrosis"[Title/Abstract]',
    "Linker cell-type death": '"linker cell"[Title] AND 2000:2020[dp]',
    "Eryptosis": '"eryptosis"[Title]',
    "Cornification": '"cornification"[Title]',
    "Triaptosis": '"triaptosis"[Title/Abstract]',
    "Spectosis": '"spectosis"[Title]',
    "Pyronecrosis": '"pyronecrosis"[Title]',
}


def get(url, retries=3):
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if i == retries - 1:
                return {"error": f"{type(e).__name__}: {str(e)[:120]}"}
            time.sleep(1 + i)


def esearch(term, retmax=1, retstart=0):
    u = (f"{EUTILS}esearch.fcgi?db=pubmed&retmode=json&retmax={retmax}"
         f"&retstart={retstart}&sort=pub+date&term=" + urllib.parse.quote(term))
    return get(u)


def esummary(pid):
    if not pid:
        return {}
    u = f"{EUTILS}esummary.fcgi?db=pubmed&retmode=json&id={pid}"
    d = get(u)
    return d.get("result", {}).get(str(pid), {})


def year_of(pubdate):
    m = re.search(r"\b(18|19|20|21)\d{2}\b", str(pubdate))
    return int(m.group()) if m else 9999


def oldest_id(term):
    """Return the PMID of the oldest hit for the term (None if no hits)."""
    res = esearch(term, retmax=1)
    if "error" in res:
        return None, 0, res["error"]
    count = int(res.get("esearchresult", {}).get("count", 0))
    if count == 0:
        return None, 0, ""
    if count <= 9999:
        r2 = esearch(term, retmax=1, retstart=count - 1)
        ids = r2.get("esearchresult", {}).get("idlist", [])
        return (ids[0] if ids else None), count, ""
    return None, count, "count>9999 (needs date-bounded lookup)"


def main():
    out = []
    for ent, term in QUERIES.items():
        pid, count, err = oldest_id(term)
        if err:
            out.append({"entity": ent, "status": "ERROR", "n_hits": count, "pmid": "",
                        "year": "", "title": "", "journal": "", "authors": "", "note": err})
            print(f"[ERR] {ent}: {err}")
            time.sleep(0.4)
            continue
        if not pid:
            out.append({"entity": ent, "status": "NO_HITS", "n_hits": 0, "pmid": "",
                        "year": "", "title": "", "journal": "", "authors": "", "note": "no PubMed hits"})
            print(f"[---] {ent}: NO HITS")
            time.sleep(0.4)
            continue
        s = esummary(pid)
        title = re.sub(r"\s+", " ", s.get("title", "")).strip()
        out.append({"entity": ent, "status": "FOUND", "n_hits": count, "pmid": str(pid),
                    "year": year_of(s.get("pubdate")), "title": title,
                    "journal": s.get("fulljournalname", s.get("source", "")),
                    "authors": ", ".join(a["name"] for a in s.get("authors", [])[:3]),
                    "note": "CANDIDATE — human-verify (two-call)"})
        print(f"[{year_of(s.get('pubdate'))}] {ent}: PMID {pid} (n={count}) — {title[:95]}")
        time.sleep(0.4)

    path = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder/founding_pmids_pending.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["entity", "status", "n_hits", "pmid", "year",
                                          "title", "journal", "authors", "note"])
        w.writeheader()
        w.writerows(out)
    print("\nSAVED:", path)


if __name__ == "__main__":
    main()
