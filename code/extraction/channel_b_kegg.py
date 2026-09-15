"""
channel_b_kegg.py — Extract genes from KEGG pathways via KGML
================================================================
Downloads KGML files for 5 RCD-relevant pathways, parses gene symbols.
Output: gene_rcd_kegg.csv
API: https://rest.kegg.jp/
"""

import csv, os, subprocess, json, xml.etree.ElementTree as ET, time

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'output databases', 'gene_rcd_kegg.csv')

PATHWAYS = {
    'hsa04210': 'Apoptosis', 'hsa04216': 'Ferroptosis', 'hsa04217': 'Necroptosis',
    'hsa04140': 'Autophagy', 'hsa04218': 'Cellular senescence',
}

def extract():
    all_rows = []
    for pid, rcd_form in PATHWAYS.items():
        url = f'https://rest.kegg.jp/get/{pid}/kgml'
        result = subprocess.run(['curl', '-s', '--max-time', '10', url], capture_output=True, text=True)
        if result.returncode != 0: continue
        
        root = ET.fromstring(result.stdout)
        genes_seen = set()
        for graphics in root.findall('.//graphics'):
            gname = graphics.get('name', '')
            if gname and not gname.startswith('TITLE:') and not gname.startswith('path:'):
                symbol = gname.split(',')[0].strip()
                if symbol and not (symbol.startswith('C') and symbol[1:].isdigit()):
                    genes_seen.add(symbol)
        
        for g in sorted(genes_seen):
            all_rows.append([g, rcd_form, pid])

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['gene_symbol','rcd_form','kegg_pathway','source_databases','source_channel','evidence_type','curator_verified'])
        for r in all_rows:
            w.writerow([r[0], r[1], r[2], 'KEGG', 'B', f'kegg_{r[2]}', 'FALSE'])
    print(f'KEGG: {len(all_rows)} entries -> {OUTPUT}')

if __name__ == '__main__':
    extract()
