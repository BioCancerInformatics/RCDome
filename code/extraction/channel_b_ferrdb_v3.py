"""
channel_b_ferrdb_v3.py — Extract genes from FerrDB v3
======================================================
Input:  ferrdb_genes_only.md (pipe-delimited)
Output: gene_rcd_ferrdb_v3.csv
Source: http://www.zhounan.org/ferrdb/
"""

import csv, os, sys

INPUT = os.path.join(os.path.dirname(__file__), '..', 'Drafts', 'ferrdb_genes_only.md')
OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'output databases', 'gene_rcd_ferrdb_v3.csv')

def extract():
    rows = []
    with open(INPUT, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('|') or 'RCD Modality' in line or '---' in line:
                continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 7: continue
            rows.append([parts[3], parts[1], parts[2], parts[4], parts[5], parts[6]])

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['gene_symbol','rcd_form','gene_type','hgnc_id','experiments','full_name',
                     'source_databases','source_channel','evidence_type','curator_verified'])
        for r in rows:
            w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], 'FerrDB', 'B', 'ferrdb_v3', 'FALSE'])
    print(f'FerrDB v3: {len(rows)} entries -> {OUTPUT}')

if __name__ == '__main__':
    extract()
