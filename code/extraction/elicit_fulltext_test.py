"""
elicit_fulltext_test.py — SINGLE test pair (DFFA) to verify that the corpus 'elicit'
session returns FULL-TEXT verbatim sentences before running the other 5.

Saves the raw extraction CSV so you can inspect it. Run on Zima.
"""
import os, json, subprocess, csv, time, sys, io

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

GENE, FORM = 'DFFA', 'Programmed cell death'

body = json.dumps({
    'researchQuestion': f'Does {GENE} mechanistically associate with {FORM}?',
    'searches': [
        {'query': f'{GENE} {FORM} mechanism', 'corpus': 'elicit', 'searchMode': 'semantic', 'maxResults': 30},
        {'query': f'{GENE} role in {FORM}', 'corpus': 'elicit', 'searchMode': 'semantic', 'maxResults': 30},
    ],
    'abstractScreening': {'generate': True},
    'extraction': {
        'generate': False, 'useFigures': False,
        'questions': [
            {'name': 'gene_symbol', 'instructions': f'HGNC symbol. Focus on {GENE}.'},
            {'name': 'mechanistic_role', 'instructions': f'Role of {GENE} in {FORM}.', 'choices': ['EXECUTOR','REGULATOR','MARKER','UNCERTAIN']},
            {'name': 'evidence_type', 'instructions': 'Evidence type.', 'choices': ['GENETIC_PERTURBATION','PHARMACOLOGICAL','EXPRESSION_CORRELATION','CITATION_ONLY']},
            {'name': 'verbatim_sentence', 'instructions': f'Copy the EXACT sentence linking {GENE} to {FORM}. Return null if none.'},
            {'name': 'role_direction', 'instructions': 'Direction.', 'choices': ['PROMOTES','PROTECTS','ASSOCIATED','BIDIRECTIONAL','UNCLEAR']},
            {'name': 'required_for_death', 'instructions': f'Is {GENE} required for {FORM}?', 'choices': ['YES','PARTIAL','NO','NOT_TESTED','UNCLEAR']},
        ]
    },
    'generateReport': False,
})

print(f"=== TEST: {GENE} ↔ {FORM} (corpus 'elicit', full-text) ===")
r = subprocess.run(['curl','-s','-X','POST',ELICIT_URL,'-H','Authorization: Bearer '+ELICIT_KEY,
                    '-H','Content-Type: application/json','-d',body], capture_output=True, text=True, timeout=60)
try:
    resp = json.loads(r.stdout)
    sid = resp.get('sessionId','') or resp.get('id','')
    if not sid:
        print("POST response (no sessionId):", r.stdout[:400])
except Exception as e:
    print("session create failed:", e, "| raw:", r.stdout[:300]); sys.exit(1)
print(f"session={sid}")

url = ELICIT_URL + '/' + sid
deadline = time.time() + 20*60
csv_text = None
while time.time() < deadline:
    rr = subprocess.run(['curl','-s',url,'-H','Authorization: Bearer '+ELICIT_KEY],
                        capture_output=True, text=True, timeout=30)
    try:
        data = json.loads(rr.stdout)
    except Exception:
        time.sleep(15); continue
    rows = data.get('extraction', {}).get('rows') or data.get('rows') or []
    if rows:
        buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        w.writeheader(); [w.writerow(x) for x in rows]; csv_text = buf.getvalue(); break
    cu = data.get('extraction', {}).get('csvUrl') or data.get('csvUrl') or ''
    if cu:
        cr = subprocess.run(['curl','-s',cu], capture_output=True, text=True, timeout=60)
        if cr.stdout.strip():
            csv_text = cr.stdout; break
    if data.get('status') in ('failed','cancelled'):
        print("session failed:", data); break
    time.sleep(15)

if csv_text:
    open('elicit_fulltext_test_dffa.csv','w',encoding='utf-8').write(csv_text)
    print("\n=== RAW EXTRACTION (first rows) — check if verbatim is body-level ===")
    reader = list(csv.DictReader(io.StringIO(csv_text)))
    print(f"rows: {len(reader)}")
    for row in reader[:5]:
        print(f"\n  gene_symbol: {row.get('gene_symbol','')}")
        print(f"  role: {row.get('mechanistic_role','')} | dir: {row.get('role_direction','')} | ev: {row.get('evidence_type','')}")
        print(f"  DOI: {row.get('DOI','')} | Title: {(row.get('Title','') or '')[:60]}")
        print(f"  verbatim: {(row.get('verbatim_sentence','') or '')[:200]}")
    print("\nSaved elicit_fulltext_test_dffa.csv")
else:
    print("no CSV after polling")
