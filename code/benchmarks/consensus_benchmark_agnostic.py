#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
consensus_benchmark_agnostic.py — AGNOSTIC benchmark (V8/V11-style, no reference).

Queries the Consensus API for the SAME 26 gene-RCD pairs, but with NO reference /
ground-truth provided. It only reports the EVIDENCE PROFILE per pair, so we can
tune the query + filters until the evidence is high-quality and unambiguous.

Agnostic metrics per pair:
  coverage      = papers returned
  support       = papers whose takeaway/abstract mention the gene AND the asked form
  top_forms     = the RCD forms the gene is actually mentioned with (across all
                  returned takeaways) — reveals whether the gene belongs to a
                  DIFFERENT form (ambiguity signal)

This mirrors DeepSeek cot_benchmark_v8/v11: no reference, self-consistent evidence.

Run (from the 'Consensus API' folder):
  python3 consensus_benchmark_agnostic.py
"""
import os, json, time, urllib.request, ssl, csv
from collections import Counter
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
API_URL = "https://api.consensus.app/v1/search"

def load_key():
    env_file = os.path.join(BASE, '..', 'extraction code snippets', '.env')
    key = os.environ.get('CONSENSUS_API_KEY', '')
    if not key and os.path.exists(env_file):
        for line in open(env_file, encoding='utf-8'):
            if line.strip().startswith('CONSENSUS_API_KEY='):
                key = line.strip().split('=', 1)[1].strip()
    return key

API_KEY = load_key()
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

# same 26 pairs (gene, form) — NO ground-truth labels used in scoring
PAIRS = [
    ("BAX","Apoptosis"),("CASP3","Apoptosis"),("CASP8","Apoptosis"),("CASP9","Apoptosis"),
    ("CYCS","Apoptosis"),("MLKL","Necroptosis"),("RIPK3","Necroptosis"),("GSDMD","Pyroptosis"),
    ("GSDME","Pyroptosis"),("CASP1","Pyroptosis"),("BCL2","Apoptosis"),("BCL2L1","Apoptosis"),
    ("XIAP","Apoptosis"),("TP53","Apoptosis"),("GPX4","Ferroptosis"),("ACSL4","Ferroptosis"),
    ("AIFM2","Ferroptosis"),("BECN1","Autophagy"),
    ("GPX4","Pyroptosis"),("MLKL","Ferroptosis"),("CASP3","Necroptosis"),("BAX","Necroptosis"),
    ("GSDMD","Ferroptosis"),("CASP1","Apoptosis"),("MLKL","Apoptosis"),("GSDMD","Necroptosis"),
]

ALL_FORM_TERMS = {
    "Apoptosis":   ["apoptosis", "apoptotic"],
    "Necroptosis": ["necroptosis", "necroptotic"],
    "Pyroptosis":  ["pyroptosis", "pyroptotic"],
    "Ferroptosis": ["ferroptosis", "ferroptotic"],
    "Autophagy":   ["autophagy", "autophagic"],
    "Necrosis":    ["necrosis", "necrotic"],
}

GENE_ALIASES = {
    "CYCS": ["cycs", "cytochrome c"],
    "CASP3": ["casp3", "caspase-3", "caspase 3"],
    "CASP8": ["casp8", "caspase-8", "caspase 8"],
    "CASP9": ["casp9", "caspase-9", "caspase 9"],
    "CASP1": ["casp1", "caspase-1", "caspase 1"],
    "BCL2L1": ["bcl2l1", "bcl-xl", "bcl xl"],
    "AIFM2": ["aifm2", "fsp1"],
    "BECN1": ["becn1", "beclin-1", "beclin 1"],
    "RIPK3": ["ripk3", "rip3"],
    "GSDMD": ["gsdmd", "gasdermin d"],
    "GSDME": ["gsdme", "gasdermin e"],
}

def aliases(gene):
    return GENE_ALIASES.get(gene, [gene.lower()])

def gene_hit(text, gene):
    t = text.lower()
    return any(a in t for a in aliases(gene))

def form_hit(text, form):
    t = text.lower()
    return any(term in t for term in ALL_FORM_TERMS.get(form, [form.lower()]))

def forms_in(text):
    t = text.lower()
    return [f for f, terms in ALL_FORM_TERMS.items() if any(term in t for term in terms)]

def search(query, page_size=10):
    url = f"{API_URL}?query={urllib.request.quote(query)}&page_size={page_size}"
    req = urllib.request.Request(url, headers={'x-api-key': API_KEY, 'User-Agent': 'Mozilla/5.0'})
    for attempt in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=30, context=CTX)
            return json.loads(r.read().decode('utf-8')).get('results', [])
        except Exception as e:
            if attempt == 2:
                print(f"  ! search error: {str(e)[:80]}")
                return []
            time.sleep(3 * (attempt + 1))
    return []

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def main():
    if not API_KEY:
        print("ERROR: CONSENSUS_API_KEY not found"); return

    rows = []
    for gene, form in PAIRS:
        query = f"{gene} {form} cell death"
        papers = search(query)
        text = ' '.join((p.get('takeaway') or '') + ' ' + (p.get('abstract') or '') + ' ' + (p.get('title') or '') for p in papers)
        n_support = sum(1 for p in papers
                        if gene_hit((p.get('takeaway') or '')+' '+(p.get('abstract') or '')+' '+(p.get('title') or ''), gene)
                        and form_hit((p.get('takeaway') or '')+' '+(p.get('abstract') or '')+' '+(p.get('title') or ''), form))
        # agnostic ambiguity: which OTHER forms does the gene appear with?
        form_counter = Counter()
        for p in papers:
            for f in forms_in((p.get('takeaway') or '') + ' ' + (p.get('title') or '')):
                form_counter[f] += 1
        top_forms = ', '.join(f"{f}:{c}" for f, c in form_counter.most_common(4))

        rows.append({
            'gene': gene, 'form_asked': form, 'query': query,
            'n_papers': len(papers), 'n_support': n_support,
            'top_forms_mentioned': top_forms,
            'top_title': (papers[0].get('title') or '')[:80] if papers else '',
            'top_doi': (papers[0].get('doi') or '') if papers else '',
        })
        log(f"  {gene:7s} {form:12s} | papers={len(papers):2d} support={n_support:2d} | forms={top_forms}")
        time.sleep(1.2)

    print()
    print("=" * 62)
    print(f"AGNOSTIC BENCHMARK (no reference) — {len(rows)} pairs")
    print("=" * 62)
    print(f"  avg coverage: {sum(r['n_papers'] for r in rows)/len(rows):.1f} papers/pair")
    print(f"  avg support:  {sum(r['n_support'] for r in rows)/len(rows):.1f} papers/pair")
    # agnostic quality signal: how many pairs have ZERO support (weak/absent evidence)
    zero = [r for r in rows if r['n_support'] == 0]
    print(f"  pairs with ZERO support: {len(zero)}/{len(rows)}  (agnostic ambiguity signal)")

    out = os.path.join(BASE, 'consensus_benchmark_agnostic_results.csv')
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"\nresults -> {out}")
    print("DONE.")

if __name__ == '__main__':
    main()
