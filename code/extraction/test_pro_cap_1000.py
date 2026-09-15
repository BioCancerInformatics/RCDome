"""Pro-plan cap test: maxResults=1000 per search (4 searches = 4000 candidates).

Measures: papers screened, governed records, unique genes.
Uses the SAME governance (HGNC + allow-list) as the benchmark.
Long poll (up to 3600s) — 4000 papers takes a while.
"""
import subprocess, json, urllib.request, io, os, csv, time
from collections import Counter
import channel_e_elicit_extract_benchmark_50 as ce

KEY = os.environ.get('ELICIT_API_KEY', '')
BASE = 'https://elicit.com/api/v2/sessions/systematic-reviews'

def call_elicit(maxr):
    body = json.dumps({
        "researchQuestion": "Gene-Ferroptosis associations in closed allow-list",
        "searches": [
            {"query": "Ferroptosis regulated cell death mechanism", "corpus": "pubmed", "searchMode": "semantic", "maxResults": maxr},
            {"query": "Ferroptosis genetic perturbation CRISPR knockout knockdown", "corpus": "pubmed", "searchMode": "semantic", "maxResults": maxr},
            {"query": "Ferroptosis pharmacological inhibitor drug mechanism", "corpus": "pubmed", "searchMode": "semantic", "maxResults": maxr},
            {"query": "Ferroptosis gene expression correlation biomarker", "corpus": "elicit", "searchMode": "semantic", "maxResults": maxr}
        ],
        "abstractScreening": {"generate": True},
        "extraction": {
            "generate": False,
            "useFigures": False,
            "questions": [
                {"name": "gene_symbol", "instructions": "HGNC gene symbol from paper. Return null if none."},
                {"name": "mechanistic_role", "instructions": "EXECUTOR if KD/KO changes Ferroptosis death. REGULATOR if modulates. MARKER if correlation only.", "choices": ["EXECUTOR", "REGULATOR", "MARKER", "UNCERTAIN"]},
                {"name": "evidence_type", "instructions": "Type: GENETIC_PERTURBATION, PHARMACOLOGICAL, EXPRESSION_CORRELATION, CITATION_ONLY.", "choices": ["GENETIC_PERTURBATION", "PHARMACOLOGICAL", "EXPRESSION_CORRELATION", "CITATION_ONLY"]},
                {"name": "verbatim_sentence", "instructions": "Copy EXACT sentence linking gene to Ferroptosis. Return null if inaccessible."},
                {"name": "role_direction", "instructions": "PROMOTES if gene increases Ferroptosis, PROTECTS if reduces.", "choices": ["PROMOTES", "PROTECTS", "ASSOCIATED", "BIDIRECTIONAL", "UNCLEAR"]},
                {"name": "required_for_death", "instructions": "Is gene required for Ferroptosis execution? YES only with perturbation data.", "choices": ["YES", "PARTIAL", "NO", "NOT_TESTED", "UNCLEAR"]}
            ]
        },
        "generateReport": False
    })
    cmd = ['curl', '-s', '-X', 'POST', BASE,
           '-H', 'Authorization: Bearer ' + KEY,
           '-H', 'Content-Type: application/json', '-d', body]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    resp = json.loads(r.stdout)
    sid = resp.get('sessionId', '')
    if not sid:
        print('SESSION CREATION FAILED:', r.stdout[:300])
    return sid

sid = call_elicit(1000)
print(f'maxResults=1000: session={sid}')
if not sid:
    exit()

# Poll (up to 60 min)
waited = 0
while waited < 3600:
    time.sleep(30)
    waited += 30
    r = subprocess.run(['curl', '-s', f'{BASE}/{sid}',
                        '-H', f'Authorization: Bearer {KEY}', '--max-time', '20'],
                       capture_output=True, text=True, timeout=30)
    resp = json.loads(r.stdout)
    status = resp.get('status', '')
    print(f'[{waited}s] status={status}', flush=True)
    if status == 'completed':
        break
    if status == 'failed':
        print('SESSION FAILED'); exit()

csv_url = resp.get('data', {}).get('extract', {}).get('csv', '')
if not csv_url:
    print('No CSV URL'); exit()

req = urllib.request.Request(csv_url)
req.add_header('User-Agent', 'Mozilla/5.0')
csv_data = urllib.request.urlopen(req, timeout=120).read().decode('utf-8-sig')

# Save raw
with open('ferroptosis_max1000_raw.csv', 'w', encoding='utf-8') as f:
    f.write(csv_data)

rows = list(csv.DictReader(io.StringIO(csv_data)))
titles = set(r.get('Title', '').strip() for r in rows if r.get('Title', '').strip())
dois = set(r.get('DOI', '').strip() for r in rows if r.get('DOI', '').strip())

# Governed parse
hgnc_symbols, hgnc_enrich = ce.load_hgnc()
genes = ce.parse_elicit_response(csv_data, hgnc_symbols, hgnc_enrich, 'Ferroptosis')
unique_genes = set(g['gene_symbol'] for g in genes)
roles = Counter(g.get('rcd_gene_type', '') for g in genes)

print('\nRESULT (maxResults=1000):')
print(f'  rows={len(rows)}')
print(f'  unique_titles={len(titles)}')
print(f'  unique_DOIs={len(dois)}')
print(f'  governed_records={len(genes)}')
print(f'  unique_genes={len(unique_genes)}')
print(f'  roles={dict(roles)}')

print('\nFULL SERIES:')
print('  maxResults=50   -> 67 papers, 393 records, 223 genes')
print('  maxResults=100  -> 148 papers')
print('  maxResults=200  -> 315 papers, 1257 records, 424 genes')
print('  maxResults=500  -> 876 papers')
print(f'  maxResults=1000 -> {len(titles)} papers, {len(genes)} records, {len(unique_genes)} genes')
