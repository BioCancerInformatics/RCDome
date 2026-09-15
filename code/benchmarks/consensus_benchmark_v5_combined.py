#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
consensus_benchmark_v5_combined.py — iteration 5: FULL PIPELINE benchmark.

For each of the 26 GROUND_TRUTH pairs:
  1. Query the Consensus API -> top papers + AI takeaways (the EVIDENCE).
  2. Feed that evidence to DeepSeek (JSON mode) -> classify role/direction/mechanistic.
  3. Score the classification against the GROUND_TRUTH (same metrics as the
     DeepSeek cot_benchmark: role accuracy, sensitivity/precision, rejection,
     false positives, coherence).

This tests whether the Consensus evidence is SUFFICIENT for a correct
classification — the real production use case.
"""
import os, json, time, re, urllib.request, ssl, csv
from collections import Counter
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
CONSENSUS_URL = "https://api.consensus.app/v1/search"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

def load_env(keyname):
    env_file = os.path.join(BASE, '..', 'extraction code snippets', '.env')
    key = os.environ.get(keyname, '')
    if not key and os.path.exists(env_file):
        for line in open(env_file, encoding='utf-8'):
            if line.strip().startswith(keyname + '='):
                key = line.strip().split('=', 1)[1].strip()
    return key

CONSENSUS_KEY = load_env('CONSENSUS_API_KEY')
DEEPSEEK_KEY  = load_env('DEEPSEEK_KEY')
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

def consensus_search(query, page_size=8):
    url = f"{CONSENSUS_URL}?query={urllib.request.quote(query)}&page_size={page_size}"
    req = urllib.request.Request(url, headers={'x-api-key': CONSENSUS_KEY, 'User-Agent': 'Mozilla/5.0'})
    for attempt in range(4):
        try:
            r = urllib.request.urlopen(req, timeout=30, context=CTX)
            return json.loads(r.read().decode('utf-8')).get('results', [])
        except Exception:
            if attempt == 3:
                return None
            time.sleep(5 * (attempt + 1))
    return None

def deepseek_classify(gene, form, evidence):
    prompt = (
        f"Gene {gene}, regulated cell death form {form}.\n\n"
        f"Literature evidence from a search (titles + AI takeaways):\n{evidence}\n\n"
        f"Using ONLY this evidence, classify the gene's relationship to this cell death form.\n"
        f"DEFINITIONS: EXECUTOR = the gene DIRECTLY executes the death (pore, cleavage, permeabilization). "
        f"REGULATOR = the gene CONTROLS the death (promotes or inhibits) but does NOT execute it. "
        f"MARKER = associated but not causal. UNCERTAIN = unclear from the evidence.\n"
        f"IMPORTANT: if the evidence shows the gene's role belongs to a DIFFERENT cell death form "
        f"(not {form}), then classify mechanistic=NO, role=UNCERTAIN, direction=UNCLEAR.\n"
        f'Output ONLY a JSON object with keys "mechanistic" ("YES"/"NO"), "role" ("EXECUTOR"/"REGULATOR"/"MARKER"/"UNCERTAIN"), '
        f'"direction" ("PROMOTES"/"PROTECTS"/"UNCLEAR"). JSON:'
    )
    body = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500, "response_format": {"type": "json_object"}}
    req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'),
                                 headers={"Authorization": "Bearer " + DEEPSEEK_KEY, "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=120, context=CTX)
            resp = json.loads(r.read().decode('utf-8'))
            content = resp['choices'][0]['message']['content'].strip()
            return safe_json(content)
        except Exception as e:
            if attempt == 2:
                print(f"  ! deepseek error: {str(e)[:60]}")
                return {}
            time.sleep(8 * (attempt + 1))
    return {}

def safe_json(s):
    s = re.sub(r'^```(json)?\s*', '', s.strip())
    s = re.sub(r'\s*```$', '', s)
    if '{' in s and '}' in s:
        s = s[s.find('{'):s.rfind('}') + 1]
    try:
        return json.loads(s)
    except Exception:
        return {}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def pct(n, d):
    return f"{n/d*100:.0f}%" if d else "n/a"

def main():
    if not CONSENSUS_KEY or not DEEPSEEK_KEY:
        print("ERROR: missing CONSENSUS_API_KEY or DEEPSEEK_KEY"); return

    results = []
    for gene, form, trole, tdir, tmech in GROUND_TRUTH:
        papers = consensus_search(f"{gene} {form} cell death")
        if papers is None:
            log(f"  {gene:7s} {form:12s} | CONSENSUS NETWORK FAIL")
            results.append({'gene': gene, 'form': form, 'true_role': trole, 'true_mech': tmech,
                            'pred_role': 'ERROR', 'pred_dir': '', 'pred_mech': ''})
            time.sleep(3); continue
        evidence = "\n".join(f"- {p.get('title','')}: {(p.get('takeaway') or '')[:200]}"
                             for p in papers[:5])
        cj = deepseek_classify(gene, form, evidence)
        role = (cj.get('role') or '').upper()
        direction = (cj.get('direction') or '').upper()
        mech = (cj.get('mechanistic') or '').upper()
        results.append({'gene': gene, 'form': form, 'true_role': trole, 'true_mech': tmech,
                        'pred_role': role, 'pred_dir': direction, 'pred_mech': mech})
        log(f"  {gene:7s} {form:12s} true={trole:9s}/{tmech:3s} | pred={role:9s}/{mech:3s}")
        time.sleep(2)

    # metrics (same as DeepSeek cot_benchmark)
    exe_true = [r for r in results if r['true_role'] == 'EXECUTOR']
    reg_true = [r for r in results if r['true_role'] == 'REGULATOR']
    neg_true = [r for r in results if r['true_role'] == 'NEGATIVE']
    exe_called = [r for r in results if r['pred_role'] == 'EXECUTOR']
    reg_called = [r for r in results if r['pred_role'] == 'REGULATOR']
    role_acc = sum(1 for r in results if r['pred_role'] == r['true_role'])
    combined = sum(1 for r in results
                   if (r['true_role'] in ('EXECUTOR','REGULATOR') and r['pred_role'] == r['true_role'])
                   or (r['true_role'] == 'NEGATIVE' and r['pred_role'] == 'UNCERTAIN' and r['pred_mech'] == 'NO'))
    neg_rej = sum(1 for r in neg_true if r['pred_role'] == 'UNCERTAIN' and r['pred_mech'] == 'NO')
    fp = sum(1 for r in neg_true if r['pred_role'] in ('EXECUTOR','REGULATOR','MARKER') or r['pred_mech'] == 'YES')
    dir_acc = sum(1 for r in reg_true if r['pred_dir'] == r['true_dir'])

    print()
    print("=" * 62)
    print(f"COMBINED BENCHMARK (Consensus evidence -> DeepSeek) — {len(results)} pairs")
    print("=" * 62)
    print(f"  role accuracy:         {role_acc}/{len(results)} ({pct(role_acc, len(results))})")
    print(f"  COMBINED accuracy:     {combined}/{len(results)} ({pct(combined, len(results))})")
    print(f"  EXECUTOR sensitivity:  {sum(1 for r in exe_true if r['pred_role']=='EXECUTOR')}/{len(exe_true)} ({pct(sum(1 for r in exe_true if r['pred_role']=='EXECUTOR'), len(exe_true))})")
    print(f"  EXECUTOR precision:    {sum(1 for r in exe_called if r['true_role']=='EXECUTOR')}/{len(exe_called)} ({pct(sum(1 for r in exe_called if r['true_role']=='EXECUTOR'), len(exe_called))})")
    print(f"  REGULATOR sensitivity: {sum(1 for r in reg_true if r['pred_role']=='REGULATOR')}/{len(reg_true)} ({pct(sum(1 for r in reg_true if r['pred_role']=='REGULATOR'), len(reg_true))})")
    print(f"  REGULATOR precision:   {sum(1 for r in reg_called if r['true_role']=='REGULATOR')}/{len(reg_called)} ({pct(sum(1 for r in reg_called if r['true_role']=='REGULATOR'), len(reg_called))})")
    print(f"  negative rejection:    {neg_rej}/{len(neg_true)} ({pct(neg_rej, len(neg_true))})")
    print(f"  FALSE POSITIVES:       {fp}/{len(neg_true)} ({pct(fp, len(neg_true))})")
    print(f"  direction accuracy:    {dir_acc}/{len(reg_true)} ({pct(dir_acc, len(reg_true))})")

    out = os.path.join(BASE, 'consensus_benchmark_v5_combined_results.csv')
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader(); w.writerows(results)
    print(f"\nresults -> {out}")
    print("DONE.")

if __name__ == '__main__':
    main()
