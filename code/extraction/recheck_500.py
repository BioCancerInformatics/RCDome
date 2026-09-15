"""Re-check the maxResults=500 session status and count papers if completed."""
import subprocess, json, urllib.request, io, os, csv

KEY = os.environ.get('ELICIT_API_KEY', '')
SID = '551a3b3e-77a0-43ec-b935-1ce7ac3b092e'
BASE = 'https://elicit.com/api/v2/sessions/systematic-reviews'

r = subprocess.run(['curl', '-s', f'{BASE}/{SID}',
                    '-H', f'Authorization: Bearer {KEY}', '--max-time', '20'],
                   capture_output=True, text=True, timeout=30)
resp = json.loads(r.stdout)
status = resp.get('status', '')
print(f'status: {status}')

if status == 'completed':
    csv_url = resp.get('data', {}).get('extract', {}).get('csv', '')
    if csv_url:
        req = urllib.request.Request(csv_url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        csv_data = urllib.request.urlopen(req, timeout=60).read().decode('utf-8-sig')
        rows = list(csv.DictReader(io.StringIO(csv_data)))
        papers = len(set(r.get('Title', '') for r in rows if r.get('Title', '').strip()))
        print(f'rows={len(rows)} papers={papers}')
        print(f'\nREFERENCE: omitted=315, maxResults=100=148, maxResults=50=67')
