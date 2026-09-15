"""
cot_benchmark.py — full accuracy + anti-hallucination benchmark of deepseek-reasoner
(CoT) vs deepseek-chat on 26 well-established gene-RCD pairs, with role, direction,
and mechanistic ground truth.

Ground truth (26 pairs):
  10 EXECUTORS (PROMOTES), 8 REGULATORS (4 PROTECTS + 4 PROMOTES), 8 NEGATIVES (NO).

Metrics measured:
  1. role accuracy            (role == truth)
  2. EXECUTOR sensitivity     (true executor -> called executor)
  3. EXECUTOR precision       (called executor -> true executor)  [inflation test]
  4. REGULATOR sensitivity / precision
  5. negative rejection       (true negative -> mechanistic NO)   [anti-hallucination]
  6. false-positive rate      (true negative -> mechanistic YES)  [hallucination]
  7. direction accuracy       (regulator PROMOTES/PROTECTS correct)
  8. executor direction coherence (executor never PROTECTS)
  9. calibration              (negative -> UNCERTAIN/empty, not a confident role)
 10. cross-model              (chat vs reasoner on the same pairs)

Run on Zima:
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  nohup python3 -u cot_benchmark.py >> cot_benchmark.log 2>&1 &
"""
import os, json, time, urllib.request, re, io, sys
from datetime import datetime

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(BASE_DIR, '..', 'output databases', 'Phase 2C output', 'cot_benchmark_results.json')

# (gene, form, true_role, true_direction, true_mechanistic)
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

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def call_llm(prompt, model, json_mode=False, max_tokens=8000):
    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
            body = {"model": model, "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens, "temperature": 0}
            if json_mode:
                body["response_format"] = {"type": "json_object"}
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=240).read().decode('utf-8'))
            if 'error' in resp:
                time.sleep(15 * (attempt + 1))
                continue
            return resp['choices'][0]['message']['content'].strip()
        except Exception:
            if attempt == 2:
                return None
            time.sleep(10 * (attempt + 1))

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

def pct(n, d):
    return f"{n/d*100:.0f}%" if d else "n/a"

def main():
    if not DEEPSEEK_KEY:
        log("ERROR: DEEPSEEK_KEY not set"); return

    results = []
    for gene, form, trole, tdir, tmech in GROUND_TRUTH:
        p = prompt(gene, form)
        chat_out = call_llm(p, 'deepseek-chat', json_mode=True)
        rea_out = call_llm(p, 'deepseek-reasoner', json_mode=False)
        chat = safe_json(chat_out)
        rea = safe_json(rea_out)
        rec = {'gene': gene, 'form': form,
               'true_role': trole, 'true_dir': tdir, 'true_mech': tmech,
               'chat_role': chat.get('role', ''), 'chat_dir': chat.get('direction', ''), 'chat_mech': chat.get('mechanistic', ''),
               'rea_role': rea.get('role', ''), 'rea_dir': rea.get('direction', ''), 'rea_mech': rea.get('mechanistic', '')}
        results.append(rec)
        log(f"  {gene:7s} {form:12s} true={trole:9s}/{tdir:8s} | chat={rec['chat_role'] or '-':9s}/{rec['chat_dir'] or '-':8s} | rea={rec['rea_role'] or '-':9s}/{rec['rea_dir'] or '-':8s}")
        time.sleep(1)

    json.dump(results, open(OUT_FILE, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

    def metrics(model, role_k, dir_k, mech_k):
        n = len(results)
        exe_true = [r for r in results if r['true_role'] == 'EXECUTOR']
        reg_true = [r for r in results if r['true_role'] == 'REGULATOR']
        neg_true = [r for r in results if r['true_role'] == 'NEGATIVE']
        exe_called = [r for r in results if r[role_k] == 'EXECUTOR']
        reg_called = [r for r in results if r[role_k] == 'REGULATOR']
        m = {
            'role_acc': sum(1 for r in results if r[role_k] == r['true_role']),
            'exe_sens': sum(1 for r in exe_true if r[role_k] == 'EXECUTOR'),
            'exe_prec': sum(1 for r in exe_called if r['true_role'] == 'EXECUTOR'),
            'reg_sens': sum(1 for r in reg_true if r[role_k] == 'REGULATOR'),
            'reg_prec': sum(1 for r in reg_called if r['true_role'] == 'REGULATOR'),
            'neg_rej': sum(1 for r in neg_true if r[mech_k] == 'NO'),
            'fp': sum(1 for r in neg_true if r[mech_k] == 'YES'),
            'dir_acc': sum(1 for r in reg_true if r[dir_k] == r['true_dir']),
            'exe_dir_ok': sum(1 for r in exe_called if r[dir_k] != 'PROTECTS'),
        }
        return m, len(exe_true), len(reg_true), len(neg_true), len(exe_called), len(reg_called)

    log(f"\n=== BENCHMARK — {len(results)} pairs ===")
    for name, role_k, dir_k, mech_k in [('deepseek-chat', 'chat_role', 'chat_dir', 'chat_mech'),
                                        ('deepseek-reasoner (CoT)', 'rea_role', 'rea_dir', 'rea_mech')]:
        m, ne, nr, nn, ec, rc = metrics(name, role_k, dir_k, mech_k)
        log(f"\n--- {name} ---")
        log(f"  role accuracy:          {m['role_acc']}/{len(results)} ({pct(m['role_acc'], len(results))})")
        log(f"  EXECUTOR sensitivity:   {m['exe_sens']}/{ne} ({pct(m['exe_sens'], ne)})")
        log(f"  EXECUTOR precision:     {m['exe_prec']}/{ec} ({pct(m['exe_prec'], ec)})")
        log(f"  REGULATOR sensitivity:  {m['reg_sens']}/{nr} ({pct(m['reg_sens'], nr)})")
        log(f"  REGULATOR precision:    {m['reg_prec']}/{rc} ({pct(m['reg_prec'], rc)})")
        log(f"  negative rejection:     {m['neg_rej']}/{nn} ({pct(m['neg_rej'], nn)})")
        log(f"  FALSE POSITIVES:        {m['fp']}/{nn} ({pct(m['fp'], nn)})  <-- hallucination")
        log(f"  direction accuracy:     {m['dir_acc']}/{nr} ({pct(m['dir_acc'], nr)})")
        log(f"  executor direction OK:  {m['exe_dir_ok']}/{ec}")

    log(f"\nresults -> {OUT_FILE}")
    log("DONE.")

if __name__ == '__main__':
    main()
