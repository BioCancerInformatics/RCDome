"""Fill the maxResults=100 and 500 gaps: governed records + unique genes.

Re-downloads both sessions' CSVs and runs the identical governance
(HGNC + allow-list via parse_elicit_response).
"""
import subprocess, json, urllib.request, io, os, csv
from collections import Counter
import channel_e_elicit_extract_benchmark_50 as ce

KEY = os.environ.get('ELICIT_API_KEY', '')
BASE = 'https://elicit.com/api/v2/sessions/systematic-reviews'

SESSIONS = {
    '100': '5578627a-531b-4919-8572-6d4dad7944b9',
    '500': '551a3b3e-77a0-43ec-b935-1ce7ac3b092e',
}

def download_csv(sid):
    r = subprocess.run(['curl', '-s', f'{BASE}/{sid}',
                        '-H', f'Authorization: Bearer {KEY}', '--max-time', '20'],
                       capture_output=True, text=True, timeout=30)
    resp = json.loads(r.stdout)
    status = resp.get('status', '')
    if status != 'completed':
        return None, status
    csv_url = resp.get('data', {}).get('extract', {}).get('csv', '')
    if not csv_url:
        return None, 'no csv url'
    req = urllib.request.Request(csv_url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    return urllib.request.urlopen(req, timeout=120).read().decode('utf-8-sig'), 'ok'

hgnc_symbols, hgnc_enrich = ce.load_hgnc()
print(f'HGNC loaded: {len(hgnc_symbols)}\n')

for label, sid in SESSIONS.items():
    csv_data, status = download_csv(sid)
    if csv_data is None:
        print(f'maxResults={label}: status={status} (cannot parse)')
        continue
    rows = list(csv.DictReader(io.StringIO(csv_data)))
    papers = len(set(r.get('Title', '').strip() for r in rows if r.get('Title', '').strip()))
    genes = ce.parse_elicit_response(csv_data, hgnc_symbols, hgnc_enrich, 'Ferroptosis')
    unique = set(g['gene_symbol'] for g in genes)
    roles = Counter(g.get('rcd_gene_type', '') for g in genes)
    print(f'maxResults={label}: papers={papers} records={len(genes)} unique_genes={len(unique)}')
    print(f'  roles={dict(roles)}')
    print()
