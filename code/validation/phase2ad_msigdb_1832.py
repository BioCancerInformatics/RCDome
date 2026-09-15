"""
phase2ad_msigdb_1832.py — Phase 2A/D validation of the 1,832 MSigDB-only pairs.

Targets ONLY the MSigDB-only rows with empty mechanistic_class in V021
(1,512 "Programmed cell death" + 320 across 10 other forms).

Regulatory-aware two-call validation (original Phase 2A/D enum):
  Call A — internal knowledge (no text)
  Call B — PubMed abstracts (majority vote over chunks)

Outputs per pair:
  mechanistic_class  (MECHANISTIC / LITERATURE_GAP / CONTEXT_GAP /
                      CO_OCCURRENCE / INSUFFICIENT_DATA / DATABASE_ONLY)
  rcd_gene_type      (EXECUTOR / REGULATOR / MARKER / UNCERTAIN)
  role_direction     (PROMOTES / PROTECTS / ASSOCIATED / UNCLEAR)
  llm_pmids, llm_evidence_force, evidence_tier

Resume-safe: phase2ad_msigdb_progress.json (per pair). Progress saved every 10.

Usage (on Zima):
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  export NCBI_KEY=$(grep NCBI_KEY .env | cut -d= -f2)
  nohup python3 -u phase2ad_msigdb_1832.py >> phase2ad_msigdb_1832.log 2>&1 &
"""
import csv, os, json, time, urllib.request, sys, re, traceback
csv.field_size_limit(sys.maxsize)
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

NCBI_KEY = os.environ.get('NCBI_KEY', '')
DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, '..', 'output databases', 'Phase 2C output')
MATRIX_FILE = os.path.join(OUTPUT_DIR, 'unified_gene_rcd_matrix_V021.csv')
BACKUP_FILE = os.path.join(OUTPUT_DIR, 'unified_gene_rcd_matrix_V021.backup_msigdb_pre2ad.csv')
PROGRESS_FILE = os.path.join(OUTPUT_DIR, 'phase2ad_msigdb_progress.json')

N_THREADS = 8
pubmed_lock = threading.Lock()
progress_lock = threading.Lock()

# Broadened child terms for the parent "Programmed cell death" form (Option C)
PCD_CHILD_TERMS = ('apoptosis', 'necroptosis', 'pyroptosis', 'ferroptosis',
                   'programmed cell death')

log_lines = []
def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    log_lines.append(line)

# ---------------- LLM ----------------
def call_llm(prompt, max_tokens=80):
    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
            body = {"model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens, "temperature": 0, "response_format": {"type": "json_object"}}
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=60).read().decode('utf-8'))
            return resp['choices'][0]['message']['content'].strip(), resp['usage']['total_tokens']
        except Exception:
            if attempt == 2:
                return None, 0
            time.sleep(5 * (attempt + 1))

def safe_json_loads(s):
    if not s:
        return None
    s = s.strip()
    s = re.sub(r'^```(json)?\s*', '', s)
    s = re.sub(r'\s*```$', '', s)
    if '{' in s and '}' in s:
        s = s[s.find('{'):s.rfind('}') + 1]
    try:
        return json.loads(s)
    except Exception:
        return None

# ---------------- PROMPTS ----------------
def prompt_a(gene, rcd_form):
    return (
        f"Gene {gene}, regulated cell death form {rcd_form}. "
        f"Using ONLY your internal knowledge, classify the gene's relationship to this cell death form. "
        f"Output ONLY a JSON object with exactly these keys:\n"
        f'- "mechanistic": "YES" if the gene is mechanistically involved (executor or regulator of the death), else "NO"\n'
        f'- "role": "EXECUTOR" (directly carries out the death), "REGULATOR" (promotes or inhibits the death), "MARKER" (associated but not causal), or "UNCERTAIN"\n'
        f'- "direction": "PROMOTES" (pro-death) or "PROTECTS" (pro-survival) if role is REGULATOR, else "UNCLEAR"\n'
        f"JSON:"
    )

