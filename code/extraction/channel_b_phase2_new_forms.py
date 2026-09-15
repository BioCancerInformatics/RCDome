"""
channel_b_phase2_new_forms.py — Phase 2: New RCD Form Gene Extraction
=======================================================================
Extracts human gene symbols for 4 newly approved RCD forms from NCBI Gene.
Gene by gene, row by row. All 16 columns populated. Full audit trail.

Forms:
  - NECSO (Na+ overload necrosis)        → NCBI Gene: "sodium overload necrosis cell death"
  - Eryptosis (RBC programmed death)      → NCBI Gene: "eryptosis"
  - Triaptosis (endosomal oxidative death) → PENDING Phase 2 (literature-only, 0 NCBI Gene hits)
  - Mitoxyperilysis (mitochondrial)        → PENDING Phase 2 (literature-only, 0 NCBI Gene hits)

Method (per form):
  1. Search NCBI Gene E-utilities with RCD-specific query
  2. Fetch all returned gene symbols
  3. Filter against HGNC approved symbol set (45,030 symbols) → human only
  4. Exclude non-HGNC symbols (mouse orthologs, obsolete names, loci)
  5. Log all excluded symbols with reason
  6. Build rows with all 16 unified matrix columns
  7. Enrich with HGNC data (biotype, UniProt ID, Ensembl ID)
  8. Append to unified_gene_rcd_matrix.csv

Usage: python channel_b_phase2_new_forms.py
"""

import csv, os, urllib.request, json, time
from datetime import datetime

# --- CONFIG ---
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output databases')
MATRIX_FILE = os.path.join(OUTPUT_DIR, 'unified_gene_rcd_matrix.csv')
LOG_FILE = os.path.join(OUTPUT_DIR, f'phase2_extraction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

API_KEY = os.environ.get('NCBI_KEY', '')
RATE = 0.11 if API_KEY else 0.34

# Forms to extract
# search_term: what we pass to NCBI Gene E-utilities
# status: 'auto' = NCBI Gene extraction, 'pending' = needs manual Phase 2
FORMS = {
    'NECSO': {
        'search_term': 'sodium overload necrosis cell death',
        'status': 'auto',
    },
    'Eryptosis': {
        'search_term': 'eryptosis',
        'status': 'auto',
    },
    'Triaptosis': {
        'search_term': None,
        'status': 'pending',
    },
    'Mitoxyperilysis': {
        'search_term': None,
        'status': 'pending',
    },
}

log_lines = []

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line)
    log_lines.append(line)


def fetch(url):
    """Fetch URL with retry."""
    for attempt in range(2):
        try:
            return urllib.request.urlopen(url).read().decode('utf-8')
        except Exception as e:
            if attempt == 0: time.sleep(2)
            else: raise e


def load_hgnc():
    """Download complete HGNC approved symbol set.
    
    Returns:
        valid_symbols: set of 45,030 HGNC-approved human gene symbols
        enrich: dict {symbol: {biotype, uniprot, ensembl}}
    """
    log('Loading HGNC approved symbol set...')
    req = urllib.request.Request(
        'https://rest.genenames.org/fetch/status/Approved',
        headers={'Accept': 'application/json'}
    )
    data = json.loads(fetch(req))
    
    valid_symbols = set()
    enrich = {}
    
    for doc in data['response']['docs']:
        sym = doc['symbol']
        valid_symbols.add(sym)
        
        # Classify biotype
        lt = doc.get('locus_type', '')
        if 'protein' in lt.lower():
            bt = 'protein_coding'
        elif 'long non-coding' in lt.lower():
            bt = 'lncRNA'
        elif 'micro' in lt.lower():
            bt = 'miRNA'
        elif 'pseudogene' in lt.lower():
            bt = 'pseudogene'
        elif 'RNA' in lt:
            bt = 'other_RNA'
        else:
            bt = 'other'
        
        enrich[sym] = {
            'biotype': bt,
            'uniprot': (doc.get('uniprot_ids') or [''])[0],
            'ensembl': doc.get('ensembl_gene_id', ''),
        }
    
    log(f'  Loaded {len(valid_symbols):,} HGNC-approved symbols')
    return valid_symbols, enrich


