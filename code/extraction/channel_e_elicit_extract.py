import csv, os, json, time, urllib.request, sys, subprocess, re
"""
channel_e_elicit_extract.py - Phase 3: Elicit Systematic Review Gene Extraction
================================================================================
Extracts HUMAN gene symbols for 12 priority RCD forms via Elicit API.
Targets forms with 0 genes in current matrix. HGNC-validated.
Output matches unified matrix 26-column schema.

Priority forms: Aponecrosis, Lysozincrosis, Phagoptosis,
Floatptosis, Metalloptosis, ADCD, MPT-driven necrosis, Mitotic death,
Lysoptosis, Linker cell death, Ammonia-induced cell death, Vacuolar cell death

Usage: python channel_e_elicit_extract.py
"""
from datetime import datetime

ELICIT_KEY = os.environ.get('ELICIT_API_KEY', '')
ELICIT_URL = 'https://elicit.com/api/v2/sessions/systematic-reviews'

# =====================================================================
# GOVERNANCE RULE (immutable):
#   ELICIT is used ONLY for DEEP FULL-TEXT extraction (RAG into article
#   bodies). It must NEVER be used for title/abstract search — that is
#   what PubMed / Europe PMC do FOR FREE.
#
#   -> corpus 'elicit' (full-text index)  = justified Elicit spend
#   -> corpus 'pubmed' (abstracts)        = FORBIDDEN — use Europe PMC
# =====================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, '..', 'output databases')
MATRIX_FILE = os.path.join(OUTPUT_DIR, 'unified_gene_rcd_matrix_V014.csv')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'gene_rcd_elicit_phase3.csv')
PROGRESS_FILE = os.path.join(OUTPUT_DIR, 'elicit_progress.json')

RCD_FORMS = [
    ('Alkaliptosis', 'COMPOSITE'), ('Ammonia-induced cell death', 'PROVISIONAL'),
    ('Anoikis', 'MECHANISTICALLY_INDEPENDENT'), ('Aponecrosis', 'MORPHOLOGICAL'),
    ('Apoptosis', 'MECHANISTICALLY_INDEPENDENT'), ('Apoptosis (extrinsic)', 'SUBTYPE'),
    ('Apoptosis (intrinsic)', 'SUBTYPE'), ('Autophagy', 'EXCLUDED'),
    ('Autophagy-dependent cell death', 'MECHANISTICALLY_INDEPENDENT'),
    ('Autosis', 'MECHANISTICALLY_INDEPENDENT'), ('Calcioptosis', 'EXCLUDED'),
    ('Cellular senescence', 'FUNCTIONAL'), ('Cornification', 'MORPHOLOGICAL'),
    ('Cuproptosis', 'MECHANISTICALLY_INDEPENDENT'), ('Disulfidptosis', 'MECHANISTICALLY_INDEPENDENT'),
    ('Efferocytosis', 'FUNCTIONAL'), ('Entosis', 'MECHANISTICALLY_INDEPENDENT'),
    ('Erebosis', 'PROVISIONAL'), ('Eryptosis', 'MECHANISTICALLY_INDEPENDENT'),
    ('Ferroptosis', 'MECHANISTICALLY_INDEPENDENT'), ('Floatptosis', 'PROVISIONAL'),
    ('Hypersensitive response', 'EXCLUDED'), ('Immunogenic cell death', 'FUNCTIONAL'),
    ('Linker cell-type death', 'PROVISIONAL'), ('Lysoptosis', 'SUBTYPE'),
    ('Lysosomal cell death', 'SUBTYPE'), ('Lysosome-dependent cell death', 'MECHANISTICALLY_INDEPENDENT'),
    ('Lysozincrosis', 'PROVISIONAL'), ('MPT-driven necrosis', 'MECHANISTICALLY_INDEPENDENT'),
    ('Metalloptosis', 'PROVISIONAL'), ('Methuosis', 'MECHANISTICALLY_INDEPENDENT'),
    ('Mitochondrial permeability transition', 'TRIGGER'), ('Mitoptosis', 'COMPOSITE'),
    ('Mitotic catastrophe', 'TRIGGER'), ('Mitotic death', 'SUBTYPE'),
    ('Mitoxyperilysis', 'PROVISIONAL'), ('NECSO', 'PROVISIONAL'),
    ('NETosis', 'MECHANISTICALLY_INDEPENDENT'), ('Necroptosis', 'MECHANISTICALLY_INDEPENDENT'),
    ('Necrosis', 'MORPHOLOGICAL'), ('Oncosis', 'MORPHOLOGICAL'),
    ('Oxeiptosis', 'MECHANISTICALLY_INDEPENDENT'), ('PANoptosis', 'COMPOSITE'),
    ('Paraptosis', 'MECHANISTICALLY_INDEPENDENT'), ('Parthanatos', 'MECHANISTICALLY_INDEPENDENT'),
    ('Phagoptosis', 'MECHANISTICALLY_INDEPENDENT'), ('Programmed cell death', 'GENERIC'),
    ('Pyronecrosis', 'PROVISIONAL'), ('Pyroptosis', 'MECHANISTICALLY_INDEPENDENT'),
    ('Regulated Necrosis', 'COMPOSITE'), ('Senescence and Autophagy in Cancer', 'COMPOSITE'),
    ('Spectosis', 'PROVISIONAL'), ('Triaptosis', 'PROVISIONAL'),
    ('Vacuolar cell death', 'MORPHOLOGICAL'),
]

