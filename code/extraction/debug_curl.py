"""Debug: why does curl return empty for the session status endpoint?"""
import subprocess, json, os

ENV = '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/extraction code snippets/.env'
key = ''
for line in open(ENV):
    if line.startswith('ELICIT_API_KEY='):
        key = line.split('=', 1)[1].strip()
        break

sid = '55d0f6d9-e124-40dc-aaee-83155b4b439e'
url = f'https://elicit.com/api/v2/sessions/systematic-reviews/{sid}'

# Without -s, with http_code and error capture
cmd = ['curl', '-w', '\nHTTP_CODE:%{http_code}\n', url, '-H', f'Authorization: Bearer {key}', '--max-time', '30']
r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
print('=== STDOUT ===')
print(repr(r.stdout[:500]))
print('=== STDERR ===')
print(repr(r.stderr[:500]))
print('=== RETURN CODE ===')
print(r.returncode)