def prompt_b(gene, rcd_form, chunk):
    return (
        f"Based on these PubMed abstracts, classify gene {gene}'s relationship to {rcd_form}. "
        f"Output ONLY a JSON object with exactly these keys: "
        f'"mechanistic" ("YES"/"NO"), "role" ("EXECUTOR"/"REGULATOR"/"MARKER"/"UNCERTAIN"), '
        f'"direction" ("PROMOTES"/"PROTECTS"/"UNCLEAR").\n\n'
        f"ABSTRACTS:\n{chunk}\n\nJSON:"
    )

# ---------------- PUBMED ----------------
def build_query(gene, rcd_form):
    if rcd_form == 'Programmed cell death':
        terms = ' OR '.join(f'"{t}"[Title/Abstract]' for t in PCD_CHILD_TERMS)
        return f'({gene}[Gene]) AND ({terms})'
    return f'({gene}[Gene]) AND ("{rcd_form}"[Title/Abstract])'

def fetch_pmids_and_abstracts(gene, rcd_form):
    # Serialize all PubMed eutils traffic to respect NCBI's ~3 req/s rate limit.
    with pubmed_lock:
        query = build_query(gene, rcd_form)
        url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term="
               + urllib.parse.quote(query) + "&retmax=100&retmode=json&api_key=" + NCBI_KEY)
        for attempt in range(3):
            try:
                time.sleep(0.35)
                data = json.loads(urllib.request.urlopen(url, timeout=30).read().decode('utf-8'))
                pmids = data['esearchresult']['idlist'][:100]
                total_count = int(data['esearchresult']['count'])
                if pmids:
                    time.sleep(0.35)
                    url2 = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id="
                            + ','.join(pmids) + "&rettype=abstract&retmode=text&api_key=" + NCBI_KEY)
                    abstract = urllib.request.urlopen(url2, timeout=30).read().decode('utf-8')[:100000]
                    return pmids, abstract, total_count
                return [], "No PubMed hits", 0
            except Exception:
                if attempt == 2:
                    return [], "PubMed search failed", 0
                time.sleep(5 * (attempt + 1))
        return [], "PubMed search failed", 0

