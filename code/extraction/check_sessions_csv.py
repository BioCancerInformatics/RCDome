import subprocess, json, os, urllib.request

KEY = os.environ.get('ELICIT_API_KEY', '')
BASE = 'https://elicit.com/api/v2/sessions/systematic-reviews'

SESSIONS = {
    'Apoptosis': '55d0f6d9-e124-40dc-aaee-83155b4b439e',
    'Autophagy': '553dfb7b-3afc-4391-bc82-c78c0bd31097',
    'Ferroptosis': '55702f21-80fe-4bcb-9814-33c01d928cb6',
}

for form, sid in SESSIONS.items():
    cmd = ['curl', '-s', f'{BASE}/{sid}', '-H', f'Authorization: Bearer {KEY}', '--max-time', '20']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    d = json.loads(r.stdout)
    extract = d.get('data', {}).get('extract', {})
    csv_url = extract.get('csv', '')
    print(f'{form}: status={d.get("status","")} | csv_url present={bool(csv_url)} | csv_url_len={len(csv_url)}')
    if csv_url:
        print(f'  URL prefix: {csv_url[:80]}')
