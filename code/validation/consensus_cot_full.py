#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
consensus_cot_full.py — FULL Consensus extraction (production run) on the V023 matrix.

For each of the 21,569 unique gene-RCD pairs:
  1. NEUTRAL Consensus query: "{gene} cell death" -> papers (evidence)
  2. Feed the takeaways to the DeepSeek v11 loop (thinking + tools + 3x vote)
  3. Classify: role / direction / mechanistic / role_form
  4. Store 11 new consensus_* columns (evidence + classification)

Resume-safe + token-aware (like deepseek_cot_v11_full.py):
  - checkpoint (consensus_progress.json) saved every 10 pairs (atomic write)
  - consecutive failures >= MAX_FAILS -> "token shortage" -> graceful exit
  - re-run continues from the checkpoint (RESUMABLE)

Output: unified_gene_rcd_matrix_V023_consensus.csv (74 columns = 63 + 11 consensus_*)
"""
import os, json, time, re, csv, urllib.request, ssl
from collections import Counter
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

csv.field_size_limit(2 ** 31 - 1)  # avoid 131KB field limit on long text cells

BASE = os.path.dirname(os.path.abspath(__file__))
CONSENSUS_URL = "https://api.consensus.app/v1/search"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
MATRIX_FILE = os.path.join(BASE, '..', 'output databases', 'Phase 2C output', 'unified_gene_rcd_matrix_V023.csv')
PROGRESS_FILE = os.path.join(BASE, '..', 'output databases', 'Phase 2C output', 'consensus_progress.json')
OUT_FILE = os.path.join(BASE, '..', 'output databases', 'Phase 2C output', 'unified_gene_rcd_matrix_V023_consensus.csv')

N_THREADS = 24
MAX_FAILS_IN_A_ROW = 20
BATCH = 200

def load_env(keyname):
    env_file = os.path.join(BASE, '..', 'extraction code snippets', '.env')
    key = os.environ.get(keyname, '')
    if not key and os.path.exists(env_file):
        for line in open(env_file, encoding='utf-8'):
            if line.strip().startswith(keyname + '='):
                key = line.strip().split('=', 1)[1].strip()
    return key

CONSENSUS_KEY = load_env('CONSENSUS_API_KEY')
DEEPSEEK_KEY = load_env('DEEPSEEK_KEY')
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

# ---- DeepSeek v11 loop (from cot_benchmark_v11) ----
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
        issues.append("EXECUTOR must PROMOTES")
    if role == 'REGULATOR' and direction not in ('PROMOTES', 'PROTECTS'):
        issues.append("REGULATOR must PROMOTES/PROTECTS")
    if role == 'MARKER' and direction in ('PROMOTES', 'PROTECTS'):
        issues.append("MARKER should not claim causal direction")
    if mech == 'NO' and role in ('EXECUTOR', 'REGULATOR', 'MARKER'):
        issues.append("mechanistic NO should use UNCERTAIN")
    if mech == 'YES' and role == 'UNCERTAIN':
        issues.append("mechanistic YES needs a confident role")
    if mech == 'NO' and direction != 'UNCLEAR':
        issues.append("mechanistic NO should be UNCLEAR")
    EXEC_WORDS = ('execute', 'execution', 'pore', 'cleav', 'permeabil', 'caspase', 'kinase',
                 'directly exec', 'cytochrome', 'apoptosome', 'release', 'initiat')
    if role == 'REGULATOR' and any(w in mechanism for w in EXEC_WORDS):
        issues.append("mechanism indicates execution -> EXECUTOR")
    if form and known_forms and mech == 'YES' and known_forms not in ('unknown', 'unclear', 'various', 'not sure'):
        if form.lower() not in known_forms:
            issues.append(f"gene known for '{known_forms}', not '{form}' -> NO/UNCERTAIN")
    VAGUE = ('unknown', 'unclear', 'various', 'not sure', 'multiple', 'cell death', 'general', 'rcd')
    if mech == 'YES':
        if not role_form or any(v in role_form for v in VAGUE):
            issues.append("state the SPECIFIC form this role belongs to")
        elif form and form.lower() not in role_form:
            issues.append(f"role belongs to '{role_form}', not '{form}' -> NO/UNCERTAIN")
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
    return {'role': maj('role'), 'direction': maj('direction'), 'mechanistic': maj('mechanistic'),
            'role_form': maj('role_form')}

def prompt_loop(gene, form, evidence):
    return (f"Gene {gene}, regulated cell death form {form}.\n\n"
            f"Literature evidence from a NEUTRAL search about this gene (titles + AI takeaways):\n{evidence}\n\n"
            f"DEFINITIONS: EXECUTOR = directly executes death; REGULATOR = controls but does not execute; "
            f"MARKER = associated but not causal. "
            f"Classify the gene's relationship to '{form}' using the evidence. "
            f"State: mechanism, known_forms (which form(s) the gene is PRIMARILY known for), "
            f"role_form (the SINGLE form this role belongs to). "
            f"A gene's role is FORM-SPECIFIC: if it belongs to a DIFFERENT form, it is NOT involved in '{form}'. "
            f"First call verify_role, then classify_gene_rcd. "
            f"Classify: mechanistic (YES/NO), role (EXECUTOR/REGULATOR/MARKER/UNCERTAIN), "
            f"direction (PROMOTES/PROTECTS/UNCLEAR), mechanism, known_forms, role_form.")

# ---- Consensus search (rate-limit aware) ----
def consensus_search(query, page_size=8):
    url = f"{CONSENSUS_URL}?query={urllib.request.quote(query)}&page_size={page_size}"
    req = urllib.request.Request(url, headers={'x-api-key': CONSENSUS_KEY, 'User-Agent': 'Mozilla/5.0'})
    backoff_429 = [10, 20, 30, 40, 50]
    for attempt in range(5):
        try:
            r = urllib.request.urlopen(req, timeout=30, context=CTX)
            return json.loads(r.read().decode('utf-8')).get('results', [])
        except urllib.error.HTTPError as e:
            if e.code == 402:
                return 'QUOTA'  # payment required — no retry
            if e.code == 429:
                if attempt == 4:
                    return 'QUOTA'
                time.sleep(backoff_429[attempt])
                continue
            if attempt == 4:
                return None
            time.sleep(5 * (attempt + 1))
        except Exception:
            if attempt == 4:
                return None
            time.sleep(5 * (attempt + 1))
    return None

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def main():
    if not CONSENSUS_KEY or not DEEPSEEK_KEY:
        log("ERROR: missing CONSENSUS_API_KEY or DEEPSEEK_KEY"); return

    # 1. load V023 matrix
    with open(MATRIX_FILE, encoding='utf-8-sig', newline='') as f:
        matrix = list(csv.DictReader(f))
    COLUMNS = list(matrix[0].keys())
    pairs = sorted({f"{r['gene_symbol']}|{r['rcd_form_canonical']}" for r in matrix})
    log(f"Loaded V023: {len(matrix):,} rows x {len(COLUMNS)} cols")
    log(f"unique pairs: {len(pairs):,}")

    # 2. load checkpoint
    progress = {}
    if os.path.exists(PROGRESS_FILE):
        try:
            progress = json.load(open(PROGRESS_FILE, encoding='utf-8'))
            log(f"Resuming: {len(progress):,} classified (dropped 0 empty)")
        except Exception:
            progress = {}
    pending = [p for p in pairs if p not in progress]
    log(f"Pending this run: {len(pending):,}")

    lock = Lock()
    consensus_lock = Lock()  # serialize Consensus queries (avoid 429 rate-limit)
    def save_checkpoint():
        tmp = PROGRESS_FILE + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(progress, f)
        os.replace(tmp, PROGRESS_FILE)

    def process(pair):
        gene, form = pair.split('|', 1)
        with consensus_lock:
            papers = consensus_search(f"{gene} cell death")
        if papers == 'QUOTA':
            return pair, {'quota': True}
        if papers is None:
            return pair, None
        evidence = "\n".join(f"- {p.get('title','')}: {(p.get('takeaway') or '')[:180]}"
                             for p in papers[:5])
        v = run_loop_voted(prompt_loop(gene, form, evidence), form, n=3)
        res = {
            'role': v.get('role', ''), 'direction': v.get('direction', ''),
            'mechanistic': v.get('mechanistic', ''), 'role_form': v.get('role_form', ''),
            'doi': papers[0].get('doi', '') if papers else '',
            'title': (papers[0].get('title', '') or '')[:200] if papers else '',
            'takeaway': (papers[0].get('takeaway') or '')[:300] if papers else '',
            'citation_count': papers[0].get('citation_count', '') if papers else '',
            'sjr': papers[0].get('sjr_best_quartile', '') if papers else '',
            'year': papers[0].get('publish_year', '') if papers else '',
            'status': 'found' if papers else 'no_result',
        }
        return pair, res

    consec_fail = 0
    quota_hits = 0
    for start in range(0, len(pending), BATCH):
        batch = pending[start:start + BATCH]
        with ThreadPoolExecutor(max_workers=N_THREADS) as pool:
            futures = {pool.submit(process, p): p for p in batch}
            for fut in as_completed(futures):
                key, res = fut.result()
                if res is None:
                    consec_fail += 1
                elif res.get('quota'):
                    quota_hits += 1
                    consec_fail += 1
                elif res.get('role') or res.get('mechanistic'):
                    with lock:
                        progress[key] = res
                    consec_fail = 0
                    if len(progress) % 10 == 0:
                        save_checkpoint()
                else:
                    consec_fail += 1
                if consec_fail >= MAX_FAILS_IN_A_ROW or quota_hits >= 10:
                    log(f"⚠️ token shortage / quota ({consec_fail} fails, {quota_hits} quota). Saving checkpoint + graceful exit.")
                    save_checkpoint()
                    log(f"RESUMABLE: {len(progress):,}/{len(pairs):,} processed. Re-run after topping up tokens.")
                    return
        save_checkpoint()
        log(f"  batch done: {len(progress):,}/{len(pairs):,}")

    save_checkpoint()
    log(f"classification complete: {len(progress):,}/{len(pairs):,}")

    # 3. write the 11 consensus_* columns into V023
    consensus_cols = ['consensus_role', 'consensus_direction', 'consensus_mechanistic',
                      'consensus_role_form', 'consensus_doi', 'consensus_title',
                      'consensus_takeaway', 'consensus_citation_count', 'consensus_sjr',
                      'consensus_year', 'consensus_status']
    for c in consensus_cols:
        if c not in COLUMNS:
            COLUMNS.append(c)
    applied = 0
    for r in matrix:
        key = f"{r['gene_symbol']}|{r['rcd_form_canonical']}"
        if key in progress:
            p = progress[key]
            r['consensus_role'] = p.get('role', '')
            r['consensus_direction'] = p.get('direction', '')
            r['consensus_mechanistic'] = p.get('mechanistic', '')
            r['consensus_role_form'] = p.get('role_form', '')
            r['consensus_doi'] = p.get('doi', '')
            r['consensus_title'] = p.get('title', '')
            r['consensus_takeaway'] = p.get('takeaway', '')
            r['consensus_citation_count'] = str(p.get('citation_count', ''))
            r['consensus_sjr'] = str(p.get('sjr', ''))
            r['consensus_year'] = str(p.get('year', ''))
            r['consensus_status'] = p.get('status', '')
            applied += 1
    log(f"applied: {applied:,} rows")

    with open(OUT_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore')
        w.writeheader(); w.writerows(matrix)
    log(f"V023+consensus written: {len(matrix):,} rows x {len(COLUMNS)} cols")
    log("DONE.")

if __name__ == '__main__':
    main()
