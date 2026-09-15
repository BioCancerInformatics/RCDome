"""
utility_map_uniprot.py — Map UniProt IDs to Gene Symbols
===========================================================
Maps UniProt accession IDs to HGNC gene symbols via UniProt REST API.
Used by channel_b_ilir.py before merge into the unified gene-RCD matrix.

Usage: python utility_map_uniprot.py <input_csv> <output_csv> --col uniprot_id
"""

import csv, sys, time, urllib.request

def map_uniprot_batch(uniprot_ids, batch_size=100):
    """
    Map a list of UniProt accession IDs to gene symbols.
    Returns dict: {uniprot_id: gene_symbol}
    """
    id_to_gene = {}
    ids = list(uniprot_ids)
    
    for i in range(0, len(ids), batch_size):
        chunk = ids[i:i+batch_size]
        query = ','.join(chunk)
        url = f"https://rest.uniprot.org/uniprotkb/accessions?accessions={query}&format=tsv&fields=accession,gene_primary&size={batch_size}"
        
        try:
            req = urllib.request.Request(url)
            resp = urllib.request.urlopen(req).read().decode('utf-8')
            for line in resp.strip().split('\n')[1:]:
                parts = line.split('\t')
                if len(parts) >= 2:
                    uid = parts[0].strip()
                    gene = parts[1].strip()
                    if gene:
                        id_to_gene[uid] = gene
            time.sleep(0.3)
        except Exception as e:
            print(f"  Error at batch {i}: {str(e)[:100]}", file=sys.stderr)
    
    return id_to_gene


def add_gene_symbols(input_csv, output_csv, uniprot_col='uniprot_id'):
    """Read CSV, map UniProt IDs, write CSV with gene_symbol column added."""
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    
    # Collect unique UniProt IDs
    uniprots = set()
    for r in rows:
        uid = r.get(uniprot_col, '').strip()
        if uid:
            uniprots.add(uid)
    
    print(f"Unique UniProt IDs: {len(uniprots)}")
    
    # Map to gene symbols
    id_to_gene = map_uniprot_batch(uniprots)
    mapped = len(id_to_gene)
    print(f"Mapped: {mapped} / {len(uniprots)} ({mapped*100//max(1,len(uniprots))}%)")
    
    # Add gene_symbol column
    for r in rows:
        uid = r.get(uniprot_col, '').strip()
        r['gene_symbol'] = id_to_gene.get(uid, '')
    
    fieldnames = list(rows[0].keys())
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    
    print(f"Output: {output_csv}")
    return rows


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        add_gene_symbols(sys.argv[1], sys.argv[2])
    else:
        # Default: process iLIR output
        import os
        base = os.path.dirname(os.path.abspath(__file__))
        inp = os.path.join(base, '..', 'output databases', 'gene_rcd_ilir.csv')
        out = inp  # overwrite
        if os.path.exists(inp):
            add_gene_symbols(inp, out)
        else:
            print(f"Usage: python utility_map_uniprot.py <input_csv> <output_csv>")
            print(f"Default input not found: {inp}")
