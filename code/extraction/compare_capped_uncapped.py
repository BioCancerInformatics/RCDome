"""Complete side-by-side governed comparison: capped vs uncapped Ferroptosis.

Re-downloads BOTH sessions' extraction CSVs and runs each through the
IDENTICAL governance (HGNC + allow-list via parse_elicit_response).
Reports papers, records, unique genes — no gaps, no guessing.
"""
import subprocess, json, urllib.request, io, os, csv
from collections import Counter
import channel_e_elicit_extract_benchmark_50 as ce

KEY = os.environ.get('ELICIT_API_KEY', '')
BASE = 'https://elicit.com/api/v2/sessions/systematic-reviews'

SESSIONS = {
    'Capped (50/search)':   '554c864f-a751-48d1-911b-95fe1e8de345',
    'Uncapped':             '55330187-e06f-49a5-b383-7e575ac1cd16',
}

def download_csv(sid):
    r = subprocess.run(['curl', '-s', f'{BASE}/{sid}',
                        '-H', f'Authorization: Bearer {KEY}', '--max-time', '20'],
                       capture_output=True, text=True, timeout=30)
    resp = json.loads(r.stdout)
    csv_url = resp.get('data', {}).get('extract', {}).get('csv', '')
    if not csv_url:
        return None
    req = urllib.request.Request(csv_url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    return urllib.request.urlopen(req, timeout=60).read().decode('utf-8-sig')

hgnc_symbols, hgnc_enrich = ce.load_hgnc()
print(f'HGNC loaded: {len(hgnc_symbols)}\n')

results = {}
for label, sid in SESSIONS.items():
    csv_data = download_csv(sid)
    if not csv_data:
        print(f'{label}: FAILED to download CSV')
        continue
    rows = list(csv.DictReader(io.StringIO(csv_data)))
    papers = len(set(r.get('Title', '') for r in rows if r.get('Title', '').strip()))
    genes = ce.parse_elicit_response(csv_data, hgnc_symbols, hgnc_enrich, 'Ferroptosis')
    unique = set(g['gene_symbol'] for g in genes)
    roles = Counter(g.get('rcd_gene_type', '') for g in genes)
    results[label] = {
        'rows': len(rows), 'papers': papers, 'records': len(genes),
        'unique_genes': len(unique), 'roles': dict(roles),
    }
    print(f'{label}:')
    print(f'  rows={len(rows)} papers={papers} records={len(genes)} unique_genes={len(unique)}')
    print(f'  roles={dict(roles)}')
    print()

print('=' * 60)
print('VERIFIED COMPARISON')
print('=' * 60)
if len(results) == 2:
    cap = results['Capped (50/search)']
    unc = results['Uncapped']
    for k in ['papers', 'records', 'unique_genes']:
        print(f'  {k}: capped={cap[k]} uncapped={unc[k]} ratio={unc[k]/cap[k]:.2f}x')
