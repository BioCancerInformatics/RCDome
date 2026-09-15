#!/usr/bin/env python3
"""Merge Phase 2D Zima results into laptop's 27-column matrix."""
import csv, os, sys
from collections import Counter

BASE = r'D:\Pré-artigo 5-optosis model\Cellular_Spatial_RCD_manuscript\RCDome_manuscript\output databases\Phase 2C output'
ZIMA_PATH = os.path.join(BASE, 'unified_gene_rcd_matrix_Elicit_356.csv')
LAPTOP_PATH = os.path.join(BASE, 'unified_gene_rcd_matrix_27cols.csv')

if not os.path.exists(ZIMA_PATH):
    print(f"ERROR: Zima file not found at {ZIMA_PATH}")
    print("Download it from Zima via AnyDesk first.")
    sys.exit(1)

if not os.path.exists(LAPTOP_PATH):
    print(f"ERROR: Laptop matrix not found at {LAPTOP_PATH}")
    sys.exit(1)

# Load
zima = list(csv.DictReader(open(ZIMA_PATH, encoding='utf-8-sig')))
laptop = list(csv.DictReader(open(LAPTOP_PATH, encoding='utf-8-sig')))
print(f"Zima:   {len(zima):>6} rows x {len(zima[0])} cols")
print(f"Laptop: {len(laptop):>6} rows x {len(laptop[0])} cols")

# Build Zima lookup
cols_2d = ['llm_status', 'llm_pmids', 'llm_evidence_force', 'mechanistic_class']
zima_lookup = {}
for r in zima:
    key = (r['gene_symbol'], r['rcd_form_canonical'])
    zima_lookup[key] = {c: r.get(c, '') for c in cols_2d}

# Merge
merged, skipped = 0, 0
for r in laptop:
    key = (r['gene_symbol'], r['rcd_form_canonical'])
    if key in zima_lookup:
        if not r.get('llm_status', '').strip():
            for c in cols_2d:
                r[c] = zima_lookup[key][c]
            merged += 1
        else:
            skipped += 1

# Write
cols = list(laptop[0].keys())
with open(LAPTOP_PATH, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
    w.writeheader(); w.writerows(laptop)

# Stats
mc = Counter(r['mechanistic_class'] for r in laptop if r.get('mechanistic_class','').strip())
empty_mc = sum(1 for r in laptop if not r.get('mechanistic_class','').strip())
empty_llm = sum(1 for r in laptop if not r.get('llm_status','').strip())

print(f"\nMerged: {merged} | Already had data: {skipped}")
print(f"mechanistic_class remaining empty: {empty_mc}")
print(f"llm_status remaining empty: {empty_llm}")
print(f"mechanistic_class breakdown: {dict(mc)}")
print(f"\nOutput: {LAPTOP_PATH}")