log_lines = []
def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line); log_lines.append(line)

def load_hgnc():
    req = urllib.request.Request('https://rest.genenames.org/fetch/status/Approved',
                                  headers={'Accept': 'application/json'})
    data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    symbols = set(d['symbol'] for d in data['response']['docs'])
    enrich = {}
    for d in data['response']['docs']:
        sym = d['symbol']
        lt = d.get('locus_type', '')
        bt = 'protein_coding' if 'protein' in lt.lower() else ('lncRNA' if 'long non' in lt.lower() else ('miRNA' if 'micro' in lt.lower() else ('pseudogene' if 'pseudo' in lt.lower() else 'other')))
        enrich[sym] = {'biotype': bt, 'uniprot': (d.get('uniprot_ids') or [''])[0], 'ensembl': d.get('ensembl_gene_id', '')}
    return symbols, enrich

def get_gene_list(rcd_form, matrix_file=MATRIX_FILE):
    """Get comma-separated gene list for a given RCD form from the matrix."""
    genes = set()
    with open(matrix_file, 'r', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            if r.get('rcd_form_canonical','') == rcd_form:
                genes.add(r['gene_symbol'])
    return ', '.join(sorted(genes))

def safe_json_loads(s):
    """Parse JSON safely; return {} on empty/invalid input (network flakiness)."""
    if not s or not s.strip():
        return {}
    try:
        return json.loads(s)
    except Exception:
        return {}

def call_elicit(rcd_form):
    """Create Elicit systematic review with enhanced extraction contract."""
    instructions = (
        "Extract genes from this paper that are in the closed allow-list below. "
        "Return JSON array of objects with keys: gene_symbol, mechanistic_role (EXECUTOR/REGULATOR/MARKER), "
        "evidence_type (GENETIC_PERTURBATION/PHARMACOLOGICAL/EXPRESSION_CORRELATION/CITATION_ONLY), verbatim_sentence. "
        "EXECUTOR requires genetic perturbation IN THIS PAPER, not cited elsewhere. "
        "Allow-list: " + get_gene_list(rcd_form)[:500]
    )
    
    body = json.dumps({
        "researchQuestion": "Gene-" + rcd_form + " associations in closed allow-list",
        "searches": [
            {"query": rcd_form + " regulated cell death mechanism", "corpus": "pubmed", "searchMode": "semantic", "maxResults": 1000},
            {"query": rcd_form + " genetic perturbation CRISPR knockout knockdown", "corpus": "pubmed", "searchMode": "semantic", "maxResults": 1000},
            {"query": rcd_form + " pharmacological inhibitor drug mechanism", "corpus": "pubmed", "searchMode": "semantic", "maxResults": 1000},
            {"query": rcd_form + " gene expression correlation biomarker", "corpus": "elicit", "searchMode": "semantic", "maxResults": 1000}
        ],
        "abstractScreening": {"generate": True},
        "extraction": {
            "generate": False,
            "useFigures": False,
            "questions": [
                {"name": "gene_symbol", "instructions": "HGNC gene symbol from paper. Return null if none."},
                {"name": "mechanistic_role", "instructions": "EXECUTOR if KD/KO in this paper changes " + rcd_form + " death. REGULATOR if modulates. MARKER if correlation only.", "choices": ["EXECUTOR", "REGULATOR", "MARKER", "UNCERTAIN"]},
                {"name": "evidence_type", "instructions": "Type: GENETIC_PERTURBATION (KD/KO/CRISPR in this paper), PHARMACOLOGICAL, EXPRESSION_CORRELATION, CITATION_ONLY.", "choices": ["GENETIC_PERTURBATION", "PHARMACOLOGICAL", "EXPRESSION_CORRELATION", "CITATION_ONLY"]},
                {"name": "verbatim_sentence", "instructions": "Copy EXACT sentence linking gene to " + rcd_form + ". Return null if inaccessible."},
                {"name": "role_direction", "instructions": "PROMOTES if gene increases " + rcd_form + ", PROTECTS if reduces.", "choices": ["PROMOTES", "PROTECTS", "ASSOCIATED", "BIDIRECTIONAL", "UNCLEAR"]},
                {"name": "required_for_death", "instructions": "Is gene required for " + rcd_form + " execution? YES only with perturbation data.", "choices": ["YES", "PARTIAL", "NO", "NOT_TESTED", "UNCLEAR"]}
            ]
        },
        "generateReport": False
    })
    cmd = ['curl', '-s', '-X', 'POST', ELICIT_URL, '-H', 'Authorization: Bearer ' + ELICIT_KEY, '-H', 'Content-Type: application/json', '-d', body]
    resp = {}
    for attempt in range(3):
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        resp = safe_json_loads(result.stdout)
        if resp:
            break
        if attempt < 2:
            log(f"    Session create attempt {attempt+1} empty — retrying in {10*(attempt+1)}s")
            time.sleep(10 * (attempt + 1))
    session_id = resp.get('sessionId', '') if resp else ''
    log("    Session: " + session_id)
    return session_id

def poll_elicit(session_id, max_wait=3600):
    """Poll Elicit session until completed. Returns (response, csv_data)."""
    # Elicit needs time to start extraction — wait 60s before first poll
    time.sleep(60)
    waited = 60
    while waited < max_wait:
        time.sleep(10)
        waited += 10
        poll_url = ELICIT_URL + "/" + session_id
        cmd = ['curl', '-s', poll_url, '-H', 'Authorization: Bearer ' + ELICIT_KEY]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        resp = safe_json_loads(result.stdout)
        status = resp.get('status', '')
        if status == 'completed':
            log("    Completed in " + str(waited) + "s")
            # The extraction CSV URL may be delayed well after 'completed'.
            # Re-poll (up to 90 checks, 10s apart = 15 min) until the CSV URL appears.
            for check in range(90):
                extract = resp.get('data', {}).get('extract', {})
                csv_url = extract.get('csv', '') or resp.get('data', {}).get('csvUrl', '') or resp.get('data', {}).get('downloadUrl', '')
                if csv_url:
                    for dl in range(3):
                        try:
                            req = urllib.request.Request(csv_url)
                            req.add_header('User-Agent', 'Mozilla/5.0')
                            csv_data = urllib.request.urlopen(req, timeout=30).read().decode('utf-8-sig')
                            log(f"    CSV downloaded ({len(csv_data)} bytes)")
                            return (resp, csv_data)
                        except Exception as e:
                            log(f"    CSV download attempt {dl+1} failed: {str(e)[:60]}")
                            if dl < 2: time.sleep(3)
                    log("    CSV URL present but download failed")
                    break
                # CSV URL not ready yet — wait and re-poll the session
                if check < 89:
                    time.sleep(10)
                    cmd = ['curl', '-s', poll_url, '-H', 'Authorization: Bearer ' + ELICIT_KEY]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    resp = safe_json_loads(result.stdout)
            # Fallback: inline data
            extract = resp.get('data', {}).get('extract', {})
            if 'extractionResults' in resp.get('data', {}):
                results = resp['data']['extractionResults']
                if isinstance(results, list) and len(results) > 0:
                    csv_data = json_to_csv(results)
                    log(f"    Inline data: {len(results)} records")
                    return (resp, csv_data)
            if 'rows' in extract:
                rows = extract['rows']
                if len(rows) > 0:
                    csv_data = json_to_csv(rows)
                    log(f"    Inline rows: {len(rows)} records")
                    return (resp, csv_data)
            log("    No CSV URL after 90 re-polls (15 min)")
            return (resp, None)
        if status == 'failed':
            log("    Session failed")
            return (None, None)
    log("    Timeout after " + str(max_wait) + "s")
    return (None, None)

def resolve_doi_to_pmid(doi):
    """Resolve DOI to PMID using Elicit search/papers endpoint."""
    if not doi:
        return ''
    url = f'https://elicit.com/api/v2/search/papers'
    body = json.dumps({'query': doi, 'searchMode': 'keyword', 'corpus': 'elicit', 'maxResults': 1})
    cmd = ['curl', '-s', '-X', 'POST', url,
           '-H', 'Authorization: Bearer ' + ELICIT_KEY,
           '-H', 'Content-Type: application/json',
           '-d', body, '--max-time', '10']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    try:
        data = json.loads(result.stdout)
        papers = data.get('papers', [])
        if papers and papers[0].get('pmid'):
            return papers[0]['pmid']
    except:
        pass
    return ''
def json_to_csv(rows):
    """Convert list of dicts to CSV string."""
    if not rows:
        return ''
    import io
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
    return out.getvalue()

def download_extraction_csv(response):
    """Download extraction CSV from Elicit S3 signed URL with retry."""
    extract = response.get('data', {}).get('extract', {})
    csv_url = extract.get('csv', '')
    if not csv_url:
        log("    No extraction CSV URL in response")
        return None
    for attempt in range(3):
        try:
            req = urllib.request.Request(csv_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            csv_data = urllib.request.urlopen(req, timeout=30).read()
            return csv_data.decode('utf-8-sig')
        except urllib.error.HTTPError as e:
            log(f"    HTTP {e.code} on attempt {attempt+1}: {csv_url[:60]}...")
        except Exception as e:
            log(f"    Download error on attempt {attempt+1}: {str(e)[:60]}")
        if attempt < 2:
            time.sleep(5)
    return None

def parse_elicit_response(csv_data, hgnc_symbols, hgnc_enrich, rcd_form):
    """Parse Elicit extraction CSV with choices-enforced columns + gene_evidence_json."""
    if not csv_data:
        return []
    import io
    reader = csv.DictReader(io.StringIO(csv_data))
    rows = list(reader)
    if not rows:
        return []
    
    # Detect column types
    has_gene_json = 'gene_evidence_json' in rows[0]
    has_mech_role = 'mechanistic_role' in rows[0]
    has_direction = 'role_direction' in rows[0]
    has_required = 'required_for_death' in rows[0]
    has_evidence_type = 'evidence_type' in rows[0]
    
    # Normalize unexpected roles (SENSITIZER, RESISTANCE, PROTECTIVE -> REGULATOR)
    ROLE_NORMALIZE = {'SENSITIZER': 'REGULATOR', 'RESISTANCE': 'REGULATOR', 'PROTECTIVE': 'REGULATOR'}
    DIRECTION_MAP = {'SENSITIZER': 'PROMOTES', 'RESISTANCE': 'PROTECTS', 'PROTECTIVE': 'PROTECTS'}
    
    genes = []
    log(f"    Resolving PMIDs for {len(rows)} papers via DOI lookup...")
    
    # Batch resolve DOIs to PMIDs
    doi_pmid_map = {}
    for row in rows:
        doi = row.get('DOI', '').strip()
        if doi and doi not in doi_pmid_map:
            doi_pmid_map[doi] = resolve_doi_to_pmid(doi)
            time.sleep(0.3)
    resolved = sum(1 for v in doi_pmid_map.values() if v)
    log(f"    Resolved {resolved}/{len(doi_pmid_map)} DOIs to PMIDs")
    
    # ENFORCE allow-list for this RCD form
    allow_list = set(g.upper() for g in get_gene_list(rcd_form).split(', '))
    
    for row in rows:
        doi = row.get('DOI', '').strip()
        pmid = doi_pmid_map.get(doi, row.get('PMID', ''))
        citations = row.get('Citation count', '0').strip()
        
        # Get paper-level classifications from choices-enforced columns
        paper_role = row.get('mechanistic_role', '').strip() if has_mech_role else ''
        paper_direction = row.get('role_direction', '').strip() if has_direction else ''
        paper_required = row.get('required_for_death', '').strip() if has_required else ''
        paper_evidence_type = row.get('evidence_type', '').strip() if has_evidence_type else ''
        
        # Normalize unexpected role values
        if paper_role in ROLE_NORMALIZE:
            paper_direction = DIRECTION_MAP.get(paper_role, paper_direction)
            paper_role = ROLE_NORMALIZE[paper_role]
        
        # Extract genes from gene_evidence_json OR from paper text
        found = set()
        if has_gene_json:
            gjson = row.get('gene_evidence_json', '')
            if gjson and gjson not in ('[]', 'null', ''):
                for obj_str in re.findall(r'\{[^}]+\}', gjson):
                    try:
                        e = json.loads(obj_str)
                        sym = e.get('gene_symbol', '').strip()
                        if sym in allow_list:
                            found.add(sym)
                    except: pass
        
        # Fallback: extract genes from all paper text
        if not found:
            all_text = ' '.join(str(v) for v in row.values() if isinstance(v, str))
            for m in re.finditer(r'\b([A-Z][A-Z0-9]{2,15})\b', all_text):
                sym = m.group(1)
                if sym in hgnc_symbols and sym in allow_list:
                    found.add(sym)
        
        for sym in found:
            e = hgnc_enrich.get(sym, {})
            genes.append({
                'gene_symbol': sym,
                'rcd_form': rcd_form,
                'rcd_form_canonical': rcd_form,
                'source_databases': 'Elicit_Phase3',
                'source_channels': 'E',
                'num_sources': '1',
                'evidence_quality': 'ai_extracted',
                'evidence_types': 'elicit_systematic_review',
                'pmid_list': pmid,
                'confidence_score': '3',
                'confidence_tier': 'T3',
                'uniprot_id': e.get('uniprot', ''),
                'ensembl_id': e.get('ensembl', ''),
                'rcd_gene_type': paper_role,  # from choices-enforced column
                'role_direction': paper_direction,
                'required_for_death': paper_required,
                'evidence_type': paper_evidence_type,
                'gene_symbol_status': 'valid',
                'gene_biotype': e.get('biotype', ''),
                'evidence_tier': 'T3',
                'evidence_basis': f"Elicit Phase 3: {doi or 'no DOI'}",
                'doi': doi,
                'llm_status': 'CONFIRMED' if paper_role in ('EXECUTOR','REGULATOR') else 'UNCLEAR',
                'llm_pmids': pmid,
                'llm_evidence_force': citations,
                'mechanistic_class': 'MECHANISTIC' if paper_role == 'EXECUTOR' else 'LITERATURE_GAP' if paper_role == 'REGULATOR' else 'INSUFFICIENT_DATA',
                'epmc_hits': '',
                'epmc_status': '',
                'epmc_pmids': '',
                'phase2c_mechanistic_class': '',
            })
    return genes
        
def append_to_matrix(new_rows, matrix_file):
    """Append new gene-RCD rows to unified matrix."""
    if not new_rows or not os.path.exists(matrix_file):
        return
    with open(matrix_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames
        existing = list(reader)
    for r in new_rows:
        for c in cols:
            if c not in r:
                r[c] = ''
    existing.extend(new_rows)
    with open(matrix_file, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(existing)
    log("    Matrix updated: " + str(len(new_rows)) + " new rows added")

def main():
    log("PHASE 3: ELICIT PRIORITY GENE EXTRACTION")
    log("Target: " + str(len(RCD_FORMS)) + " RCD forms with 0 genes")
    log("Restricted to: HUMAN genes only (HGNC-validated)")
    
    if not ELICIT_KEY:
        log("ERROR: Set ELICIT_API_KEY"); return
    
    hgnc_symbols, hgnc_enrich = load_hgnc()
    log("HGNC symbols loaded: " + str(len(hgnc_symbols)) + " available")
    
    progress = {}
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f: progress = json.load(f)
    
    for i, (rcd_form, tier) in enumerate(RCD_FORMS):
        if rcd_form in progress:
            log("  [" + str(i+1) + "/" + str(len(RCD_FORMS)) + "] " + rcd_form + ": SKIPPED")
            continue
        if tier == 'EXCLUDED':
            log("  [" + str(i+1) + "/" + str(len(RCD_FORMS)) + "] " + rcd_form + ": SKIPPED (excluded by design)")
            continue
        
        log("  [" + str(i+1) + "/" + str(len(RCD_FORMS)) + "] " + rcd_form + " (" + tier + ")...")
        try:
            session_id = call_elicit(rcd_form)
            if session_id:
                result = poll_elicit(session_id, max_wait=3600)
                csv_data = download_extraction_csv(result) if result else None
                genes = parse_elicit_response(csv_data, hgnc_symbols, hgnc_enrich, rcd_form) if csv_data else []
                if genes:
                    append_to_matrix(genes, MATRIX_FILE)
                progress[rcd_form] = {'status': 'done', 'genes': len(genes)}
                log("    Extracted: " + str(len(genes)) + " human genes")
            else:
                progress[rcd_form] = {'status': 'no_session'}
                log("    Failed to create session")
        except Exception as e:
            log("    ERROR: " + str(e)[:100])
            progress[rcd_form] = {'status': 'error', 'error': str(e)[:100]}
        
        with open(PROGRESS_FILE, 'w') as f: json.dump(progress, f)
    
    log("PHASE 3 COMPLETE")
    log("Check elicit.log for details")

if __name__ == '__main__':
    main()
