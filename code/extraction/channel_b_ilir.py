"""
channel_b_ilir.py — Extract LIR-containing proteins from iLIR
===============================================================
Downloads iLIR export for Homo sapiens
Output: gene_rcd_ilir.csv
Source: https://ilir.warwick.ac.uk/export.php?organism=4
"""

import csv, os, subprocess

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'output databases', 'gene_rcd_ilir.csv')
URL = "https://ilir.warwick.ac.uk/export.php?organism=4"

def extract():
    result = subprocess.run(['curl', '-s', '-L', '-k', '--max-time', '15', URL], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"iLIR: download failed")
        return

    all_rows = []
    for line in result.stdout.strip().split('\n')[1:]:  # skip header
        parts = line.split('\t')
        if len(parts) >= 7:
            all_rows.append([parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]])

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['uniprot_id','start','end','lir_pattern','anchor_no','protein_description',
                     'rcd_form','source_databases','source_channel','evidence_type','curator_verified'])
        for r in all_rows:
            w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], 'Autophagy', 'iLIR', 'B', 'ilir_curated', 'FALSE'])
    print(f'iLIR: {len(all_rows)} entries -> {OUTPUT}')

if __name__ == '__main__':
    extract()
