"""
channel_b_reactome.py — Extract genes from Reactome PCD hierarchy
====================================================================
Queries Reactome ContentService API for Programmed Cell Death participants.
Output: gene_rcd_reactome.csv
API: https://reactome.org/ContentService/
"""

import csv, os, subprocess, json

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'output databases', 'gene_rcd_reactome.csv')
URL = "https://reactome.org/ContentService/data/participants/R-HSA-5357801"

def extract():
    result = subprocess.run(['curl', '-s', '--max-time', '15', URL], capture_output=True, text=True)
    if result.returncode != 0: return

    data = json.loads(result.stdout)
    genes = set()
    for item in data:
        for ref in item.get('refEntities', []):
            name = ref.get('geneName') or ref.get('displayName', '')
            if not name or 'ChEBI' in name or 'Guide to Pharmacology' in name: continue
            if name.startswith('ATP') or name.startswith('ADP') or name.startswith('UDP'): continue
            if 'ENSEMBL:' in name or 'UniProt:' in name:
                gene = name.split()[-1].strip()
                if gene: genes.add(gene)

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['gene_symbol','rcd_form','source_databases','source_channel','evidence_type','curator_verified'])
        for g in sorted(genes):
            w.writerow([g, 'Programmed cell death', 'Reactome', 'B', 'reactome_R-HSA-5357801', 'FALSE'])
    print(f'Reactome: {len(genes)} entries -> {OUTPUT}')

if __name__ == '__main__':
    extract()
