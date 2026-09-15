"""
channel_b_go.py — Extract genes from Gene Ontology via QuickGO
=================================================================
Queries QuickGO REST API for RCD-specific GO terms (taxon 9606).
Output: gene_rcd_go.csv
API: https://www.ebi.ac.uk/QuickGO/services/annotation/search
"""

import csv, os, subprocess, json

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'output databases', 'gene_rcd_go.csv')

GO_TERMS = {
    'GO:0006915': 'Apoptosis', 'GO:0097527': 'Necroptosis', 'GO:0070269': 'Pyroptosis',
    'GO:0097695': 'Ferroptosis', 'GO:0048102': 'Autophagy', 'GO:0097300': 'Necrosis',
    'GO:0090398': 'Cellular senescence',
}

def extract():
    all_rows = []
    for go_id, rcd_form in sorted(GO_TERMS.items()):
        genes = set()
        page = 1
        while page <= 40:
            url = f'https://www.ebi.ac.uk/QuickGO/services/annotation/search?goId={go_id}&taxonId=9606&limit=200&page={page}'
            result = subprocess.run(['curl', '-s', '--max-time', '10', url], capture_output=True, text=True)
            if result.returncode != 0 or not result.stdout.strip(): break
            try:
                data = json.loads(result.stdout)
                results = data.get('results', [])
                if not results: break
                for r in results:
                    symbol = r.get('symbol', '')
                    if symbol: genes.add(symbol)
                page += 1
            except Exception as e:
                print(f'  Parse error page {page}: {e}')
                break
        print(f'  {rcd_form}: {len(genes)} genes')
        for g in sorted(genes):
            all_rows.append([g, rcd_form, go_id])

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['gene_symbol','rcd_form','go_term','source_databases','source_channel','evidence_type','curator_verified'])
        for r in all_rows:
            w.writerow([r[0], r[1], r[2], 'GO', 'B', f'go_{r[2]}', 'FALSE'])
    print(f'GO: {len(all_rows)} entries -> {OUTPUT}')

if __name__ == '__main__':
    extract()
