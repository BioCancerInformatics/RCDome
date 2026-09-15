"""Verify: do Elicit extraction CSV rows = papers, or gene-paper pairs?

Fetches the session, downloads the CSV, and counts:
  - total rows
  - unique DOIs
  - unique Titles
  - papers in search/screen stage
"""
import subprocess, json, urllib.request, csv, io, os

KEY = os.environ.get('ELICIT_API_KEY', '')
SID = '55330187-e06f-49a5-b383-7e575ac1cd16'
BASE = 'https://elicit.com/api/v2/sessions/systematic-reviews'

# 1. Fetch session
r = subprocess.run(['curl', '-s', f'{BASE}/{SID}',
                    '-H', f'Authorization: Bearer {KEY}',
                    '--max-time', '20'],
                   capture_output=True, text=True, timeout=30)
resp = json.loads(r.stdout)
data = resp.get('data', {})

# 2. Search/screen paper counts
search = data.get('search', {})
screen = data.get('screen', {})
print('search keys:', list(search.keys()) if isinstance(search, dict) else type(search))
print('screen keys:', list(screen.keys()) if isinstance(screen, dict) else type(screen))

# Try to count papers in search/screen
for name, obj in [('search', search), ('screen', screen)]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, list):
                print(f'{name}.{k}: {len(v)} items')

# 3. Download CSV and count
csv_url = data.get('extract', {}).get('csv', '')
if not csv_url:
    print('No CSV URL found')
    exit()

req = urllib.request.Request(csv_url)
req.add_header('User-Agent', 'Mozilla/5.0')
csv_data = urllib.request.urlopen(req, timeout=60).read().decode('utf-8-sig')
rows = list(csv.DictReader(io.StringIO(csv_data)))

total = len(rows)
dois = set(r.get('DOI', '') for r in rows if r.get('DOI', '').strip())
titles = set(r.get('Title', '') for r in rows if r.get('Title', '').strip())

print(f'\nCSV total rows: {total}')
print(f'Unique DOIs: {len(dois)}')
print(f'Unique Titles: {len(titles)}')

if total == len(titles):
    print('\nVERDICT: rows = papers (one row per paper, genes in a cell)')
else:
    print(f'\nVERDICT: rows != papers ({total} rows vs {len(titles)} papers) -> multiple rows per paper (gene-paper pairs)')

# Show a sample: first paper's gene_symbol cell
if rows:
    gs = rows[0].get('gene_symbol', '')
    print(f'\nSample gene_symbol cell (first row): {gs[:200]!r}')
