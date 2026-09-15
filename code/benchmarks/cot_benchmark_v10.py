"""
cot_benchmark_v10.py — v9 + role_form specificity gate (rule 9).

The 2 residual false positives (GPX4/Pyroptosis, MLKL/Apoptosis) come from
form-over-generalization. v10 adds a SELF-PROVIDED "role_form" field
(the single RCD form this gene's role belongs to) and rule 9:
  if role_form != asked_form and mechanistic == YES -> flag NO/UNCERTAIN.

Still fully agnostic (no external reference, no matrix reference).

Run on Zima:
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  nohup python3 -u cot_benchmark_v10.py >> cot_benchmark_v10.log 2>&1 &
"""
import os, json, time, urllib.request, re, io, sys
from collections import Counter
from datetime import datetime

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(BASE_DIR, '..', 'output databases', 'Phase 2C output', 'cot_benchmark_v10_results.json')

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
    {"type": "function", "function": {
        "name": "verify_role",
        "description": "Check a preliminary classification against the governance rules",
        "parameters": {"type": "object", "properties": PROPS, "required": REQUIRED}}},
    {"type": "function", "function": {
        "name": "classify_gene_rcd",
        "description": "Submit the final classification",
        "parameters": {"type": "object", "properties": PROPS, "required": REQUIRED}}},
]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def check_rules(args, form=None):
    role = (args.get('role') or '').upper()
    mech = (args.get('mechanistic') or '').upper()
    direction = (args.get('direction') or '').upper()
    mechanism = (args.get('mechanism') or '').lower()
    known_forms = (args.get('known_forms') or '').lower()
    role_form = (args.get('role_form') or '').lower()
    issues = []
    # 1-6 logic rules
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
    # 7. executor-keyword (self-provided mechanism)
    EXEC_WORDS = ('execute', 'execution', 'pore', 'cleav', 'permeabil', 'caspase', 'kinase', 'directly exec')
    if role == 'REGULATOR' and any(w in mechanism for w in EXEC_WORDS):
        issues.append("your stated mechanism indicates execution, so the role should be EXECUTOR")
    # 8. form-mismatch (self-provided known_forms)
    if form and known_forms and mech == 'YES' and known_forms not in ('unknown', 'unclear', 'various', 'not sure'):
        if form.lower() not in known_forms:
            issues.append(f"you stated the gene is known for '{known_forms}', not '{form}' — mark NO/UNCERTAIN")
    # 9. role-form specificity (self-provided role_form)
    VAGUE = ('unknown', 'unclear', 'various', 'not sure', 'multiple', 'cell death', 'general', 'rcd')
    if mech == 'YES':
        if not role_form or any(v in role_form for v in VAGUE):
            issues.append("state the SPECIFIC RCD form this role belongs to")
        elif form and form.lower() not in role_form:
            issues.append(f"this gene's role belongs to '{role_form}', not '{form}' — mark NO/UNCERTAIN")
    return {"status": "consistent"} if not issues else {"status": "inconsistent", "issues": issues}

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
    return (f"Gene {gene}, regulated cell death form {form}. "
            f"DEFINITIONS: EXECUTOR = the gene DIRECTLY executes death (pore-forming, cleavage, permeabilization). "
            f"REGULATOR = the gene CONTROLS death (promotes or inhibits it) but does NOT execute it. "
            f"MARKER = associated but not causal. "
            f"In every tool call you MUST also state: (a) mechanism — the gene's molecular action, "
            f"(b) known_forms — which RCD form(s) the gene is primarily known for, and "
            f"(c) role_form — the SINGLE RCD form this gene's role belongs to. "
            f"A gene's role is FORM-SPECIFIC: if the role belongs to a DIFFERENT form, it is NOT involved in this form. "
            f"First call verify_role, then call classify_gene_rcd with your final answer. "
            f"Classify: mechanistic (YES/NO), role (EXECUTOR/REGULATOR/MARKER/UNCERTAIN), "
            f"direction (PROMOTES/PROTECTS/UNCLEAR), mechanism (string), known_forms (string), role_form (string).")

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
        v = run_loop_voted(prompt_loop(gene, form), form, n=3)
        rec = {'gene': gene, 'form': form, 'true_role': trole, 'true_dir': tdir, 'true_mech': tmech,
               'chat': {'role': cj.get('role',''), 'dir': cj.get('direction',''), 'mech': cj.get('mechanistic','')},
               'reasoner': {'role': rj.get('role',''), 'dir': rj.get('direction',''), 'mech': rj.get('mechanistic','')},
               'self': {'role': v.get('role',''), 'dir': v.get('direction',''), 'mech': v.get('mechanistic','')}}
        results.append(rec)
        log(f"  {gene:7s} {form:12s} true={trole:9s} | chat={rec['chat']['role'] or '-':9s} | "
            f"rea={rec['reasoner']['role'] or '-':9s} | self={rec['self']['role'] or '-':9s}")
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
            'combined': sum(1 for r in results if (r['true_role'] in ('EXECUTOR','REGULATOR') and r[arm]['role'] == r['true_role']) or (r['true_role'] == 'NEGATIVE' and r[arm]['role'] == 'UNCERTAIN' and r[arm]['mech'] == 'NO')),
            'exe_sens': sum(1 for r in exe_true if r[arm]['role'] == 'EXECUTOR'),
            'exe_prec': sum(1 for r in exe_called if r['true_role'] == 'EXECUTOR'),
            'reg_sens': sum(1 for r in reg_true if r[arm]['role'] == 'REGULATOR'),
            'reg_prec': sum(1 for r in reg_called if r['true_role'] == 'REGULATOR'),
            'neg_rej': sum(1 for r in neg_true if r[arm]['role'] == 'UNCERTAIN' and r[arm]['mech'] == 'NO'),
            'fp': sum(1 for r in neg_true if r[arm]['role'] in ('EXECUTOR', 'REGULATOR', 'MARKER') or r[arm]['mech'] == 'YES'),
            'coherent': sum(1 for r in results if (r[arm]['mech'] == 'NO' and r[arm]['role'] == 'UNCERTAIN') or (r[arm]['mech'] == 'YES' and r[arm]['role'] in ('EXECUTOR','REGULATOR','MARKER'))),
            'dir_acc': sum(1 for r in reg_true if r[arm]['dir'] == r['true_dir']),
        }, len(exe_true), len(reg_true), len(neg_true), len(exe_called), len(reg_called)

    log(f"\n=== BENCHMARK v10 (role_form gate) — {len(results)} pairs ===")
    for arm, name in [('chat','deepseek-chat'), ('reasoner','deepseek-reasoner'), ('self','self-provided loop (v10)')]:
        mm, ne, nr, nn, ec, rc = metrics(arm)
        log(f"\n--- {name} ---")
        log(f"  role accuracy:        {mm['role_acc']}/{len(results)} ({pct(mm['role_acc'], len(results))})")
        log(f"  COMBINED accuracy:    {mm['combined']}/{len(results)} ({pct(mm['combined'], len(results))})")
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
