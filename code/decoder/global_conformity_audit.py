import pandas as pd, re, os, sys, json, hashlib, subprocess
sys.stdout.reconfigure(encoding='utf-8')
B = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
MIR = r"D:/RCDome_github"
P = F = 0
def ck(n, ok, d=''):
    global P, F
    print(f'  [{"PASS" if ok else "FAIL"}] {n} {d}')
    P += bool(ok); F += (not bool(ok))

EXPECT = {'L1':16,'L2':5,'L3':2,'L4':12,'L5':18}
CAT2LVL = {'Executioner':'L1','CORE_RCD_FORM':'L1','CORE_PENDING':'L1','SUBTYPE':'L2','SYNONYM':'L2','Trigger':'L3','Functional':'L4','CONTEXTUAL':'L4','CELL_TYPE':'L4','DIFFERENTIATION':'L4','MORPHOLOGY':'L4','CLEARANCE_PROCESS':'L4','INTEGRATED_PROGRAM':'L4','CELLULAR_PROCESS':'L5','UMBRELLA':'L5','LEGACY':'L5','TAXON':'L5','EMERGING':'L5','COMPOSITE':'L5'}

print('='*72)
print('GLOBAL CONFORMITY AUDIT — matrix, decoder, manuscript, app, GitHub')
print('='*72)

# ---- MATRIX ----
print('\n[1] MATRIX V026')
m = pd.read_csv(B + '/output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv', low_memory=False)
ck('22,473 x 71', m.shape == (22473, 71), str(m.shape))
ck('levels 16/5/2/12/18', m.drop_duplicates('rcd_form_canonical').rcdome_level.value_counts().to_dict() == EXPECT)
ck('decoder_* 4 cols present', all(c in m.columns for c in ['decoder_operational_definition','decoder_key_molecules','decoder_category','decoder_hard_gate_status']))
ck('53 forms', m.rcd_form_canonical.nunique() == 53)

# ---- DECODER ----
print('\n[2] DECODER')
d = pd.read_csv(B + '/RCDome Decoder/RCDome_Decoder_53.csv')
ck('53 x 39', d.shape == (53, 39), str(d.shape))
ck('hgs 16/37', (d.hard_gate_status=='L1-ELIGIBLE').sum()==16 and (d.hard_gate_status=='NOT-L1').sum()==37)
ck('definitions 53/53', d.operational_definition.notna().all() and (d.operational_definition.astype(str).str.strip()!='').all())
d['lv'] = d.category.map(CAT2LVL)
mat_lv = m.drop_duplicates('rcd_form_canonical').set_index('rcd_form_canonical').rcdome_level
merged = d.set_index('rcd_form').lv.to_dict()
mism = [e for e in merged if e in mat_lv.index and merged[e] != mat_lv[e]]
ck('decoder level == matrix level (53/53)', len(mism)==0, f'{len(mism)} mism {mism[:5]}')

# ---- MANUSCRIPT ----
print('\n[3] MANUSCRIPT')
import docx
doc = docx.Document(B + '/RCDome_manuscript_governance_V026.docx')
txt = ' '.join(p.text for p in doc.paragraphs)
ck('version-free (no V0xx)', not re.search(r'V0\d\d', txt))
ck('71 columns (not 67)', '71 columns' in txt and '67 columns' not in txt and '67-column' not in txt)
ck('Database S1 (not Dataset)', 'Database S1' in txt and 'Dataset S1' not in txt)
ck('16 modalities (not 38)', '16 RCD modalities' in txt and '38 modalities' not in txt and '38 RCD modalities' not in txt)
ck('hard gates', 'Hard gates (L1 admission)' in txt or 'hard gates G0-G6' in txt)
ck('D2 two validations', 'Two distinct validations' in txt)
ck('Table S12 callout', 'documented in Table S12' in txt)

