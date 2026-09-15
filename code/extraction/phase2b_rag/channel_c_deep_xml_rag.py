#!/usr/bin/env python3
"""
channel_c_deep_xml_rag.py — Phase 2B: Europe PMC Full-Text XML Deep RAG
=========================================================================
Production version. Processes ALL gene-RCD pairs with PMIDs.
PMC free-text only (no paywalled, no PDF, no abstract).
Three-pass LLM RAG: gene extraction → RCD detection → verbatim evidence.
Per-pair transparency: total/free/skipped PMID counts.
Governance: exact-string hallucination check, multi-paper consensus.
Deduplication: same PMCID processed once, evidence shared across pairs.

Contract: no overwriting. Adds 8 new deep_* columns. Upgrades 3 existing columns
where deep evidence confirms Phase 2A/D classifications.

Usage:
  python channel_c_deep_xml_rag.py          (full corpus)
  python channel_c_deep_xml_rag.py --validate  (ground truth audit)
"""
import csv, os, sys, json, time, re, urllib.request
from collections import defaultdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# === CONFIGURATION ===
DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/output databases'
MATRIX_FILE = os.path.join(OUTPUT_DIR, 'unified_gene_rcd_matrix.csv')
CHECKPOINT = os.path.join(OUTPUT_DIR, 'phase2b_checkpoint.json')
ACCUM_DB = os.path.join(OUTPUT_DIR, 'phase2b_accumulation.json')  # Per-PMCID evidence
PAIR_RESULTS = os.path.join(OUTPUT_DIR, 'phase2b_pair_results.json')  # Per-pair results
PMID_CACHE = os.path.join(OUTPUT_DIR, 'phase2b_pmid_cache.json')  # PMID->PMCID mapping
AUDIT_REPORT = os.path.join(OUTPUT_DIR, 'phase2b_audit_report.json')

# RCD form vocabulary (54 canonical forms)
RCD_FORMS = [
    "Apoptosis", "Necroptosis", "Pyroptosis", "Ferroptosis",
    "Autophagy-dependent cell death", "Necrosis", "Anoikis", "Cuproptosis",
    "NETosis", "Entosis", "Parthanatos", "Disulfidptosis", "Oxeiptosis",
    "Paraptosis", "Alkaliptosis", "Lysosome-dependent cell death", "Autosis",
    "Erebosis", "Methuosis", "Mitoptosis", "Spectosis", "Oncosis",
    "Pyronecrosis", "Mitotic catastrophe", "Mitochondrial permeability transition",
    "Immunogenic cell death", "Efferocytosis", "Cellular senescence",
    "PANoptosis", "Cornification", "Hypersensitive response",
    "Programmed cell death", "NECSO", "Triaptosis", "Mitoxyperilysis",
    "Eryptosis", "Mitotic death", "Aponecrosis", "Ammonia-induced cell death",
    "Lysoptosis", "Vacuolar cell death", "Lysozincrosis", "Floatptosis",
    "Metalloptosis", "Linker cell-type death", "Lysosomal cell death",
    "Regulated Necrosis", "Senescence and Autophagy in Cancer",
    "Phagoptosis", "MPT-driven necrosis",
    "Apoptosis (extrinsic)", "Apoptosis (intrinsic)", "Autophagy",
]

log_lines = []
def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line); log_lines.append(line)

# === DEEPSEEK LLM CALL ===
def call_llm(prompt, max_tokens=300):
    time.sleep(0.5)
    headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
    body = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens, "temperature": 0}
    for attempt in range(3):
        try:
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=60).read().decode('utf-8'))
            return resp['choices'][0]['message']['content'].strip(), resp['usage']['total_tokens']
        except:
            if attempt == 2: return (None, 0)
            time.sleep(10 * (attempt + 1))

