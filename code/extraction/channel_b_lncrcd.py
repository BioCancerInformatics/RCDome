"""
channel_b_lncrcd.py — Extract genes from LncRCD
================================================
Input:  lnRCD_geneset_12_RCD.csv (pcg, pathway)
Output: gene_rcd_lncrcd.csv
Source: https://lncrcddb.bio-database.com/
"""

import csv, os

INPUT = os.path.join(os.path.dirname(__file__), '..', 'Drafts', 'lnRCD_12_RCD-geneset', 'lnRCD_geneset_12_RCD.csv')
OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'output databases', 'gene_rcd_lncrcd.csv')

def extract():
    rows = []
    with open(INPUT, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            rows.append([row['pcg'].strip(), row['pathway'].strip()])

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['gene_symbol','rcd_form','source_databases','source_channel','evidence_type','curator_verified'])
        for r in rows:
            w.writerow([r[0], r[1], 'LncRCD', 'B', 'lncrcd_curated', 'FALSE'])
    print(f'LncRCD: {len(rows)} entries -> {OUTPUT}')

if __name__ == '__main__':
    extract()
