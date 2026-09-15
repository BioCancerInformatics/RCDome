import pandas as pd, re, sys
sys.stdout.reconfigure(encoding='utf-8')
B = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
P = F = 0
def ck(n, ok, d=''):
    global P, F
    print(f'  [{"PASS" if ok else "FAIL"}] {n} {d}')
    P += bool(ok); F += (not bool(ok))

m = pd.read_csv(B + '/output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv', low_memory=False)
d = pd.read_csv(B + '/RCDome Decoder/RCDome_Decoder_53.csv')
pairs = m.drop_duplicates(['gene_symbol','rcd_form_canonical'])

print('='*70)
print('MANUSCRIPT CONFORMITY vs MATRIX V026 + DECODER')
print('='*70)

print('\n[1] CORE DIMENSIONS')
ck('22,473 rows', len(m)==22473, str(len(m)))
ck('21,568 pairs', len(pairs)==21568, str(len(pairs)))
ck('9,265 genes', m.gene_symbol.nunique()==9265, str(m.gene_symbol.nunique()))
ck('53 entities', m.rcd_form_canonical.nunique()==53)
ck('71 columns', m.shape[1]==71, str(m.shape[1]))

print('\n[2] LEVEL COUNTS (16/5/2/12/18)')
lc = m.drop_duplicates('rcd_form_canonical').rcdome_level.value_counts().to_dict()
ck('L1=16 L2=5 L3=2 L4=12 L5=18', lc=={'L1':16,'L2':5,'L3':2,'L4':12,'L5':18}, str(lc))

print('\n[3] EXECUTORS / REGULATORS')
execs = pairs[(pairs.cot_role=='EXECUTOR') & (pairs.cot_mechanistic=='YES')]
regs = pairs[(pairs.cot_role=='REGULATOR') & (pairs.cot_mechanistic=='YES')]
yes = pairs[pairs.cot_mechanistic=='YES']
ck('469 executors', len(execs)==469, str(len(execs)))
ck('9,489 regulators', len(regs)==9489, str(len(regs)))
ck('10,016 mechan YES (46.4%)', len(yes)==10016, str(len(yes)))
ck('11,552 mechan NO (53.6%)', (pairs.cot_mechanistic=='NO').sum()==11552)

print('\n[4] MECHANISTIC CLASS (7 classes)')
mc = m.mechanistic_class.value_counts().to_dict()
exp_mc = {'INSUFFICIENT_DATA':8863,'CONTEXT_GAP':6170,'MECHANISTIC':3063,'CO_OCCURRENCE':2416,'LITERATURE_GAP':1519,'DATABASE_ONLY':442}
ck('mechanistic_class counts', mc==exp_mc, str(mc))
ck('3,063 MECHANISTIC (13.6%)', mc.get('MECHANISTIC')==3063)
ck('2,416 CO_OCCURRENCE (10.8%)', mc.get('CO_OCCURRENCE')==2416)
ck('8,863 INSUFFICIENT (39.4%)', mc.get('INSUFFICIENT_DATA')==8863)
ck('1,519 LITERATURE_GAP (6.8%)', mc.get('LITERATURE_GAP')==1519)
ck('442 DATABASE_ONLY (2.0%)', mc.get('DATABASE_ONLY')==442)

print('\n[5] LEVEL MECHANISTIC FRACTIONS (L1 64.7% / L5 31.4%)')
for lv, exp in [('L1', 64.7), ('L5', 31.4)]:
    sub = pairs[pairs.rcdome_level==lv]
    fr = (sub.cot_mechanistic=='YES').sum()/len(sub)*100
    ck(f'{lv} = {exp}%', abs(fr-exp)<0.1, f'{fr:.1f}%')

print('\n[6] TOP ENTITY GENE COUNTS')
top = m.groupby('rcd_form_canonical').gene_symbol.nunique().sort_values(ascending=False)
for e, exp in [('Apoptosis', 5897), ('Autophagy', 4634), ('Ferroptosis', 1724), ('Programmed cell death', 1710), ('Autosis', 1105), ('Necrosis', 1092), ('Anoikis', 488)]:
    got = top.get(e, 0)
    ck(f'{e} = {exp}', got==exp, f'{got}')

print('\n[7] DECODER CENSUS (20 NCCD + 12 Rodrigues + 20 drafted + 1 composite)')
ds = d.definition_status.value_counts().to_dict()
ods = d.operational_definition_source.value_counts().to_dict()
ck('20 NCCD-verbatim', ods.get('NCCD_2018_VERBATIM')==20, str(ods.get('NCCD_2018_VERBATIM')))
ck('12 Rodrigues-verbatim', ods.get('RODRIGUES_S1A')==12, str(ods.get('RODRIGUES_S1A')))
ck('20 drafted (FOUNDING_DRAFT + PRE_PUBMED)', ods.get('FOUNDING_DRAFT',0)+ods.get('PRE_PUBMED',0)==20, str(ods.get('FOUNDING_DRAFT',0)+ods.get('PRE_PUBMED',0)))
ck('1 COMPOSITE', ds.get('COMPOSITE')==1)

print('\n[8] HARD GATES (16 L1-ELIGIBLE / 37 NOT-L1)')
ck('16 L1-ELIGIBLE', (d.hard_gate_status=='L1-ELIGIBLE').sum()==16)
ck('37 NOT-L1', (d.hard_gate_status=='NOT-L1').sum()==37)

print(f'\n===== MANUSCRIPT CONFORMITY: {P} PASS, {F} FAIL =====')
