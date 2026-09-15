"""
channel_c_evidence_tier.py - Phase 2A: Evidence Tier + LLM Validation
=======================================================================
Two-call independent LLM validation. retmax=100, 100 PMIDs stored.
7-class mechanistic classification. Kappa, sensitivity, concordance.
Auto-restart. Progress save every 10 pairs.
"""
import csv, os, json, time, urllib.request, sys, re, traceback
from datetime import datetime

NCBI_KEY = os.environ.get('NCBI_KEY', '')
DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, '..', 'output databases')
MATRIX_FILE = os.path.join(OUTPUT_DIR, 'unified_gene_rcd_matrix.csv')
PROGRESS_FILE = os.path.join(OUTPUT_DIR, 'llm_verification_progress.json')

log_lines = []
def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    log_lines.append(line)

def call_llm(prompt, max_tokens=20):
    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
            body = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0}
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=30).read().decode('utf-8'))
            return resp['choices'][0]['message']['content'].strip(), resp['usage']['total_tokens']
        except:
            if attempt == 2: return (None, 0)
            time.sleep(5 * (attempt + 1))

def fetch_pmids_and_abstracts(gene, rcd_form):
    query = f'({gene}[Gene]) AND ({rcd_form}[Title/Abstract])'
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query.replace(' ','%20')}&retmax=100&retmode=json&api_key={NCBI_KEY}"
    for attempt in range(3):
        try:
            data = json.loads(urllib.request.urlopen(url, timeout=30).read().decode('utf-8'))
            pmids = data['esearchresult']['idlist'][:100]
            total_count = int(data['esearchresult']['count'])
            time.sleep(0.12)
            if pmids:
                url2 = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(pmids)}&rettype=abstract&retmode=text&api_key={NCBI_KEY}"
                abstract = urllib.request.urlopen(url2, timeout=30).read().decode('utf-8')[:100000]
                return pmids, abstract, total_count
            return [], "No PubMed hits", 0
        except:
            if attempt == 2: return [], "PubMed search failed", 0
            time.sleep(5 * (attempt + 1))
    return [], "PubMed search failed", 0

def llm_verify(gene, rcd_form):
    tokens_total = 0
    time.sleep(0.1)
    prompt_a = "Is gene " + gene + " mechanistically involved in the regulated cell death form " + rcd_form + "? Answer only CONFIRMED or UNCLEAR."
    resp_a, tok_a = call_llm(prompt_a)
    tokens_total += tok_a
    call_a_confirmed = resp_a and resp_a.startswith('CONFIRMED')
    
    pmids, abstract_text, total_count = fetch_pmids_and_abstracts(gene, rcd_form)
    
    if pmids and abstract_text not in ("PubMed search failed", "No PubMed hits"):
        chunks = [abstract_text[i:i+4000] for i in range(0, min(len(abstract_text), 20000), 4000)]
        batch_votes = []
        for chunk in chunks:
            time.sleep(0.1)
            prompt_b = "Based on these PubMed abstracts, is gene " + gene + " genuinely involved in " + rcd_form + "? Answer only CONFIRMED or UNCLEAR.\n\nABSTRACTS:\n" + chunk
            resp_b, tok_b = call_llm(prompt_b, max_tokens=20)
            tokens_total += tok_b
            if resp_b:
                batch_votes.append(resp_b.startswith('CONFIRMED'))
        if batch_votes:
            call_b_confirmed = sum(batch_votes) >= len(batch_votes) / 2
        else:
            call_b_confirmed = None
    else:
        call_b_confirmed = None
    
    if call_a_confirmed and call_b_confirmed:
        status = 'CONFIRMED'; basis = 'LLM knowledge + PubMed both confirm'
    elif call_a_confirmed and call_b_confirmed is False:
        status = 'NEEDS_LITERATURE'; basis = 'LLM confirms; PubMed does not'
    elif call_a_confirmed and call_b_confirmed is None:
        status = 'CONFIRMED'; basis = 'LLM confirms; no PubMed data'
    elif call_a_confirmed is False and call_b_confirmed:
        status = 'NEEDS_CONTEXT'; basis = 'PubMed confirms; LLM uncertain'
    elif call_a_confirmed is None and call_b_confirmed:
        status = 'CONFIRMED'; basis = 'PubMed confirms'
    elif call_a_confirmed is False and call_b_confirmed is False:
        status = 'UNCLEAR'; basis = 'Neither confirms'
    elif call_a_confirmed is False and call_b_confirmed is None:
        status = 'UNCLEAR'; basis = 'LLM uncertain; no PubMed'
    else:
        status = 'UNVERIFIED'; basis = 'Both calls failed'
    
    return {'llm_status': status, 'llm_basis': basis, 'llm_pmids': ';'.join(pmids[:100]) if pmids else '', 'llm_evidence_force': total_count, 'llm_tokens': tokens_total}

