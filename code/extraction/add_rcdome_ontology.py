"""
add_rcdome_ontology.py — Add 5-level ontological classification to V013 matrix.

Contract:
- NEVER overwrites source columns (rodr_category, rcd_form_canonical, etc.)
- Adds TWO new columns: rcdome_level (L1-L5) and rcdome_level_name
- Writes V014 (new file), V013 preserved untouched.

Level mapping (confirmed by Enrique Medina-Acosta, 2026-08-12):
  L1 Modalities          (38 forms): bona fide cell death mechanisms
  L2 Subtypes             (5 forms): Apoptosis (extrinsic), Apoptosis (intrinsic),
                                     Autosis, Lysosomal cell death, Mitotic death
  L3 Triggers             (3 forms): MPT-driven necrosis, MPT, Mitotic catastrophe
  L4 Functional/conceptual(4 forms): Cellular senescence, Efferocytosis, ICD, PANoptosis
  L5 Generic/composite    (3 forms): Programmed cell death, Senescence+Autophagy, Autophagy
"""

import csv, os

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, '..', 'output databases', 'Phase 2C output', 'unified_gene_rcd_matrix_V013.csv')
DST = os.path.join(BASE, '..', 'output databases', 'Phase 2C output', 'unified_gene_rcd_matrix_V014.csv')

# Canonical mapping (53 forms -> level, name)
LEVEL_MAP = {
    # L1 Modalities (39)
    'Alkaliptosis': ('L1', 'L1 Modalities'),
    'Ammonia-induced cell death': ('L1', 'L1 Modalities'),
    'Anoikis': ('L1', 'L1 Modalities'),
    'Aponecrosis': ('L1', 'L1 Modalities'),
    'Apoptosis': ('L1', 'L1 Modalities'),
    'Autophagy-dependent cell death': ('L1', 'L1 Modalities'),
    'Cornification': ('L1', 'L1 Modalities'),
    'Cuproptosis': ('L1', 'L1 Modalities'),
    'Disulfidptosis': ('L1', 'L1 Modalities'),
    'Entosis': ('L1', 'L1 Modalities'),
    'Erebosis': ('L1', 'L1 Modalities'),
    'Eryptosis': ('L1', 'L1 Modalities'),
    'Ferroptosis': ('L1', 'L1 Modalities'),
    'Floatptosis': ('L1', 'L1 Modalities'),
    'Hypersensitive response': ('L1', 'L1 Modalities'),
    'Linker cell-type death': ('L1', 'L1 Modalities'),
    'Lysoptosis': ('L1', 'L1 Modalities'),
    'Lysosome-dependent cell death': ('L1', 'L1 Modalities'),
    'Lysozincrosis': ('L1', 'L1 Modalities'),
    'Metalloptosis': ('L1', 'L1 Modalities'),
    'Methuosis': ('L1', 'L1 Modalities'),
    'Mitoptosis': ('L1', 'L1 Modalities'),
    'Mitoxyperilysis': ('L1', 'L1 Modalities'),
    'NECSO': ('L1', 'L1 Modalities'),
    'NETosis': ('L1', 'L1 Modalities'),
    'Necroptosis': ('L1', 'L1 Modalities'),
    'Necrosis': ('L1', 'L1 Modalities'),
    'Oncosis': ('L1', 'L1 Modalities'),
    'Oxeiptosis': ('L1', 'L1 Modalities'),
    'Paraptosis': ('L1', 'L1 Modalities'),
    'Parthanatos': ('L1', 'L1 Modalities'),
    'Phagoptosis': ('L1', 'L1 Modalities'),
    'Pyronecrosis': ('L1', 'L1 Modalities'),
    'Pyroptosis': ('L1', 'L1 Modalities'),
    'Regulated Necrosis': ('L1', 'L1 Modalities'),
    'Spectosis': ('L1', 'L1 Modalities'),
    'Triaptosis': ('L1', 'L1 Modalities'),
    'Vacuolar cell death': ('L1', 'L1 Modalities'),
    # L2 Subtypes (5)
    'Apoptosis (extrinsic)': ('L2', 'L2 Subtypes'),
    'Apoptosis (intrinsic)': ('L2', 'L2 Subtypes'),
    'Autosis': ('L2', 'L2 Subtypes'),
    'Lysosomal cell death': ('L2', 'L2 Subtypes'),
    'Mitotic death': ('L2', 'L2 Subtypes'),
    # L3 Triggers (3)
    'MPT-driven necrosis': ('L3', 'L3 Triggers'),
    'Mitochondrial permeability transition': ('L3', 'L3 Triggers'),
    'Mitotic catastrophe': ('L3', 'L3 Triggers'),
    # L4 Functional/conceptual (4)
    'Cellular senescence': ('L4', 'L4 Functional/conceptual'),
    'Efferocytosis': ('L4', 'L4 Functional/conceptual'),
    'Immunogenic cell death': ('L4', 'L4 Functional/conceptual'),
    'PANoptosis': ('L4', 'L4 Functional/conceptual'),
    # L5 Generic/composite (3)
    'Programmed cell death': ('L5', 'L5 Generic/composite'),
    'Senescence and Autophagy in Cancer': ('L5', 'L5 Generic/composite'),
    'Autophagy': ('L5', 'L5 Generic/composite'),
}

