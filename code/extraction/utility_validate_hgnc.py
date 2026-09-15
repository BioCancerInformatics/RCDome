"""
utility_validate_hgnc.py — Validate Gene Symbols Against HGNC
===============================================================
Downloads the complete HGNC approved symbol set and validates
all gene_symbol entries in the unified matrix.

Usage: python utility_validate_hgnc.py <input_csv> <output_csv>
"""

import csv, sys, urllib.request, json

HGNC_API = 'https://rest.genenames.org/fetch/status/Approved'

def load_hgnc_approved():
    """Download and return set of all HGNC-approved gene symbols."""
    print(f"Downloading HGNC approved symbols from {HGNC_API}...")
    req = urllib.request.Request(HGNC_API, headers={'Accept': 'application/json'})
    resp = urllib.request.urlopen(req).read().decode('utf-8')
    data = json.loads(resp)
    symbols = set(d['symbol'] for d in data['response']['docs'])
    print(f"  Loaded {len(symbols):,} HGNC-approved symbols")
    return symbols


def validate(input_csv, output_csv):
    """Add gene_symbol_status column to CSV based on HGNC validation."""
    hgnc = load_hgnc_approved()

    with open(input_csv, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    valid = 0
    invalid = 0
    for r in rows:
        g = r.get('gene_symbol', '').strip()
        if g in hgnc:
            r['gene_symbol_status'] = 'valid'
            valid += 1
        else:
            r['gene_symbol_status'] = 'invalid'
            invalid += 1

    fieldnames = list(rows[0].keys())
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"Results: {valid:,} valid, {invalid:,} invalid ({invalid*100//max(1,valid+invalid)}%)")
    return rows


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        validate(sys.argv[1], sys.argv[2])
    else:
        # Default: validate the unified matrix
        import os
        base = os.path.dirname(os.path.abspath(__file__))
        inp = os.path.join(base, '..', 'output databases', 'unified_gene_rcd_matrix.csv')
        out = inp
        if os.path.exists(inp):
            validate(inp, out)
        else:
            print("Usage: python utility_validate_hgnc.py <input_csv> <output_csv>")