def assign_mechanistic_class(llm_status, evidence_force):
    if llm_status == 'CONFIRMED': return 'MECHANISTIC'
    if llm_status == 'NEEDS_LITERATURE': return 'LITERATURE_GAP'
    if llm_status == 'NEEDS_CONTEXT': return 'CONTEXT_GAP'
    if llm_status == 'ERROR': return 'TECHNICAL_FAILURE'
    q3 = 26
    force = int(evidence_force) if evidence_force else 0
    if force >= q3: return 'CO_OCCURRENCE'
    if force > 0: return 'INSUFFICIENT_DATA'
    return 'DATABASE_ONLY'

def assign_evidence_tier(num_sources, source_databases, pmid_list, llm_status):
    nc = int(num_sources)
    rcddb = 'RCDdb' in source_databases
    pmid = pmid_list.strip() if pmid_list else ''
    if (nc >= 4 and rcddb and pmid) or nc >= 6: return 'T1', 'Multi-database consensus + RCDdb'
    if nc >= 4 or (nc >= 2 and rcddb and pmid): return 'T1', f'{nc} sources'
    if nc >= 3: return 'T2', f'{nc} sources'
    if llm_status == 'CONFIRMED': return 'T2', f'{nc} sources + LLM confirmed'
    if nc >= 2: return 'T3', f'{nc} sources, LLM: {llm_status}'
    if llm_status in ('NEEDS_CONTEXT', 'NEEDS_LITERATURE'): return 'T3', f'{nc} sources, LLM: {llm_status}'
    return 'T4', f'{nc} sources, LLM: {llm_status}'

def compute_kappa(a_results, b_results):
    n = len(a_results)
    if n < 2: return 0
    n_agree = sum(1 for a, b in zip(a_results, b_results) if a == b)
    p_o = n_agree / n
    from collections import Counter
    ca = Counter(a_results); cb = Counter(b_results)
    p_e = sum((ca[k]/n)*(cb[k]/n) for k in set(list(a_results)+list(b_results)))
    return (p_o - p_e) / (1 - p_e) if p_e < 1 else 1.0

def run_accuracy_test():
    GROUND_TRUTH = [
        ("BAX", "Apoptosis"), ("CASP3", "Apoptosis"), ("BCL2", "Apoptosis"),
        ("MLKL", "Necroptosis"), ("RIPK3", "Necroptosis"),
        ("GSDMD", "Pyroptosis"), ("CASP1", "Pyroptosis"),
        ("GPX4", "Ferroptosis"), ("BECN1", "Autophagy"),
        ("GPX4", "Pyroptosis"), ("MLKL", "Ferroptosis"), ("CASP3", "Necroptosis"),
        ("BAX", "Necroptosis"), ("GSDMD", "Ferroptosis"),
    ]
    a_results = []; b_results = []; correct = 0
    for gene, rcd in GROUND_TRUTH:
        r = llm_verify(gene, rcd)
        is_true_positive = (gene, rcd) not in [("GPX4","Pyroptosis"),("MLKL","Ferroptosis"),("CASP3","Necroptosis"),("BAX","Necroptosis"),("GSDMD","Ferroptosis")]
        llm_says_yes = r['llm_status'] == 'CONFIRMED'
        match = llm_says_yes == is_true_positive
        if match: correct += 1
        a_results.append(1 if (r['llm_status']=='CONFIRMED') else 0)
        b_results.append(1 if (r['llm_evidence_force'] > 0) else 0)
        log(f"  {gene:8s}+{rcd:18s} -> {r['llm_status']:20s} {'OK' if match else 'WRONG'}")
    
    acc = correct * 100 // len(GROUND_TRUTH)
    kappa = compute_kappa(a_results, b_results)
    tp = sum(1 for i in range(len(GROUND_TRUTH)) if (GROUND_TRUTH[i][0],GROUND_TRUTH[i][1]) not in [("GPX4","Pyroptosis"),("MLKL","Ferroptosis"),("CASP3","Necroptosis"),("BAX","Necroptosis"),("GSDMD","Ferroptosis")] and a_results[i]==1)
    fp = sum(1 for i in range(len(GROUND_TRUTH)) if (GROUND_TRUTH[i][0],GROUND_TRUTH[i][1]) in [("GPX4","Pyroptosis"),("MLKL","Ferroptosis"),("CASP3","Necroptosis"),("BAX","Necroptosis"),("GSDMD","Ferroptosis")] and a_results[i]==1)
    fn = sum(1 for i in range(len(GROUND_TRUTH)) if (GROUND_TRUTH[i][0],GROUND_TRUTH[i][1]) not in [("GPX4","Pyroptosis"),("MLKL","Ferroptosis"),("CASP3","Necroptosis"),("BAX","Necroptosis"),("GSDMD","Ferroptosis")] and a_results[i]==0)
    sens = tp/(tp+fn) if (tp+fn)>0 else 0
    spec = sum(1 for i in range(len(GROUND_TRUTH)) if (GROUND_TRUTH[i][0],GROUND_TRUTH[i][1]) in [("GPX4","Pyroptosis"),("MLKL","Ferroptosis"),("CASP3","Necroptosis"),("BAX","Necroptosis"),("GSDMD","Ferroptosis")] and a_results[i]==0) / max(1,sum(1 for i in range(len(GROUND_TRUTH)) if (GROUND_TRUTH[i][0],GROUND_TRUTH[i][1]) in [("GPX4","Pyroptosis"),("MLKL","Ferroptosis"),("CASP3","Necroptosis"),("BAX","Necroptosis"),("GSDMD","Ferroptosis")]))
    log(f"Accuracy: {acc}% | Kappa: {kappa:.2f} | Sensitivity: {sens:.2f} | Specificity: {spec:.2f}")

