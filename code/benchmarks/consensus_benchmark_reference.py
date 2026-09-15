#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
consensus_benchmark_reference.py — REFERENCE-BASED benchmark (V7-style).

Queries the Consensus API for the 26 GROUND_TRUTH gene-RCD pairs (known
classifications) and scores the returned EVIDENCE against the reference:
  - positive pairs (EXECUTOR/REGULATOR + YES)  -> evidence should SUPPORT
  - negative pairs (NEGATIVE + NO)              -> evidence must NOT falsely support

Mirrors the DeepSeek cot_benchmark_v7 design, adapted to a search API.

Metrics:
  positive support rate  (fraction of positives with >=1 supporting paper)
  negative false-support rate (fraction of negatives with >=1 falsely supporting paper)
  support density        (avg supporting papers per positive)
  coverage               (papers returned per pair)

Run (from the 'Consensus API' folder):
  python3 consensus_benchmark_reference.py
"""
import os, json, time, urllib.request, ssl, csv
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
API_URL = "https://api.consensus.app/v1/search"

# read the API key from the shared .env (extraction code snippets)
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

# GROUND_TRUTH: (gene, form, true_role, true_direction, true_mechanistic)
GROUND_TRUTH = [
    # 18 positives
    ("BAX", "Apoptosis", "EXECUTOR", "PROMOTES", "YES"),
    ("CASP3", "Apoptosis", "EXECUTOR", "PROMOTES", "YES"),
    ("CASP8", "Apoptosis", "EXECUTOR", "PROMOTES", "YES"),
    ("CASP9", "Apoptosis", "EXECUTOR", "PROMOTES", "YES"),
    ("CYCS", "Apoptosis", "EXECUTOR", "PROMOTES", "YES"),
    ("MLKL", "Necroptosis", "EXECUTOR", "PROMOTES", "YES"),
    ("RIPK3", "Necroptosis", "EXECUTOR", "PROMOTES", "YES"),
    ("GSDMD", "Pyroptosis", "EXECUTOR", "PROMOTES", "YES"),
    ("GSDME", "Pyroptosis", "EXECUTOR", "PROMOTES", "YES"),
    ("CASP1", "Pyroptosis", "EXECUTOR", "PROMOTES", "YES"),
    ("BCL2", "Apoptosis", "REGULATOR", "PROTECTS", "YES"),
    ("BCL2L1", "Apoptosis", "REGULATOR", "PROTECTS", "YES"),
    ("XIAP", "Apoptosis", "REGULATOR", "PROTECTS", "YES"),
    ("TP53", "Apoptosis", "REGULATOR", "PROMOTES", "YES"),
    ("GPX4", "Ferroptosis", "REGULATOR", "PROTECTS", "YES"),
    ("ACSL4", "Ferroptosis", "REGULATOR", "PROMOTES", "YES"),
    ("AIFM2", "Ferroptosis", "REGULATOR", "PROTECTS", "YES"),
    ("BECN1", "Autophagy", "REGULATOR", "PROMOTES", "YES"),
    # 8 negatives
    ("GPX4", "Pyroptosis", "NEGATIVE", "UNCLEAR", "NO"),
    ("MLKL", "Ferroptosis", "NEGATIVE", "UNCLEAR", "NO"),
    ("CASP3", "Necroptosis", "NEGATIVE", "UNCLEAR", "NO"),
    ("BAX", "Necroptosis", "NEGATIVE", "UNCLEAR", "NO"),
    ("GSDMD", "Ferroptosis", "NEGATIVE", "UNCLEAR", "NO"),
    ("CASP1", "Apoptosis", "NEGATIVE", "UNCLEAR", "NO"),
    ("MLKL", "Apoptosis", "NEGATIVE", "UNCLEAR", "NO"),
    ("GSDMD", "Necroptosis", "NEGATIVE", "UNCLEAR", "NO"),
]

FORM_TERMS = {
    "Apoptosis":   ["apoptosis", "apoptotic"],
    "Necroptosis": ["necroptosis", "necroptotic"],
    "Pyroptosis":  ["pyroptosis", "pyroptotic"],
    "Ferroptosis": ["ferroptosis", "ferroptotic"],
    "Autophagy":   ["autophagy", "autophagic"],
}

GENE_ALIASES = {
    "CYCS": ["cycs", "cytochrome c"],
    "CASP3": ["casp3", "caspase-3", "caspase 3"],
    "CASP8": ["casp8", "caspase-8", "caspase 8"],
    "CASP9": ["casp9", "caspase-9", "caspase 9"],
    "CASP1": ["casp1", "caspase-1", "caspase 1"],
    "BCL2L1": ["bcl2l1", "bcl-xl", "bcl xl", "bcl2l"],
    "AIFM2": ["aifm2", "fsp1"],
    "BECN1": ["becn1", "beclin-1", "beclin 1"],
    "RIPK3": ["ripk3", "rip3"],
    "GSDMD": ["gsdmd", "gasdermin d"],
    "GSDME": ["gsdme", "gasdermin e"],
}

def aliases(gene):
    return GENE_ALIASES.get(gene, [gene.lower()])

def form_hit(text, form):
    t = text.lower()
    return any(term in t for term in FORM_TERMS.get(form, [form.lower()]))

def gene_hit(text, gene):
    t = text.lower()
    return any(a in t for a in aliases(gene))

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
    for gene, form, trole, tdir, tmech in GROUND_TRUTH:
        query = f"{gene} {form} cell death"
        papers = search(query)
        # count supporting papers (takeaway OR abstract mentions gene + form)
        n_support = sum(1 for p in papers
                        if gene_hit((p.get('takeaway') or '') + ' ' + (p.get('abstract') or '') + ' ' + (p.get('title') or ''), gene)
                        and form_hit((p.get('takeaway') or '') + ' ' + (p.get('abstract') or '') + ' ' + (p.get('title') or ''), form))
        is_positive = tmech == 'YES'
        rows.append({
            'gene': gene, 'form': form, 'true_role': trole, 'true_mech': tmech,
            'query': query, 'n_papers': len(papers), 'n_support': n_support,
            'top_title': (papers[0].get('title') or '')[:80] if papers else '',
            'top_doi': (papers[0].get('doi') or '') if papers else '',
        })
        log(f"  {gene:7s} {form:12s} true={trole:9s}/{tmech:3s} | papers={len(papers):2d} support={n_support:2d}")
        time.sleep(1.2)  # be polite to the API

    # scoring
    pos = [r for r in rows if r['true_mech'] == 'YES']
    neg = [r for r in rows if r['true_mech'] == 'NO']
    pos_supported = [r for r in pos if r['n_support'] >= 1]
    neg_false = [r for r in neg if r['n_support'] >= 1]

    print()
    print("=" * 62)
    print(f"REFERENCE-BASED BENCHMARK — {len(rows)} pairs")
    print("=" * 62)
    print(f"  positive support rate:  {len(pos_supported)}/{len(pos)} = {len(pos_supported)/len(pos)*100:.0f}%")
    print(f"  negative false-support: {len(neg_false)}/{len(neg)} = {len(neg_false)/len(neg)*100:.0f}%  (target 0%)")
    print(f"  avg support density (positives): {sum(r['n_support'] for r in pos)/len(pos):.1f} papers")
    print(f"  avg coverage: {sum(r['n_papers'] for r in rows)/len(rows):.1f} papers/pair")
    if neg_false:
        print("  FALSE-POSITIVE pairs:")
        for r in neg_false:
            print(f"    - {r['gene']} + {r['form']} (support={r['n_support']})")

    out = os.path.join(BASE, 'consensus_benchmark_reference_results.csv')
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"\nresults -> {out}")
    print("DONE.")

if __name__ == '__main__':
    main()
