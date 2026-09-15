"""
cot_benchmark_v6.py — v4 loop + coherence metric + A/B/C upgrades.

New vs v4:
  A. sharper prompt: explicit EXECUTOR vs REGULATOR definitions
  B. mechanism lookup: reference returns the gene's mechanism (not its role)
  C. rule "promotes/inhibits => REGULATOR" (uses the mechanism to catch over-calls)

Plus a COHERENCE rule in the metrics:
  - a negative is correctly rejected only if role == UNCERTAIN AND mechanistic == NO
  - a false positive = confident role (EXECUTOR/REGULATOR/MARKER) OR mechanistic == YES
  (so "REGULATOR + NO" is counted as a contradiction/hallucination, not a rejection)

Arms (same run): chat, reasoner, v4loop (voted + rules + mechanism lookup).

Run on Zima:
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  nohup python3 -u cot_benchmark_v6.py >> cot_benchmark_v6.log 2>&1 &
"""
import os, json, time, urllib.request, re, io, sys
from collections import Counter
from datetime import datetime

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(BASE_DIR, '..', 'output databases', 'Phase 2C output', 'cot_benchmark_v6_results.json')

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

# B: mechanism reference (gene -> form(s) + mechanism; NOT the role)
REFERENCE = {
    'BAX':    {'forms': ['Apoptosis'],    'mechanism': 'forms the mitochondrial outer-membrane pore (direct execution)'},
    'CASP3':  {'forms': ['Apoptosis'],    'mechanism': 'executioner caspase, cleaves substrates (direct execution)'},
    'CASP8':  {'forms': ['Apoptosis'],    'mechanism': 'initiator caspase, activates executioner caspases (direct execution)'},
    'CASP9':  {'forms': ['Apoptosis'],    'mechanism': 'initiator caspase, activates executioner caspases (direct execution)'},
    'CYCS':   {'forms': ['Apoptosis'],    'mechanism': 'directly executes apoptosis by initiating the caspase cascade (direct execution)'},
    'MLKL':   {'forms': ['Necroptosis'],  'mechanism': 'pore-forming executioner of necroptosis (direct execution)'},
    'RIPK3':  {'forms': ['Necroptosis'],  'mechanism': 'directly executes necroptosis by phosphorylating MLKL (direct execution)'},
    'GSDMD':  {'forms': ['Pyroptosis'],   'mechanism': 'pore-forming executioner of pyroptosis (direct execution)'},
    'GSDME':  {'forms': ['Pyroptosis'],   'mechanism': 'pore-forming executioner of pyroptosis (direct execution)'},
    'CASP1':  {'forms': ['Pyroptosis'],   'mechanism': 'cleaves gasdermin D to execute pyroptosis (direct execution)'},
    'BCL2':   {'forms': ['Apoptosis'],    'mechanism': 'anti-apoptotic; inhibits apoptosis (promotes survival)'},
    'BCL2L1': {'forms': ['Apoptosis'],    'mechanism': 'anti-apoptotic; inhibits apoptosis'},
    'XIAP':   {'forms': ['Apoptosis'],    'mechanism': 'inhibitor of apoptosis'},
    'TP53':   {'forms': ['Apoptosis'],    'mechanism': 'pro-apoptotic transcription factor; promotes apoptosis'},
    'GPX4':   {'forms': ['Ferroptosis'],  'mechanism': 'inhibits lipid peroxidation (inhibits ferroptosis)'},
    'ACSL4':  {'forms': ['Ferroptosis'],  'mechanism': 'catalyzes lipid peroxidation (promotes ferroptosis)'},
    'AIFM2':  {'forms': ['Ferroptosis'],  'mechanism': 'inhibits lipid peroxidation (inhibits ferroptosis)'},
    'BECN1':  {'forms': ['Autophagy'],    'mechanism': 'initiates autophagosome formation (promotes autophagy)'},
}

PROPS = {
    "mechanistic": {"type": "string", "enum": ["YES", "NO"]},
    "role": {"type": "string", "enum": ["EXECUTOR", "REGULATOR", "MARKER", "UNCERTAIN"]},
    "direction": {"type": "string", "enum": ["PROMOTES", "PROTECTS", "UNCLEAR"]},
}

