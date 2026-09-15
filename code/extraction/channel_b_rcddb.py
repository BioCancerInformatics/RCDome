"""
channel_b_rcddb.py — Extract genes from RCDdb
===============================================
Downloads per-form CSV files from RCDdb (15 RCD forms)
Input:  http://chenyclab.com/RCDdb/download/{Form}.csv
Output: gene_rcd_rcddb.csv
Source: http://chenyclab.com/RCDdb/
Reference: PMID 39257527
"""

import csv, os, subprocess, sys
from datetime import datetime

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'Drafts', 'RCDdb_downloads')
OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'output databases', 'gene_rcd_rcddb.csv')
BASE_URL = "http://chenyclab.com/RCDdb/download"

FORMS = [
    "Alkaliptosis", "Apoptosis", "Autophagy_dependent_cell_death",
    "Cuproptosis", "Disulfidptosis", "Entotic_cell_death",
    "Ferroptosis", "Immunogenic_cell_death", "Lysosome_dependent_cell_death",
    "MPT_driven_necrosis", "NETotic_cell_death", "Necroptosis",
    "Oxeiptosis", "Parthanatos", "Pyroptosis",
]

def extract():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    all_rows = []

    for form in FORMS:
        url = f"{BASE_URL}/{form}.csv"
        fpath = os.path.join(DOWNLOAD_DIR, f"{form}.csv")
        
        # Download if not present
        if not os.path.exists(fpath):
            result = subprocess.run(['curl', '-s', '-L', '--max-time', '10', url, '-o', fpath])
        
        # Parse
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, quotechar='"')
                next(reader)  # header
                for row in reader:
                    if len(row) >= 3 and row[1].strip():
                        all_rows.append([row[1].strip(), form, row[5] if len(row)>5 else '', row[3] if len(row)>3 else ''])

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['gene_symbol','rcd_form','pmid','ensembl_id',
                     'source_databases','source_channel','evidence_type','curator_verified'])
        for r in all_rows:
            w.writerow([r[0], r[1], r[2], r[3], 'RCDdb', 'B', 'rcddb_curated', 'FALSE'])
    print(f'RCDdb: {len(all_rows)} entries -> {OUTPUT}')

if __name__ == '__main__':
    extract()
