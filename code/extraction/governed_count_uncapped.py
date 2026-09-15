"""Governed count: run uncapped Ferroptosis extraction CSV through the SAME
governance pipeline as the capped benchmark (HGNC + allow-list), giving a
record count directly comparable to the benchmark's 393.

Reuses parse_elicit_response from channel_e_elicit_extract.py — no reimplementation.
Saves the raw CSV to disk for traceability.
"""
import subprocess, json, urllib.request, io, os, csv
import channel_e_elicit_extract_benchmark_50 as ce

KEY = os.environ.get('ELICIT_API_KEY', '')
SID = '55330187-e06f-49a5-b383-7e575ac1cd16'
BASE = 'https://elicit.com/api/v2/sessions/systematic-reviews'

# 1. Download CSV
r = subprocess.run(['curl', '-s', f'{BASE}/{SID}',
                    '-H', f'Authorization: Bearer {KEY}', '--max-time', '20'],
                   capture_output=True, text=True, timeout=30)
resp = json.loads(r.stdout)
csv_url = resp.get('data', {}).get('extract', {}).get('csv', '')
if not csv_url:
    print('No CSV URL'); exit()

req = urllib.request.Request(csv_url)
req.add_header('User-Agent', 'Mozilla/5.0')
csv_data = urllib.request.urlopen(req, timeout=60).read().decode('utf-8-sig')

# 2. Save raw CSV to disk (traceability)
raw_path = 'uncapped_ferroptosis_extract_raw.csv'
with open(raw_path, 'w', encoding='utf-8') as f:
    f.write(csv_data)
print(f'Saved raw CSV: {raw_path}')

rows = list(csv.DictReader(io.StringIO(csv_data)))
print(f'Raw rows: {len(rows)}')
print(f'Unique titles: {len(set(r.get("Title","") for r in rows if r.get("Title","").strip()))}')

# 3. Load HGNC
hgnc_symbols, hgnc_enrich = ce.load_hgnc()
print(f'HGNC symbols loaded: {len(hgnc_symbols)}')

# 4. Governed parse (allow-list + HGNC, same as benchmark)
genes = ce.parse_elicit_response(csv_data, hgnc_symbols, hgnc_enrich, 'Ferroptosis')
print(f'\nGOVERNED RECORDS (HGNC + allow-list): {len(genes)}')

# 5. Breakdown
from collections import Counter
roles = Counter(g.get('rcd_gene_type', '') for g in genes)
print(f'Role distribution: {dict(roles)}')

unique_genes = set(g['gene_symbol'] for g in genes)
print(f'Unique genes: {len(unique_genes)}')

# Save governed records to CSV
if genes:
    out = 'uncapped_ferroptosis_governed.csv'
    with open(out, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(genes[0].keys()))
        w.writeheader()
        w.writerows(genes)
    print(f'Saved governed records: {out}')

print('\nCOMPARISON:')
print(f'  Capped (67 papers):   393 governed records')
print(f'  Uncapped (315 papers): {len(genes)} governed records')
