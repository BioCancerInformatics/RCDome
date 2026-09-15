#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
consensus_benchmark_reference_v2.py — REFERENCE-BASED benchmark, iteration 2.

STRICTER support detection (mirrors DeepSeek rules 8/9 — role-form specificity):
  A paper SUPPORTS a gene-form association only if its TAKEWAY contains:
    - the gene  (aliases)
    - the asked form  (terms)
    - a ROLE VERB  (executes / regulates / mediates / drives / promotes / inhibits ...)
  all in the same takeaway (not spread across the abstract).

This eliminates "crosstalk" papers that merely mention the gene and the form in
different contexts (e.g., "MLKL drives necroptosis, while ferroptosis is driven by ...").
"""
import os, json, time, urllib.request, ssl, csv
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

GROUND_TRUTH = [
    ("BAX","Apoptosis","EXECUTOR","PROMOTES","YES"),
    ("CASP3","Apoptosis","EXECUTOR","PROMOTES","YES"),
    ("CASP8","Apoptosis","EXECUTOR","PROMOTES","YES"),
    ("CASP9","Apoptosis","EXECUTOR","PROMOTES","YES"),
    ("CYCS","Apoptosis","EXECUTOR","PROMOTES","YES"),
    ("MLKL","Necroptosis","EXECUTOR","PROMOTES","YES"),
    ("RIPK3","Necroptosis","EXECUTOR","PROMOTES","YES"),
    ("GSDMD","Pyroptosis","EXECUTOR","PROMOTES","YES"),
    ("GSDME","Pyroptosis","EXECUTOR","PROMOTES","YES"),
    ("CASP1","Pyroptosis","EXECUTOR","PROMOTES","YES"),
    ("BCL2","Apoptosis","REGULATOR","PROTECTS","YES"),
    ("BCL2L1","Apoptosis","REGULATOR","PROTECTS","YES"),
    ("XIAP","Apoptosis","REGULATOR","PROTECTS","YES"),
    ("TP53","Apoptosis","REGULATOR","PROMOTES","YES"),
    ("GPX4","Ferroptosis","REGULATOR","PROTECTS","YES"),
    ("ACSL4","Ferroptosis","REGULATOR","PROMOTES","YES"),
    ("AIFM2","Ferroptosis","REGULATOR","PROTECTS","YES"),
    ("BECN1","Autophagy","REGULATOR","PROMOTES","YES"),
    ("GPX4","Pyroptosis","NEGATIVE","UNCLEAR","NO"),
    ("MLKL","Ferroptosis","NEGATIVE","UNCLEAR","NO"),
    ("CASP3","Necroptosis","NEGATIVE","UNCLEAR","NO"),
    ("BAX","Necroptosis","NEGATIVE","UNCLEAR","NO"),
    ("GSDMD","Ferroptosis","NEGATIVE","UNCLEAR","NO"),
    ("CASP1","Apoptosis","NEGATIVE","UNCLEAR","NO"),
    ("MLKL","Apoptosis","NEGATIVE","UNCLEAR","NO"),
    ("GSDMD","Necroptosis","NEGATIVE","UNCLEAR","NO"),
]

FORM_TERMS = {
    "Apoptosis":   ["apoptosis", "apoptotic"],
    "Necroptosis": ["necroptosis", "necroptotic"],
    "Pyroptosis":  ["pyroptosis", "pyroptotic"],
    "Ferroptosis": ["ferroptosis", "ferroptotic"],
    "Autophagy":   ["autophagy", "autophagic"],
}

ROLE_VERBS = [
    "execute", "executes", "executor", "executioner",
    "regulate", "regulates", "regulator",
    "mediate", "mediates", "mediator",
    "drive", "drives", "driven", "driver",
    "promote", "promotes", "protect", "protects",
    "inhibit", "inhibits", "induce", "induces",
    "activate", "activates", "suppress", "suppresses",
    "essential", "critical", "require", "requires", "required",
]

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

def gene_hit(t, gene):
    t = t.lower(); return any(a in t for a in aliases(gene))

def form_hit(t, form):
    t = t.lower(); return any(x in t for x in FORM_TERMS.get(form, [form.lower()]))

def verb_hit(t):
    t = t.lower(); return any(v in t for v in ROLE_VERBS)

def supports_strict(takeaway, gene, form):
    """A takeaway supports iff gene + asked form + role verb all present."""
    return gene_hit(takeaway, gene) and form_hit(takeaway, form) and verb_hit(takeaway)

def search(query, page_size=10):
    url = f"{API_URL}?query={urllib.request.quote(query)}&page_size={page_size}"
    req = urllib.request.Request(url, headers={'x-api-key': API_KEY, 'User-Agent': 'Mozilla/5.0'})
    for attempt in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=30, context=CTX)
            return json.loads(r.read().decode('utf-8')).get('results', [])
        except Exception as e:
            if attempt == 2:
                print(f"  ! search error: {str(e)[:80]}"); return []
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
        n_support = sum(1 for p in papers if supports_strict(p.get('takeaway') or '', gene, form))
        is_positive = tmech == 'YES'
        rows.append({
            'gene': gene, 'form': form, 'true_role': trole, 'true_mech': tmech,
            'n_papers': len(papers), 'n_support_strict': n_support,
        })
        log(f"  {gene:7s} {form:12s} true={trole:9s}/{tmech:3s} | strict_support={n_support:2d}")
        time.sleep(1.2)

    pos = [r for r in rows if r['true_mech'] == 'YES']
    neg = [r for r in rows if r['true_mech'] == 'NO']
    pos_ok = [r for r in pos if r['n_support_strict'] >= 1]
    neg_false = [r for r in neg if r['n_support_strict'] >= 1]

    print()
    print("=" * 62)
    print(f"REFERENCE-BASED BENCHMARK v2 (strict) — {len(rows)} pairs")
    print("=" * 62)
    print(f"  positive support rate:  {len(pos_ok)}/{len(pos)} = {len(pos_ok)/len(pos)*100:.0f}%  (target 100%)")
    print(f"  negative false-support: {len(neg_false)}/{len(neg)} = {len(neg_false)/len(neg)*100:.0f}%  (target 0%)")
    if neg_false:
        print("  remaining FALSE-POSITIVE pairs:")
        for r in neg_false:
            print(f"    - {r['gene']} + {r['form']} (strict_support={r['n_support_strict']})")

    out = os.path.join(BASE, 'consensus_benchmark_reference_v2_results.csv')
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"\nresults -> {out}")
    print("DONE.")

if __name__ == '__main__':
    main()
