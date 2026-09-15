"""
cot_benchmark_v4.py — 3-arm benchmark with the FULLY UPGRADED tool-call loop.

v4 loop = v3 loop + three upgrades:
  B. self-consistency (3 loop runs per pair, majority vote)
  C. richer rule-check (executor/regulator/marker/direction logic)
  D. reference-lookup tool (lookup_known_forms -> the gene's known RCD forms)

Arms (all in the SAME run):
  chat       (deepseek-chat, plain JSON)
  reasoner   (deepseek-reasoner, plain JSON)
  v4loop     (deepseek-v4-pro + tools + loop + upgrades)

Run on Zima:
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  nohup python3 -u cot_benchmark_v4.py >> cot_benchmark_v4.log 2>&1 &
"""
import os, json, time, urllib.request, re, io, sys
from collections import Counter
from datetime import datetime

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(BASE_DIR, '..', 'output databases', 'Phase 2C output', 'cot_benchmark_v4_results.json')

GROUND_TRUTH = [
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
    ("GPX4", "Pyroptosis", "NEGATIVE", "UNCLEAR", "NO"),
    ("MLKL", "Ferroptosis", "NEGATIVE", "UNCLEAR", "NO"),
    ("CASP3", "Necroptosis", "NEGATIVE", "UNCLEAR", "NO"),
    ("BAX", "Necroptosis", "NEGATIVE", "UNCLEAR", "NO"),
    ("GSDMD", "Ferroptosis", "NEGATIVE", "UNCLEAR", "NO"),
    ("CASP1", "Apoptosis", "NEGATIVE", "UNCLEAR", "NO"),
    ("MLKL", "Apoptosis", "NEGATIVE", "UNCLEAR", "NO"),
    ("GSDMD", "Necroptosis", "NEGATIVE", "UNCLEAR", "NO"),
]

# Reference: gene -> known RCD form(s) (general knowledge, not the benchmark answer)
REFERENCE = {
    'BAX': ['Apoptosis'], 'CASP3': ['Apoptosis'], 'CASP8': ['Apoptosis'],
    'CASP9': ['Apoptosis'], 'CYCS': ['Apoptosis'], 'MLKL': ['Necroptosis'],
    'RIPK3': ['Necroptosis'], 'GSDMD': ['Pyroptosis'], 'GSDME': ['Pyroptosis'],
    'CASP1': ['Pyroptosis'], 'BCL2': ['Apoptosis'], 'BCL2L1': ['Apoptosis'],
    'XIAP': ['Apoptosis'], 'TP53': ['Apoptosis'], 'GPX4': ['Ferroptosis'],
    'ACSL4': ['Ferroptosis'], 'AIFM2': ['Ferroptosis'], 'BECN1': ['Autophagy'],
}

PROPS = {
    "mechanistic": {"type": "string", "enum": ["YES", "NO"]},
    "role": {"type": "string", "enum": ["EXECUTOR", "REGULATOR", "MARKER", "UNCERTAIN"]},
    "direction": {"type": "string", "enum": ["PROMOTES", "PROTECTS", "UNCLEAR"]},
}

TOOLS = [
    {"type": "function", "function": {
        "name": "lookup_known_forms",
        "description": "Look up the RCD form(s) a gene is known for",
        "parameters": {"type": "object", "properties": {"gene": {"type": "string"}},
                       "required": ["gene"]}}},
    {"type": "function", "function": {
        "name": "verify_role",
        "description": "Check a preliminary classification against the governance rules",
        "parameters": {"type": "object", "properties": PROPS, "required": ["mechanistic", "role", "direction"]}}},
    {"type": "function", "function": {
        "name": "classify_gene_rcd",
        "description": "Submit the final classification",
        "parameters": {"type": "object", "properties": PROPS, "required": ["mechanistic", "role", "direction"]}}},
]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def check_rules(args):
    role = (args.get('role') or '').upper()
    mech = (args.get('mechanistic') or '').upper()
    direction = (args.get('direction') or '').upper()
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
    return {"status": "consistent"} if not issues else {"status": "inconsistent", "issues": issues}

