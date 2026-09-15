import pandas as pd, re, os, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
APP = BASE + r"/Shiny app/RCDome_Atlas/APP"
P = F = 0
def ck(n, ok, d=''):
    global P, F
    print(f'  [{"PASS" if ok else "FAIL"}] {n} {d}')
    P += bool(ok); F += (not bool(ok))

# Canonical truth
m = pd.read_csv(BASE + '/output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv',
                usecols=['rcd_form_canonical','rcdome_level'], low_memory=False).drop_duplicates('rcd_form_canonical')
truth = dict(zip(m.rcd_form_canonical, m.rcdome_level))
EXPECT = {'L1':16,'L2':5,'L3':2,'L4':12,'L5':18}
LEVEL_LABELS = {'L1':'L1 modalities','L2':'L2 subtypes','L3':'L3 triggers','L4':'L4 Functional/contextual','L5':'L5 Generic/umbrella/legacy/taxon/emerging'}

print('='*70)
print('DEEPEST APP AUDIT — every line, level, label vs V026 truth')
print('='*70)

# ---- 1. HTML pages: LEVEL_COUNTS + LEVEL_NAMES ----
print('\n=== 1. HTML pages: LEVEL_COUNTS + LEVEL_NAMES ===')
html_files = ['www/landing_page.html','www/dome_prototype.html','www/detail_page_wireframe.html','www/explore.html']
for f in html_files:
    p = os.path.join(APP, f)
    if not os.path.exists(p):
        ck(f'{f} exists', False, 'missing'); continue
    t = open(p, encoding='utf-8').read()
    # LEVEL_COUNTS
    lc = re.search(r'LEVEL_COUNTS = \{([^}]*)\}', t)
    if lc:
        counts = dict(re.findall(r'"(L\d)"\s*:\s*(\d+)', lc.group(1)))
        ok = all(counts.get(k)==str(v) for k,v in EXPECT.items())
        ck(f'{f} LEVEL_COUNTS = {counts}', ok)
    # LEVEL_NAMES
    ln = re.search(r'LEVEL_NAMES = \{([^}]*)\}', t)
    if ln:
        bad = []
        body = ln.group(1)
        if 'L4 categories' in body or 'L5 concepts' in body or 'L4 category' in body or 'L5 concept' in body:
            bad.append('OLD L4/L5 label')
        if 'functional/conceptual' in body or 'generic/composite' in body:
            bad.append('OLD functional/conceptual or generic/composite')
        ck(f'{f} LEVEL_NAMES labels', not bad, str(bad))

# ---- 2. HTML pages: entity levels in DATA ----
print('\n=== 2. HTML pages: entity levels in DATA vs matrix ===')
for f in ['www/landing_page.html','www/dome_prototype.html','www/detail_page_wireframe.html']:
    p = os.path.join(APP, f)
    t = open(p, encoding='utf-8').read()
    # entity entries {name, level}
    entries = re.findall(r'"name":\s*"([^"]+)"\s*,\s*"level":\s*"(L\d)"', t)
    seen = {}
    mism = []
    for nm, lv in entries:
        if nm in truth and truth[nm] != lv:
            mism.append((nm, lv, truth[nm]))
        seen[nm] = lv
    # only check unique entity names (not gene-association repeats)
    uniq_mism = list(set(mism))
    n_uniq = len(set(nm for nm, lv in entries if nm in truth))
    ck(f'{f}: {n_uniq}/53 entities, level mismatches', len(uniq_mism)==0,
       f'{len(uniq_mism)} mism {uniq_mism[:8]}' if uniq_mism else f'{n_uniq} entities checked')

# ---- 3. explore.html stats ----
print('\n=== 3. explore.html stats ===')
t = open(os.path.join(APP, 'www/explore.html'), encoding='utf-8').read()
for lbl, pat in [('21,568 pairs','21,568'), ('9,265 genes','9,265'), ('469 executors','469'), ('9,489 regulators','9,489'), ('10,141 PMIDs','10,141')]:
    ck(f'explore: {lbl}', pat in t)

# ---- 4. R modules: level_class + entity source ----
print('\n=== 4. R modules functional checks ===')
t = open(os.path.join(APP, 'modules/mod_omic.R'), encoding='utf-8').read()
ck('mod_omic: level_class L1..L5', all(s in t for s in ['L1','L2','L3','L4','L5']))
ck('mod_omic: data.table ..cols fixed', 'df[, ..cols]' in t and 'drop = FALSE]' not in t)
ck('mod_omic: no old L4 category/L5 concept', 'L4 category' not in t and 'L5 concept' not in t)
t2 = open(os.path.join(APP, 'modules/mod_rcd_grid.R'), encoding='utf-8').read()
ck('mod_rcd_grid: 53 entities from decoder', 'decoder_df' in t2 and 'base_names <- as.character(decoder_df$rcd_form)' in t2)
t3 = open(os.path.join(APP, 'global.R'), encoding='utf-8').read()
ck('global.R: loads V026 matrix', 'unified_gene_rcd_matrix_V026.rds' in t3)
ck('global.R: loads decoder', 'RCDome_Decoder_53.csv' in t3)

# ---- 5. generate scripts ----
print('\n=== 5. generate scripts ===')
for f in ['Shiny app/generate_dome.py','Shiny app/generate_detail_page.py']:
    p = os.path.join(BASE, f)
    if os.path.exists(p):
        t = open(p, encoding='utf-8').read()
        ck(f'{f}: reads V026', 'unified_gene_rcd_matrix_V026.csv' in t)
        ck(f'{f}: new labels', 'L4 Functional/contextual' in t and 'L5 Generic/umbrella' in t)

# ---- 6. parent HTML + wireframe ----
print('\n=== 6. parent HTML + wireframe ===')
for f in ['Shiny app/landing_page.html','Shiny app/dome_prototype.html','Shiny app/detail_page_wireframe.html','Shiny app/landing_page_wireframe.html']:
    p = os.path.join(BASE, f)
    if os.path.exists(p):
        t = open(p, encoding='utf-8').read()
        lc = re.search(r'LEVEL_COUNTS = \{([^}]*)\}', t)
        old_counts = re.search(r'L1 modalities \(38\)|L4 categories|L5 concepts|\(4\)|\(3\)', t)
        ck(f'{f}: no old counts/labels', not old_counts, str(old_counts.group(0)) if old_counts else '')

print(f'\n===== DEEPEST APP AUDIT: {P} PASS, {F} FAIL =====')
