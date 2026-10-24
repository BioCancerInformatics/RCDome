# -*- coding: utf-8 -*-
import json, urllib.request, urllib.error, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

token = open('D:/gh_token.txt').read().strip()
owner, repo = 'BioCancerInformatics', 'RCDome'
base = f'https://api.github.com/repos/{owner}/{repo}'
log = []

def ts():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

def audit(msg):
    line = f'- [{ts()}] {msg}'
    print(line)
    log.append(line)

def api(method, url, data=None, headers_extra=None):
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github+json', 'User-Agent': 'rcdome-deploy'}
    if headers_extra:
        headers.update(headers_extra)
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read().decode() or '{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or '{}')

# 1. Verify repo + current visibility
audit('Starting public transition (scripted).')
status, r = api('GET', base)
audit(f'GET repo -> HTTP {status}; private={r.get("private")}')

# 2. Create the Release
status, rel = api('POST', base + '/releases', {
    'tag_name': 'v1.0',
    'name': 'RCDome v1.0 — large assets',
    'body': 'Large assets for reproducing the RCDome app: entity figures, the matrix CSV, and multi-omics tables. Unzip into the app data folder.'
})
audit(f'POST release -> HTTP {status}; id={rel.get("id")}; url={rel.get("html_url")}')

# 3. Upload the ZIP asset
if 'id' in rel:
    zip_path = 'D:/RCDome_release_v1.0.zip'
    with open(zip_path, 'rb') as f:
        zip_data = f.read()
    upload_url = f"https://uploads.github.com/repos/{owner}/{repo}/releases/{rel['id']}/assets?name=RCDome_assets_v1.0.zip"
    headers = {'Content-Type': 'application/zip', 'Content-Length': str(len(zip_data))}
    req = urllib.request.Request(upload_url, data=zip_data, method='POST',
                                 headers={'Authorization': f'token {token}', 'User-Agent': 'rcdome-deploy', **headers})
    try:
        resp = urllib.request.urlopen(req)
        audit(f'Upload asset -> HTTP {resp.status} ({len(zip_data)/1048576:.1f} MB)')
    except urllib.error.HTTPError as e:
        audit(f'Upload asset -> HTTP {e.code}: {e.read().decode()[:200]}')

# 4. Flip public
status, r2 = api('PATCH', base, {'private': False})
audit(f'PATCH visibility -> HTTP {status}; private={r2.get("private")}; html_url={r2.get("html_url")}')

# 5. Write audit log
with open('D:/RCDome_github/audit_public_transition.md', 'w', encoding='utf-8') as f:
    f.write('# RCDome — public transition audit\n\n')
    f.write('\n'.join(log))
    f.write('\n')
print('\nAudit log written to D:/RCDome_github/audit_public_transition.md')
