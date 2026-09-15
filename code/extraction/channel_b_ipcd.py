"""
channel_b_ipcd.py — Extract genes from iPCD
=============================================
Downloads per-form ZIP files from iPCD, filters Homo sapiens, parses PCD direction flags.
Output: gene_rcd_ipcd.csv
Source: https://ipcd.biocuckoo.cn/Download.php
"""

import csv, os, subprocess, zipfile

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'Drafts', 'iPCD_downloads')
OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'output databases', 'gene_rcd_ipcd.csv')
BASE_URL = "https://ipcd.biocuckoo.cn/Download"

FORMS = [
    'Apoptosis', 'Anoikis', 'Necroptosis', 'Pyroptosis', 'Ferroptosis',
    'Autophagy', 'Alkaliptosis', 'Autosis', 'Entosis', 'Oxeiptosis',
    'Oncosis', 'Pyronecrosis', 'Cornification', 'Lysosomal_cell_death',
    'Hypersensitive_response',
]

def extract():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    all_rows = []

    for form in FORMS:
        fpath = os.path.join(DOWNLOAD_DIR, f'{form}.zip')
        if not os.path.exists(fpath):
            result = subprocess.run(['curl', '-s', '-L', '--max-time', '120',
                                     f'{BASE_URL}/{form}.zip', '-o', fpath])
        
        if not os.path.exists(fpath) or os.path.getsize(fpath) < 1000:
            print(f'  {form}: download failed or empty')
            continue

        try:
            with zipfile.ZipFile(fpath) as z:
                for name in z.namelist():
                    with z.open(name) as f:
                        for line in f.read().decode('utf-8', errors='replace').split('\n')[1:]:
                            if not line.strip(): continue
                            parts = line.split('\t')
                            if len(parts) < 7: continue
                            species = parts[5].strip()
                            if species != 'Homo sapiens': continue
                            gene = parts[6].strip()
                            pcd_raw = parts[4].strip()
                            status = parts[3].strip()
                            uniprot = parts[2].strip() if len(parts) > 2 else ''
                            
                            # Parse "Apoptosis,+" -> form=Apoptosis, direction=+
                            if ',' in pcd_raw:
                                rcd_form, direction = pcd_raw.split(',', 1)
                                rcd_form = rcd_form.strip()
                            else:
                                rcd_form = pcd_raw.strip()
                                direction = ''
                            
                            if not rcd_form or rcd_form in ('-', '+'): continue
                            all_rows.append([gene, rcd_form, status, uniprot])
            print(f'  {form}: extracted')
        except Exception as e:
            print(f'  {form}: error - {e}')

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['gene_symbol','rcd_form','status','uniprot_id',
                     'source_databases','source_channel','evidence_type','curator_verified'])
        for r in all_rows:
            w.writerow([r[0], r[1], r[2], r[3], 'iPCD', 'B', 'ipcd_curated', 'FALSE'])
    print(f'iPCD: {len(all_rows)} entries -> {OUTPUT}')

if __name__ == '__main__':
    extract()
