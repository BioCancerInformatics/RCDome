#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
consensus_benchmark_v6_v11loop.py — iteration 6: FULL v11 loop on Consensus evidence.

Same as the DeepSeek cot_benchmark_v11 (deepseek-v4-pro thinking + tool-call loop
+ verify_role governance rules + 3x vote), but the prompt includes the CONSENSUS
EVIDENCE (titles + takeaways) instead of relying only on internal knowledge.

Tests whether the Consensus evidence is sufficient for the v11 loop to reach
100% combined / 0% false positives on the 26 GROUND_TRUTH pairs.
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

# ---- DeepSeek v11 loop (from cot_benchmark_v11.py) ----
PROPS = {
    "mechanistic": {"type": "string", "enum": ["YES", "NO"]},
    "role": {"type": "string", "enum": ["EXECUTOR", "REGULATOR", "MARKER", "UNCERTAIN"]},
    "direction": {"type": "string", "enum": ["PROMOTES", "PROTECTS", "UNCLEAR"]},
    "mechanism": {"type": "string"},
    "known_forms": {"type": "string"},
    "role_form": {"type": "string"},
}
REQUIRED = ["mechanistic", "role", "direction", "mechanism", "known_forms", "role_form"]
TOOLS = [
    {"type": "function", "function": {"name": "verify_role",
        "description": "Check a preliminary classification against the governance rules",
        "parameters": {"type": "object", "properties": PROPS, "required": REQUIRED}}},
    {"type": "function", "function": {"name": "classify_gene_rcd",
        "description": "Submit the final classification",
        "parameters": {"type": "object", "properties": PROPS, "required": REQUIRED}}},
]

def check_rules(args, form=None):
    role = (args.get('role') or '').upper()
    mech = (args.get('mechanistic') or '').upper()
    direction = (args.get('direction') or '').upper()
    mechanism = (args.get('mechanism') or '').lower()
    known_forms = (args.get('known_forms') or '').lower()
    role_form = (args.get('role_form') or '').lower()
    issues = []
    if role == 'EXECUTOR' and direction != 'PROMOTES':
        issues.append("an EXECUTOR must have direction PROMOTES")
    if role == 'REGULATOR' and direction not in ('PROMOTES', 'PROTECTS'):
        issues.append("a REGULATOR must have direction PROMOTES or PROTECTS")
    if role == 'MARKER' and direction in ('PROMOTES', 'PROTECTS'):
        issues.append("a MARKER should not claim a causal direction")
    if mech == 'NO' and role in ('EXECUTOR', 'REGULATOR', 'MARKER'):
        issues.append("mechanistic NO should not carry a confident role")
    if mech == 'YES' and role == 'UNCERTAIN':
        issues.append("mechanistic YES should have a confident role")
    if mech == 'NO' and direction != 'UNCLEAR':
        issues.append("mechanistic NO should have direction UNCLEAR")
    EXEC_WORDS = ('execute', 'execution', 'pore', 'cleav', 'permeabil', 'caspase', 'kinase',
                 'directly exec', 'cytochrome', 'apoptosome', 'release', 'initiat')
    if role == 'REGULATOR' and any(w in mechanism for w in EXEC_WORDS):
        issues.append("mechanism indicates execution, so role should be EXECUTOR")
    if form and known_forms and mech == 'YES' and known_forms not in ('unknown', 'unclear', 'various', 'not sure'):
        if form.lower() not in known_forms:
            issues.append(f"gene is known for '{known_forms}', not '{form}' — mark NO/UNCERTAIN")
    VAGUE = ('unknown', 'unclear', 'various', 'not sure', 'multiple', 'cell death', 'general', 'rcd')
    if mech == 'YES':
        if not role_form or any(v in role_form for v in VAGUE):
            issues.append("state the SPECIFIC RCD form this role belongs to")
        elif form and form.lower() not in role_form:
            issues.append(f"role belongs to '{role_form}', not '{form}' — mark NO/UNCERTAIN")
    return {"status": "consistent"} if not issues else {"status": "inconsistent", "issues": issues}

def call_llm(messages, max_tokens=32000, timeout=900):
    for attempt in range(3):
        try:
            headers = {"Authorization": "Bearer " + DEEPSEEK_KEY, "Content-Type": "application/json"}
            body = {"model": "deepseek-v4-pro", "messages": messages,
                    "max_tokens": max_tokens, "thinking": {"type": "enabled"},
                    "reasoning_effort": "max", "tools": TOOLS}
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=timeout, context=CTX).read().decode('utf-8'))
            if 'error' in resp:
                time.sleep(15); continue
            return resp['choices'][0]['message']
        except Exception:
            if attempt == 2:
                return None
            time.sleep(10 * (attempt + 1))
    return None

def run_loop(prompt, form, max_rounds=6):
    messages = [{"role": "user", "content": prompt}]
    for _ in range(max_rounds):
        msg = call_llm(messages)
        if msg is None:
            return {}
        assistant = {"role": "assistant", "content": msg.get('content', '') or '',
                     "reasoning_content": msg.get('reasoning_content', '') or ''}
        tool_calls = msg.get('tool_calls')
        if tool_calls:
            assistant['tool_calls'] = tool_calls
        messages.append(assistant)
        if not tool_calls:
            return {}
        for tc in tool_calls:
            fn = tc['function']['name']
            try:
                args = json.loads(tc['function'].get('arguments') or '{}')
            except Exception:
                args = {}
            if fn == 'classify_gene_rcd':
                return args
            elif fn == 'verify_role':
                messages.append({"role": "tool", "tool_call_id": tc['id'],
                                 "content": json.dumps(check_rules(args, form))})
    return {}

