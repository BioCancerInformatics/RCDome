"""
channel_b_msigdb.py — Extract genes from MSigDB/GSEA gene sets
=================================================================
AMENDED (Victor Lopes curation, 2026): replaces the original 13 hardcoded
gene sets with the 238 biologically curated "considerar" sets from the
systematic search of all 54 RCD entities (main + complementary terms).

Conceptual improvement:
  - Original: 13 hand-picked gene sets (limited, undocumented selection)
  - Amended:  238 curated sets, each with documented biological rationale
               (inclusion vs exclusion criteria recorded in
               RCDome_MSigDB_Curadoria_Manual_Completa.xlsx)

Source: MSigDB 2026.1 (https://data.broadinstitute.org/gsea-msigdb/)
Output: gene_rcd_msigdb.csv
"""
import csv, os, io, sys, urllib.request, openpyxl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(BASE_DIR, 'output databases', 'gene_rcd_msigdb.csv')
XLSX = os.path.join(BASE_DIR, 'Victor_analysis', 'RCDome_MSigDB_Curadoria_Manual_Completa.xlsx')

# Gene sets retired in MSigDB (archived). Excluded with note per Victor Lopes (2026-08-17):
# REACTOME_EXTRINSIC_PATHWAY_FOR_APOPTOSIS was moved to the archive in v7.3 (obsolete Reactome build).
ARCHIVED_SETS = {'REACTOME_EXTRINSIC_PATHWAY_FOR_APOPTOSIS'}

# MSigDB 2026.1 GMT release URLs
GMT_URLS = [
    'https://data.broadinstitute.org/gsea-msigdb/msigdb/release/2026.1.Hs/c5.all.v2026.1.Hs.symbols.gmt',   # GO
    'https://data.broadinstitute.org/gsea-msigdb/msigdb/release/2026.1.Hs/c2.all.v2026.1.Hs.symbols.gmt',   # curated (KEGG/Reactome/WP)
    'https://data.broadinstitute.org/gsea-msigdb/msigdb/release/2026.1.Hs/h.all.v2026.1.Hs.symbols.gmt',    # Hallmark
]

def download_gmt(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=120).read().decode('utf-8')

def parse_gmt(data):
    gs = {}
    for line in data.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) >= 3:
            gs[parts[0]] = set(g for g in parts[2:] if g.strip())
    return gs

def load_victor_curation():
    """Read the 238 'considerar' sets (RCD form + gene set name) from Victor's Excel."""
    wb = openpyxl.load_workbook(XLSX, read_only=True)
    ws = wb['Novos_Candidatos']
    sets = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        rcd = str(row[0]).strip() if row[0] else ''
        name = str(row[1]).strip() if row[1] else ''
        consider = str(row[3]).strip() if row[3] else ''
        if rcd and name and consider not in ('—', '-', 'None', ''):
            sets.append((rcd, name))
    return sets

def extract():
    # 1. Download + parse GMT (full collections)
    print("Downloading MSigDB 2026.1 GMT collections...")
    gmt = {}
    for url in GMT_URLS:
        gmt.update(parse_gmt(download_gmt(url)))
    print(f"  Parsed {len(gmt)} gene sets")

    # 2. Load Victor's curated 'considerar' sets
    curation = load_victor_curation()
    print(f"  Victor's 'considerar' sets: {len(curation)}")

    # 2b. Exclude archived (retired) sets — per Victor Lopes (2026-08-17)
    archived = [s for s in curation if s[1] in ARCHIVED_SETS]
    curation = [s for s in curation if s[1] not in ARCHIVED_SETS]
    if archived:
        print(f"  Archived sets excluded (obsolete Reactome build): {[a[1] for a in archived]}")

    # 3. Match to GMT and extract genes
    matched = [(rcd, name) for rcd, name in curation if name in gmt]
    unmatched = [name for rcd, name in curation if name not in gmt]
    print(f"  Matched: {len(matched)} | Unmatched (renamed/removed in 2026.1): {len(unmatched)}")

    all_rows = []
    for rcd, gs_name in matched:
        for g in sorted(gmt[gs_name]):
            all_rows.append([g, rcd, gs_name])

    # 4. Write output
    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['gene_symbol', 'rcd_form', 'msigdb_gene_set', 'source_databases',
                    'source_channel', 'evidence_type', 'curator_verified'])
        for r in all_rows:
            w.writerow([r[0], r[1], r[2], 'MSigDB', 'B', f'msigdb_{r[2]}', 'FALSE'])

    print(f"\nMSigDB (amended): {len(all_rows)} gene-RCD entries -> {OUTPUT}")
    if unmatched:
        print(f"  Excluded {len(unmatched)} unmatched sets (pending Victor's confirmation):")
        for n in unmatched:
            print(f"    {n}")

    return all_rows, unmatched

if __name__ == '__main__':
    extract()