def main():
    if '--validate' in sys.argv:
        run_accuracy_test()
        return
    
    log("PHASE 2A — LLM VALIDATION")
    log(f"Keys: NCBI={'YES' if NCBI_KEY else 'NO'}, DeepSeek={'YES' if DEEPSEEK_KEY else 'NO'}")
    if not NCBI_KEY or not DEEPSEEK_KEY:
        log("ERROR: Set NCBI_KEY and DEEPSEEK_KEY"); return
    
    with open(MATRIX_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        COLUMNS = list(reader.fieldnames)
        matrix = list(reader)
    log(f"Loaded: {len(matrix):,} rows")
    
    progress = {}
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            progress = json.load(f)
        log(f"Resuming: {len(progress)} pairs done")
    
    pairs = sorted(set((r['gene_symbol'], r['rcd_form_canonical']) for r in matrix))
    pending = [(g, r) for g, r in pairs if f"{g}|{r}" not in progress]
    log(f"Total: {len(pairs):,} | Pending: {len(pending):,}")
    
    results = dict(progress)
    for i, (gene, rcd) in enumerate(pending):
        key = f"{gene}|{rcd}"
        try:
            r = llm_verify(gene, rcd)
        except Exception as e:
            r = {'llm_status': 'ERROR', 'llm_basis': str(e)[:200], 'llm_pmids': '', 'llm_evidence_force': 0, 'llm_tokens': 0}
        results[key] = r
        progress[key] = r
        if (i+1) % 10 == 0:
            c = sum(1 for v in results.values() if v['llm_status']=='CONFIRMED')
            log(f"  {len(progress)}/{len(pairs)} | CONFIRMED: {c}")
        if (i+1) % 10 == 0:
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(progress, f)
    
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)
    
    log("Applying tiers...")
    new_cols = ['evidence_tier', 'evidence_basis', 'llm_status', 'llm_pmids', 'llm_evidence_force', 'mechanistic_class']
    for c in new_cols:
        if c not in COLUMNS:
            COLUMNS.append(c)
    
    tier_counts = {}
    class_counts = {}
    for r in matrix:
        key = f"{r['gene_symbol']}|{r['rcd_form_canonical']}"
        lr = results.get(key, {})
        llm_status = lr.get('llm_status', '')
        tier, basis = assign_evidence_tier(r['num_sources'], r.get('source_databases', ''), r.get('pmid_list', ''), llm_status)
        mc = assign_mechanistic_class(llm_status, lr.get('llm_evidence_force', 0))
        r['evidence_tier'] = tier; r['evidence_basis'] = basis
        r['llm_status'] = llm_status; r['llm_pmids'] = lr.get('llm_pmids', '')
        r['llm_evidence_force'] = str(lr.get('llm_evidence_force', 0))
        r['mechanistic_class'] = mc
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        class_counts[mc] = class_counts.get(mc, 0) + 1
    
    with open(MATRIX_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore')
        w.writeheader(); w.writerows(matrix)
    
    # Concordance
    concordance = 0
    for r in matrix:
        mc = r.get('mechanistic_class', '')
        tier = r.get('evidence_tier', '')
        if (mc == 'MECHANISTIC' and tier in ('T1','T2')) or \
           (mc in ('LITERATURE_GAP','CONTEXT_GAP','CO_OCCURRENCE') and tier in ('T2','T3')) or \
           (mc in ('INSUFFICIENT_DATA','DATABASE_ONLY') and tier in ('T3','T4')):
            concordance += 1
    
    log(f"\nDONE: {len(matrix):,} rows, {len(COLUMNS)} columns")
    for t in ['T1','T2','T3','T4']: log(f"  {t}: {tier_counts.get(t,0):,}")
    log(f"\nMechanistic classes:")
    for mc in ['MECHANISTIC','LITERATURE_GAP','CONTEXT_GAP','CO_OCCURRENCE','INSUFFICIENT_DATA','DATABASE_ONLY','TECHNICAL_FAILURE']:
        log(f"  {mc}: {class_counts.get(mc,0):,}")
    log(f"\nConcordance: {concordance}/{len(matrix)} ({concordance*100//len(matrix)}%)")
    tok = sum(v.get('llm_tokens',0) for v in results.values())
    log(f"Tokens: {tok:,}")
    
    lp = os.path.join(OUTPUT_DIR, f'validation_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    with open(lp, 'w', encoding='utf-8') as lf:
        lf.write('\n'.join(log_lines))
    log(f"Log: {lp}")

if __name__ == '__main__':
    main()
