"""Check the test session's current status."""
import subprocess, json, os

ENV = '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/extraction code snippets/.env'
key = ''
for line in open(ENV):
    if line.startswith('ELICIT_API_KEY='):
        key = line.split('=', 1)[1].strip()
        break

sid = '5519ab96-d11b-4f7e-b0fd-94f2d649c73a'
url = f'https://elicit.com/api/v2/sessions/systematic-reviews/{sid}'
cmd = ['curl', '-s', url, '-H', f'Authorization: Bearer {key}', '--max-time', '30']
r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
raw = r.stdout.strip()
if not raw:
    print('EMPTY response (network/DNS)')
else:
    try:
        d = json.loads(raw)
        print(f"status: {d.get('status')}")
        print(f"data keys: {list(d.get('data', {}).keys())}")
        ext = d.get('data', {}).get('extract', {})
        print(f"extract keys: {list(ext.keys())}")
        print(f"csv present: {bool(ext.get('csv', ''))}")
    except Exception:
        print(f'non-JSON: {raw[:300]}')
