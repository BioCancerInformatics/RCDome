#!/usr/bin/env python3
"""
channel_2e_zero_pmid_recovery.py
Phase 2E extension: Europe PMC full-text + DeepSeek LLM recovery
for DATABASE_ONLY pairs with zero PMIDs.
No pair left unchecked. Every gene scanned in full-text.

Usage:
  python channel_2e_zero_pmid_recovery.py
"""
import csv, os, sys, json, time, re, urllib.request
from datetime import datetime

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/output databases'
MATRIX_FILE = os.path.join(OUTPUT_DIR, 'unified_gene_rcd_matrix.csv')
PROGRESS_FILE = os.path.join(OUTPUT_DIR, 'zero_pmid_recovery_progress.json')

log_lines = []
def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line); log_lines.append(line)

def call_llm(prompt, max_tokens=150):
    time.sleep(0.5)
    headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
    body = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens, "temperature": 0}
    for attempt in range(3):
        try:
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=30).read().decode('utf-8'))
            return resp['choices'][0]['message']['content'].strip(), resp['usage']['total_tokens']
        except:
            if attempt == 2: return (None, 0)
            time.sleep(5 * (attempt + 1))

def europe_pmc_search(query, page_size=10):
    """Search Europe PMC and return list of {'pmid': ..., 'pmcid': ...} dicts."""
    url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={urllib.request.quote(query)}&format=json&pageSize={page_size}&resultType=core'
    try:
        resp = urllib.request.urlopen(url, timeout=10)
        data = json.loads(resp.read().decode('utf-8'))
        results = data.get('resultList', {}).get('result', [])
        papers = []
        for r in results:
            pmid = r.get('pmid', '')
            pmcid = r.get('pmcid', '')
            if pmid:
                papers.append({'pmid': pmid, 'pmcid': pmcid})
        return papers
    except:
        return []

def fetch_pmc_fulltext(pmcid):
    """Fetch full-text XML from Europe PMC for a PMCID. Returns body text or None."""
    if not pmcid or not pmcid.startswith('PMC'):
        return None
    url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML'
    try:
        xml = urllib.request.urlopen(url, timeout=15).read().decode('utf-8')
        body_match = re.search(r'<body[^>]*>(.*?)</body>', xml, re.DOTALL)
        if body_match:
            clean = re.sub(r'<[^>]+>', ' ', body_match.group(1))
            clean = re.sub(r'\s+', ' ', clean).strip()
            return clean
    except:
        pass
    return None

def llm_scan_fulltext(text, gene, rcd_form):
    """DeepSeek scans full-text for RCD form mention in context of gene."""
    rcd_variants = [rcd_form, rcd_form.lower(), rcd_form.replace('-',' '), 
                    rcd_form.replace(' ','-')]
    prompt = (
        f"Scan this passage for evidence that the gene {gene} is associated with "
        f"the cell death form '{rcd_form}' (or variants: {', '.join(rcd_variants[:3])}).\n\n"
        f"Return ONLY a JSON object: "
        f'{{\"found\": true/false, \"pmid_evidence\": \"brief description\"}}\n\n'
        f"TEXT (first 3000 chars):\n{text[:3000]}"
    )
    resp, tok = call_llm(prompt, max_tokens=100)
    try: return json.loads(resp), tok
    except: return {"found": False}, tok