def lookup_known_forms(gene):
    g = gene.upper()
    forms = REFERENCE.get(g, [])
    return {"gene": g, "known_forms": forms,
            "note": f"{g} is known for {forms} in curated references" if forms else f"{g} not in the reference"}

def call_llm(messages, max_tokens=32000, timeout=900):
    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
            body = {"model": "deepseek-v4-pro", "messages": messages,
                    "max_tokens": max_tokens, "thinking": {"type": "enabled"},
                    "reasoning_effort": "max", "tools": TOOLS}
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8'))
            if 'error' in resp:
                log(f"  API error: {str(resp['error'].get('message',''))[:100]}")
                time.sleep(15 * (attempt + 1))
                continue
            return resp['choices'][0]['message']
        except Exception:
            if attempt == 2:
                return None
            time.sleep(10 * (attempt + 1))
    return None

def run_loop(prompt, max_rounds=5):
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
                                 "content": json.dumps(check_rules(args))})
            elif fn == 'lookup_known_forms':
                messages.append({"role": "tool", "tool_call_id": tc['id'],
                                 "content": json.dumps(lookup_known_forms(args.get('gene', '')))})
    return {}

def run_loop_voted(prompt, n=3):
    """Self-consistency: n independent loops, majority vote per field."""
    votes = [run_loop(prompt) for _ in range(n)]
    def maj(key):
        vals = [v.get(key, '') for v in votes if v.get(key)]
        return Counter(vals).most_common(1)[0][0] if vals else ''
    return {'role': maj('role'), 'direction': maj('direction'), 'mechanistic': maj('mechanistic')}

def safe_json(s):
    if not s:
        return {}
    s = re.sub(r'^```(json)?\s*', '', s.strip())
    s = re.sub(r'\s*```$', '', s)
    if '{' in s and '}' in s:
        s = s[s.find('{'):s.rfind('}') + 1]
    try:
        return json.loads(s)
    except Exception:
        return {}

def call_llm_simple(prompt, model, json_mode=False, max_tokens=8000):
    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
            body = {"model": model, "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens}
            if json_mode:
                body["response_format"] = {"type": "json_object"}
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=120).read().decode('utf-8'))
            if 'error' in resp:
                time.sleep(10 * (attempt + 1))
                continue
            return resp['choices'][0]['message']['content'].strip()
        except Exception:
            if attempt == 2:
                return None
            time.sleep(8 * (attempt + 1))
    return None

def prompt_plain(gene, form):
    return (f"Gene {gene}, regulated cell death form {form}. Using ONLY your internal knowledge, classify the gene's "
            f"relationship to this cell death form. Output ONLY a JSON object with these keys: "
            f'"mechanistic" ("YES"/"NO"), "role" ("EXECUTOR"/"REGULATOR"/"MARKER"/"UNCERTAIN"), '
            f'"direction" ("PROMOTES"/"PROTECTS"/"UNCLEAR"). JSON:')

def prompt_loop(gene, form):
    return (f"Gene {gene}, regulated cell death form {form}. First call lookup_known_forms to check which forms "
            f"{gene} is known for, then call verify_role to check your preliminary classification, then call "
            f"classify_gene_rcd with your final answer. Classify: mechanistic (YES/NO), role "
            f"(EXECUTOR/REGULATOR/MARKER/UNCERTAIN), direction (PROMOTES/PROTECTS/UNCLEAR).")

def pct(n, d):
    return f"{n/d*100:.0f}%" if d else "n/a"

