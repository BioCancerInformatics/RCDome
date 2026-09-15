"""
elicit_targeted_17.py — targeted PROVE/DISPROVE extraction for the 17 verbatim-only
legacy rows (12 unique gene-form pairs).

Different from the P1/P2/P3 systematic review: instead of 4 generic form-wide
searches + a 73-gene allow-list, this runs ONE specific query per gene-form pair
and VERIFIES that the returned paper mentions BOTH the gene and the form.

Output per pair: PROVED (doi + pmid + title + abstract snippet) or NOT_PROVED.
Run on Zima (ELICIT_API_KEY in .env). Writes elicit_targeted_17.csv/.json.
"""
import os, json, subprocess, csv, sys

ELICIT_KEY = os.environ.get('ELICIT_API_KEY', '')
SEARCH_URL = 'https://elicit.com/api/v2/search/papers'

if not ELICIT_KEY:
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith('ELICIT_API_KEY='):
                ELICIT_KEY = line.split('=', 1)[1].strip()

if not ELICIT_KEY:
    print("ERROR: ELICIT_API_KEY not set and .env not found."); sys.exit(1)

# (gene, form, form-keyword-for-verification)
PAIRS = [
    ('DAXX',   'Apoptosis (intrinsic)',           'intrinsic apoptosis'),
    ('DFFA',   'Programmed cell death',           'programmed cell death'),
    ('EIF2S1', 'Immunogenic cell death',          'immunogenic cell death'),
    ('FLCN',   'Autophagy',                       'autophagy'),
    ('GATA4',  'Apoptosis',                       'apoptosis'),
    ('MAP3K5', 'Apoptosis',                       'apoptosis'),
    ('MT1X',   'Cuproptosis',                     'cuproptosis'),
    ('PLA2G4A','Apoptosis',                       'apoptosis'),
    ('SMAD4',  'Anoikis',                         'anoikis'),
    ('TNFSF10','Apoptosis',                       'apoptosis'),
    ('EPAS1',  'Ammonia-induced cell death',      'ammonia'),
    ('BMP2',   'Senescence and Autophagy in Cancer','senescence autophagy'),
]

def _get(p, *keys):
    for k in keys:
        if p.get(k):
            return p[k]
    return ''

def query(gene, form, form_kw):
    """Return (status, doi, pmid, title, abstract_snippet) for one pair."""
    body = json.dumps({'query': f'{gene} {form} cell death', 'searchMode': 'semantic',
                       'corpus': 'pubmed', 'maxResults': 3})
    cmd = ['curl', '-s', '-X', 'POST', SEARCH_URL,
           '-H', 'Authorization: Bearer ' + ELICIT_KEY,
           '-H', 'Content-Type: application/json', '-d', body, '--max-time', '25']
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        data = json.loads(r.stdout)
        papers = data.get('papers', []) or []
        for p in papers:
            title = _get(p, 'title', 'displayTitle', 'name')
            abstract = _get(p, 'abstract', 'abstractText', 'snippet', 'summary')
            text = (title + ' ' + abstract).lower()
            gene_hit = gene.lower() in text
            form_hit = any(kw in text for kw in form_kw.split())
            if gene_hit and form_hit:
                return ('PROVED', _get(p, 'doi', 'sourceDoi'), _get(p, 'pmid'),
                        title, (abstract or '')[:200])
        return ('NOT_PROVED', '', '', '', '')
    except Exception as e:
        return ('ERROR', '', '', '', str(e)[:80])

results = []
for gene, form, form_kw in PAIRS:
    status, doi, pmid, title, abstr = query(gene, form, form_kw)
    results.append({'gene': gene, 'form': form, 'status': status, 'doi': doi,
                    'pmid': pmid, 'title': title[:80], 'abstract_snippet': abstr})
    print(f"{status:<10} {gene:<8} {form:<30} doi={doi[:28]:<30} pmid={pmid:<10} {title[:50]}")

with open('elicit_targeted_17.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)
keys = ['gene', 'form', 'status', 'doi', 'pmid', 'title', 'abstract_snippet']
with open('elicit_targeted_17.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
    w.writeheader(); w.writerows(results)

n_proved = sum(1 for r in results if r['status'] == 'PROVED')
n_not = sum(1 for r in results if r['status'] == 'NOT_PROVED')
print(f"\nPROVED: {n_proved} | NOT_PROVED: {n_not} | total pairs: {len(results)}")
print("Saved elicit_targeted_17.json/.csv")
