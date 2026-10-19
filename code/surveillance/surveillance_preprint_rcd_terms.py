"""RCDome — bioRxiv/medRxiv preprint surveillance (2024-2026).

Runs the planned Layer-4 step: mine Europe PMC preprint records (SRC:PPR)
for cell-death papers published 2024-2026, extract -ptosis/-osis terms from
titles and abstracts, and tally novel RCD-form candidates.

Output:
  output databases/Phase 0 discovery/surveillance_preprint_rcd_terms.csv
  output databases/Phase 0 discovery/surveillance_preprint_progress.json
"""
import json, re, sys, time, urllib.parse, urllib.request, os, csv

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE, 'output databases', 'Phase 0 discovery')
os.makedirs(OUT_DIR, exist_ok=True)
CSV = os.path.join(OUT_DIR, 'surveillance_preprint_rcd_terms.csv')
PROG = os.path.join(OUT_DIR, 'surveillance_preprint_progress.json')

API = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search'
QUERY = '(cell death) AND (SRC:PPR) AND (FIRST_PDATE:[2024-01-01 TO 2026-12-31])'
PAGE = 100

# terms to mine: any -ptosis/-osis word in title/abstract
TERM_RE = re.compile(r'([A-Za-z][a-z]{2,}(?:ptosis|osis))')

# known RCD/umbrella vocabulary (to mark as known vs novel)
KNOWN = set('''apoptosis necroptosis pyroptosis ferroptosis paraptosis oncosis anoikis
    autosis entosis methuosis netosis cuproptosis disulfidptosis oxeiptosis alkaliptosis
    lysoptosis mitoptosis mitochodrialosis vacuolarosis cornification necrosis mitoxiperilysis
    triaptosis spectosis floatptosis lysozincrosis metalloptosis parthanatos erebosis
    efferocytosis phagoptosis pyronecrosis aponecrosis necso lysosomalosis'''.split())

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'RCDome-surveillance/1.0'})
    return json.loads(urllib.request.urlopen(req, timeout=90).read().decode('utf-8'))

def main():
    prog = {}
    if os.path.exists(PROG):
        prog = json.load(open(PROG, encoding='utf-8'))

    tally = prog.get('tally', {})
    cursor = prog.get('cursor', 0)
    seen = prog.get('seen', 0)

    first = True
    while True:
        url = API + '?' + urllib.parse.urlencode({
            'query': QUERY, 'format': 'json', 'pageSize': PAGE,
            'cursorMark': '*' if first else prog.get('mark', '*'), 'resultType': 'core'})
        try:
            d = get(url)
        except Exception as e:
            print('ERR', e, flush=True)
            time.sleep(10)
            continue

        hit_count = int(d.get('hitCount', 0) or 0)
        res = d.get('resultList', {}).get('result', [])
        if not res or (hit_count and seen >= hit_count):
            break
        mark = d.get('nextCursorMark', '*')
        for r in res:
            text = (r.get('title', '') or '') + ' ' + (r.get('abstractText', '') or '')
            terms = set(m.group(1).lower() for m in TERM_RE.finditer(text))
            for t in terms:
                tally[t] = tally.get(t, 0) + 1
        seen += len(res)
        prog.update({'tally': tally, 'cursor': cursor + len(res), 'seen': seen, 'mark': mark})
        cursor += len(res)
        if seen % 1000 < PAGE:
            print(f'  seen={seen} terms={len(tally)}', flush=True)
        if mark == '*':
            break
        json.dump(prog, open(PROG, 'w', encoding='utf-8'))
        time.sleep(0.3)

    json.dump(prog, open(PROG, 'w', encoding='utf-8'))
    rows = sorted(tally.items(), key=lambda kv: -kv[1])
    with open(CSV, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['term', 'preprint_mentions', 'known'])
        for term, n in rows:
            w.writerow([term, n, 'yes' if term in KNOWN else 'no'])
    print('DONE seen=%d terms=%d -> %s' % (seen, len(tally), CSV))
    for term, n in rows[:60]:
        print(f'  {term:22} {n}')

if __name__ == '__main__':
    main()
