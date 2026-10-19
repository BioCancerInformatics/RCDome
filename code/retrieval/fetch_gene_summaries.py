# RCDome — one-time NCBI Gene summary pre-fetch
# Builds data/gene_info_lookup.json: for each of the 9,265 genes in the matrix,
# store HGNC fields (name, aliases, locus type, location, entrez_id) + the NCBI
# Gene summary (functional description), fetched in batches via E-utilities.
import csv, json, time, sys, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
csv.field_size_limit(10**9)

MATRIX = 'output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv'
HGNC = 'RCDome_distribution/data/hgnc_complete_set.txt'
OUT = 'RCDome_distribution/data/gene_info_lookup.json'

# 1. genes in the matrix
genes = set()
with open(MATRIX, encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        genes.add(r['gene_symbol'])
print('matrix genes:', len(genes))

# 2. HGNC map
hgnc = {}
with open(HGNC, encoding='utf-8') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        hgnc[r.get('symbol', '')] = {
            'entrez_id': r.get('entrez_id', ''),
            'name': r.get('name', ''),
            'alias': r.get('alias_symbol', ''),
            'locus_type': r.get('locus_type', ''),
            'location': r.get('location', ''),
        }

gene_info = {}
ids = []
for g in sorted(genes):
    info = hgnc.get(g, {'entrez_id': '', 'name': '', 'alias': '', 'locus_type': '', 'location': ''})
    gene_info[g] = info
    if info['entrez_id']:
        ids.append((g, info['entrez_id']))
print('genes with entrez_id:', len(ids))

# 3. batch-fetch summaries (200 ids per request)
base = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
summaries = {}
B = 200
for i in range(0, len(ids), B):
    batch = ids[i:i + B]
    idstr = ','.join(eid for _, eid in batch)
    data = urllib.parse.urlencode({'db': 'gene', 'id': idstr, 'retmode': 'json'}).encode()
    req = urllib.request.Request(base, data=data)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                j = json.loads(resp.read().decode())
            break
        except Exception as e:
            if attempt == 2:
                print('  fetch error on batch', i, ':', e)
                j = None
            time.sleep(2)
    if j:
        res = j.get('result', {})
        for eid in res.get('uids', []):
            summaries[eid] = {
                'summary': res[eid].get('summary', ''),
                'ncbi_name': res[eid].get('name', ''),
            }
    print(f'  batch {i // B + 1}: {len(summaries)} summaries so far')
    time.sleep(0.4)  # respect NCBI rate limit (3 req/s)

# 4. merge + save
for g, eid in ids:
    if eid in summaries:
        gene_info[g]['summary'] = summaries[eid]['summary']
        gene_info[g]['ncbi_name'] = summaries[eid]['ncbi_name']

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(gene_info, f, ensure_ascii=False)
print('saved', OUT, 'with', len(summaries), 'NCBI summaries')