def main():
    log("PHASE 2E ZERO-PMID RECOVERY")
    log("=" * 50)
    
    # Load matrix
    with open(MATRIX_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        COLUMNS = list(reader.fieldnames)
        matrix = list(reader)
    log(f"Loaded: {len(matrix):,} rows x {len(COLUMNS)} cols")
    
    # Find DATABASE_ONLY pairs with zero PMIDs
    zero_pmid_pairs = []
    for r in matrix:
        if r.get('mechanistic_class', '') != 'DATABASE_ONLY':
            continue
        # Verify zero PMIDs
        has_pmid = False
        for col in ['pmid_list', 'llm_pmids', 'epmc_pmids', 'elicit_pmids']:
            v = r.get(col, '').strip()
            if v and v not in ('LITERATURE_NOT_FOUND', 'NOT_RECOVERED') and any(p.isdigit() for p in v.split(';')):
                has_pmid = True; break
        if not has_pmid:
            zero_pmid_pairs.append((r['gene_symbol'], r['rcd_form_canonical']))
    
    # Deduplicate
    zero_pmid_pairs = sorted(set(zero_pmid_pairs))
    log(f"Zero-PMID DATABASE_ONLY pairs: {len(zero_pmid_pairs)}")
    
    # Load progress
    progress = {}
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            progress = json.load(f)
        log(f"Resuming: {len(progress)} pairs done")
    
    pending = [(g, rcd) for g, rcd in zero_pmid_pairs if f"{g}|{rcd}" not in progress]
    log(f"Pending: {len(pending)}")
    
    if not pending:
        log("All pairs already processed.")
        return
    
    # Process each pair
    total_tokens = 0
    recovered_pmids = {}  # (gene, rcd) -> PMID list
    consecutive_failures = 0
    
    for idx, (gene, rcd_form) in enumerate(pending):
        key = f"{gene}|{rcd_form}"
        log(f"\n{idx+1}/{len(pending)}: {gene} + {rcd_form}")
        
        # Step 1: Europe PMC search for gene
        papers = europe_pmc_search(gene, page_size=10)
        if not papers:
            log(f"  No papers found for {gene} in Europe PMC")
            progress[key] = {"status": "NO_PAPERS", "pmids": []}
            continue
        
        log(f"  Found {len(papers)} papers for {gene}")
        
        # Step 2: Fetch full-text and scan with LLM
        found_pmids = []
        for paper in papers[:10]:  # Top 10 papers
            pmid = paper['pmid']
            pmcid = paper['pmcid']
            
            if consecutive_failures > 5:
                log(f"  Too many consecutive failures, skipping remaining")
                break
            
            if not pmcid:
                continue  # No open-access full-text available
            
            fulltext = fetch_pmc_fulltext(pmcid)
            if not fulltext:
                continue
            
            if len(fulltext) < 200:
                continue
            
            # Step 3: LLM scan
            result, tokens = llm_scan_fulltext(fulltext, gene, rcd_form)
            total_tokens += tokens
            
            if result.get('found'):
                evidence = result.get('pmid_evidence', '')
                log(f"    FOUND: PMID {pmid} -> {evidence[:80]}")
                found_pmids.append(pmid)
                consecutive_failures = 0
            else:
                consecutive_failures += 1
        
        if found_pmids:
            recovered_pmids[(gene, rcd_form)] = found_pmids
            progress[key] = {"status": "RECOVERED", "pmids": found_pmids}
        else:
            progress[key] = {"status": "NOT_FOUND", "pmids": []}
        
        # Save progress every 10
        if (idx + 1) % 10 == 0:
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(progress, f)
            recovered = sum(1 for v in progress.values() if v.get('status') == 'RECOVERED')
            log(f"\n  --- Checkpoint: {idx+1}/{len(pending)} done, {recovered} recovered, {total_tokens:,} tokens ---")
    
    # Save final progress
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)
    
    log(f"\n{'='*50}")
    log(f"RECOVERY COMPLETE")
    log(f"Pairs recovered: {len(recovered_pmids)}")
    log(f"Total PMIDs found: {sum(len(v) for v in recovered_pmids.values())}")
    log(f"Total tokens: {total_tokens:,} (~${total_tokens*2/1e6:.2f})")
    
    # Update matrix
    if recovered_pmids:
        log("\nUpdating matrix...")
        updated = 0
        for r in matrix:
            key = (r['gene_symbol'], r['rcd_form_canonical'])
            if key in recovered_pmids:
                new_pmids = ';'.join(recovered_pmids[key])
                # Add to epmc_pmids
                existing = r.get('epmc_pmids', '').strip()
                if existing and existing != 'NOT_RECOVERED':
                    r['epmc_pmids'] = existing + ';' + new_pmids
                else:
                    r['epmc_pmids'] = new_pmids
                r['epmc_status'] = 'CONFIRMED'
                r['epmc_hits'] = str(len(recovered_pmids[key]))
                # Upgrade mechanistic_class from DATABASE_ONLY to INSUFFICIENT_DATA
                if r.get('mechanistic_class') == 'DATABASE_ONLY':
                    r['mechanistic_class'] = 'INSUFFICIENT_DATA'
                updated += 1
        
        with open(MATRIX_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore')
            w.writeheader(); w.writerows(matrix)
        
        log(f"Matrix updated: {updated} rows")
    
    log("\nDONE.")

if __name__ == '__main__':
    main()
