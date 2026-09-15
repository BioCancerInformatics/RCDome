"""Download the extract.csv from the completed DFFA test session and print the
verbatim sentences (to verify full-text extraction)."""
import json, subprocess, urllib.request, os, csv, io, sys

SID = '55dff88d-3e3a-49d2-881d-0fa7bfaed678'
KEY = os.environ.get('ELICIT_API_KEY', '')
if not KEY:
    env = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env):
        for line in open(env):
            if line.startswith('ELICIT_API_KEY='):
                KEY = line.split('=', 1)[1].strip()

r = subprocess.run(['curl','-s',
    'https://elicit.com/api/v2/sessions/systematic-reviews/' + SID,
    '-H','Authorization: Bearer ' + KEY], capture_output=True, text=True)
d = json.loads(r.stdout)
url = d['data']['extract']['csv']
urllib.request.urlretrieve(url, 'extract.csv')
print('downloaded extract.csv')

rows = list(csv.DictReader(open('extract.csv', encoding='utf-8-sig')))
print('rows:', len(rows))
for row in rows[:8]:
    print('---')
    for k in ['Title','gene_symbol','mechanistic_role','evidence_type','role_direction','verbatim_sentence','DOI']:
        v = (row.get(k) or '').strip()
        if v and v.lower() not in ('null','none'):
            print(f'  {k}: {v[:200]}')
