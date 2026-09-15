"""Recover the 3 completed sessions' CSVs (proves the delay hypothesis + saves money)."""
import subprocess, json, os, urllib.request, io, csv
import sys

# Absolute .env path (NOT expanduser — Python HOME differs from shell ~ on Zima)
ENV = '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/extraction code snippets/.env'
key = ''
for line in open(ENV):
    if line.startswith('ELICIT_API_KEY='):
        key = line.split('=', 1)[1].strip()
        break

print(f'Key loaded: {key[:12]}... (len={len(key)})')

BASE = 'https://elicit.com/api/v2/sessions/systematic-reviews'

SESSIONS = {
    'Apoptosis': '55d0f6d9-e124-40dc-aaee-83155b4b439e',
    'Autophagy': '553dfb7b-3afc-4391-bc82-c78c0bd31097',
    'Ferroptosis': '55702f21-80fe-4bcb-9814-33c01d928cb6',
}

for form, sid in SESSIONS.items():
    cmd = ['curl', '-s', f'{BASE}/{sid}', '-H', f'Authorization: Bearer {key}', '--max-time', '20']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    raw = r.stdout.strip()
    if not raw:
        print(f'{form}: EMPTY response (check key/network)')
        continue
    try:
        d = json.loads(raw)
    except Exception:
        print(f'{form}: non-JSON response: {raw[:200]}')
        continue
    extract = d.get('data', {}).get('extract', {})
    csv_url = extract.get('csv', '')
    print(f'{form}: status={d.get("status","")} | csv_url present={bool(csv_url)}')
    if csv_url:
        req = urllib.request.Request(csv_url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        csv_data = urllib.request.urlopen(req, timeout=60).read().decode('utf-8-sig')
        rows = list(csv.DictReader(io.StringIO(csv_data)))
        out = f'{form.replace(" ", "_")}_recovered.csv'
        with open(out, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        print(f'  Downloaded {len(rows)} rows -> {out}')