# ---------------- VALIDATION ----------------
def llm_verify(gene, rcd_form):
    tokens = 0
    time.sleep(0.1)
    # Call A
    resp_a, tok_a = call_llm(prompt_a(gene, rcd_form))
    tokens += tok_a
    if resp_a is None:
        a_mech = None
        a_role = 'UNCERTAIN'
        a_dir = 'UNCLEAR'
    else:
        ja = safe_json_loads(resp_a) or {}
        a_mech = ja.get('mechanistic', '').upper() == 'YES'
        a_role = ja.get('role', '').upper() if ja.get('role') else 'UNCERTAIN'
        a_dir = ja.get('direction', '').upper() if ja.get('direction') else 'UNCLEAR'

    # Call B
    pmids, abstract_text, total_count = fetch_pmids_and_abstracts(gene, rcd_form)
    b_votes = {'YES': 0, 'NO': 0}
    b_roles, b_dirs = [], []
    if pmids and abstract_text not in ("PubMed search failed", "No PubMed hits"):
        chunks = [abstract_text[i:i+4000] for i in range(0, min(len(abstract_text), 20000), 4000)]
        for chunk in chunks:
            time.sleep(0.1)
            resp_b, tok_b = call_llm(prompt_b(gene, rcd_form, chunk))
            tokens += tok_b
            jb = safe_json_loads(resp_b) or {}
            m = jb.get('mechanistic', '').upper()
            if m in ('YES', 'NO'):
                b_votes[m] += 1
            if jb.get('role'):
                b_roles.append(jb['role'].upper())
            if jb.get('direction'):
                b_dirs.append(jb['direction'].upper())
        b_mech = b_votes['YES'] >= b_votes['NO'] if (b_votes['YES'] + b_votes['NO']) else None
    else:
        b_mech = None

    # ---- merge (original Phase 2A/D logic, plus role/direction) ----
    if a_mech and b_mech:
        status, basis = 'CONFIRMED', 'LLM knowledge + PubMed both confirm'
    elif a_mech and b_mech is False:
        status, basis = 'NEEDS_LITERATURE', 'LLM confirms; PubMed does not'
    elif a_mech and b_mech is None:
        status, basis = 'CONFIRMED', 'LLM confirms; no PubMed data'
    elif a_mech is False and b_mech:
        status, basis = 'NEEDS_CONTEXT', 'PubMed confirms; LLM uncertain'
    elif a_mech is None and b_mech:
        status, basis = 'CONFIRMED', 'PubMed confirms'
    elif a_mech is False and b_mech is False:
        status, basis = 'UNCLEAR', 'Neither confirms'
    elif a_mech is False and b_mech is None:
        status, basis = 'UNCLEAR', 'LLM uncertain; no PubMed'
    else:
        status, basis = 'UNVERIFIED', 'Both calls failed'

    # role: prefer Call A (internal), fall back to Call B majority
    role = a_role if a_role in ('EXECUTOR', 'REGULATOR', 'MARKER', 'UNCERTAIN') else 'UNCERTAIN'
    if role == 'UNCERTAIN' and b_roles:
        role = max(set(b_roles), key=b_roles.count)

    # direction
    direction = 'UNCLEAR'
    if status == 'CONFIRMED':
        if role == 'REGULATOR':
            d = a_dir if a_dir in ('PROMOTES', 'PROTECTS') else (
                max(set(b_dirs), key=b_dirs.count) if b_dirs else 'UNCLEAR')
            direction = d if d in ('PROMOTES', 'PROTECTS') else 'UNCLEAR'
        elif role == 'EXECUTOR':
            direction = 'PROMOTES'
        elif role == 'MARKER':
            direction = 'ASSOCIATED'
        else:
            direction = 'UNCLEAR'

    return {
        'llm_status': status, 'llm_basis': basis,
        'llm_pmids': ';'.join(pmids[:100]) if pmids else '',
        'llm_evidence_force': total_count, 'llm_tokens': tokens,
        'rcd_gene_type': role if status == 'CONFIRMED' else '',
        'role_direction': direction if status == 'CONFIRMED' else '',
    }

def assign_mechanistic_class(llm_status, evidence_force):
    if llm_status == 'CONFIRMED':
        return 'MECHANISTIC'
    if llm_status == 'NEEDS_LITERATURE':
        return 'LITERATURE_GAP'
    if llm_status == 'NEEDS_CONTEXT':
        return 'CONTEXT_GAP'
    if llm_status == 'ERROR':
        return 'TECHNICAL_FAILURE'
    force = int(evidence_force) if evidence_force else 0
    if force >= 26:
        return 'CO_OCCURRENCE'
    if force > 0:
        return 'INSUFFICIENT_DATA'
    return 'DATABASE_ONLY'

def assign_evidence_tier(num_sources, llm_status):
    nc = int(num_sources) if num_sources else 1
    if llm_status == 'CONFIRMED':
        return 'T2', f'{nc} sources + LLM confirmed'
    if llm_status in ('NEEDS_CONTEXT', 'NEEDS_LITERATURE'):
        return 'T3', f'{nc} sources, LLM: {llm_status}'
    return 'T4', f'{nc} sources, LLM: {llm_status}'

