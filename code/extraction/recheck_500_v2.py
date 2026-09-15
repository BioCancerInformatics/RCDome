"""Careful re-count of maxResults=500 session: rows, unique DOIs, unique titles."""
import subprocess, json, urllib.request, io, os, csv

KEY = os.environ.get('ELICIT_API_KEY', '')
SID = '551a3b3e-77a0-43ec-b935-1ce7ac3b092e'
BASE = 'https://elicit.com/api/v2/sessions/systematic-reviews'

r = subprocess.run(['curl', '-s', f'{BASE}/{SID}',
                    '-H', f'Authorization: Bearer {KEY}', '--max-time', '20'],
                   capture_output=True, text=True, timeout=30)
resp = json.loads(r.stdout)
print('status:', resp.get('status', ''))

csv_url = resp.get('data', {}).get('extract', {}).get('csv', '')
if not csv_url:
    print('No CSV'); exit()

req = urllib.request.Request(csv_url)
req.add_header('User-Agent', 'Mozilla/5.0')
csv_data = urllib.request.urlopen(req, timeout=60).read().decode('utf-8-sig')

rows = list(csv.DictReader(io.StringIO(csv_data)))
total = len(rows)
dois = set(r.get('DOI', '').strip() for r in rows if r.get('DOI', '').strip())
titles = set(r.get('Title', '').strip() for r in rows if r.get('Title', '').strip())

print('rows_total:', total)
print('unique_DOIs:', len(dois))
print('unique_titles:', len(titles))

print('\nSample of first 3 titles:')
for r in rows[:3]:
    print('  ', repr(r.get('Title', '')[:80]))

print('\nREFERENCE:')
print('  maxResults=50   -> 67 papers')
print('  maxResults=100  -> 148 papers')
print('  omitted         -> 315 papers')
print('  maxResults=500  -> ?')
