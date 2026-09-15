#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
consensus_benchmark_reference_v3.py — REFERENCE-BASED benchmark, iteration 3.

Iteration 3 rules (push to 100% / 0%):
  R1 (sentence-level): the takeaway must contain gene + asked form + role verb
      in the SAME SENTENCE (not spread across the whole takeaway/abstract).
  R2 (role-form specificity, DeepSeek rule 9 analog): if a sentence links the
      gene + a DIFFERENT form + verb, that sentence CONTRADICTS the asked form;
      a paper supports ONLY if it has >=1 supporting sentence and 0 contradicting.

Network hardening: 5 retries with backoff 5/10/20/30/40 s, and 2 s between pairs.
"""
import os, json, re, time, urllib.request, ssl, csv
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
    "execute", "executes", "executor", "executioner", "execution",
    "regulate", "regulates", "regulator", "regulatory",
    "mediate", "mediates", "mediator",
    "drive", "drives", "driven", "driver",
    "promote", "promotes", "protect", "protects",
    "inhibit", "inhibits", "induce", "induces",
    "activate", "activates", "suppress", "suppresses",
    "essential", "critical", "require", "requires", "required", "key",
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

def sentences(text):
    return [s.strip() for s in re.split(r'[.!?;]', text) if s.strip()]

def other_forms(form):
    return [f for f in FORM_TERMS if f != form]

def analyze_takeaway(takeaway, gene, form):
    """Return (support, contradict) based on sentence-level rules R1+R2."""
    support = 0
    contradict = 0
    for sent in sentences(takeaway):
        g = gene_hit(sent, gene)
        f = form_hit(sent, form)
        v = verb_hit(sent)
        if g and f and v:
            support += 1
        elif g and v and any(form_hit(sent, of) for of in other_forms(form)):
            # gene + verb + a DIFFERENT form (rule 9: role belongs elsewhere)
            contradict += 1
    return support, contradict

def search(query, page_size=10):
    url = f"{API_URL}?query={urllib.request.quote(query)}&page_size={page_size}"
    req = urllib.request.Request(url, headers={'x-api-key': API_KEY, 'User-Agent': 'Mozilla/5.0'})
    backoff = [5, 10, 20, 30, 40]
    for attempt, wait in enumerate(backoff):
        try:
            r = urllib.request.urlopen(req, timeout=30, context=CTX)
            return json.loads(r.read().decode('utf-8')).get('results', [])
        except Exception as e:
            if attempt == len(backoff) - 1:
                print(f"  ! search failed after retries: {str(e)[:60]}")
                return None  # signal network failure
            time.sleep(wait)
    return None

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def main():
    if not API_KEY:
        print("ERROR: CONSENSUS_API_KEY not found"); return

    rows = []
    failed = []
    for gene, form, trole, tdir, tmech in GROUND_TRUTH:
        query = f"{gene} {form} cell death"
        papers = search(query)
        if papers is None:
            failed.append((gene, form))
            rows.append({'gene': gene, 'form': form, 'true_role': trole, 'true_mech': tmech,
                         'n_papers': -1, 'n_support': -1, 'n_contradict': -1})
            log(f"  {gene:7s} {form:12s} | NETWORK FAILURE")
            time.sleep(3)
            continue
        sup = con = 0
        for p in papers:
            s, c = analyze_takeaway(p.get('takeaway') or '', gene, form)
            sup += (1 if s >= 1 and c == 0 else 0)
            con += c
        rows.append({'gene': gene, 'form': form, 'true_role': trole, 'true_mech': tmech,
                     'n_papers': len(papers), 'n_support': sup, 'n_contradict': con})
        log(f"  {gene:7s} {form:12s} true={trole:9s}/{tmech:3s} | support={sup:2d} contradict={con:2d}")
        time.sleep(2)

    # scoring (only on pairs that fetched successfully)
    valid = [r for r in rows if r['n_papers'] >= 0]
    pos = [r for r in valid if r['true_mech'] == 'YES']
    neg = [r for r in valid if r['true_mech'] == 'NO']
    pos_ok = [r for r in pos if r['n_support'] >= 1]
    neg_false = [r for r in neg if r['n_support'] >= 1]

    print()
    print("=" * 62)
    print(f"REFERENCE-BASED BENCHMARK v3 (sentence-level + rule9) — {len(valid)} pairs fetched")
    print("=" * 62)
    if failed:
        print(f"  NETWORK FAILURES: {len(failed)} — {failed}")
    print(f"  positive support rate:  {len(pos_ok)}/{len(pos)} = {len(pos_ok)/len(pos)*100:.0f}%  (target 100%)")
    print(f"  negative false-support: {len(neg_false)}/{len(neg)} = {len(neg_false)/len(neg)*100:.0f}%  (target 0%)")
    if neg_false:
        print("  remaining FALSE-POSITIVE pairs:")
        for r in neg_false:
            print(f"    - {r['gene']} + {r['form']} (support={r['n_support']})")

    out = os.path.join(BASE, 'consensus_benchmark_reference_v3_results.csv')
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"\nresults -> {out}")
    print("DONE.")

if __name__ == '__main__':
    main()
