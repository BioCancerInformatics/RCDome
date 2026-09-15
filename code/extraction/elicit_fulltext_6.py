"""
elicit_fulltext_6.py — the SAME code that worked in elicit_fulltext_test.py +
download_extract.py, just looped over the 4 remaining pairs.

No new logic. Reused verbatim:
  - create_session body = identical to elicit_fulltext_test.py
  - CSV download       = identical to download_extract.py (data.extract.csv)
"""
import os, json, subprocess, csv, time, sys, io, urllib.request

ELICIT_KEY = os.environ.get('ELICIT_API_KEY', '')
ELICIT_URL = 'https://elicit.com/api/v2/sessions/systematic-reviews'

if not ELICIT_KEY:
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith('ELICIT_API_KEY='):
                ELICIT_KEY = line.split('=', 1)[1].strip()
if not ELICIT_KEY:
    print("ERROR: no key"); sys.exit(1)

PAIRS = [
    ('EIF2S1', 'Immunogenic cell death'),
    ('MT1X',   'Cuproptosis'),
    ('EPAS1',  'Ammonia-induced cell death'),
    ('BMP2',   'Senescence and Autophagy in Cancer'),
]

def create_session(gene, form):
    # IDENTICAL to elicit_fulltext_test.py's working body
    body = json.dumps({
        'researchQuestion': f'Does {gene} mechanistically associate with {form}?',
        'searches': [
            {'query': f'{gene} {form} mechanism', 'corpus': 'elicit', 'searchMode': 'semantic', 'maxResults': 30},
            {'query': f'{gene} role in {form}', 'corpus': 'elicit', 'searchMode': 'semantic', 'maxResults': 30},
        ],
        'abstractScreening': {'generate': True},
        'extraction': {
            'generate': False, 'useFigures': False,
            'questions': [
                {'name': 'gene_symbol', 'instructions': f'HGNC symbol. Focus on {gene}.'},
                {'name': 'mechanistic_role', 'instructions': f'Role of {gene} in {form}.', 'choices': ['EXECUTOR','REGULATOR','MARKER','UNCERTAIN']},
                {'name': 'evidence_type', 'instructions': 'Evidence type.', 'choices': ['GENETIC_PERTURBATION','PHARMACOLOGICAL','EXPRESSION_CORRELATION','CITATION_ONLY']},
                {'name': 'verbatim_sentence', 'instructions': f'Copy the EXACT sentence linking {gene} to {form}. Return null if none.'},
                {'name': 'role_direction', 'instructions': 'Direction.', 'choices': ['PROMOTES','PROTECTS','ASSOCIATED','BIDIRECTIONAL','UNCLEAR']},
                {'name': 'required_for_death', 'instructions': f'Is {gene} required for {form}?', 'choices': ['YES','PARTIAL','NO','NOT_TESTED','UNCLEAR']},
            ]
        },
        'generateReport': False,
    })
    r = subprocess.run(['curl','-s','-X','POST',ELICIT_URL,'-H','Authorization: Bearer '+ELICIT_KEY,
                        '-H','Content-Type: application/json','-d',body], capture_output=True, text=True, timeout=60)
    try:
        resp = json.loads(r.stdout)
        return resp.get('sessionId','') or resp.get('id','')
    except Exception:
        return ''

def get_extract_csv(session_id, max_minutes=20):
    # IDENTICAL to download_extract.py's working logic
    url = ELICIT_URL + '/' + session_id
    deadline = time.time() + max_minutes * 60
    while time.time() < deadline:
        r = subprocess.run(['curl','-s',url,'-H','Authorization: Bearer '+ELICIT_KEY],
                           capture_output=True, text=True, timeout=30)
        try:
            data = json.loads(r.stdout)
        except Exception:
            time.sleep(15); continue
        csv_url = data.get('data', {}).get('extract', {}).get('csv', '')
        if csv_url:
            rr = subprocess.run(['curl','-s',csv_url], capture_output=True, text=True, timeout=120)
            if rr.stdout.strip():
                return rr.stdout
        if data.get('status') in ('failed','cancelled'):
            return None
        time.sleep(15)
    return None

def analyze(csv_text, gene):
    if not csv_text:
        return ('NO_DATA','','','')
    for row in csv.DictReader(io.StringIO(csv_text)):
        gs = (row.get('gene_symbol','') or '').upper()
        verb = (row.get('verbatim_sentence','') or '').strip()
        doi = (row.get('DOI','') or '').strip()
        if gene in gs and verb and verb.lower() not in ('null','none','') and 'not mentioned' not in verb.lower():
            return ('PROVED', doi, '', verb)
    return ('DISPROVED','','','')

def main():
    results = []
    for gene, form in PAIRS:
        print(f"=== {gene} ↔ {form} (FULL-TEXT) ===", flush=True)
        sid = create_session(gene, form)
        if not sid:
            print("  session creation failed", flush=True)
            results.append({'gene': gene, 'form': form, 'status': 'ERROR'}); continue
        print(f"  session={sid}", flush=True)
        csv_text = get_extract_csv(sid)
        status, doi, pmid, verb = analyze(csv_text, gene)
        print(f"  {status}  doi={doi[:30]}  {verb[:80]}", flush=True)
        results.append({'gene': gene, 'form': form, 'status': status, 'doi': doi, 'verbatim_sentence': verb[:300]})

    with open('elicit_fulltext_6.json','w',encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    keys = ['gene','form','status','doi','verbatim_sentence']
    with open('elicit_fulltext_6.csv','w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        w.writeheader(); w.writerows(results)
    n = sum(1 for r in results if r['status'] == 'PROVED')
    print(f"\nPROVED: {n} | total: {len(results)}", flush=True)

if __name__ == '__main__':
    main()
