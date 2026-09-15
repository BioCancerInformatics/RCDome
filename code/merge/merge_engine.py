"""
merge_engine.py — Unified Gene-RCD Matrix Builder (V3 — Evidence Quality)
===========================================================================
Merges 15 certified CSVs. Tracks curated vs keyword evidence quality.
Preserves original rcd_form. Adds rcd_form_canonical placeholder.

Output: unified_gene_rcd_matrix.csv
"""

import csv, os
from collections import defaultdict

INPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output databases')
OUTPUT = os.path.join(INPUT_DIR, 'unified_gene_rcd_matrix.csv')

SOURCES = {
    'gene_rcd_rodrigues2025.csv': 'Rodrigues2025',
    'gene_rcd_ferrdb_v3.csv': 'FerrDB',
    'gene_rcd_rcddb.csv': 'RCDdb',
    'gene_rcd_ipcd.csv': 'iPCD',
    'gene_rcd_lncrcd.csv': 'LncRCD',
    'gene_rcd_ilir.csv': 'iLIR',
    'gene_rcd_hadb.csv': 'HADb',
    'gene_rcd_hamdb.csv': 'HAMdb',
    'gene_rcd_atd.csv': 'ATD',
    'gene_rcd_amtdb.csv': 'AMT-DB',
    'gene_rcd_kegg.csv': 'KEGG',
    'gene_rcd_reactome.csv': 'Reactome',
    'gene_rcd_go.csv': 'GO',
    'gene_rcd_msigdb.csv': 'MSigDB',
    'gene_rcd_ncbi_gene.csv': 'NCBI_Gene',
}

# Evidence quality per source: curated (explicit RCD association) vs keyword (text search)
EVIDENCE_QUALITY = {
    'Rodrigues2025': 'curated', 'FerrDB': 'curated', 'RCDdb': 'curated',
    'iPCD': 'curated', 'LncRCD': 'curated', 'iLIR': 'curated',
    'HADb': 'curated', 'HAMdb': 'curated', 'ATD': 'curated',
    'AMT-DB': 'curated', 'KEGG': 'curated', 'Reactome': 'curated',
    'GO': 'curated', 'MSigDB': 'curated',
    'NCBI_Gene': 'keyword',
}


def merge():
    matrix = defaultdict(lambda: {
        'sources': set(), 'channels': set(), 'pmids': set(),
        'evidences': [], 'qualities': set(), 'uniprot': '', 'ensembl': '', 'gene_type': ''
    })

    for fname, source_name in SOURCES.items():
        fpath = os.path.join(INPUT_DIR, fname)
        if not os.path.exists(fpath):
            print(f"  SKIP: {fname}")
            continue

        with open(fpath, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))

        for row in rows:
            gene = row.get('gene_symbol', '').strip()
            rcd_original = row.get('rcd_form', '').strip()
            if not gene or not rcd_original:
                continue

            key = (gene, rcd_original)
            entry = matrix[key]
            entry['sources'].add(source_name)
            entry['qualities'].add(EVIDENCE_QUALITY.get(source_name, 'curated'))

            ch = row.get('source_channel', '').strip()
            for c in ch.split(','):
                c = c.strip()
                if c: entry['channels'].add(c)

            pmid = row.get('pmid', '') or row.get('pmid_list', '')
            for p in pmid.replace(';', ',').split(','):
                p = p.strip()
                if p.isdigit(): entry['pmids'].add(p)

            ev = row.get('evidence_type', '').strip()
            if ev: entry['evidences'].append(ev)

            for col, target in [('uniprot_id', 'uniprot'), ('ensembl_id', 'ensembl'), ('gene_type', 'gene_type')]:
                val = row.get(col, '').strip()
                if val and not entry[target]:
                    entry[target] = val

    # Build output
    output_rows = []
    for (gene, rcd_original), entry in sorted(matrix.items()):
        sources = sorted(entry['sources'])
        channels = sorted(entry['channels'])
        pmids = sorted(entry['pmids'])
        evidences = sorted(set(entry['evidences']))
        qualities = sorted(entry['qualities'])

        # Evidence quality: curated-only, keyword-only, or mixed
        if len(qualities) == 1:
            eq = qualities[0]
        else:
            eq = 'mixed'

        # Confidence score
        score = 0
        if 'D' in channels: score += 4
        if 'B' in channels: score += 3
        if 'A' in channels: score += 1
        if 'C' in channels: score += 1
        tier = 'T1' if score >= 7 else 'T2' if score >= 4 else 'T3' if score >= 2 else 'T4'

        output_rows.append({
            'gene_symbol': gene,
            'rcd_form': rcd_original,
            'rcd_form_canonical': '',
            'source_databases': ';'.join(sources),
            'source_channels': ';'.join(channels),
            'num_sources': len(sources),
            'evidence_quality': eq,
            'evidence_types': ';'.join(evidences),
            'pmid_list': ';'.join(pmids[:10]),
            'confidence_score': score,
            'confidence_tier': tier,
            'uniprot_id': entry['uniprot'],
            'ensembl_id': entry['ensembl'],
            'gene_type': entry['gene_type'],
        })

    fieldnames = ['gene_symbol', 'rcd_form', 'rcd_form_canonical',
                  'source_databases', 'source_channels', 'num_sources',
                  'evidence_quality', 'evidence_types', 'pmid_list',
                  'confidence_score', 'confidence_tier',
                  'uniprot_id', 'ensembl_id', 'gene_type']

    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        w.writerows(output_rows)

    # Stats
    genes = set(r['gene_symbol'] for r in output_rows)
    raw_forms = set(r['rcd_form'] for r in output_rows)
    tiers = defaultdict(int)
    eq_counts = defaultdict(int)
    for r in output_rows:
        tiers[r['confidence_tier']] += 1
        eq_counts[r['evidence_quality']] += 1

    print("=" * 60)
    print("UNIFIED GENE-RCD MATRIX — MERGE COMPLETE (V3)")
    print("=" * 60)
    print(f"Rows: {len(output_rows):,}  |  Genes: {len(genes):,}  |  RCD forms: {len(raw_forms)}")
    print(f"\nEvidence quality:")
    for eq in ['curated', 'mixed', 'keyword']:
        print(f"  {eq}: {eq_counts.get(eq, 0):,}")
    print(f"\nConfidence tiers:")
    for t in ['T1', 'T2', 'T3', 'T4']:
        print(f"  {t}: {tiers.get(t, 0):,}")
    print(f"\nOutput: {OUTPUT}")

if __name__ == '__main__':
    merge()
