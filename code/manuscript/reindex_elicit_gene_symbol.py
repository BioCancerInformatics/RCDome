# -*- coding: utf-8 -*-
"""
reindex_elicit_gene_symbol.py — re-index the Elicit Phase 3B raw data by the
gene_symbol column ONLY (split by comma/semicolon), keeping ALL genes, and add
the elicit_multi_gene flag. Produces a DELTA report + a re-indexed matrix copy.
Does NOT overwrite the live matrix (a separate -reindexed file is written).

Governance: the original reintegrate_phase3b_v020.py is untouched; the matrix
stays V027 (this is an amendment, logged by date + delta).
"""
import csv, glob, re, os, sys
from collections import defaultdict

csv.field_size_limit(2**31 - 1)
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript'
P3B = os.path.join(BASE, 'output databases', 'Phase 3B output')
MAT = os.path.join(BASE, 'RCDome_distribution', 'data', 'unified_gene_rcd_matrix_V027.csv')
OUT = os.path.join(BASE, 'RCDome_distribution', 'data', 'unified_gene_rcd_matrix_V027_reindexed.csv')
DELTA = os.path.join(BASE, 'docs', 'TRACEABILITY_elicit_reindex_delta.csv')

GENE_OK = re.compile(r'^[A-Z][A-Z0-9-]{1,30}$')

# 1. build the corrected index: (form, gene) -> list of raw rows, gene from gene_symbol column
corrected = defaultdict(list)
multi_gene_papers = {}  # (form, DOI or first title) -> bool
for fn in glob.glob(os.path.join(P3B, '*_output', '*_raw.csv')):
    base = os.path.basename(fn).replace('_raw.csv', '')
    gfn = os.path.join(os.path.dirname(fn), base + '_governed.csv')
    form = None
    if os.path.exists(gfn):
        rows = list(csv.DictReader(open(gfn, encoding='utf-8-sig')))
        if rows:
            form = rows[0].get('rcd_form_canonical', '').strip() or base.replace('_', ' ')
    if not form:
        form = base.replace('_', ' ')
    for r in csv.DictReader(open(fn, encoding='utf-8-sig')):
        gs = (r.get('gene_symbol') or '').strip()
        genes = {g.strip().upper() for g in re.split(r'[,;]', gs)
                 if g.strip() and GENE_OK.match(g.strip())}
        paper_key = (form, (r.get('DOI') or '').strip() or (r.get('Title') or '').strip())
        multi_gene_papers[paper_key] = len(genes) > 1
        for g in genes:
            corrected[(form, g)].append(r)

# 2. recompute the raw-derived Elicit columns for each matrix row
rows = list(csv.DictReader(open(MAT, encoding='utf-8-sig')))
cols = list(rows[0].keys())
if 'elicit_multi_gene' not in cols:
    cols.append('elicit_multi_gene')
    for r in rows:
        r['elicit_multi_gene'] = ''

raw_cols = ['elicit_verbatim_sentence', 'elicit_doi', 'elicit_title',
            'elicit_authors', 'elicit_venue', 'elicit_year']

delta = []
for r in rows:
    g = (r.get('gene_symbol') or '').strip().upper()
    form = (r.get('rcd_form_canonical') or '').strip()
    raw = corrected.get((form, g), [])
    new = {}
    for c in raw_cols:
        src = {'elicit_verbatim_sentence': 'verbatim_sentence',
               'elicit_doi': 'DOI', 'elicit_title': 'Title',
               'elicit_authors': 'Authors', 'elicit_venue': 'Venue',
               'elicit_year': 'Year'}[c]
        new[c] = '; '.join(x.get(src, '').strip() for x in raw if x.get(src, '').strip())
    multi = any(multi_gene_papers.get((form, (x.get('DOI') or '').strip() or (x.get('Title') or '').strip()), False)
                for x in raw)
    old_verb = (r.get('elicit_verbatim_sentence') or '').strip()
    new_verb = new['elicit_verbatim_sentence'].strip()
    # classification for the delta
    if old_verb == new_verb:
        cls = 'SAME'
    elif not new_verb:
        cls = 'LOSE'
    elif re.sub(r'\s+', '', old_verb) == re.sub(r'\s+', '', new_verb):
        cls = 'TRIVIAL'
    else:
        cls = 'SWAP'
    if cls != 'SAME':
        delta.append({'gene_symbol': r.get('gene_symbol'), 'rcd_form_canonical': r.get('rcd_form_canonical'),
                      'change': cls, 'old_verbatim': old_verb[:500], 'new_verbatim': new_verb[:500]})
    # apply to the row
    for c in raw_cols:
        r[c] = new[c]
    r['elicit_multi_gene'] = 'TRUE' if multi else 'FALSE'

# 3. write the re-indexed matrix + the delta
with open(OUT, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

with open(DELTA, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['gene_symbol', 'rcd_form_canonical', 'change', 'old_verbatim', 'new_verbatim'])
    w.writeheader()
    w.writerows(delta)

from collections import Counter
c = Counter(d['change'] for d in delta)
print('reindexed matrix written:', OUT)
print('delta written:', DELTA)
print('delta classification:', dict(c))
print('rows with elicit_multi_gene=TRUE:', sum(1 for r in rows if r['elicit_multi_gene'] == 'TRUE'))
