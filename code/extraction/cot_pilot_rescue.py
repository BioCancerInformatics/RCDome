"""
cot_pilot_rescue.py — re-run the reasoner on the pairs where it returned an empty
role (the max_tokens=2000 issue, now fixed to 8000).

Reads cot_pilot_results.json, re-runs deepseek-reasoner (max_tokens=8000) on the
entries with empty reasoner_role, and updates the file in place.

Run on Zima:
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  nohup python3 -u cot_pilot_rescue.py >> cot_pilot_rescue.log 2>&1 &
"""
import os, json, time, urllib.request, re, io, sys
from datetime import datetime

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FILE = os.path.join(BASE_DIR, '..', 'output databases', 'Phase 2C output', 'cot_pilot_results.json')

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def call_llm(prompt, model, max_tokens=8000):
    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
            body = {"model": model, "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens, "temperature": 0}
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=180).read().decode('utf-8'))
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

    results = json.load(open(RESULTS_FILE, encoding='utf-8'))
    empty = [x for x in results if not x.get('reasoner_role')]
    log(f"empty reasoner results: {len(empty)}")

    fixed = 0
    for x in empty:
        p = prompt(x['gene'], x['form'])
        out = call_llm(p, 'deepseek-reasoner', max_tokens=8000)
        j = safe_json(out)
        x['reasoner_role'] = j.get('role', '')
        x['reasoner_dir'] = j.get('direction', '')
        if x['reasoner_role']:
            fixed += 1
        log(f"  {x['gene']} {x['form']}: matrix={x['matrix_role']} -> reasoner={x['reasoner_role']} ({x['reasoner_dir']})")
        time.sleep(0.5)

    json.dump(results, open(RESULTS_FILE, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    log(f"fixed: {fixed}/{len(empty)}")
    log("DONE.")

if __name__ == '__main__':
    main()
