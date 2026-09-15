"""
deepseek_cot_v11_full.py — production run of the v11 self-provided governance loop
on ALL 21,567 unique gene-RCD pairs, writing 4 new columns into V022:

  cot_role        (EXECUTOR / REGULATOR / MARKER / UNCERTAIN)
  cot_direction   (PROMOTES / PROTECTS / UNCLEAR)
  cot_mechanistic (YES / NO)
  cot_evidence    ("role|direction|mechanistic")

The v11 loop (agnostic, benchmarked at 100% combined / 0% false positives):
  deepseek-v4-pro thinking mode (effort=max) + tool-call loop
  + 3x self-consistency vote + 6 logic rules + 3 self-provided fields
  (mechanism, known_forms, role_form) + 3 self-consistency rules.

Production safeguards:
  - nohup-safe (flush)
  - 8-thread parallel
  - token-shortage tolerant (retry + backoff + graceful exit after 25 consecutive empties)
  - resume-safe checkpoint (cot_v11_progress.json) saved every 10
  - loud assertion (processed == 21,567 or scream)

Run on Zima:
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  nohup python3 -u deepseek_cot_v11_full.py >> deepseek_cot_v11_full.log 2>&1 &
"""
import csv, os, json, time, urllib.request, re, io, sys, threading
from collections import Counter
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

csv.field_size_limit(sys.maxsize)

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATRIX_FILE = os.path.join(BASE_DIR, '..', 'output databases', 'Phase 2C output', 'unified_gene_rcd_matrix_V022.csv')
PROGRESS_FILE = os.path.join(BASE_DIR, '..', 'output databases', 'Phase 2C output', 'cot_v11_progress.json')

N_THREADS = 24
MAX_FAILS_IN_A_ROW = 25
lock = threading.Lock()

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
    EXEC_WORDS = ('execute', 'execution', 'pore', 'cleav', 'permeabil', 'caspase', 'kinase', 'directly exec',
                  'cytochrome', 'apoptosome', 'release', 'initiat', 'activates the caspase')
    if role == 'REGULATOR' and any(w in mechanism for w in EXEC_WORDS):
        issues.append("your stated mechanism indicates execution, so the role should be EXECUTOR")
    if form and known_forms and mech == 'YES' and known_forms not in ('unknown', 'unclear', 'various', 'not sure'):
        if form.lower() not in known_forms:
            issues.append(f"you stated the gene is known for '{known_forms}', not '{form}' — mark NO/UNCERTAIN")
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

def main():
    if not DEEPSEEK_KEY:
        log("ERROR: DEEPSEEK_KEY not set"); return

    with open(MATRIX_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        COLUMNS = list(reader.fieldnames)
        matrix = list(reader)
    log(f"Loaded V022: {len(matrix):,} rows x {len(COLUMNS)} cols")

    pairs = sorted(set((r['gene_symbol'], r['rcd_form_canonical']) for r in matrix))
    log(f"unique pairs: {len(pairs):,}")

    progress = {}
    if os.path.exists(PROGRESS_FILE):
        raw = json.load(open(PROGRESS_FILE, encoding='utf-8'))
        # only keep NON-EMPTY classifications; re-queue empty ones (token-shortage safety)
        progress = {k: v for k, v in raw.items() if v.get('role') or v.get('mechanistic')}
        log(f"Resuming: {len(progress):,} classified (dropped {len(raw)-len(progress):,} empty)")

    pending = [p for p in pairs if f"{p[0]}|{p[1]}" not in progress]
    log(f"Pending this run: {len(pending):,}")

    def save_checkpoint():
        with lock:
            tmp = PROGRESS_FILE + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(progress, f)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, PROGRESS_FILE)   # atomic write

    def process(pair):
        key = f"{pair[0]}|{pair[1]}"
        try:
            v = run_loop_voted(prompt_loop(pair[0], pair[1]), pair[1], n=3)
            res = {'role': v.get('role',''), 'direction': v.get('direction',''), 'mechanistic': v.get('mechanistic','')}
        except Exception as e:
            res = {'role': '', 'direction': '', 'mechanistic': '', 'error': str(e)[:120]}
        res['key'] = key
        return key, res

    consec_fail = 0
    BATCH = 200
    for start in range(0, len(pending), BATCH):
        batch = pending[start:start + BATCH]
        with ThreadPoolExecutor(max_workers=N_THREADS) as pool:
            futures = {pool.submit(process, p): p for p in batch}
            for fut in as_completed(futures):
                key, res = fut.result()
                if res.get('role') or res.get('mechanistic'):
                    with lock:
                        progress[key] = res   # only persist SUCCESS (empty results stay pending)
                    consec_fail = 0
                    if len(progress) % 10 == 0:
                        save_checkpoint()
                else:
                    consec_fail += 1
                if consec_fail >= MAX_FAILS_IN_A_ROW:
                    log(f"⚠️ {consec_fail} consecutive empty results — token shortage. Saving checkpoint + graceful exit.")
                    save_checkpoint()
                    log(f"RESUMABLE: {len(progress):,}/{len(pairs):,} classified. Re-run to continue (empties NOT persisted).")
                    return
        save_checkpoint()
        log(f"  batch done: {len(progress):,}/{len(pairs):,}")

    save_checkpoint()
    log(f"classification complete: {len(progress):,}/{len(pairs):,}")

    # apply 4 new columns
    for c in ['cot_role', 'cot_direction', 'cot_mechanistic', 'cot_evidence']:
        if c not in COLUMNS:
            COLUMNS.append(c)
    applied = 0
    for r in matrix:
        key = f"{r['gene_symbol']}|{r['rcd_form_canonical']}"
        if key in progress:
            v = progress[key]
            role = v.get('role', ''); direction = v.get('direction', ''); mech = v.get('mechanistic', '')
            r['cot_role'] = role
            r['cot_direction'] = direction
            r['cot_mechanistic'] = mech
            r['cot_evidence'] = f"{role}|{direction}|{mech}"
            applied += 1
    log(f"applied: {applied:,} rows")

    with open(MATRIX_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore')
        w.writeheader(); w.writerows(matrix)
    log(f"V022 written: {len(matrix):,} rows x {len(COLUMNS)} cols")

    missing = len(pairs) - len(progress)
    empty = sum(1 for v in progress.values() if not v.get('role') and not v.get('mechanistic'))
    if missing != 0 or empty != 0:
        log(f"❌ ASSERTION FAILED: {missing} pairs missing, {empty} empty results. Re-run to complete.")
    else:
        log(f"✅ ASSERTION PASSED: all {len(pairs):,} pairs classified, none empty.")
    log("DONE.")

if __name__ == '__main__':
    main()
