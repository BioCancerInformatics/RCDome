#!/usr/bin/env python3
"""
XDeathDB extraction. Victor to provide: XDeathDB.csv (downloaded from Shiny app)
1. Read CSV, normalize gene symbols to HGNC approved
2. Map 12 RCD forms to RCDome canonical forms
3. Append to unified_gene_rcd_matrix
Source: https://pcm2019.shinyapps.io/XDeathDB/
"""
import csv, json, os, sys, urllib.request

# === CONFIG ===
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XDEATHDB_CSV = os.path.join(BASE, 'output databases', 'XDeathDB.csv')
MATRIX_FILE = os.path.join(BASE, 'output databases', 'Phase 2C output', 'unified_gene_rcd_matrix_26cols.csv')

XDATH_MAP = {
    # Map XDeathDB cell death names to RCDome canonical
    'apoptosis': 'Apoptosis',
    'necroptosis': 'Necroptosis',
    'pyroptosis': 'Pyroptosis',
    'ferroptosis': 'Ferroptosis',
    'autophagy': 'Autophagy-dependent cell death',
    'parthanatos': 'Parthanatos',
    'netosis': 'NETosis',
    'entosis': 'Entotic cell death',
    'mitotic catastrophe': 'Mitotic death',
    'immunogenic cell death': 'Immunogenic cell death',
    'anoikis': 'Anoikis',
    'lysosomal cell death': 'Lysosomal cell death',
}

def load_hgnc():
    """Load HGNC approved symbols and alias map."""
    req = urllib.request.Request(
        'https://rest.genenames.org/fetch/status/Approved',
        headers={'Accept': 'application/json'}
    )
    data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    approved = set(doc['symbol'] for doc in data['response']['docs'])
    alias_map = {}
    for doc in data['response']['docs']:
        approved_sym = doc['symbol']
        alias_map[approved_sym] = approved_sym
        for alias in doc.get('alias_symbol', []):
            alias_map[alias.upper()] = approved_sym
        for prev in doc.get('prev_symbol', []):
            alias_map[prev.upper()] = approved_sym
    return approved, alias_map

def normalize_gene(symbol, approved, alias_map):
    """Normalize a gene symbol to HGNC approved."""
    s = symbol.strip().upper()
    if s in alias_map:
        return alias_map[s]
    return None

def main():
    if not os.path.exists(XDEATHDB_CSV):
        print(f"ERROR: {XDEATHDB_CSV} not found. Download from https://pcm2019.shinyapps.io/XDeathDB/")
        sys.exit(1)

    approved, alias_map = load_hgnc()
    print(f"HGNC: {len(approved)} approved symbols, {len(alias_map)} aliases")

    # Read XDeathDB CSV
    xdeath_genes = []
    with open(XDEATHDB_CSV, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        print(f"XDeathDB CSV: {len(header)} columns: {header}")

        for row in reader:
            if len(row) < 2:
                continue
            # Try to detect gene and RCD columns
            gene_sym = row[0].strip()
            rcd_name = row[1].strip() if len(row) > 1 else ''

            # Try mapping
            rcd_canonical = XDATH_MAP.get(rcd_name.lower(), rcd_name)
            norm = normalize_gene(gene_sym, approved, alias_map)
            if norm:
                xdeath_genes.append({
                    'gene': norm,
                    'rcd_original': rcd_name,
                    'rcd_canonical': rcd_canonical,
                    'original': gene_sym,
                })

    print(f"Normalized: {len(xdeath_genes)} genes")

    # Add to matrix
    matrix = list(csv.DictReader(open(MATRIX_FILE, encoding='utf-8-sig')))
    cols = list(matrix[0].keys())
    added = 0

    for item in xdeath_genes:
        r = {c: '' for c in cols}
        r.update({
            'gene_symbol': item['gene'],
            'rcd_form': item['rcd_canonical'],
            'rcd_form_canonical': item['rcd_canonical'],
            'source_databases': 'XDeathDB',
            'source_channels': 'B',
            'num_sources': '1',
            'evidence_quality': 'curated',
            'evidence_types': 'xdeathdb_curated',
            'evidence_basis': f'XDeathDB: Crosstalk Death-DB curated inventory (original: {item["original"]})',
            'confidence_score': '5',
            'confidence_tier': 'T2',
            'evidence_tier': 'T2',
            'gene_symbol_status': 'valid',
        })
        matrix.append(r)
        added += 1

    with open(MATRIX_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(matrix)

    print(f"Added: {added} rows | Matrix: {len(matrix)} rows")
    # Summary
    from collections import Counter
    forms = Counter(item['rcd_canonical'] for item in xdeath_genes)
    for f, c in forms.most_common():
        print(f"  {f}: {c}")

if __name__ == '__main__':
    main()