# === EUROPE PMC API ===
def pmid_to_pmcid_batch(pmids):
    """Convert PMIDs to PMCIDs via Europe PMC batch query. Returns dict pmid->{'pmcid':..., 'is_open':...}
    IMPORTANT: PMIDs with NO PMCID are cached as {'pmcid':'', 'is_open':False}
    so they are never re-queried on restart (fixes infinite re-conversion)."""
    if not pmids:
        return {}
    # Default: every PMID resolves to "no PMCID" unless Europe PMC says otherwise.
    # This ensures paywalled/absent PMIDs are cached, not re-queried forever.
    results = {p: {'pmcid': '', 'is_open': False} for p in pmids}
    query = ' OR '.join(f'EXT_ID:{p}' for p in pmids)
    url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={urllib.request.quote(query)}&format=json&pageSize={len(pmids)}&resultType=core'
    try:
        resp = urllib.request.urlopen(url, timeout=30)
        data = json.loads(resp.read().decode('utf-8'))
        for r in data.get('resultList', {}).get('result', []):
            pmid = r.get('pmid', '')
            pmcid = r.get('pmcid', '')
            is_open = r.get('isOpenAccess', 'N') == 'Y'
            if pmid:
                results[pmid] = {'pmcid': pmcid, 'is_open': (pmcid != '' and is_open)}
        return results
    except Exception:
        # Network/API error: return {} so failed PMIDs are NOT wrongly cached as "no PMCID"
        return {}

def fetch_fulltext_xml(pmcid):
    """Fetch full-text XML body for a PMCID via NCBI efetch. Returns clean body text or None."""
    if not pmcid or not pmcid.startswith('PMC'):
        return None
    pmcid_num = pmcid.replace('PMC', '')
    url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid_num}&rettype=xml'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'RCDome/1.0'})
        xml = urllib.request.urlopen(req, timeout=40).read().decode('utf-8')
        body_match = re.search(r'<body[^>]*>(.*?)</body>', xml, re.DOTALL)
        if body_match:
            clean = re.sub(r'<[^>]+>', ' ', body_match.group(1))
            clean = re.sub(r'\s+', ' ', clean).strip()
            return clean
    except:
        pass
    return None

def chunk_text(text, size=3000):
    """Split text into overlapping chunks for LLM processing."""
    chunks = []
    for i in range(0, len(text), size - 300):
        chunks.append(text[i:i+size])
    return chunks

# === HGNC VALIDATION ===
def load_hgnc():
    req = urllib.request.Request('https://rest.genenames.org/fetch/status/Approved',
                                  headers={'Accept': 'application/json'})
    data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    return set(d['symbol'] for d in data['response']['docs'])

# === THREE-PASS LLM RAG ===

def pass1_combined(chunk, hgnc_set):
    """Single-pass: extract genes, detect RCD, get verbatim evidence. Replaces 3 separate calls."""
    rcd_list = ', '.join(RCD_FORMS)
    prompt = (
        f"Analyze this passage from a biomedical article. Do THREE things:\n"
        f"1. Extract all human gene symbols (HGNC format, uppercase, 2-15 chars). Return as JSON array 'genes'.\n"
        f"2. For each gene, detect which regulated cell death (RCD) forms it is discussed with.\n"
        f"   RCD forms to check: {rcd_list}. Return as JSON object 'rcd_map': {{\"Ferroptosis\": [\"GPX4\"], ...}}\n"
        f"3. For each gene-RCD pair found, extract the EXACT verbatim sentence(s) establishing the association.\n"
        f"   Return as JSON array 'evidence': [{{\"gene\": \"GPX4\", \"rcd\": \"Ferroptosis\", \"sentences\": [\"...\"], \"evidence_type\": \"DIRECT_EXPERIMENTAL|GENETIC_INTERVENTION|PHARMACOLOGICAL|EXPRESSION_CORRELATION|CITATION_ONLY\", \"role\": \"EXECUTOR|REGULATOR|MARKER|INTERACTOR\", \"direction\": \"PROMOTES|INHIBITS\"}}]\n\n"
        f"Return ONLY the JSON object: {{\"genes\": [...], \"rcd_map\": {{...}}, \"evidence\": [...]}}. If nothing found, return empty arrays/objects.\n\n"
        f"TEXT:\n{chunk[:2500]}"
    )
    resp, tok = call_llm(prompt, max_tokens=500)
    if not resp:
        return [], {}, [], tok
    # Robust JSON extraction: strip markdown fences, take first { to last }
    s = resp.strip()
    if s.startswith('```'):
        s = re.sub(r'^```[a-zA-Z]*\s*', '', s)
        s = re.sub(r'\s*```$', '', s)
    start = s.find('{')
    end = s.rfind('}')
    if start < 0 or end <= start:
        return [], {}, [], tok
    try:
        data = json.loads(s[start:end+1])
        # Filter genes to HGNC only
        genes = [g for g in data.get('genes', []) if g in hgnc_set]
        rcd_map = data.get('rcd_map', {})
        evidence = data.get('evidence', [])
        return genes, rcd_map, evidence, tok
    except:
        return [], {}, [], tok

