"""
channel_b_hamdb.py — Extract genes from HAMdb
===============================================
Parses protein-role-csv.zip from HAMdb downloads
Output: gene_rcd_hamdb.csv
Source: http://hamdb.scbdd.com/
"""

import csv, os, zipfile, io

INPUT = os.path.join(os.path.dirname(__file__), '..', 'Drafts', 'HAMdb_downloads', 'protein-role-csv.zip')
OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'output databases', 'gene_rcd_hamdb.csv')

def extract():
    genes = set()
    with zipfile.ZipFile(INPUT) as z:
        with z.open('protein-role.csv') as f:
            content = f.read().decode('latin-1')
            for row in csv.DictReader(io.StringIO(content)):
                g = row.get('Symbol', '').strip()
                if g: genes.add(g)

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['gene_symbol','rcd_form','source_databases','source_channel','evidence_type','curator_verified'])
        for g in sorted(genes):
            w.writerow([g, 'Autophagy', 'HAMdb', 'B', 'hamdb_curated', 'FALSE'])
    print(f'HAMdb: {len(genes)} entries -> {OUTPUT}')

if __name__ == '__main__':
    extract()