def main():
    if not DEEPSEEK_KEY:
        log("ERROR: DEEPSEEK_KEY not set"); return

    results = []
    for gene, form, trole, tdir, tmech in GROUND_TRUTH:
        c = call_llm_simple(prompt_plain(gene, form), 'deepseek-chat', json_mode=True)
        cj = safe_json(c) if c else {}
        r = call_llm_simple(prompt_plain(gene, form), 'deepseek-reasoner')
        rj = safe_json(r) if r else {}
        v = run_loop_voted(prompt_loop(gene, form), n=3)
        rec = {'gene': gene, 'form': form, 'true_role': trole, 'true_dir': tdir, 'true_mech': tmech,
               'chat': {'role': cj.get('role',''), 'dir': cj.get('direction',''), 'mech': cj.get('mechanistic','')},
               'reasoner': {'role': rj.get('role',''), 'dir': rj.get('direction',''), 'mech': rj.get('mechanistic','')},
               'v4loop': {'role': v.get('role',''), 'dir': v.get('direction',''), 'mech': v.get('mechanistic','')}}
        results.append(rec)
        log(f"  {gene:7s} {form:12s} true={trole:9s} | chat={rec['chat']['role'] or '-':9s} | "
            f"rea={rec['reasoner']['role'] or '-':9s} | v4loop={rec['v4loop']['role'] or '-':9s}")
        time.sleep(2)

    json.dump(results, open(OUT_FILE, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

    def metrics(arm):
        exe_true = [r for r in results if r['true_role'] == 'EXECUTOR']
        reg_true = [r for r in results if r['true_role'] == 'REGULATOR']
        neg_true = [r for r in results if r['true_role'] == 'NEGATIVE']
        exe_called = [r for r in results if r[arm]['role'] == 'EXECUTOR']
        reg_called = [r for r in results if r[arm]['role'] == 'REGULATOR']
        return {
            'role_acc': sum(1 for r in results if r[arm]['role'] == r['true_role']),
            'exe_sens': sum(1 for r in exe_true if r[arm]['role'] == 'EXECUTOR'),
            'exe_prec': sum(1 for r in exe_called if r['true_role'] == 'EXECUTOR'),
            'reg_sens': sum(1 for r in reg_true if r[arm]['role'] == 'REGULATOR'),
            'reg_prec': sum(1 for r in reg_called if r['true_role'] == 'REGULATOR'),
            'neg_rej': sum(1 for r in neg_true if r[arm]['mech'] == 'NO'),
            'fp': sum(1 for r in neg_true if r[arm]['mech'] == 'YES'),
            'dir_acc': sum(1 for r in reg_true if r[arm]['dir'] == r['true_dir']),
        }, len(exe_true), len(reg_true), len(neg_true), len(exe_called), len(reg_called)

    log(f"\n=== BENCHMARK v4 (3 arms + upgraded loop) — {len(results)} pairs ===")
    for arm, name in [('chat','deepseek-chat'), ('reasoner','deepseek-reasoner'), ('v4loop','v4-pro loop (voted + rules + lookup)')]:
        mm, ne, nr, nn, ec, rc = metrics(arm)
        log(f"\n--- {name} ---")
        log(f"  role accuracy:        {mm['role_acc']}/{len(results)} ({pct(mm['role_acc'], len(results))})")
        log(f"  EXECUTOR sensitivity: {mm['exe_sens']}/{ne} ({pct(mm['exe_sens'], ne)})")
        log(f"  EXECUTOR precision:   {mm['exe_prec']}/{ec} ({pct(mm['exe_prec'], ec)})")
        log(f"  REGULATOR sensitivity:{mm['reg_sens']}/{nr} ({pct(mm['reg_sens'], nr)})")
        log(f"  REGULATOR precision:  {mm['reg_prec']}/{rc} ({pct(mm['reg_prec'], rc)})")
        log(f"  negative rejection:   {mm['neg_rej']}/{nn} ({pct(mm['neg_rej'], nn)})")
        log(f"  FALSE POSITIVES:      {mm['fp']}/{nn} ({pct(mm['fp'], nn)})")
        log(f"  direction accuracy:   {mm['dir_acc']}/{nr} ({pct(mm['dir_acc'], nr)})")

    log(f"\nresults -> {OUT_FILE}")
    log("DONE.")

if __name__ == '__main__':
    main()