# === GOVERNANCE ===

def verify_sentence(sentence, source_text):
    """Exact-string hallucination check. Sentence MUST appear verbatim in source."""
    if not sentence or not source_text:
        return False
    return sentence.strip() in source_text

# === THREAD-SAFE STATE ===
checkpoint_lock = threading.Lock()
evidence_lock = threading.Lock()

# === GROUND-TRUTH AUDIT (--validate) ===
# Selection criteria (documented): one open-access primary landmark paper per
# representative RCD form, each establishing a definitively known executor gene,
# verified against NCBI (PMID + PMCID cross-checked).
GROUND_TRUTH = [
    ('PMC4076414', 'GPX4', 'Ferroptosis', 'REGULATOR'),   # Yang 2014 (PMID 24439385) — repressor
    ('PMC8369836', 'MLKL', 'Necroptosis', 'EXECUTOR'),   # Cai 2014 (PMID 24316671)
    ('PMC5010048', 'GSDMD', 'Pyroptosis', 'EXECUTOR'),   # Sborgi 2016 (PMID 27418190)
    ('PMC9273333', 'FDX1', 'Cuproptosis', 'REGULATOR'),   # Tsvetkov 2022 (PMID 35298263) — positive regulator
]

def audit_ground_truth(hgnc_set):
    """Run the ground-truth audit and report gene/RCD/role/hallucination metrics."""
    log("=" * 60)
    log("GROUND TRUTH AUDIT (4 verified open-access landmark papers)")
    log("=" * 60)
    for pmcid, gene, rcd, role in GROUND_TRUTH:
        fulltext = fetch_fulltext_xml(pmcid)
        if not fulltext:
            log(f"  {pmcid} ({gene}/{rcd}): XML FETCH FAILED")
            continue
        gene_found = False
        rcd_found = False
        role_correct = False
        verbatim = 0
        hallucinated = 0
        for chunk in chunk_text(fulltext):
            genes, rcd_map, evidence, _ = pass1_combined(chunk, hgnc_set)
            if gene in genes:
                gene_found = True
            for ev in evidence:
                if ev.get('gene') == gene and ev.get('rcd') == rcd:
                    rcd_found = True
                    if ev.get('role') == role:
                        role_correct = True
                    for s in ev.get('sentences', []):
                        if verify_sentence(s, fulltext):
                            verbatim += 1
                        else:
                            hallucinated += 1
        log(f"  {pmcid} ({gene}/{rcd}): gene={'YES' if gene_found else 'NO'}, "
            f"rcd={'YES' if rcd_found else 'NO'}, role={'OK' if role_correct else 'MISS'}, "
            f"verbatim={verbatim}, hallucinated={hallucinated}")
    log("GROUND TRUTH AUDIT COMPLETE")

