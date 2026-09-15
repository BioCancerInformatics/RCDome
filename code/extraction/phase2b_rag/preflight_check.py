#!/usr/bin/env python3
"""Pre-flight check for Phase 2B. Validates matrix before RAG processing."""
import csv, sys

MATRIX_FILE = '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/output databases/unified_gene_rcd_matrix.csv'

EXPECTED = {
    'rows': 24834,
    'cols': 28,
    'has_elicit': True,
    'min_pairs_with_pmids': 24500,
    'has_mechanistic_class': True,
    'has_cancer_gene_type': True,
    'has_rcd_gene_type': True,
}

with open(MATRIX_FILE, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))
    cols = list(rows[0].keys())

errors = []

if len(rows) != EXPECTED['rows']:
    errors.append(f"ROWS: {len(rows)} (expected {EXPECTED['rows']})")
if len(cols) != EXPECTED['cols']:
    errors.append(f"COLS: {len(cols)} (expected {EXPECTED['cols']}) — WRONG MATRIX VERSION")
if 'elicit_pmids' not in cols:
    errors.append("MISSING elicit_pmids column — OLD MATRIX")
if 'mechanistic_class' not in cols:
    errors.append("MISSING mechanistic_class column")
if 'cancer_gene_type' not in cols:
    errors.append("MISSING cancer_gene_type column")
if 'rcd_gene_type' not in cols:
    errors.append("MISSING rcd_gene_type column")

pairs_with = 0
for r in rows:
    for c in ['pmid_list','llm_pmids','epmc_pmids','elicit_pmids']:
        v = r.get(c,'').strip()
        if v and v not in ('LITERATURE_NOT_FOUND','NOT_RECOVERED') and any(p.isdigit() for p in v.split(';')):
            pairs_with += 1
            break

if pairs_with < EXPECTED['min_pairs_with_pmids']:
    errors.append(f"PAIRS WITH PMIDS: {pairs_with} (expected >= {EXPECTED['min_pairs_with_pmids']})")

if errors:
    print("PRE-FLIGHT FAILED:")
    for e in errors:
        print(f"  X {e}")
    sys.exit(1)
else:
    print(f"PRE-FLIGHT PASSED: {len(rows)} rows x {len(cols)} cols, {pairs_with} pairs with PMIDs")
