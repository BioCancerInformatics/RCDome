"""
utility_normalize_rcd_forms.py - RCD Form Name Normalization
=============================================================
Applies the documented 11-rename mapping to fill rcd_form_canonical.
This step was originally performed manually; this script codifies it
for full pipeline reproducibility.

Mapping (documented in manuscript normalization table):
  Entotic-cell-death -> Entosis
  Entotic cell death  -> Entosis
  NETotic-cell-death  -> NETosis
  Netotic cell death  -> NETosis
  Lysosomal cell death -> Lysosome-dependent cell death
  LDCD                -> Lysosome-dependent cell death
  ADCD                -> Autosis
  MPT-driven-necrosis -> Mitochondrial permeability transition
  Mitotic-death       -> Mitotic catastrophe
  Regulated-necrosis  -> Necrosis
  Immunogenic-cell-death -> Immunogenic cell death

Usage: python utility_normalize_rcd_forms.py <input_csv> <output_csv>
"""

import csv, sys

NORMALIZATION = {
    'Entotic-cell-death': 'Entosis',
    'Entotic cell death': 'Entosis',
    'NETotic-cell-death': 'NETosis',
    'Netotic cell death': 'NETosis',
    'Lysosomal cell death': 'Lysosome-dependent cell death',
    'LDCD': 'Lysosome-dependent cell death',
    'ADCD': 'Autosis',
    'MPT-driven-necrosis': 'Mitochondrial permeability transition',
    'Mitotic-death': 'Mitotic catastrophe',
    'Regulated-necrosis': 'Necrosis',
    'Immunogenic-cell-death': 'Immunogenic cell death',
}

def main():
    if len(sys.argv) < 3:
        print("Usage: python utility_normalize_rcd_forms.py <input.csv> <output.csv>")
        return
    
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    
    normalized = 0
    for r in rows:
        raw = r['rcd_form']
        canonical = NORMALIZATION.get(raw, raw)
        r['rcd_form_canonical'] = canonical
        if canonical != raw:
            normalized += 1
    
    cols = list(rows[0].keys())
    with open(sys.argv[2], 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    
    print(f"Normalized {normalized}/{len(rows)} rows. Output: {len(rows)} rows -> {sys.argv[2]}")

if __name__ == '__main__':
    main()
