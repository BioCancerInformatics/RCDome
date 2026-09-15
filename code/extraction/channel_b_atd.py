"""
channel_b_atd.py — Extract genes from ATD (Autophagy To Disease)
==================================================================
Downloads autophagy_related_gene_detail.xlsx
Output: gene_rcd_atd.csv
Source: http://auto2disease.nwsuaflmz.com/
"""

import csv, os, subprocess, openpyxl

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'Drafts', 'iPCD_downloads')
OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'output databases', 'gene_rcd_atd.csv')
URL = "http://auto2disease.nwsuaflmz.com/autophagy_related_gene_detail.xlsx"

def extract():
    fpath = os.path.join(DOWNLOAD_DIR, 'atd_genes.xlsx')
    if not os.path.exists(fpath):
        subprocess.run(['curl', '-s', '-L', '--max-time', '15', URL, '-o', fpath])
    
    genes = []
    wb = openpyxl.load_workbook(fpath, read_only=True, data_only=True)
    ws = wb['Sheet1']
    for row in ws.iter_rows(min_row=2, values_only=True):
        symbol = str(row[2]).strip() if row[2] else ''
        if symbol and symbol != 'None': genes.append(symbol)
    wb.close()

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['gene_symbol','rcd_form','source_databases','source_channel','evidence_type','curator_verified'])
        for g in genes:
            w.writerow([g, 'Autophagy', 'ATD', 'B', 'atd_curated', 'FALSE'])
    print(f'ATD: {len(genes)} entries -> {OUTPUT}')

if __name__ == '__main__':
    extract()
