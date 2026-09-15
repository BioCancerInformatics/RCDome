"""
channel_b_hadb.py — Extract genes from HADb (Human Autophagy Database)
=========================================================================
Scrapes 371 autophagy genes from https://autophagy.lu/genes/
Output: gene_rcd_hadb.csv
"""

import csv, os, re, subprocess, sys

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'output databases', 'gene_rcd_hadb.csv')
URL = "https://autophagy.lu/genes/"

def extract():
    result = subprocess.run(['curl', '-s', '-L', '--max-time', '15', URL], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"HADb: download failed")
        return

    genes = re.findall(r'<a href="/genes/\d+">([^<]+)</a>\s*</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>', result.stdout)

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['gene_symbol','gene_name','gene_family','molecular_type','rcd_form','source_databases','source_channel','evidence_type','curator_verified'])
        for g in genes:
            w.writerow([g[0], g[1], g[2], g[3], 'Autophagy', 'HADb', 'B', 'hadb_curated', 'FALSE'])
    print(f'HADb: {len(genes)} entries -> {OUTPUT}')

if __name__ == '__main__':
    extract()
