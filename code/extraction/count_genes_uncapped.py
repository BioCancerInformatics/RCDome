"""Count genes per paper in the uncapped Ferroptosis extraction CSV.

Does NOT assume the gene_symbol cell format. Inspects samples first,
then counts with the detected delimiter.
"""
import subprocess, json, urllib.request, csv, io, os, re
from collections import Counter

KEY = os.environ.get('ELICIT_API_KEY', '')
SID = '55330187-e06f-49a5-b383-7e575ac1cd16'
BASE = 'https://elicit.com/api/v2/sessions/systematic-reviews'

# Fetch session + CSV
r = subprocess.run(['curl', '-s', f'{BASE}/{SID}',
                    '-H', f'Authorization: Bearer {KEY}',
                    '--max-time', '20'],
                   capture_output=True, text=True, timeout=30)
resp = json.loads(r.stdout)
csv_url = resp.get('data', {}).get('extract', {}).get('csv', '')
if not csv_url:
    print('No CSV URL'); exit()

req = urllib.request.Request(csv_url)
req.add_header('User-Agent', 'Mozilla/5.0')
csv_data = urllib.request.urlopen(req, timeout=60).read().decode('utf-8-sig')
rows = list(csv.DictReader(io.StringIO(csv_data)))

print(f'Total rows: {len(rows)}')
print(f'Unique titles: {len(set(r.get("Title","") for r in rows if r.get("Title","").strip()))}')

# Inspect gene_symbol cell format
gs_cells = [r.get('gene_symbol', '') for r in rows if r.get('gene_symbol', '').strip()]
empty = len(rows) - len(gs_cells)
print(f'\nNon-empty gene_symbol cells: {len(gs_cells)}')
print(f'Empty gene_symbol cells: {empty}')

print('\n--- Sample gene_symbol cells (first 10 non-empty) ---')
for c in gs_cells[:10]:
    print(f'  {c!r}')

# Detect delimiter: check for newline, comma, semicolon, pipe
newline_cells = sum(1 for c in gs_cells if '\n' in c)
comma_cells = sum(1 for c in gs_cells if ',' in c)
semicolon_cells = sum(1 for c in gs_cells if ';' in c)
pipe_cells = sum(1 for c in gs_cells if '|' in c)
print(f'\nCells with newline: {newline_cells}')
print(f'Cells with comma: {comma_cells}')
print(f'Cells with semicolon: {semicolon_cells}')
print(f'Cells with pipe: {pipe_cells}')

# Count genes: split on newline AND comma (most likely delimiters)
all_genes = []
for c in gs_cells:
    parts = re.split(r'[\n,;|]+', c)
    for p in parts:
        p = p.strip()
        if p:
            all_genes.append(p)

print(f'\nTotal gene tokens (split on newline/comma/semicolon/pipe): {len(all_genes)}')
print(f'Unique gene symbols: {len(set(all_genes))}')

# Distribution
per_paper = Counter()
for c in gs_cells:
    parts = [p.strip() for p in re.split(r'[\n,;|]+', c) if p.strip()]
    per_paper[len(parts)] += 1

print(f'\nGenes per paper distribution (top 15):')
for n, cnt in sorted(per_paper.items())[:15]:
    print(f'  {n} gene(s): {cnt} papers')

print(f'\nTotal papers with >=1 gene: {sum(per_paper.values())}')
print(f'Papers with 0 genes (empty cell): {empty}')
