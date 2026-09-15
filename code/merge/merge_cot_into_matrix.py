#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_cot_into_V023.py — merge DeepSeek CoT results into V023.

Merges the DeepSeek chain-of-thought classification (4 new columns:
cot_role, cot_direction, cot_mechanistic, cot_evidence) from the
DeepSeek-updated V022 matrix (transferred from Zima) into the V023
truth-reference matrix (laptop).

USAGE:
    python3 merge_cot_into_V023.py <deepseek_v022.csv> [output.csv]

WHAT IT DOES:
    1. Reads the DeepSeek-updated V022 (must contain the 4 cot_* columns).
    2. Reads V023 (laptop truth reference, 22,474 rows).
    3. Builds pair-key -> cot_* lookup from V022.
    4. For each V023 row, matches by gene_symbol|rcd_form_canonical,
       applying the 6-symbol REVERSE remap (V023 name -> V022 name).
    5. Fills the 4 cot_* columns (leaves empty when no match).
    6. Writes the merged V023 and prints an audit report.

EXPECTED RESULT:
    matched  = 22,472 rows
    renamed  = 7 rows (the 6 remapped symbols; IL1RL1 has 2 rows)
    unmatched= 2 rows (NLRX1, PPIF — the Elicit additions, not in the run)
"""
import csv
import os
import sys

csv.field_size_limit(2 ** 31 - 1)  # avoid 131KB field limit on long text cells

BASE = os.path.dirname(os.path.abspath(__file__))
V023_FILE = os.path.join(BASE, '..', 'output databases', 'Phase 2C output', 'unified_gene_rcd_matrix_V023.csv')
DEFAULT_OUT = os.path.join(BASE, '..', 'output databases', 'Phase 2C output', 'unified_gene_rcd_matrix_V023_cot.csv')

COT_COLS = ['cot_role', 'cot_direction', 'cot_mechanistic', 'cot_evidence']

# Reverse remap: V023 (current) -> V022 (old, used by DeepSeek)
REMAP_V023_TO_V022 = {
    'IL33R': 'IL1RL1',
    'LMTK1': 'AATK',
    'TIPE1': 'TNFAIP8L1',
    'TIPE2': 'TNFAIP8L2',
    'TIPE3': 'TNFAIP8L3',
    'CBSL': 'ENSG00000274276',
}

# The 2 pairs added from the Elicit alert — expected to be UNMATCHED (not in the run)
EXPECTED_UNMATCHED = {'NLRX1|MPT-driven necrosis', 'PPIF|MPT-driven necrosis'}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    deepseek_v022 = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT

    # 1. Read DeepSeek-updated V022
    with open(deepseek_v022, encoding='utf-8-sig', newline='') as f:
        rows22 = list(csv.DictReader(f))
    missing = [c for c in COT_COLS if c not in rows22[0]]
    if missing:
        print(f"ERROR: DeepSeek V022 is missing columns {missing}. Is the run complete?")
        sys.exit(1)
    print(f"[1] DeepSeek V022 : {len(rows22):,} rows, cot_* columns present")

    # 2. Read V023
    with open(V023_FILE, encoding='utf-8-sig', newline='') as f:
        rows23 = list(csv.DictReader(f))
    print(f"[2] V023          : {len(rows23):,} rows")

    # 3. Build lookup
    lookup = {}
    for r in rows22:
        key = f"{r['gene_symbol']}|{r['rcd_form_canonical']}"
        lookup[key] = {c: r.get(c, '') for c in COT_COLS}
    print(f"[3] lookup keys   : {len(lookup):,}")

    # 4. Merge
    matched = renamed = unmatched = 0
    unmatched_pairs = set()
    for r in rows23:
        sym = r['gene_symbol']
        sym22 = REMAP_V023_TO_V022.get(sym, sym)
        key = f"{sym22}|{r['rcd_form_canonical']}"
        if key in lookup:
            for c in COT_COLS:
                r[c] = lookup[key][c]
            matched += 1
            if sym22 != sym:
                renamed += 1
        else:
            unmatched += 1
            unmatched_pairs.add(f"{sym}|{r['rcd_form_canonical']}")

    # 5. Write merged
    fieldnames = list(rows23[0].keys())
    for c in COT_COLS:
        if c not in fieldnames:
            fieldnames.append(c)
    with open(out_file, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows23)
    print(f"[4] merged written: {out_file}")
    print(f"    ({len(rows23):,} rows x {len(fieldnames)} cols)")

    # 6. Audit report
    print()
    print("=== MERGE REPORT ===")
    print(f"  matched  : {matched:,}")
    print(f"  renamed  : {renamed:,}  (6-symbol reverse remap)")
    print(f"  unmatched: {unmatched:,}")
    for p in sorted(unmatched_pairs):
        print(f"      - {p}")

    # 7. Assertions
    extra = unmatched_pairs - EXPECTED_UNMATCHED
    if extra:
        print()
        print(f"WARNING: unexpected unmatched pairs: {sorted(extra)}")
        print("         review these before accepting the merge.")
    else:
        print()
        print("OK: only the 2 expected Elicit-additions (NLRX1, PPIF) are unmatched.")
    if matched + unmatched != len(rows23):
        print("ERROR: matched+unmatched != total V023 rows — data integrity issue.")


if __name__ == '__main__':
    main()