# Validate: 54 forms mapped
assert len(LEVEL_MAP) == 53, f"Expected 53 forms, got {len(LEVEL_MAP)}"

def main():
    with open(SRC, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f"V013: {len(rows)} rows, {len(fieldnames)} columns")

    # Check all forms in matrix are mapped
    matrix_forms = set(r['rcd_form_canonical'] for r in rows)
    unmapped = matrix_forms - set(LEVEL_MAP.keys())
    if unmapped:
        print(f"WARNING: {len(unmapped)} forms in matrix NOT in map: {unmapped}")

    # Add two new columns (after rcd_form_canonical for logical grouping)
    new_fieldnames = list(fieldnames)
    # Insert rcdome_level and rcdome_level_name right after rcd_form_canonical
    if 'rcdome_level' not in new_fieldnames:
        idx = new_fieldnames.index('rcd_form_canonical') + 1
        new_fieldnames.insert(idx, 'rcdome_level_name')
        new_fieldnames.insert(idx, 'rcdome_level')

    new_rows = []
    mapped_count = 0
    for r in rows:
        form = r['rcd_form_canonical']
        if form in LEVEL_MAP:
            level, name = LEVEL_MAP[form]
            r['rcdome_level'] = level
            r['rcdome_level_name'] = name
            mapped_count += 1
        else:
            r['rcdome_level'] = ''
            r['rcdome_level_name'] = ''
        new_rows.append(r)

    with open(DST, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"V014 written: {len(new_rows)} rows, {len(new_fieldnames)} columns")
    print(f"Forms mapped: {mapped_count} rows with ontology assignment")

    # Summary stats
    from collections import Counter
    level_counts = Counter(r['rcdome_level'] for r in new_rows if r['rcdome_level'])
    print(f"\nLevel distribution (rows):")
    for lv in ['L1', 'L2', 'L3', 'L4', 'L5']:
        print(f"  {lv}: {level_counts.get(lv, 0):,} rows")

    # Forms per level
    form_level = {}
    for r in new_rows:
        form_level[r['rcd_form_canonical']] = r['rcdome_level']
    level_forms = Counter(form_level.values())
    print(f"\nLevel distribution (forms):")
    for lv in ['L1', 'L2', 'L3', 'L4', 'L5']:
        forms = sorted(f for f, l in form_level.items() if l == lv)
        print(f"  {lv}: {level_forms.get(lv, 0)} forms")
        for f in forms:
            print(f"    - {f}")

    print(f"\nOutput: {DST}")

if __name__ == '__main__':
    main()
