"""
cot_benchmark_v2.py — 4-way model comparison using DeepSeek thinking mode +
function calling (per the DeepSeek docs).

Arms:
  1. deepseek-chat            baseline (JSON mode)
  2. deepseek-reasoner        old CoT (plain text)
  3. deepseek-v4-pro  thinking + tools, effort=high
  4. deepseek-v4-pro  thinking + tools, effort=max

The v4-pro arms use function calling (strict enum schema) + thinking mode, and
save reasoning_content for inspection. Silence-error handling: retry + backoff,
never crashes on API errors.

Run on Zima:
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  nohup python3 -u cot_benchmark_v2.py >> cot_benchmark_v2.log 2>&1 &
"""
import os, json, time, urllib.request, re, io, sys
from datetime import datetime

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(BASE_DIR, '..', 'output databases', 'Phase 2C output', 'cot_benchmark_v2_results.json')

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

TOOLS = [{
    "type": "function",
    "function": {
        "name": "classify_gene_rcd",
        "description": "Classify a gene's relationship to a regulated cell death form",
        "parameters": {
            "type": "object",
            "properties": {
                "mechanistic": {"type": "string", "enum": ["YES", "NO"]},
                "role": {"type": "string", "enum": ["EXECUTOR", "REGULATOR", "MARKER", "UNCERTAIN"]},
                "direction": {"type": "string", "enum": ["PROMOTES", "PROTECTS", "UNCLEAR"]},
            },
            "required": ["mechanistic", "role", "direction"],
        },
    },
}]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def call_llm(prompt, model, json_mode=False, thinking=False, effort=None, max_tokens=16000):
    """Silence-error call: 3 retries with backoff; returns dict with content/reasoning or None."""
    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
            body = {"model": model, "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens}
            if json_mode:
                body["response_format"] = {"type": "json_object"}
            if thinking:
                body["thinking"] = {"type": "enabled"}
                if effort:
                    body["reasoning_effort"] = effort
                body["tools"] = TOOLS
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=900).read().decode('utf-8'))
            if 'error' in resp:
                log(f"  API error: {str(resp['error'].get('message',''))[:100]}")
                time.sleep(15 * (attempt + 1))
                continue
            msg = resp['choices'][0]['message']
            return {'content': msg.get('content', '') or '',
                    'reasoning': msg.get('reasoning_content', '') or '',
                    'tool_calls': msg.get('tool_calls')}
        except Exception:
            if attempt == 2:
                return None
            time.sleep(10 * (attempt + 1))
    return None

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

def prompt(gene, form):
    return (f"Gene {gene}, regulated cell death form {form}. Using ONLY your internal knowledge, classify the gene's "
            f"relationship to this cell death form. Output ONLY a JSON object with these keys: "
            f'"mechanistic" ("YES"/"NO"), "role" ("EXECUTOR"/"REGULATOR"/"MARKER"/"UNCERTAIN"), '
            f'"direction" ("PROMOTES"/"PROTECTS"/"UNCLEAR"). JSON:')

def parse_tool_result(msg):
    """Extract classification from a v4-pro tool call (guaranteed JSON)."""
    if not msg:
        return {}
    tc = msg.get('tool_calls')
    if tc and tc[0].get('function', {}).get('arguments'):
        try:
            return json.loads(tc[0]['function']['arguments'])
        except Exception:
            return {}
    return {}

def pct(n, d):
    return f"{n/d*100:.0f}%" if d else "n/a"

def main():
    if not DEEPSEEK_KEY:
        log("ERROR: DEEPSEEK_KEY not set"); return

    results = []
    for gene, form, trole, tdir, tmech in GROUND_TRUTH:
        p = prompt(gene, form)
        rec = {'gene': gene, 'form': form, 'true_role': trole, 'true_dir': tdir, 'true_mech': tmech}

        # arm 1: chat (JSON mode)
        c = call_llm(p, 'deepseek-chat', json_mode=True)
        cj = safe_json(c['content']) if c else {}
        rec['chat'] = {'role': cj.get('role',''), 'dir': cj.get('direction',''), 'mech': cj.get('mechanistic','')}

        # arm 2: reasoner (old CoT)
        r = call_llm(p, 'deepseek-reasoner')
        rj = safe_json(r['content']) if r else {}
        rec['reasoner'] = {'role': rj.get('role',''), 'dir': rj.get('direction',''), 'mech': rj.get('mechanistic','')}

        # arm 3: v4-pro high
        h = call_llm(p, 'deepseek-v4-pro', thinking=True, effort='high', max_tokens=16000)
        hj = parse_tool_result(h)
        rec['v4pro_high'] = {'role': hj.get('role',''), 'dir': hj.get('direction',''), 'mech': hj.get('mechanistic',''),
                             'reasoning': (h or {}).get('reasoning','')[:300]}

        # arm 4: v4-pro max
        m = call_llm(p, 'deepseek-v4-pro', thinking=True, effort='max', max_tokens=32000)
        mj = parse_tool_result(m)
        rec['v4pro_max'] = {'role': mj.get('role',''), 'dir': mj.get('direction',''), 'mech': mj.get('mechanistic',''),
                            'reasoning': (m or {}).get('reasoning','')[:300]}

        results.append(rec)
        log(f"  {gene:7s} {form:12s} true={trole:9s} | chat={rec['chat']['role'] or '-':9s} | "
            f"rea={rec['reasoner']['role'] or '-':9s} | v4high={rec['v4pro_high']['role'] or '-':9s} | "
            f"v4max={rec['v4pro_max']['role'] or '-':9s}")
        time.sleep(1)

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

    log(f"\n=== BENCHMARK v2 — {len(results)} pairs, 4 arms ===")
    for arm, name in [('chat','deepseek-chat'), ('reasoner','deepseek-reasoner'),
                      ('v4pro_high','deepseek-v4-pro effort=high'), ('v4pro_max','deepseek-v4-pro effort=max')]:
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
