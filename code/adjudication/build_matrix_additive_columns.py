# -*- coding: utf-8 -*-
"""Build the additive adjudication columns for the V027 matrix (Option B + agreement policy).
Never overwrites cot_*/consensus_*. Adds 11 columns. Saves CSV (and RDS via R).
"""
import sys, csv, json, glob, os
import openpyxl
sys.stdout.reconfigure(encoding='utf-8')
csv.field_size_limit(10**9)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = glob.glob(os.path.join(ROOT, 'manuscript_V027', 'Higor*'))[0] + os.sep
MATRIX = os.path.join(ROOT, 'RCDome_distribution', 'data', 'unified_gene_rcd_matrix_V027.csv')
OUT = os.path.join(ROOT, 'RCDome_distribution', 'data', 'unified_gene_rcd_matrix_V027.csv')

# 1. load Track tables -> per (gene,form,label) records
track = {}  # (g,f,label) -> dict(final_verdict, gpt4o, higor, victor, evidence, source)
for t in ['A', 'B']:
    wb = openpyxl.load_workbook(base + f'human_resolution_worksheet_track{t}_Higor_Victor.xlsx', read_only=True)
    ws = wb.active; hdr = [c.value for c in ws[1]]; cmap = {h: i for i, h in enumerate(hdr)}
    evcol = 'verbatim' if t == 'A' else 'abstract'
    for row in ws.iter_rows(values_only=True):
        if row[cmap['label']] in (None, 'label'): continue
        g, f, lab = row[cmap['gene_symbol']], row[cmap['rcd_form_canonical']], row[cmap['label']]
        track[(g, f, lab)] = {
            'final': row[cmap['final_verdict']],
            'gpt4o': row[cmap['gpt4o_verdict']] if 'gpt4o_verdict' in cmap else '',
            'higor': row[cmap['higor_verdict']] if 'higor_verdict' in cmap else '',
            'victor': row[cmap['victor_verdict']] if 'victor_verdict' in cmap else '',
            'evidence': (row[cmap[evcol]] or ''),
            'source': 'verbatim' if t == 'A' else 'abstract',
        }

# 2. load delta pairs
delta = set()
for t in ['A', 'B']:
    wb = openpyxl.load_workbook(base + f'human_resolution_worksheet_delta_track{t}_Higor_Victor.xlsx', read_only=True)
    ws = wb.active; hdr = [c.value for c in ws[1]]; cmap = {h: i for i, h in enumerate(hdr)}
    for row in ws.iter_rows(values_only=True):
        if row[cmap['label']] in (None, 'label'): continue
        delta.add((row[cmap['gene_symbol']], row[cmap['rcd_form_canonical']]))

# 3. load agreement pool abstract-based check + verbatim
ag_final = json.load(open(os.path.join(ROOT, 'manuscript_V027', 'agreement_pool_final_verdicts.json'), encoding='utf-8'))
ag_prog = json.load(open(os.path.join(ROOT, 'manuscript_V027', 'verbatim_agreement_progress.json'), encoding='utf-8'))

# 4. load matrix + build new rows
r = list(csv.DictReader(open(MATRIX, encoding='utf-8-sig')))
orig_fields = list(r[0].keys())
ADD = ['final_mechanistic', 'final_role', 'final_direction', 'final_verdict',
       'gpt4o_verdict', 'curator_1_verdict', 'curator_2_verdict',
       'deciding_evidence', 'evidence_source', 'decision_status', 'abstract_check']

def get_track_pair(g, f):
    recs = {lab: track.get((g, f, lab)) for lab in ['mechanistic', 'role', 'direction']}
    return recs

def join3(recs, key):
    vals = []
    for lab in ['mechanistic', 'role', 'direction']:
        r = recs.get(lab)
        vals.append(str(r[key]) if r and r[key] not in (None, '') else '')
    return '|'.join(vals)