# ---------------- MAIN ----------------
def main():
    log("PHASE 2A/D — MSigDB 1,832 PAIRS (regulatory-aware)")
    log(f"Keys: NCBI={'YES' if NCBI_KEY else 'NO'}, DeepSeek={'YES' if DEEPSEEK_KEY else 'NO'}")
    if not NCBI_KEY or not DEEPSEEK_KEY:
        log("ERROR: set NCBI_KEY and DEEPSEEK_KEY"); return

    run_all = '--all' in sys.argv
    progress_file = os.path.join(OUTPUT_DIR, 'phase2ad_all_progress.json' if run_all else 'phase2ad_msigdb_progress.json')
    log("SCOPE: --all (every unique gene-RCD pair)" if run_all else "SCOPE: MSigDB-only unvalidated rows")

    with open(MATRIX_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        COLUMNS = list(reader.fieldnames)
        matrix = list(reader)
    log(f"Loaded V021: {len(matrix):,} rows")

    # backup before writing
    if not os.path.exists(BACKUP_FILE):
        with open(MATRIX_FILE, 'r', encoding='utf-8-sig') as f, open(BACKUP_FILE, 'w', encoding='utf-8-sig', newline='') as g:
            g.write(f.read())
        log(f"Backup written: {BACKUP_FILE}")

    # target selection
    if run_all:
        seen = set()
        targets = []
        for r in matrix:
            k = (r['gene_symbol'], r['rcd_form_canonical'])
            if k not in seen:
                seen.add(k)
                targets.append(r)
        log(f"Target: ALL unique pairs ({len(targets)})")
    else:
        targets = [r for r in matrix if 'MSigDB' in r['source_databases'] and not r['mechanistic_class'].strip()]
        log(f"Target MSigDB-only unvalidated rows: {len(targets)}")

    progress = {}
    if os.path.exists(progress_file):
        with open(progress_file, encoding='utf-8') as f:
            progress = json.load(f)
        log(f"Resuming: {len(progress)} pairs done")

    pending = [r for r in targets if f"{r['gene_symbol']}|{r['rcd_form_canonical']}" not in progress]
    log(f"Pending this run: {len(pending)}")

    def process_one(r):
        key = f"{r['gene_symbol']}|{r['rcd_form_canonical']}"
        try:
            res = llm_verify(r['gene_symbol'], r['rcd_form_canonical'])
        except Exception as e:
            res = {'llm_status': 'ERROR', 'llm_basis': str(e)[:200], 'llm_pmids': '',
                   'llm_evidence_force': 0, 'llm_tokens': 0, 'rcd_gene_type': '', 'role_direction': ''}
        res['key'] = key
        return key, res

    done = 0
    with ThreadPoolExecutor(max_workers=N_THREADS) as pool:
        futures = {pool.submit(process_one, r): r for r in pending}
        for fut in as_completed(futures):
            key, res = fut.result()
            with progress_lock:
                progress[key] = res
                done += 1
            if done % 10 == 0:
                c = sum(1 for v in progress.values() if v['llm_status'] == 'CONFIRMED')
                log(f"  {done}/{len(pending)} | CONFIRMED: {c}")
                with progress_lock:
                    with open(progress_file, 'w', encoding='utf-8') as f:
                        json.dump(progress, f)

    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f)
    log(f"Validation complete: {len(progress)} pairs processed")

    # apply results back to matrix
    log("Applying results to V021...")
    applied = 0
    for r in matrix:
        key = f"{r['gene_symbol']}|{r['rcd_form_canonical']}"
        if key in progress:
            v = progress[key]
            r['mechanistic_class'] = assign_mechanistic_class(v['llm_status'], v['llm_evidence_force'])
            if v['llm_status'] == 'CONFIRMED':
                r['rcd_gene_type'] = v.get('rcd_gene_type', '')
                r['role_direction'] = v.get('role_direction', '')
            r['llm_status'] = v['llm_status']
            r['llm_pmids'] = v.get('llm_pmids', '')
            r['llm_evidence_force'] = str(v.get('llm_evidence_force', 0))
            tier, basis = assign_evidence_tier(r.get('num_sources', '1'), v['llm_status'])
            r['evidence_tier'] = tier
            r['evidence_basis'] = basis
            applied += 1
    log(f"Applied: {applied} rows")

    with open(MATRIX_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore')
        w.writeheader(); w.writerows(matrix)
    log(f"V021 written: {len(matrix):,} rows x {len(COLUMNS)} cols")

    tok = sum(v.get('llm_tokens', 0) for v in progress.values())
    log(f"Total tokens: {tok:,}")
    lp = os.path.join(OUTPUT_DIR, f'phase2ad_msigdb_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    with open(lp, 'w', encoding='utf-8') as lf:
        lf.write('\n'.join(log_lines))
    log(f"Log: {lp}")
    log("DONE.")

if __name__ == '__main__':
    main()