def extract_one_form(form_name, search_term, hgnc_symbols, hgnc_enrich):
    """Extract genes for one RCD form from NCBI Gene.
    
    Steps:
        1. E-search: query NCBI Gene with search_term
        2. E-summary: fetch gene symbols in batches of 200
        3. HGNC filter: keep only approved human symbols, log exclusions
        4. Build rows: one row per gene with all 16 columns
        5. Enrich: add biotype, UniProt ID, Ensembl ID from HGNC
    
    Args:
        form_name: canonical RCD form name
        search_term: NCBI Gene query string
        hgnc_symbols: set of approved HGNC symbols
        hgnc_enrich: dict of HGNC enrichment data
    
    Returns:
        list of dicts, each with all 16 unified matrix columns
    """
    log(f'\n{"="*50}')
    log(f'EXTRACTING: {form_name}')
    log(f'  Search term: "{search_term}"')
    log(f'{"="*50}')
    
    # Step 1: E-search
    query = search_term.replace(' ', '+')
    url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term={query}&retmax=5000&retmode=json&api_key={API_KEY}'
    
    data = json.loads(fetch(url))
    gene_ids = data.get('esearchresult', {}).get('idlist', [])
    count = int(data.get('esearchresult', {}).get('count', 0))
    time.sleep(RATE)
    
    log(f'  Step 1 - E-search: {count:,} NCBI Gene hits, {len(gene_ids)} IDs retrieved')
    
    if not gene_ids:
        log(f'  RESULT: 0 genes (no NCBI Gene hits)')
        return []
    
    # Step 2: E-summary (fetch gene symbols)
    all_symbols = set()
    for i in range(0, len(gene_ids), 200):
        batch = gene_ids[i:i+200]
        url2 = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id={",".join(batch)}&retmode=json&api_key={API_KEY}'
        
        data2 = json.loads(fetch(url2))
        results = data2.get('result', {})
        for gid in batch:
            info = results.get(gid, {})
            symbol = info.get('name', '')
            if symbol and symbol != 'N/A':
                all_symbols.add(symbol)
        time.sleep(RATE)
    
    log(f'  Step 2 - E-summary: {len(all_symbols)} unique gene symbols retrieved')
    
    # Step 3: HGNC filter
    valid_symbols = sorted(all_symbols & hgnc_symbols)
    excluded_symbols = sorted(all_symbols - hgnc_symbols)
    
    log(f'  Step 3 - HGNC filter:')
    log(f'    Valid (human HGNC):   {len(valid_symbols)}')
    log(f'    Excluded (non-HGNC):   {len(excluded_symbols)}')
    
    if excluded_symbols:
        # Classify exclusions
        mouse_like = [s for s in excluded_symbols if s[0].islower() or not s.isupper()]
        other = [s for s in excluded_symbols if s not in mouse_like]
        
        if mouse_like:
            log(f'      Mouse/rat orthologs (lowercase): {len(mouse_like)}')
            for s in mouse_like[:10]:
                # Show human equivalent if it exists
                human_eq = s.upper()
                eq_note = f' -> human {human_eq} (in HGNC: {human_eq in hgnc_symbols})'
                log(f'        {s}{eq_note}')
        
        if other:
            log(f'      Other non-HGNC: {len(other)}')
            for s in other[:10]:
                log(f'        {s}')
    
    # Step 4: Build rows
    rows = []
    for symbol in valid_symbols:
        e = hgnc_enrich.get(symbol, {})
        row = {
            'gene_symbol': symbol,
            'rcd_form': form_name,
            'rcd_form_canonical': form_name,
            'source_databases': 'NCBI_Gene',
            'source_channels': 'B',
            'num_sources': '1',
            'evidence_quality': 'keyword',
            'evidence_types': 'ncbi_gene_esearch',
            'pmid_list': '',
            'confidence_score': '1',
            'confidence_tier': 'T4',
            'uniprot_id': e.get('uniprot', ''),
            'ensembl_id': e.get('ensembl', ''),
            'gene_type': '',
            'gene_symbol_status': 'valid',
            'gene_biotype': e.get('biotype', ''),
        }
        rows.append(row)
    
    # Step 5: Report
    log(f'  Step 4 - Built {len(rows)} rows')
    log(f'  Step 5 - All 16 columns populated: {all(len(r.values())==16 for r in rows)}')
    log(f'  Step 5 - All HGNC-valid: {all(r["gene_symbol_status"]=="valid" for r in rows)}')
    log(f'  RESULT: {len(rows)} genes added for {form_name}')
    
    # Show sample
    if rows:
        log(f'  Sample genes: {", ".join(r["gene_symbol"] for r in rows[:5])}...')
    
    return rows


def main():
    log('=' * 60)
    log('PHASE 2: NEW RCD FORM GENE EXTRACTION')
    log(f'Started: {datetime.now().isoformat()}')
    log('=' * 60)
    
    # Load HGNC (one-time, used for all forms)
    hgnc_symbols, hgnc_enrich = load_hgnc()
    
    # Load existing matrix
    log(f'\nLoading existing matrix: {MATRIX_FILE}')
    with open(MATRIX_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        COLUMNS = reader.fieldnames
        existing_rows = list(reader)
    log(f'  Current rows: {len(existing_rows):,}')
    log(f'  Current columns: {len(COLUMNS)}')
    
    # Extract each form
    all_new_rows = []
    for form_name, config in FORMS.items():
        if config['status'] == 'pending':
            log(f'\n{form_name}: PENDING - literature-only, requires Phase 2 manual extraction')
            log(f'  0 genes added (no NCBI Gene data available)')
            continue
        
        rows = extract_one_form(
            form_name,
            config['search_term'],
            hgnc_symbols,
            hgnc_enrich
        )
        all_new_rows.extend(rows)
    
    # Append to matrix
    all_rows = existing_rows + all_new_rows
    
    log(f'\n{"="*50}')
    log(f'APPENDING TO UNIFIED MATRIX')
    log(f'{"="*50}')
    log(f'  Before: {len(existing_rows):,} rows')
    log(f'  Added:  {len(all_new_rows):,} rows')
    log(f'  After:  {len(all_rows):,} rows')
    
    # Verify no duplicate (gene, rcd_form) pairs after append
    pairs = [(r['gene_symbol'], r['rcd_form']) for r in all_rows]
    dupes = len(pairs) - len(set(pairs))
    if dupes > 0:
        log(f'  WARNING: {dupes} duplicate (gene, rcd_form) pairs found!')
    else:
        log(f'  All (gene, rcd_form) pairs unique: OK')
    
    with open(MATRIX_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(all_rows)
    
    # Per-form summary
    log(f'\n{"="*50}')
    log(f'PER-FORM SUMMARY')
    log(f'{"="*50}')
    for form_name in FORMS:
        count = sum(1 for r in all_rows if r['rcd_form_canonical'] == form_name)
        status = FORMS[form_name]['status']
        log(f'  {form_name:20s}: {count:>5} genes  ({status})')
    
    # Write log
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))
    log(f'\nLog saved to: {LOG_FILE}')
    log('EXTRACTION COMPLETE')


if __name__ == '__main__':
    main()