def run_loop_voted(prompt, form, n=3):
    votes = [run_loop(prompt, form) for _ in range(n)]
    def maj(key):
        vals = [v.get(key, '') for v in votes if v.get(key)]
        return Counter(vals).most_common(1)[0][0] if vals else ''
    return {'role': maj('role'), 'direction': maj('direction'), 'mechanistic': maj('mechanistic')}

def prompt_loop(gene, form, evidence):
    return (f"Gene {gene}, regulated cell death form {form}.\n\n"
            f"Literature evidence from a search (titles + AI takeaways):\n{evidence}\n\n"
            f"DEFINITIONS: EXECUTOR = the gene DIRECTLY executes death (pore-forming, cleavage, permeabilization). "
            f"REGULATOR = the gene CONTROLS death (promotes or inhibits it) but does NOT execute it. "
            f"MARKER = associated but not causal. "
            f"Using the evidence above, classify the gene's relationship to this form. "
            f"In every tool call you MUST also state: (a) mechanism — the gene's molecular action, "
            f"(b) known_forms — which RCD form(s) the gene is primarily known for, and "
            f"(c) role_form — the SINGLE RCD form this gene's role belongs to. "
            f"A gene's role is FORM-SPECIFIC: if the role belongs to a DIFFERENT form, it is NOT involved in this form. "
            f"First call verify_role, then call classify_gene_rcd with your final answer. "
            f"Classify: mechanistic (YES/NO), role (EXECUTOR/REGULATOR/MARKER/UNCERTAIN), "
            f"direction (PROMOTES/PROTECTS/UNCLEAR), mechanism (string), known_forms (string), role_form (string).")

# ---- Consensus search ----
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

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def pct(n, d):
    return f"{n/d*100:.0f}%" if d else "n/a"

def main():
    if not CONSENSUS_KEY or not DEEPSEEK_KEY:
        print("ERROR: missing keys"); return

    results = []
    for gene, form, trole, tdir, tmech in GROUND_TRUTH:
        papers = consensus_search(f"{gene} {form} cell death")
        if papers is None:
            log(f"  {gene:7s} {form:12s} | CONSENSUS FAIL")
            results.append({'gene': gene, 'form': form, 'true_role': trole, 'true_dir': tdir, 'true_mech': tmech,
                            'pred_role': 'ERROR', 'pred_dir': '', 'pred_mech': ''})
            time.sleep(3); continue
        evidence = "\n".join(f"- {p.get('title','')}: {(p.get('takeaway') or '')[:180]}"
                             for p in papers[:5])
        v = run_loop_voted(prompt_loop(gene, form, evidence), form, n=3)
        results.append({'gene': gene, 'form': form, 'true_role': trole, 'true_dir': tdir, 'true_mech': tmech,
                        'pred_role': v.get('role',''), 'pred_dir': v.get('direction',''), 'pred_mech': v.get('mechanistic','')})
        log(f"  {gene:7s} {form:12s} true={trole:9s}/{tmech:3s} | pred={v.get('role','') or '-':9s}/{v.get('mechanistic','') or '-':3s}")
        time.sleep(2)

    # metrics (same as cot_benchmark)
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
    print("=" * 64)
    print(f"COMBINED BENCHMARK v6 (Consensus evidence -> v11 loop) — {len(results)} pairs")
    print("=" * 64)
    print(f"  role accuracy:         {role_acc}/{len(results)} ({pct(role_acc, len(results))})")
    print(f"  COMBINED accuracy:     {combined}/{len(results)} ({pct(combined, len(results))})")
    print(f"  EXECUTOR sensitivity:  {pct(sum(1 for r in exe_true if r['pred_role']=='EXECUTOR'), len(exe_true))}")
    print(f"  EXECUTOR precision:    {pct(sum(1 for r in exe_called if r['true_role']=='EXECUTOR'), len(exe_called))}")
    print(f"  REGULATOR sensitivity: {pct(sum(1 for r in reg_true if r['pred_role']=='REGULATOR'), len(reg_true))}")
    print(f"  REGULATOR precision:   {pct(sum(1 for r in reg_called if r['true_role']=='REGULATOR'), len(reg_called))}")
    print(f"  negative rejection:    {neg_rej}/{len(neg_true)} ({pct(neg_rej, len(neg_true))})")
    print(f"  FALSE POSITIVES:       {fp}/{len(neg_true)} ({pct(fp, len(neg_true))})")
    print(f"  direction accuracy:    {dir_acc}/{len(reg_true)} ({pct(dir_acc, len(reg_true))})")

    out = os.path.join(BASE, 'consensus_benchmark_v6_results.csv')
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader(); w.writerows(results)
    print(f"\nresults -> {out}")
    print("DONE.")

if __name__ == '__main__':
    main()