out_rows = []
for x in r:
    g, f = x['gene_symbol'], x['rcd_form_canonical']
    add = {c: '' for c in ADD}
    if (g, f) in delta:
        add['decision_status'] = 'PENDING_DELTA'
    elif (g, f, 'mechanistic') in track or (g, f, 'role') in track or (g, f, 'direction') in track:
        recs = get_track_pair(g, f)
        for lab, col in [('mechanistic', 'final_mechanistic'), ('role', 'final_role'), ('direction', 'final_direction')]:
            r_ = recs.get(lab)
            if r_ and r_['final'] not in (None, ''):
                add[col] = str(r_['final'])
            else:
                # dimension was AGREED (no Track row) -> full-text agreement value
                add[col] = x.get('cot_' + lab, '') or x.get('consensus_' + lab, '')
        add['final_verdict'] = '|'.join(add[c] for c in ['final_mechanistic', 'final_role', 'final_direction'])
        add['gpt4o_verdict'] = join3(recs, 'gpt4o')
        add['curator_1_verdict'] = join3(recs, 'higor')
        add['curator_2_verdict'] = join3(recs, 'victor')
        # evidence: prefer mechanistic verbatim, else role, else direction
        # evidence: first non-empty Track row (mechanistic -> role -> direction)
        ev = ''; src = ''
        for _lab in ['mechanistic', 'role', 'direction']:
            _r = recs.get(_lab)
            if _r and _r.get('evidence'):
                ev = _r['evidence']; src = _r.get('source', ''); break
        add['deciding_evidence'] = ev[:400]
        add['evidence_source'] = src
        add['decision_status'] = 'UNIFORM_PIPELINE'
        add['abstract_check'] = ''
    else:
        # agreement pool: full-text agreement stands
        add['final_mechanistic'] = x['cot_mechanistic']
        add['final_role'] = x['cot_role']
        add['final_direction'] = x['cot_direction']
        add['final_verdict'] = '|'.join([x['cot_mechanistic'], x['cot_role'], x['cot_direction']])
        add['decision_status'] = 'AGREED_LABEL_ABSTRACT'
        key = f'{g}|{f}'
        chk = ag_final.get(key, {})
        # abstract check (mechanistic axis)
        a_m = chk.get('mech', 'UNCLEAR')
        if a_m == 'UNCLEAR':
            add['abstract_check'] = 'INSUFFICIENT'
        elif a_m == x['cot_mechanistic']:
            add['abstract_check'] = 'CONFIRMED'
        else:
            add['abstract_check'] = 'DIFFERENT_VIEW'
        # evidence source
        src = chk.get('source', '')
        if src in ('fetched_verbatim',):
            add['evidence_source'] = 'fetched_verbatim'
            add['deciding_evidence'] = ag_prog.get(key, {}).get('verbatim', '')[:400]
        elif src in ('elicit_verbatim',):
            add['evidence_source'] = 'elicit_verbatim'
            add['deciding_evidence'] = (x.get('elicit_verbatim_sentence') or '')[:400]
        elif src in ('deep_best_sentence',):
            add['evidence_source'] = 'deep_best_sentence'
            add['deciding_evidence'] = (x.get('deep_best_sentence') or '')[:400]
        else:
            add['evidence_source'] = 'abstract_no_link'
            add['deciding_evidence'] = (x.get('consensus_takeaway') or '')[:400]
    out_rows.append({**x, **add})

# write CSV (append 11 columns; original columns byte-identical values)
fields = orig_fields + ADD
with open(OUT, 'w', newline='', encoding='utf-8-sig') as fp:
    w = csv.DictWriter(fp, fieldnames=fields)
    w.writeheader()
    w.writerows(out_rows)
print(f'wrote {len(out_rows)} rows x {len(fields)} columns to {OUT}')
# summary
from collections import Counter
c = Counter(x['decision_status'] for x in out_rows)
print('decision_status:', dict(c))
c2 = Counter(x['abstract_check'] for x in out_rows if x['abstract_check'])
print('abstract_check:', dict(c2))
c3 = Counter(x['evidence_source'] for x in out_rows if x['evidence_source'])
print('evidence_source:', dict(c3))
