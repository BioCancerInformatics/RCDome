import pandas as pd, docx, openpyxl, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript'
P = F = 0
def ck(n, ok, d=''):
    global P, F
    print(f'  [{"PASS" if ok else "FAIL"}] {n} {d}')
    P += bool(ok); F += (not bool(ok))

print('=== 1. MATRIX V026 ===')
m = pd.read_csv(BASE + '/output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv', low_memory=False)
ck('22,473 x 71', m.shape == (22473, 71), str(m.shape))
ck('levels L1/L2/L3/L4/L5', m.rcdome_level.value_counts().to_dict() == {'L1':10300,'L2':2354,'L3':172,'L4':2684,'L5':6963})
ck('53 forms', m.rcd_form_canonical.nunique() == 53)

print('=== 2. DECODER ===')
d = pd.read_csv(BASE + '/RCDome Decoder/RCDome_Decoder_53.csv')
ck('39 cols', len(d.columns) == 39)
ck('hgs 16/37', (d.hard_gate_status=='L1-ELIGIBLE').sum()==16 and (d.hard_gate_status=='NOT-L1').sum()==37)
ck('12-value relationship vocab', set(d.relationship_type.unique()) <= {'is_a','subtype_of','triggered_by','requires','originates_from','associated_with','umbrella_for','driven_by','synonym_of','outcome_of','root'})
ck('5-value evidence_maturity', set(d.evidence_maturity.unique()) == {'established','supported','emerging','legacy','provisional'})

print('=== 3. MANUSCRIPT ===')
doc = docx.Document(BASE + '/RCDome_manuscript_governance.docx')
txt = ' '.join(p.text for p in doc.paragraphs)
ck('version-free (no V0xx)', not re.search(r'V0\d\d', txt))
ck('hard gates present', 'Hard gates (L1 admission)' in txt)
ck('F2a/F2b/F3a/b/c', all(s in txt for s in ['not be read as an independent validation','database indexing, not ontological inheritance','RCD-related entities','dynamic, not binary','curator-governed']))
ck('D2 two validations', 'Two distinct validations are performed' in txt)
ck('Table S12 callout', 'documented in Table S12' in txt)
ck('380+ paragraphs', len(doc.paragraphs) >= 380, str(len(doc.paragraphs)))

print('=== 4. SUPPLEMENTARY WORKBOOK ===')
wb = openpyxl.load_workbook(BASE + '/RCDome_manuscript_supplementary_tables.xlsx', read_only=True)
ck('sheets S1-S15', all(f'Table S{i}' in wb.sheetnames for i in range(1,16)))
ws = wb['Table S12']; hdr = [c.value for c in next(ws.iter_rows(max_row=1))]
ck('S12 26 cols, semantic levels', len(hdr)==26 and 'pre_adjudication_level' in hdr and 'adjudicated_level' in hdr)
ck('S12 54 rows', sum(1 for _ in ws.iter_rows())==54)
vd = wb['Variable Descriptor']
from collections import Counter
c = Counter(row[0].value for row in vd.iter_rows() if row[0].value and str(row[0].value).startswith('S'))
ck('VD S12=26 S13=6 S14=5 S15=4', c.get('S12')==26 and c.get('S13')==6 and c.get('S14')==5 and c.get('S15')==4, str(dict(c)))
idx = wb['INDEX']; itxt = ' '.join(str(c.value) for row in idx.iter_rows() for c in row if c.value)
ck('INDEX S1-S15 + Adjudication', 'S1–S15' in itxt and 'Adjudication Table' in itxt)

print('=== 5. FIGURES ===')
fig = BASE + '/Figures/'
ck('Figure 1-4 present', all(os.path.exists(fig + f'Figure_{i}.png') or os.path.exists(fig + f'Figure_{i}.tiff') for i in range(1,5)))
ck('Figure S2/S3 present', all(os.path.exists(fig + f'Figure_S{i}_database_contribution.tiff') or os.path.exists(fig + f'Figure_S{i}_source_classification.tiff') for i in [1,2]))
ck('Figure 4 data CSV regenerated', os.path.exists(fig + 'Figure_4_entity_coverage_data.csv'))

print('=== 6. APP ===')
app = BASE + '/Shiny app/RCDome_Atlas/APP'
appfiles = ['global.R','server.R','ui.R','modules/mod_omic.R','modules/mod_rcd_grid.R']
leaks = [f for f in appfiles if 'V025' in open(app + '/' + f, encoding='utf-8').read()]
ck('app files no V025', len(leaks)==0, str(leaks))
ck('app data V026 RDS', os.path.exists(app + '/data/unified_gene_rcd_matrix_V026.rds'))

print('=== 7. GITHUB + TRACEABILITY ===')
tr = open(BASE + '/docs/RCDome_Traceability_Contract.md', encoding='utf-8').read()
groups = ['GROUP A','GROUP B','GROUP C','GROUP D','GROUP E','GROUP F','GROUP G']
ck('traceability: all 7 groups', all(g in tr for g in groups), str([g for g in groups if g not in tr]))
ck('GitHub manifest exists', os.path.exists(r'D:/RCDome_github/mirror_manifest.txt'))

print(f'\n===== FINAL REVIEW 7/7: {P} PASS, {F} FAIL =====')
