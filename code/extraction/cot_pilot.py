"""
cot_pilot.py — chain-of-thought pilot on ~100 borderline gene-RCD pairs.

Compares deepseek-chat (baseline) vs deepseek-reasoner (chain-of-thought) on
the SAME regulatory-aware role/direction prompt, across three strata:
  40 UNCERTAIN-role pairs   (resolution test)
  30 EXECUTOR-role pairs    (inflation test)
  30 REGULATOR-role pairs   (control)

Outputs: cot_pilot_results.json (per-pair) + summary stats.

Run on Zima:
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  nohup python3 -u cot_pilot.py >> cot_pilot.log 2>&1 &
"""
import csv, os, json, time, urllib.request, re, io, sys, random
from datetime import datetime

csv.field_size_limit(sys.maxsize)
DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATRIX_FILE = os.path.join(BASE_DIR, '..', 'output databases', 'Phase 2C output', 'unified_gene_rcd_matrix_V021.csv')
OUT_FILE = os.path.join(BASE_DIR, '..', 'output databases', 'Phase 2C output', 'cot_pilot_results.json')

N_UNCERTAIN, N_EXECUTOR, N_REGULATOR = 40, 30, 30
random.seed(42)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def call_llm(prompt, model, json_mode=False, max_tokens=200):
    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
            body = {"model": model, "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens, "temperature": 0}
            if json_mode:
                body["response_format"] = {"type": "json_object"}
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=120).read().decode('utf-8'))
            return resp['choices'][0]['message']['content'].strip()
        except Exception:
            if attempt == 2:
                return None
            time.sleep(5 * (attempt + 1))

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

def main():
    if not DEEPSEEK_KEY:
        log("ERROR: DEEPSEEK_KEY not set"); return

    V = list(csv.DictReader(open(MATRIX_FILE, encoding='utf-8-sig')))
    unc = [r for r in V if r['rcd_gene_type'] == 'UNCERTAIN']
    exe = [r for r in V if r['rcd_gene_type'] == 'EXECUTOR']
    reg = [r for r in V if r['rcd_gene_type'] == 'REGULATOR']
    log(f"pool: UNCERTAIN={len(unc)} EXECUTOR={len(exe)} REGULATOR={len(reg)}")

    sample = (random.sample(unc, min(N_UNCERTAIN, len(unc))) +
              random.sample(exe, min(N_EXECUTOR, len(exe))) +
              random.sample(reg, min(N_REGULATOR, len(reg))))
    log(f"sample: {len(sample)} pairs")

    results = []
    for i, r in enumerate(sample, 1):
        gene, form = r['gene_symbol'], r['rcd_form_canonical']
        p = prompt(gene, form)
        chat_out = call_llm(p, 'deepseek-chat', json_mode=True)
        reasoner_out = call_llm(p, 'deepseek-reasoner', json_mode=False, max_tokens=8000)
        chat = safe_json(chat_out)
        rea = safe_json(reasoner_out)
        rec = {
            'gene': gene, 'form': form, 'matrix_role': r['rcd_gene_type'],
            'chat_role': chat.get('role', ''), 'chat_dir': chat.get('direction', ''),
            'reasoner_role': rea.get('role', ''), 'reasoner_dir': rea.get('direction', ''),
        }
        results.append(rec)
        if i % 10 == 0:
            log(f"  {i}/{len(sample)}")
        time.sleep(0.5)

    json.dump(results, open(OUT_FILE, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

    # summary
    from collections import Counter
    resolved = sum(1 for x in results if x['matrix_role'] == 'UNCERTAIN' and x['reasoner_role'] in ('EXECUTOR', 'REGULATOR', 'MARKER'))
    flips = sum(1 for x in results if x['matrix_role'] in ('EXECUTOR', 'REGULATOR') and x['reasoner_role'] in ('EXECUTOR', 'REGULATOR') and x['reasoner_role'] != x['matrix_role'])
    agree = sum(1 for x in results if x['chat_role'] == x['reasoner_role'])
    log(f"\n=== SUMMARY ===")
    log(f"pairs: {len(results)}")
    log(f"resolution rate (UNCERTAIN -> confident): {resolved}/{N_UNCERTAIN}")
    log(f"flip rate (EXECUTOR<->REGULATOR): {flips}/{N_EXECUTOR + N_REGULATOR}")
    log(f"chat-reasoner agreement: {agree}/{len(results)}")
    log(f"reasoner roles: {dict(Counter(x['reasoner_role'] for x in results))}")
    log(f"results -> {OUT_FILE}")
    log("DONE.")

if __name__ == '__main__':
    main()
