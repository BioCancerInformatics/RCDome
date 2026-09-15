"""Inspect the uncapped session's search/screen data structure.

Question: is 315 papers truly 'uncapped', or does Elicit impose its own
default maxResults when the parameter is omitted?

Dumps the full structure of data.search and data.screen to see paper counts
per search, and whether any search hit a ceiling.
"""
import subprocess, json, os

KEY = os.environ.get('ELICIT_API_KEY', '')
SID = '55330187-e06f-49a5-b383-7e575ac1cd16'
BASE = 'https://elicit.com/api/v2/sessions/systematic-reviews'

r = subprocess.run(['curl', '-s', f'{BASE}/{SID}',
                    '-H', f'Authorization: Bearer {KEY}', '--max-time', '20'],
                   capture_output=True, text=True, timeout=30)
resp = json.loads(r.stdout)
data = resp.get('data', {})

print('TOP-LEVEL data keys:', list(data.keys()))

for section in ['search', 'screen']:
    obj = data.get(section, {})
    print(f'\n=== data.{section} ===')
    print(f'type: {type(obj).__name__}')
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, list):
                print(f'  {k}: list of {len(v)} items')
            elif isinstance(v, dict):
                print(f'  {k}: dict with keys {list(v.keys())[:10]}')
            elif isinstance(v, str):
                print(f'  {k}: string ({len(v)} chars) -> {v[:80]}')
            else:
                print(f'  {k}: {type(v).__name__} = {v}')
    elif isinstance(obj, list):
        print(f'  list of {len(obj)} items')
        if obj:
            print(f'  first item keys: {list(obj[0].keys()) if isinstance(obj[0], dict) else obj[0]}')