# ---- APP ----
print('\n[4] APP')
APP = B + '/Shiny app/RCDome_Atlas/APP'
import pyreadr
r = pyreadr.read_r(APP + '/data/unified_gene_rcd_matrix_V026.rds')
kk = list(r.keys())[0]
ck('app RDS 71 cols', r[kk].shape == (22473, 71), str(r[kk].shape))
# HTML pages
for f in ['www/landing_page.html','www/dome_prototype.html']:
    t = open(APP + '/' + f, encoding='utf-8').read()
    lc = re.search(r'LEVEL_COUNTS = \{([^}]*)\}', t)
    counts = dict(re.findall(r'"(L\d)"\s*:\s*(\d+)', lc.group(1))) if lc else {}
    ck(f'{f} counts 16/5/2/12/18', all(counts.get(k)==str(v) for k,v in EXPECT.items()), str(counts))
    entries = re.findall(r'"name":\s*"([^"]+)"\s*,\s*"level":\s*"(L\d)"', t)
    bad = set((nm,lv) for nm,lv in entries if nm in mat_lv.index and lv != mat_lv[nm])
    ck(f'{f} entity levels == matrix', len(bad)==0, f'{len(bad)}')
# detail page definitions verbatim
t = open(APP + '/www/detail_page_wireframe.html', encoding='utf-8').read()
i = t.find('"entities"'); start = t.find('{', i); depth=0; end=None
for k in range(start, len(t)):
    if t[k]=='{': depth+=1
    elif t[k]=='}':
        depth-=1
        if depth==0: end=k+1; break
ents = json.loads(t[start:end])
dmism = [(nm, ents[nm].get('definition','')[:30]) for nm in d.rcd_form if nm not in ents or str(ents[nm].get('definition','')).strip() != str(d.set_index('rcd_form').loc[nm,'operational_definition']).strip()]
ck('detail page defs verbatim == decoder (53/53)', len(dmism)==0, f'{len(dmism)}')
# R modules
mod = open(APP + '/modules/mod_omic.R', encoding='utf-8').read()
ck('mod_omic 71 + ..cols + no old labels', '71 columns' in mod and 'df[, ..cols]' in mod and 'L4 category' not in mod)
grd = open(APP + '/modules/mod_rcd_grid.R', encoding='utf-8').read()
ck('mod_rcd_grid 53 from decoder', 'base_names <- as.character(decoder_df$rcd_form)' in grd)
glob = open(APP + '/global.R', encoding='utf-8').read()
ck('global.R V026 + decoder', 'unified_gene_rcd_matrix_V026.rds' in glob and 'RCDome_Decoder_53.csv' in glob)
# explore stats
ex = open(APP + '/www/explore.html', encoding='utf-8').read()
ck('explore stats 21,568/469/9,489', all(s in ex for s in ['21,568','469','9,489']))
ck('explore human curation', 'Human ontological curation' in ex)

# ---- GITHUB ----
print('\n[5] GITHUB')
g = pd.read_csv(MIR + '/data/unified_gene_rcd_matrix_V026.csv', nrows=3, low_memory=False)
ck('GitHub matrix 71 + decoder_*', g.shape[1]==71 and all(c in g.columns for c in ['decoder_operational_definition','decoder_key_molecules','decoder_category','decoder_hard_gate_status']))
def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda: f.read(65536), b''): h.update(c)
    return h.hexdigest()
mism=0
for l in open(MIR + '/mirror_manifest.txt', encoding='utf-8').read().splitlines():
    if not l.strip(): continue
    parts = l.split('  ')
    if len(parts)!=2: continue
    h, rel = parts
    p = os.path.join(MIR, rel.replace('/', os.sep))
    if os.path.exists(p) and sha256(p) != h: mism += 1
ck('manifest hashes match', mism==0, f'{mism}')
st = subprocess.run(['git','-C',MIR,'status','--porcelain'], capture_output=True, text=True).stdout.strip()
ck('git clean', st=='', st[:80] if st else '')
keys = ['data/unified_gene_rcd_matrix_V026.csv','data/RCDome_Decoder_53.csv','data/D1_adjudication_table.csv','docs/manuscript/RCDome_manuscript_governance_V026.docx','docs/supplementary/RCDome_manuscript_V026_supplementary_tables.xlsx','app/www/detail_page_wireframe.html']
ck('key files present', all(os.path.exists(MIR+'/'+k) for k in keys), '')

print(f'\n===== GLOBAL CONFORMITY: {P} PASS, {F} FAIL =====')
