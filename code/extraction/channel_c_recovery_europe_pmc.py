"""
channel_c_recovery_europe_pmc.py - Phase 2C: Europe PMC + DeepSeek Recovery
=============================================================================
Recovers non-MECHANISTIC pairs from v2 using Europe PMC full-text search.
Finds PMIDs hidden from PubMed [Gene] field, validates with DeepSeek LLM.
Reclassifies all 5 unresolved mechanistic classes.

Usage: python channel_c_recovery_europe_pmc.py
"""
import csv, os, json, time, urllib.request, sys
from datetime import datetime

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
EPMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, '..', 'output databases')
MATRIX_FILE = os.path.join(OUTPUT_DIR, 'unified_gene_rcd_matrix.csv')
PROGRESS_FILE = os.path.join(OUTPUT_DIR, 'recovery_progress_phase2e.json')

log_lines = []
def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line); log_lines.append(line)

def call_llm(prompt, max_tokens=20):
    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
            body = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens, "temperature": 0}
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=30).read().decode('utf-8'))
            return resp['choices'][0]['message']['content'].strip(), resp['usage']['total_tokens']
        except:
            if attempt == 2: return (None, 0)
            time.sleep(5 * (attempt + 1))

def search_europe_pmc(gene, rcd_form):
    query = f'({gene}) AND ({rcd_form})'
    url = f"{EPMC_URL}?query={query.replace(' ','%20')}&format=json&pageSize=20&resultType=core"
    try:
        data = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
        results = data.get('resultList', {}).get('result', [])
        pmids = []
        snippets = []
        for r in results:
            pmid = r.get('pmid', '')
            title = r.get('title', '')
            snip = r.get('snippet', '') or ''
            if pmid:
                pmids.append(pmid)
                snippets.append("TITLE:" + title[:120] + " | TEXT:" + snip[:250])
        return pmids, chr(10).join(snippets), data.get('hitCount', 0)
    except:
        return [], "", 0

def validate_single(gene, rcd_form):
    tokens_total = 0
    time.sleep(0.1)
    
    # Call A: Internal knowledge
    prompt_a = "Is gene " + gene + " mechanistically involved in the regulated cell death form " + rcd_form + "? Answer only CONFIRMED or UNCLEAR."
    resp_a, tok_a = call_llm(prompt_a)
    tokens_total += tok_a
    call_a = resp_a and resp_a.startswith('CONFIRMED')
    
    # Call B: Europe PMC full-text snippets
    pmids, snippets, hit_count = search_europe_pmc(gene, rcd_form)
    
    # Use Europe PMC PMIDs to fetch PubMed abstracts for DeepSeek validation
    abstracts_text = ""
    if pmids:
        try:
            pubmed_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=" + ",".join(pmids[:10]) + "&rettype=abstract&retmode=text"
            abstracts_text = urllib.request.urlopen(pubmed_url).read().decode('utf-8')[:8000]
        except:
            pass
    
    if abstracts_text and len(abstracts_text) > 100:
        time.sleep(0.1)
        prompt_b = "Based on these PubMed abstracts (papers found via Europe PMC full-text search), is gene " + gene + " genuinely involved in " + rcd_form + "? Answer only CONFIRMED or UNCLEAR." + chr(10) + chr(10) + "ABSTRACTS:" + chr(10) + abstracts_text[:6000]
        resp_b, tok_b = call_llm(prompt_b, max_tokens=20)
        tokens_total += tok_b
        call_b = resp_b and resp_b.startswith('CONFIRMED')
    else:
        call_b = None
    
    # Merge independently
    if call_a and call_b:
        status = 'CONFIRMED'; basis = 'LLM + Europe PMC confirm (' + str(hit_count) + ' full-text hits)'
    elif call_a and call_b is False:
        status = 'NEEDS_LITERATURE'; basis = 'LLM knows; Europe PMC unclear (' + str(hit_count) + ' hits)'
    elif call_a is False and call_b:
        status = 'NEEDS_CONTEXT'; basis = 'Europe PMC confirms; LLM unsure (' + str(hit_count) + ' hits)'
    elif call_a and call_b is None:
        status = 'CONFIRMED'; basis = 'LLM confirms; no Europe PMC data'
    else:
        status = 'UNCLEAR'; basis = 'Unclear (' + str(hit_count) + ' Europe PMC hits)'
    
    return {'llm_status': status, 'llm_basis': basis, 'new_pmids': ';'.join(pmids[:20]) if pmids else '',
            'epmc_hits': hit_count, 'llm_tokens': tokens_total}