TOOLS = [
    {"type": "function", "function": {
        "name": "lookup_known_forms",
        "description": "Look up the RCD form(s) and mechanism a gene is known for",
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

def check_rules(args, gene=None):
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
        issues.append("mechanistic NO should not carry a confident role (use UNCERTAIN)")
    if mech == 'YES' and role == 'UNCERTAIN':
        issues.append("mechanistic YES should have a confident role")
    if mech == 'NO' and direction != 'UNCLEAR':
        issues.append("mechanistic NO should have direction UNCLEAR")
    # C: mechanism-based rule — promote/inhibit => REGULATOR, not EXECUTOR
    if gene and gene in REFERENCE:
        note = REFERENCE[gene]['mechanism'].lower()
        if role == 'EXECUTOR' and ('promot' in note or 'inhibit' in note):
            issues.append(f"{gene}'s mechanism is '{REFERENCE[gene]['mechanism']}' (promotes/inhibits), so it is a REGULATOR, not an EXECUTOR")
        # D: executor-keyword enforcement — direct execution => EXECUTOR, not REGULATOR
        EXEC_KEYWORDS = ('direct execution', 'directly executes', 'pore-forming', 'cleaves', 'executioner', 'permeabil')
        if role == 'REGULATOR' and any(k in note for k in EXEC_KEYWORDS):
            issues.append(f"{gene}'s mechanism is '{REFERENCE[gene]['mechanism']}' (direct execution), so it is an EXECUTOR, not a REGULATOR")
    return {"status": "consistent"} if not issues else {"status": "inconsistent", "issues": issues}

def lookup_known_forms(gene):
    g = gene.upper()
    info = REFERENCE.get(g, {'forms': [], 'mechanism': ''})
    return {"gene": g, "known_forms": info['forms'], "mechanism": info['mechanism']}

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

def run_loop(prompt, gene, max_rounds=6):
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
                                 "content": json.dumps(check_rules(args, gene))})
            elif fn == 'lookup_known_forms':
                messages.append({"role": "tool", "tool_call_id": tc['id'],
                                 "content": json.dumps(lookup_known_forms(args.get('gene', '')))})
    return {}

def run_loop_voted(prompt, gene, n=3):
    votes = [run_loop(prompt, gene) for _ in range(n)]
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
    # A: sharper definitions
    return (f"Gene {gene}, regulated cell death form {form}. "
            f"DEFINITIONS: EXECUTOR = the gene DIRECTLY executes death (pore-forming, cleavage, permeabilization). "
            f"REGULATOR = the gene CONTROLS death (promotes or inhibits it) but does NOT execute it. "
            f"MARKER = associated but not causal. "
            f"First call lookup_known_forms to check {gene}'s known form(s) and mechanism, then call verify_role, "
            f"then call classify_gene_rcd with your final answer. Classify: mechanistic (YES/NO), role "
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
        v = run_loop_voted(prompt_loop(gene, form), gene, n=3)
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
        # COHERENCE rule: rejection = UNCERTAIN AND NO; false positive = confident role OR YES
        neg_rej = sum(1 for r in neg_true if r[arm]['role'] == 'UNCERTAIN' and r[arm]['mech'] == 'NO')
        fp = sum(1 for r in neg_true if r[arm]['role'] in ('EXECUTOR', 'REGULATOR', 'MARKER') or r[arm]['mech'] == 'YES')
        coherent = sum(1 for r in results if
                       (r[arm]['mech'] == 'NO' and r[arm]['role'] == 'UNCERTAIN') or
                       (r[arm]['mech'] == 'YES' and r[arm]['role'] in ('EXECUTOR', 'REGULATOR', 'MARKER')))
        return {
            'role_acc': sum(1 for r in results if r[arm]['role'] == r['true_role']),
            'exe_sens': sum(1 for r in exe_true if r[arm]['role'] == 'EXECUTOR'),
            'exe_prec': sum(1 for r in exe_called if r['true_role'] == 'EXECUTOR'),
            'reg_sens': sum(1 for r in reg_true if r[arm]['role'] == 'REGULATOR'),
            'reg_prec': sum(1 for r in reg_called if r['true_role'] == 'REGULATOR'),
            'neg_rej': neg_rej, 'fp': fp, 'coherent': coherent,
            'dir_acc': sum(1 for r in reg_true if r[arm]['dir'] == r['true_dir']),
        }, len(exe_true), len(reg_true), len(neg_true), len(exe_called), len(reg_called)

    log(f"\n=== BENCHMARK v6 (coherence + A/B/C/D) — {len(results)} pairs ===")
    for arm, name in [('chat','deepseek-chat'), ('reasoner','deepseek-reasoner'), ('v4loop','v4-pro loop (voted + rules + mechanism)')]:
        mm, ne, nr, nn, ec, rc = metrics(arm)
        log(f"\n--- {name} ---")
        log(f"  role accuracy:        {mm['role_acc']}/{len(results)} ({pct(mm['role_acc'], len(results))})")
        log(f"  EXECUTOR sensitivity: {mm['exe_sens']}/{ne} ({pct(mm['exe_sens'], ne)})")
        log(f"  EXECUTOR precision:   {mm['exe_prec']}/{ec} ({pct(mm['exe_prec'], ec)})")
        log(f"  REGULATOR sensitivity:{mm['reg_sens']}/{nr} ({pct(mm['reg_sens'], nr)})")
        log(f"  REGULATOR precision:  {mm['reg_prec']}/{rc} ({pct(mm['reg_prec'], rc)})")
        log(f"  coherent rejection:   {mm['neg_rej']}/{nn} ({pct(mm['neg_rej'], nn)})")
        log(f"  FALSE POSITIVES:      {mm['fp']}/{nn} ({pct(mm['fp'], nn)})")
        log(f"  role-mech coherence:  {mm['coherent']}/{len(results)} ({pct(mm['coherent'], len(results))})")
        log(f"  direction accuracy:   {mm['dir_acc']}/{nr} ({pct(mm['dir_acc'], nr)})")

    log(f"\nresults -> {OUT_FILE}")
    log("DONE.")

if __name__ == '__main__':
    main()
