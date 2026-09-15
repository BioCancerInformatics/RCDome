"""
channel_b_ncbi_gene.py — Extract genes from NCBI Gene via E-utilities
========================================================================
Searches NCBI Gene for all 32 RCD forms, fetches gene symbols.
Uses NCBI API key for higher rate limits.
Output: gene_rcd_ncbi_gene.csv
API: https://eutils.ncbi.nlm.nih.gov/
"""

import csv, os, urllib.request, json, time

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'output databases', 'gene_rcd_ncbi_gene.csv')

# NCBI API key for 10 req/sec (obtain from https://ncbi.nlm.nih.gov/account/)
API_KEY = os.environ.get('NCBI_API_KEY', '')
RATE = 0.11 if API_KEY else 0.34

CANONICAL_FORMS = [
    "Alkaliptosis", "Anoikis", "Apoptosis", "Autophagy", "Autosis",
    "Cellular senescence", "Cornification", "Cuproptosis", "Disulfidptosis",
    "Efferocytosis", "Entosis", "Erebosis", "Ferroptosis",
    "Hypersensitive response", "Immunogenic cell death",
    "Lysosome-dependent cell death", "Methuosis",
    "Mitochondrial permeability transition", "Mitoptosis", "Mitotic catastrophe",
    "NETosis", "Necroptosis", "Necrosis", "Oncosis", "Oxeiptosis",
    "PANoptosis", "Paraptosis", "Parthanatos", "Programmed cell death",
    "Pyronecrosis", "Pyroptosis", "Spectosis",
]

def fetch(url):
    return urllib.request.urlopen(url).read().decode('utf-8')

def extract():
    all_rows = []
    for form in CANONICAL_FORMS:
        query = form.replace(' ', '+')
        key_param = f"&api_key={API_KEY}" if API_KEY else ""
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term={query}[All+Fields]&retmax=5000&retmode=json{key_param}"
        
        try:
            data = json.loads(fetch(url))
            gene_ids = data.get('esearchresult', {}).get('idlist', [])
            count = int(data.get('esearchresult', {}).get('count', 0))
            time.sleep(RATE)
        except Exception as e:
            print(f'  {form}: search error - {e}')
            continue
        
        if not gene_ids:
            print(f'  {form}: 0 hits')
            continue
        
        symbols = []
        for i in range(0, len(gene_ids), 200):
            batch = gene_ids[i:i+200]
            url2 = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id={','.join(batch)}&retmode=json{key_param}"
            try:
                data2 = json.loads(fetch(url2))
                results = data2.get('result', {})
                for gid in batch:
                    info = results.get(gid, {})
                    symbol = info.get('name', '')
                    if symbol and symbol != 'N/A': symbols.append(symbol)
                time.sleep(RATE)
            except Exception as e:
                print(f'  {form}: fetch error - {e}')
        
        print(f'  {form}: {count} hits, {len(symbols)} symbols')
        for s in sorted(set(symbols)):
            all_rows.append([s, form])

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['gene_symbol','rcd_form','source_databases','source_channel','evidence_type','curator_verified'])
        for r in all_rows:
            w.writerow([r[0], r[1], 'NCBI_Gene', 'B', 'ncbi_gene_esearch', 'FALSE'])
    print(f'\nNCBI Gene: {len(all_rows)} entries -> {OUTPUT}')

if __name__ == '__main__':
    extract()
