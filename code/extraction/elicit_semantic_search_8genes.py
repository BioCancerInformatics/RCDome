"""
elicit_semantic_search_8genes.py — semantic deep search for the 8 remaining
legacy gene-form pairs, using Elicit's /api/v2/search/papers endpoint.
Run on Zima (ELICIT_API_KEY is set there).

Output: elicit_semantic_8genes.json + .csv
"""
import os, json, subprocess, csv, sys

ELICIT_KEY = os.environ.get('ELICIT_API_KEY', '')
SEARCH_URL = 'https://elicit.com/api/v2/search/papers'

if not ELICIT_KEY:
    # auto-load from the .env file (same folder as this script)
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith('ELICIT_API_KEY='):
                ELICIT_KEY = line.split('=', 1)[1].strip()

if not ELICIT_KEY:
    print("ERROR: ELICIT_API_KEY not set and .env not found."); sys.exit(1)

# (gene, form, semantic query)
GENES = [
    ('HSF1',  'Linker cell-type death', 'HSF1 linker cell death C. elegans EBAX-1 ubiquitin ligase'),
    ('BTBD2', 'Linker cell-type death', 'BTBD2 linker cell death C. elegans E3 ubiquitin ligase'),
    ('SIAH1', 'Linker cell-type death', 'SIAH1 linker cell death C. elegans'),
    ('BTG2',  'Aponecrosis', 'BTG2 aponecrosis apoptosis necrosis cell death'),
    ('CDK1',  'Aponecrosis', 'CDK1 aponecrosis mitotic cell death'),
    ('SFN',   'Aponecrosis', 'SFN 14-3-3 sigma aponecrosis cell death'),
    ('TOP2A', 'Aponecrosis', 'TOP2A aponecrosis mitotic cell death'),
    ('BTG2',  'Floatptosis', 'BTG2 floatptosis vacuolization cell death'),
]

results = []
def _get(p, *keys):
    for k in keys:
        if p.get(k):
            return p[k]
    return ''

for gene, form, query in GENES:
    body = json.dumps({'query': query, 'searchMode': 'semantic', 'corpus': 'pubmed', 'maxResults': 3})
    cmd = ['curl', '-s', '-X', 'POST', SEARCH_URL,
           '-H', 'Authorization: Bearer ' + ELICIT_KEY,
           '-H', 'Content-Type: application/json',
           '-d', body, '--max-time', '25']
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        data = json.loads(r.stdout)
        papers = data.get('papers', []) or []
        if not papers:
            results.append({'gene': gene, 'form': form, 'query': query, 'note': 'no papers', 'raw': r.stdout[:200]})
        for p in papers:
            title = _get(p, 'title', 'displayTitle', 'name')
            abstract = _get(p, 'abstract', 'abstractText', 'snippet', 'summary')
            # relevance check: does title/abstract mention the gene? (flag only, human verifies)
            mentions_gene = gene.lower() in (title + ' ' + abstract).lower()
            results.append({
                'gene': gene, 'form': form, 'query': query,
                'title': title,
                'doi': _get(p, 'doi', 'sourceDoi', 'externalIds.DOI'),
                'pmid': _get(p, 'pmid', 'externalIds.PubMed', 'externalIds.PMID'),
                'year': _get(p, 'year', 'publicationYear', 'publicationDate'),
                'abstract_snippet': (abstract or '')[:250],
                'mentions_gene': mentions_gene,
            })
    except Exception as e:
        results.append({'gene': gene, 'form': form, 'query': query, 'error': str(e)})

with open('elicit_semantic_8genes.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

# CSV
keys = ['gene', 'form', 'query', 'title', 'doi', 'pmid', 'year', 'abstract_snippet', 'mentions_gene', 'note', 'error']
with open('elicit_semantic_8genes.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
    w.writeheader()
    w.writerows(results)

print(json.dumps(results, indent=2))
print(f"\nSaved {len(results)} results to elicit_semantic_8genes.json/.csv")