def assign_mechanistic_class(status, epmc_hits):
    if status == 'CONFIRMED': return 'MECHANISTIC'
    if status == 'NEEDS_LITERATURE': return 'LITERATURE_GAP'
    if status == 'NEEDS_CONTEXT': return 'CONTEXT_GAP'
    if epmc_hits >= 26: return 'CO_OCCURRENCE'
    if epmc_hits > 0: return 'INSUFFICIENT_DATA'
    return 'DATABASE_ONLY'

def main():
    log("PHASE 2C: EUROPE PMC + DEEPSEEK RECOVERY")
    log("DeepSeek key: " + ('YES' if DEEPSEEK_KEY else 'NO'))
    if not DEEPSEEK_KEY:
        log("ERROR: Set DEEPSEEK_KEY"); return
    
    with open(MATRIX_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        COLUMNS = list(reader.fieldnames)
        matrix = list(reader)
    log("Loaded: " + str(len(matrix)) + " rows")
    
    to_recover = sorted(set((r['gene_symbol'], r['rcd_form_canonical']) 
                            for r in matrix if r.get('mechanistic_class', '') != 'MECHANISTIC'))
    log("Non-MECHANISTIC pairs: " + str(len(to_recover)))
    
    progress = {}
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f: progress = json.load(f)
        log("Resuming: " + str(len(progress)) + " done")
    
    results = dict(progress)
    consecutive_failures = 0
    for i, (gene, rcd) in enumerate(to_recover):
        key = gene + "|" + rcd
        if key in results: continue
        
        if consecutive_failures >= 5:
            log("COOLDOWN: " + str(consecutive_failures) + " failures. Pausing 60s...")
            with open(PROGRESS_FILE, 'w') as f: json.dump(progress, f)
            time.sleep(60)
            consecutive_failures = 0
        
        try:
            r = validate_single(gene, rcd)
        except Exception as e:
            r = {'llm_status': 'ERROR', 'llm_basis': str(e)[:100], 'new_pmids': '', 'epmc_hits': 0, 'llm_tokens': 0}
            consecutive_failures += 1
        
        results[key] = r
        
        if (i+1) % 10 == 0:
            new_c = sum(1 for v in results.values() if v['llm_status'] == 'CONFIRMED')
            log("  " + str(len(results)) + "/" + str(len(to_recover)) + " | New MECHANISTIC: " + str(new_c))
        if (i+1) % 10 == 0:
            with open(PROGRESS_FILE, 'w') as f: json.dump(results, f)
    
    with open(PROGRESS_FILE, 'w') as f: json.dump(results, f)
    
    # Add new columns for Phase 2C
    new_cols = ['epmc_hits', 'epmc_status', 'epmc_pmids', 'phase2c_mechanistic_class']
    for c in new_cols:
        if c not in COLUMNS:
            COLUMNS.append(c)
    
    log("Updating matrix with Phase 2C results...")
    updated = 0
    recovered = 0
    for r in matrix:
        key = r['gene_symbol'] + "|" + r['rcd_form_canonical']
        if key in results:
            res = results[key]
            r['epmc_hits'] = str(res.get('epmc_hits', 0))
            r['epmc_status'] = res.get('llm_status', '')
            r['epmc_pmids'] = res.get('new_pmids', '')
            if res['llm_status'] == 'CONFIRMED':
                # NEVER overwrite v2 mechanistic_class - use phase2c column
                r['phase2c_mechanistic_class'] = 'MECHANISTIC'
                recovered += 1
                r['phase2c_mechanistic_class'] = assign_mechanistic_class(res['llm_status'], res['epmc_hits'])
            if res['new_pmids'] and not r.get('llm_pmids','').strip():
                r['llm_pmids'] = res['new_pmids']
        else:
            r['phase2c_mechanistic_class'] = r.get('mechanistic_class', '')
            r['epmc_hits'] = ''
            r['epmc_status'] = ''
            r['epmc_pmids'] = ''
    
    with open(MATRIX_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore')
        w.writeheader(); w.writerows(matrix)
    
    log("DONE: " + str(updated) + " pairs upgraded to MECHANISTIC")
    tok = sum(v.get('llm_tokens', 0) for v in results.values())
    log("Tokens: " + str(tok) + " (~$" + str(round(tok*0.000002, 2)) + ")")
    
    # Save execution log
    logpath = os.path.join(OUTPUT_DIR, 'recovery_log_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.txt')
    with open(logpath, 'w', encoding='utf-8') as lf:
        lf.write(chr(10).join(log_lines))
    log('Log saved: ' + logpath)

if __name__ == '__main__':
    import traceback
    while True:
        try:
            main()
            log('PHASE 2C COMPLETED SUCCESSFULLY')
            break
        except Exception as e:
            log('CRASH: ' + str(e)[:200])
            log('Auto-restarting in 30 seconds (progress auto-saved)...')
            time.sleep(30)