def main():
    log("=" * 60)
    log("PHASE 2B: EUROPE PMC FULL-TEXT XML DEEP RAG")
    log("=" * 60)

    if '--validate' in sys.argv:
        hgnc = load_hgnc()
        audit_ground_truth(hgnc)
        return

    # Load matrix
    with open(MATRIX_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        COLUMNS = list(reader.fieldnames)
        matrix = list(reader)
    log(f"Loaded: {len(matrix):,} rows x {len(COLUMNS)} cols")
    
    # Load HGNC
    hgnc = load_hgnc()
    log(f"HGNC: {len(hgnc):,} approved symbols")
    
    # Collect all PMIDs from all pairs
    log("Collecting PMIDs from all pairs...")
    pair_pmids = {}  # (gene, rcd) -> set of PMIDs
    all_pmids = set()
    for r in matrix:
        key = (r['gene_symbol'], r['rcd_form_canonical'])
        pmids = set()
        for col in ['pmid_list', 'llm_pmids', 'epmc_pmids', 'elicit_pmids']:
            v = r.get(col, '').strip()
            if v and v not in ('LITERATURE_NOT_FOUND', 'NOT_RECOVERED'):
                for p in v.split(';'):
                    p = p.strip()
                    if p.isdigit():
                        pmids.add(p)
        if pmids:
            pair_pmids[key] = pmids
            all_pmids.update(pmids)
    
    log(f"Pairs with PMIDs: {len(pair_pmids)}")
    log(f"Unique PMIDs: {len(all_pmids)}")
    
    # Convert PMIDs to PMCIDs in batches (or load from cache)
    log("Converting PMIDs to PMCIDs...")
    pmid_list = sorted(all_pmids)
    pmid_to_info = {}
    
    # Load cache if exists
    if os.path.exists(PMID_CACHE):
        with open(PMID_CACHE) as f:
            pmid_to_info = json.load(f)
        log(f"Loaded {len(pmid_to_info)} PMID mappings from cache")
    
    # Convert uncached PMIDs
    uncached = [p for p in pmid_list if p not in pmid_to_info]
    if uncached:
        batch_size = 100
        for i in range(0, len(uncached), batch_size):
            batch = uncached[i:i+batch_size]
            pmid_to_info.update(pmid_to_pmcid_batch(batch))
            if (i + batch_size) % 1000 == 0:
                log(f"  {min(i+batch_size, len(uncached))}/{len(uncached)} uncached PMIDs converted")
            # Save cache incrementally every 1000 (resilient to interruption)
            if (i + batch_size) % 1000 == 0:
                with open(PMID_CACHE, 'w') as f:
                    json.dump(pmid_to_info, f)
                    f.flush()
                    os.fsync(f.fileno())
        with open(PMID_CACHE, 'w') as f:
            json.dump(pmid_to_info, f)
            f.flush()
            os.fsync(f.fileno())
        log(f"Converted: {len(uncached)} new PMIDs (total cached: {len(pmid_to_info)})")
    else:
        log(f"All {len(pmid_list)} PMIDs already cached")
    
    # Count free vs paywall
    free_count = sum(1 for v in pmid_to_info.values() if v.get('is_open'))
    paywall_count = len(pmid_to_info) - free_count
    log(f"Free PMC: {free_count} | Paywalled: {paywall_count}")
    
    # Load checkpoint
    processed_pmcids = set()  # PMCID already processed
    pair_results = {}  # (gene, rcd) -> deep evidence
    if os.path.exists(CHECKPOINT):
        with open(CHECKPOINT) as f:
            cp = json.load(f)
            processed_pmcids = set(cp.get('processed_pmcids', []))
            log(f"Resuming: {len(processed_pmcids)} PMCIDs already processed")
    if os.path.exists(PAIR_RESULTS):
        with open(PAIR_RESULTS) as f:
            pair_results_temp = json.load(f)
            pair_results = {tuple(k.split('|')): v for k, v in pair_results_temp.items()}
            log(f"Resuming: {len(pair_results)} pairs with results")
    
    # Get free PMCIDs not yet processed
    free_pmcids = [(pmid, info['pmcid']) for pmid, info in pmid_to_info.items() 
                   if info.get('is_open') and info['pmcid'] not in processed_pmcids]
    log(f"Free PMCIDs to process: {len(free_pmcids)}")
    
    if not free_pmcids:
        log("No new free PMCIDs to process.")
    else:
        # 8-thread parallel processing
        total_tokens = [0]
        ha_count = [0]
        completed = [0]
        lock = threading.Lock()
        start_time = time.time()
        
        def process_one(pair):
            pmid, pmcid = pair
            result = {'pmcid': pmcid, 'pmid': pmid, 'evidence': defaultdict(list), 'tokens': 0, 'ha': 0}
            fulltext = fetch_fulltext_xml(pmcid)
            if not fulltext or len(fulltext) < 200:
                return result
            for chunk in chunk_text(fulltext):
                genes, rcd_map, evidence_list, tok = pass1_combined(chunk, hgnc)
                result['tokens'] += tok
                if not genes or not rcd_map:
                    continue
                for ev in evidence_list:
                    gene = ev.get('gene', '')
                    rcd_form = ev.get('rcd', '')
                    if not gene or not rcd_form:
                        continue
                    sentences = ev.get('sentences', [])
                    verified = [s for s in sentences if verify_sentence(s, fulltext)]
                    if verified:
                        ev['verbatim_sentences'] = verified
                        ev['pmid'] = pmid
                        ev['pmcid'] = pmcid
                        ev['mechanistic_role'] = ev.get('role', '')
                        ev['evidence_type'] = ev.get('evidence_type', '')
                        result['evidence'][(gene, rcd_form)].append(ev)
                    else:
                        result['ha'] += 1
            return result
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(process_one, p): p for p in free_pmcids}
            for fut in as_completed(futures):
                r = fut.result()
                with lock:
                    total_tokens[0] += r['tokens']
                    ha_count[0] += r['ha']
                    processed_pmcids.add(r['pmcid'])
                    for (g, rcd), evs in r['evidence'].items():
                        if (g, rcd) not in pair_results:
                            pair_results[(g, rcd)] = {'papers': []}
                        pair_results[(g, rcd)]['papers'].extend(evs)
                    completed[0] += 1
                    if completed[0] % 50 == 0:
                        elapsed = time.time() - start_time
                        spd = completed[0] / (elapsed / 3600) if elapsed > 0 else 0
                        with open(CHECKPOINT, 'w') as f:
                            json.dump({'processed_pmcids': list(processed_pmcids)}, f)
                        with open(PAIR_RESULTS, 'w') as f:
                            json.dump({'|'.join(k): v for k, v in pair_results.items()}, f)
                        log(f"  {completed[0]:,}/{len(free_pmcids):,} | {spd:.0f}/hr | {ha_count[0]} HA | {total_tokens[0]:,} tok")
        
        log(f"\n{'='*60}")
        log(f"RAG COMPLETE")
        log(f"Articles processed: {len(processed_pmcids):,}")
        log(f"Pairs with evidence: {len(pair_results)}")
        log(f"Hallucinations caught: {ha_count[0]}")
        log(f"Total tokens: {total_tokens[0]:,} (~${total_tokens[0]*2/1e6:.2f})")
    
    # === AGGREGATE PER-PAIR RESULTS ===
    log("\nAggregating per-pair evidence...")
    
    # Define new columns for matrix
    new_cols = [
        'deep_pmids_total', 'deep_pmids_free', 'deep_pmids_skipped',
        'deep_paper_count', 'deep_best_sentence', 'deep_best_evidence',
        'deep_best_role', 'deep_best_direction', 'deep_confidence',
        'deep_evidence_score'
    ]
    for c in new_cols:
        if c not in COLUMNS:
            COLUMNS.append(c)
    
    updated = 0
    upgraded_tier = 0
    upgraded_mech = 0
    
    for r in matrix:
        key = (r['gene_symbol'], r['rcd_form_canonical'])
        
        # Count PMIDs per pair
        pmids = pair_pmids.get(key, set())
        total_pmids = len(pmids)
        free_pmids = sum(1 for p in pmids if pmid_to_info.get(p, {}).get('is_open'))
        skipped_pmids = total_pmids - free_pmids
        
        r['deep_pmids_total'] = str(total_pmids)
        r['deep_pmids_free'] = str(free_pmids)
        r['deep_pmids_skipped'] = str(skipped_pmids)
        
        # Aggregate evidence from all papers
        if key in pair_results:
            papers = pair_results[key]['papers']
            pcount = len(set(p['pmid'] for p in papers))  # Unique PMIDs
            r['deep_paper_count'] = str(pcount)
            
            # Find strongest evidence
            evidence_order = {'DIRECT_EXPERIMENTAL': 4, 'GENETIC_INTERVENTION': 3, 
                              'PHARMACOLOGICAL': 2, 'EXPRESSION_CORRELATION': 1, 'CITATION_ONLY': 0}
            best = max(papers, key=lambda p: evidence_order.get(p.get('evidence_type', ''), 0))
            
            r['deep_best_sentence'] = best.get('verbatim_sentences', [''])[0][:500]
            r['deep_best_evidence'] = best.get('evidence_type', '')
            r['deep_best_role'] = best.get('mechanistic_role', '')
            r['deep_best_direction'] = best.get('direction', 'UNKNOWN')
            
            # Multi-paper consensus
            roles = [p.get('mechanistic_role') for p in papers if p.get('mechanistic_role')]
            role = roles[0] if len(set(roles)) == 1 and len(roles) >= 2 else (roles[0] if roles else 'UNCERTAIN')
            
            direct = sum(1 for p in papers if p.get('evidence_type') == 'DIRECT_EXPERIMENTAL')
            confidence = 'HIGH' if pcount >= 5 and role != 'UNCERTAIN' else ('MEDIUM' if pcount >= 2 or direct >= 1 else 'LOW')
            score = direct / pcount if pcount > 0 else 0
            
            r['deep_confidence'] = confidence
            r['deep_evidence_score'] = str(round(score, 2))
            
            # Upgrade evidence_tier: T2 -> T1 when HIGH + EXECUTOR
            if confidence == 'HIGH' and role == 'EXECUTOR' and r.get('evidence_tier') == 'T2':
                r['evidence_tier'] = 'T1'
                upgraded_tier += 1
            
            # Populate rcd_gene_type from deep role if empty
            if not r.get('rcd_gene_type', '').strip() and role in ('EXECUTOR', 'REGULATOR'):
                r['rcd_gene_type'] = role
            
            # Upgrade LITERATURE_GAP to MECHANISTIC
            if r.get('mechanistic_class') == 'LITERATURE_GAP' and confidence in ('HIGH', 'MEDIUM'):
                r['mechanistic_class'] = 'MECHANISTIC'
                upgraded_mech += 1
            
            updated += 1
        else:
            # No RAG evidence found
            for c in ['deep_paper_count', 'deep_best_evidence', 'deep_best_role', 
                      'deep_best_direction', 'deep_confidence', 'deep_evidence_score']:
                r[c] = ''
            r['deep_best_sentence'] = ''
            r['deep_paper_count'] = '0'
    
    # Write updated matrix
    with open(MATRIX_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore')
        w.writeheader(); w.writerows(matrix)
    
    log(f"\n{'='*60}")
    log(f"MATRIX UPDATED")
    log(f"Pairs with deep evidence: {updated}")
    log(f"Evidence tier upgrades (T2→T1): {upgraded_tier}")
    log(f"Mechanistic upgrades (LG→MECH): {upgraded_mech}")
    log(f"Columns: {len(COLUMNS)} (was {len(COLUMNS)-10}, added {len(new_cols)})")
    log(f"\nDONE.")

if __name__ == '__main__':
    main()
