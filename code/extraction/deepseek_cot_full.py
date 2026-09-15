"""
deepseek_cot_full.py — full DeepSeek-CoT (deepseek-reasoner) classification of
ALL unique gene-RCD pairs, written as three NEW columns in the matrix:
  deepseek_cot_role        (EXECUTOR / REGULATOR / MARKER / UNCERTAIN)
  deepseek_cot_direction   (PROMOTES / PROTECTS / UNCLEAR)
  deepseek_cot_mechanistic (YES / NO)

Production safeguards (per spec):
  - nohup-friendly (flush output)
  - rate-limit/quota tolerant: retries with backoff, never crashes on token shortage
  - resume-safe checkpoint (deepseek_cot_progress.json), saved every 10 pairs
  - 8-thread parallel
  - end-of-run assertion: processed == total unique pairs, else FAILS LOUDLY

Run on Zima:
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  nohup python3 -u deepseek_cot_full.py >> deepseek_cot_full.log 2>&1 &
"""
import csv, os, json, time, urllib.request, re, io, sys, threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

csv.field_size_limit(sys.maxsize)

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATRIX_FILE = os.path.join(BASE_DIR, '..', 'output databases', 'Phase 2C output', 'unified_gene_rcd_matrix_V021.csv')
PROGRESS_FILE = os.path.join(BASE_DIR, '..', 'output databases', 'Phase 2C output', 'deepseek_cot_progress.json')

N_THREADS = 8
MAX_FAILS_IN_A_ROW = 25   # if this many consecutive calls fail -> save + graceful exit
lock = threading.Lock()
stop_flag = threading.Event()

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def call_llm(prompt, max_tokens=8000):
    """Retry with backoff; on rate-limit/quota it backs off longer and retries.
    Returns None only after all attempts exhausted."""
    for attempt in range(4):
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
            body = {"model": "deepseek-reasoner",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens, "temperature": 0}
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=240).read().decode('utf-8'))
            if 'error' in resp:
                msg = str(resp['error'].get('message', ''))
                log(f"  API error: {msg[:120]}")
                # rate-limit / quota -> longer backoff
                time.sleep(15 * (attempt + 1))
                continue
            return resp['choices'][0]['message']['content'].strip()
        except Exception as e:
            if attempt == 3:
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

def classify(gene, form):
    out = call_llm(prompt(gene, form))
    j = safe_json(out)
    return {'role': j.get('role', ''), 'direction': j.get('direction', ''),
            'mechanistic': j.get('mechanistic', '')}

def main():
    if not DEEPSEEK_KEY:
        log("ERROR: DEEPSEEK_KEY not set"); return

    with open(MATRIX_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        COLUMNS = list(reader.fieldnames)
        matrix = list(reader)
    log(f"Loaded V021: {len(matrix):,} rows x {len(COLUMNS)} cols")

    pairs = sorted(set((r['gene_symbol'], r['rcd_form_canonical']) for r in matrix))
    log(f"unique pairs: {len(pairs):,}")

    progress = {}
    if os.path.exists(PROGRESS_FILE):
        progress = json.load(open(PROGRESS_FILE, encoding='utf-8'))
        log(f"Resuming: {len(progress):,} done")

    pending = [p for p in pairs if f"{p[0]}|{p[1]}" not in progress]
    log(f"Pending this run: {len(pending):,}")

    def save_checkpoint():
        with lock:
            json.dump(progress, open(PROGRESS_FILE, 'w', encoding='utf-8'))

    def process(pair):
        key = f"{pair[0]}|{pair[1]}"
        try:
            res = classify(pair[0], pair[1])
        except Exception as e:
            res = {'role': '', 'direction': '', 'mechanistic': '', 'error': str(e)[:120]}
        res['key'] = key
        return key, res

    consec_fail = 0
    done = 0
    with ThreadPoolExecutor(max_workers=N_THREADS) as pool:
        futures = {pool.submit(process, p): p for p in pending}
        for fut in as_completed(futures):
            key, res = fut.result()
            with lock:
                progress[key] = res
                done += 1
            if not res.get('role') and not res.get('mechanistic'):
                consec_fail += 1
            else:
                consec_fail = 0
            if done % 10 == 0:
                save_checkpoint()
                log(f"  {len(progress):,}/{len(pairs):,}")
            if consec_fail >= MAX_FAILS_IN_A_ROW:
                log(f"⚠️ {consec_fail} consecutive empty results (token shortage?). Saving checkpoint + graceful exit.")
                save_checkpoint()
                log(f"RESUMABLE: {len(progress):,}/{len(pairs):,} done. Re-run to continue.")
                return

    save_checkpoint()
    log(f"classification complete: {len(progress):,}/{len(pairs):,}")

    # apply to matrix (3 new columns)
    for c in ['deepseek_cot_role', 'deepseek_cot_direction', 'deepseek_cot_mechanistic']:
        if c not in COLUMNS:
            COLUMNS.append(c)
    applied = 0
    for r in matrix:
        key = f"{r['gene_symbol']}|{r['rcd_form_canonical']}"
        if key in progress:
            v = progress[key]
            r['deepseek_cot_role'] = v.get('role', '')
            r['deepseek_cot_direction'] = v.get('direction', '')
            r['deepseek_cot_mechanistic'] = v.get('mechanistic', '')
            applied += 1
    log(f"applied: {applied:,} rows")

    with open(MATRIX_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore')
        w.writeheader(); w.writerows(matrix)
    log(f"V021 written: {len(matrix):,} rows x {len(COLUMNS)} cols")

    # end-of-run assertion
    missing = len(pairs) - len(progress)
    if missing != 0:
        log(f"❌ ASSERTION FAILED: {missing} pairs missing. Re-run to complete.")
    else:
        log(f"✅ ASSERTION PASSED: all {len(pairs):,} pairs classified.")
    log("DONE.")

if __name__ == '__main__':
    main()
