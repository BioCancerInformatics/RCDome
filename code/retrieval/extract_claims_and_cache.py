# -*- coding: utf-8 -*-
"""Stage 1 — extract all claims from the 49 descriptions and build the full-text cache."""
import sys, os, re, json, urllib.request, urllib.parse, time
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Criação de cartoon representations for RCDome/RCD modulo revisao'
DESC = os.path.join(BASE, 'descricao RCDs')
REF = os.path.join(BASE, 'referencias')

def load_refs(entity):
    refs = {}
    path = os.path.join(REF, entity + '.txt')
    if not os.path.exists(path):
        return refs
    for line in open(path, encoding='utf-8'):
        m = re.search(r'^\[?(\d+)\]?\.?\s+', line.strip())
        if not m:
            continue
        num = m.group(1)
        doi = re.search(r'(?:DOI|doi):\s*\**\s*(10\.[^\s*]+)', line)
        pmid = re.search(r'PMID:\s*(\d+)', line)
        pmcid = re.search(r'PMCID:\s*(PMC\d+)', line)
        refs[num] = {
            'doi': doi.group(1).rstrip('.').lower() if doi else '',
            'pmid': pmid.group(1) if pmid else '',
            'pmcid': pmcid.group(1) if pmcid else '',
        }
    return refs

def split_claims(text):
    """Split prose into sentences and attach their [n] citations."""
    # normalize citation ranges like [3–5] and [1,3,7] to lists
    sentences = re.split(r'(?<=[.!?])\s+', text)
    claims = []
    for s in sentences:
        cites = []
        for m in re.finditer(r'\[([0-9,\s\u2013\-]+)\]', s):
            part = m.group(1)
            for tok in re.split(r'[,]', part):
                tok = tok.strip()
                if not tok:
                    continue
                rng = re.match(r'^(\d+)\s*[\u2013-]\s*(\d+)$', tok)
                if rng:
                    cites.extend(str(x) for x in range(int(rng.group(1)), int(rng.group(2)) + 1))
                elif tok.isdigit():
                    cites.append(tok)
        if cites and len(s) > 30:
            claims.append({'sentence': s.strip(), 'cites': sorted(set(cites))})
    return claims

# ---- 1. extract claims ----
print('Extracting claims from all descriptions...')
all_claims = []
for fn in sorted(os.listdir(DESC)):
    if not fn.endswith('.txt'):
        continue
    entity = os.path.splitext(fn)[0]
    text = open(os.path.join(DESC, fn), encoding='utf-8', errors='ignore').read()
    for c in split_claims(text):
        all_claims.append({'entity': entity, 'sentence': c['sentence'], 'cites': c['cites']})

print(f'total claims: {len(all_claims)}')

# unique PMIDs cited
pmids = set()
for c in all_claims:
    refs = load_refs(c['entity'])
    for n in c['cites']:
        if n in refs and refs[n]['pmid']:
            pmids.add(refs[n]['pmid'])
print(f'unique PMIDs across all claims: {len(pmids)}')

# ---- 2. build full-text cache for unique PMIDs ----
print('\nBuilding full-text cache (this may take a few minutes)...')
cache_file = os.path.join(BASE, '_fulltext_cache.json')
cache = json.load(open(cache_file)) if os.path.exists(cache_file) else {}

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'RCDome-audit/1.0 (mailto:quique@uenf.br)'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode('utf-8', 'ignore')

def strip_html(s):
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', s)

# load PMID -> PMCID
pmid2pmcid = json.load(open(os.path.join(BASE, '_pmid_to_pmcid.json')))
# load DOI per PMID (reverse from references)
pmid2doi = {}
for fn in os.listdir(REF):
    if not fn.endswith('.txt'):
        continue
    for line in open(os.path.join(REF, fn), encoding='utf-8'):
        pmid = re.search(r'PMID:\s*(\d+)', line)
        doi = re.search(r'(?:DOI|doi):\s*\**\s*(10\.[^\s*]+)', line)
        if pmid and doi:
            pmid2doi.setdefault(pmid.group(1), doi.group(1).rstrip('.').lower())

def get_fulltext(pmid):
    if pmid in cache:
        return cache[pmid], 'cache'
    pc = pmid2pmcid.get(pmid)
    if pc:
        try:
            xml = fetch(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pc}/fullTextXML')
            cache[pmid] = strip_html(xml)[:60000]
            return cache[pmid], 'europepmc'
        except Exception:
            pass
    doi = pmid2doi.get(pmid)
    if doi:
        try:
            d = json.loads(fetch('https://api.openalex.org/works/https://doi.org/' + urllib.parse.quote(doi)))
            oa_url = (d.get('open_access') or {}).get('oa_url')
            if oa_url:
                m = re.search(r'articles/(PMC\d+)', oa_url)
                if m:
                    try:
                        xml = fetch(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{m.group(1)}/fullTextXML')
                        cache[pmid] = strip_html(xml)[:60000]
                        return cache[pmid], 'green->europepmc'
                    except Exception:
                        pass
                cache[pmid] = strip_html(fetch(oa_url))[:60000]
                return cache[pmid], 'green-html'
        except Exception:
            pass
        # preprint (bioRxiv / medRxiv)
        if doi.startswith('10.1101/'):
            for server in ('biorxiv', 'medrxiv'):
                try:
                    d = json.loads(fetch(f'https://api.biorxiv.org/details/{server}/' + doi))
                    if d.get('collection'):
                        txt = fetch(f'https://www.{server}.org/content/{doi}v1.full')
                        cache[pmid] = strip_html(txt)[:60000]
                        return cache[pmid], f'{server}-preprint'
                except Exception:
                    pass
    try:
        txt = fetch(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&rettype=abstract&retmode=text')
        cache[pmid] = txt[:60000]
        return cache[pmid], 'abstract'
    except Exception:
        pass
    cache[pmid] = ''
    return '', 'no-route'

routes = {}
for i, pmid in enumerate(sorted(pmids), 1):
    _, route = get_fulltext(pmid)
    routes[route] = routes.get(route, 0) + 1
    if i % 200 == 0:
        print(f'  {i}/{len(pmids)} cached', flush=True)
        json.dump(cache, open(cache_file, 'w', encoding='utf-8'))

json.dump(cache, open(cache_file, 'w', encoding='utf-8'))
print(f'\ncache saved: {cache_file} ({len(cache)} PMIDs)')
print('route distribution:', routes)
print(f'claims with at least one cached full text: {sum(1 for c in all_claims if any(n in load_refs(c["entity"]) and load_refs(c["entity"])[n]["pmid"] in cache and cache[load_refs(c["entity"])[n]["pmid"]] for n in c["cites"]))}')
