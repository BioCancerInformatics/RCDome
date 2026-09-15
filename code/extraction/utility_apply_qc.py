"""
utility_apply_qc.py - Quality Control: NCBI Noise Exclusion + HGNC Validation
==============================================================================
Takes raw merge_engine output and produces the final pre-Phase 2A matrix.
Steps:
  1. Exclude NCBI Gene keyword-only noise (10,857 rows)
  2. Validate against HGNC, exclude invalid symbols (696 rows)
  3. Enrich with gene_symbol_status, gene_biotype, uniprot_id, ensembl_id

Usage: python utility_apply_qc.py <raw_matrix.csv> <output_matrix.csv>
"""

import csv, sys, urllib.request, json

def load_hgnc():
    req = urllib.request.Request('https://rest.genenames.org/fetch/status/Approved',
                                  headers={'Accept': 'application/json'})
    data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    symbols = set(d['symbol'] for d in data['response']['docs'])
    enrich = {}
    for d in data['response']['docs']:
        sym = d['symbol']
        lt = d.get('locus_type', '')
        if 'protein' in lt.lower(): bt = 'protein_coding'
        elif 'long non-coding' in lt.lower(): bt = 'lncRNA'
        elif 'micro' in lt.lower(): bt = 'miRNA'
        elif 'pseudogene' in lt.lower(): bt = 'pseudogene'
        elif 'RNA' in lt: bt = 'other_RNA'
        else: bt = 'other'
        enrich[sym] = {'biotype': bt, 'uniprot': (d.get('uniprot_ids') or [''])[0],
                       'ensembl': d.get('ensembl_gene_id', '')}
    return symbols, enrich

def main():
    if len(sys.argv) < 3:
        print("Usage: python utility_apply_qc.py <raw_matrix.csv> <output_matrix.csv>")
        return
    
    input_csv = sys.argv[1]
    output_csv = sys.argv[2]
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    print(f"Loaded: {len(rows)} rows")
    
    # Step 1: Exclude NCBI Gene keyword-only noise
    excluded_noise = [r for r in rows if r.get('evidence_quality') == 'keyword' and r.get('source_channels') == 'B']
    rows = [r for r in rows if r not in excluded_noise]
    print(f"After NCBI noise exclusion: {len(rows)} rows ({len(excluded_noise)} excluded)")
    
    # Step 2-3: HGNC validation + enrichment
    hgnc_symbols, hgnc_enrich = load_hgnc()
    
    excluded_hgnc = [r for r in rows if r['gene_symbol'] not in hgnc_symbols]
    rows = [r for r in rows if r['gene_symbol'] in hgnc_symbols]
    print(f"After HGNC validation: {len(rows)} rows ({len(excluded_hgnc)} excluded)")
    
    # Enrich
    enriched = 0
    for r in rows:
        s = r['gene_symbol']
        e = hgnc_enrich.get(s, {})
        r['gene_symbol_status'] = 'valid' if s in hgnc_symbols else 'invalid'
        r['gene_biotype'] = e.get('biotype', '')
        if not r.get('uniprot_id', '').strip():
            r['uniprot_id'] = e.get('uniprot', '')
        if not r.get('ensembl_id', '').strip():
            r['ensembl_id'] = e.get('ensembl', '')
        enriched += 1
    
    columns = list(rows[0].keys())
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)
    
    print(f"Output: {len(rows)} rows, {len(columns)} columns -> {output_csv}")

if __name__ == '__main__':
    main()
