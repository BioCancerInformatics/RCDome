# -*- coding: utf-8 -*-
import os, zipfile, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Shiny app/RCDome_Atlas/APP'
MATRIX = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/output databases/Phase 2C output/unified_gene_rcd_matrix_V025.rds'

# ---- CHANGELOG ----
changelog = '''# RCDome — CHANGELOG V025

## V024 → V025
- **Orphan row removed**: EPAS1 / Ammonia-induced cell death (retracted Elicit record, empty provenance). Matrix 22,474 → 22,473 rows; 21,569 → 21,568 unique pairs; corroboration rows unchanged (905).
- **Mini-run pairs classified (Phase 2A/D)**: NLRX1 → CONTEXT_GAP (PMID 41739553); PPIF → MECHANISTIC (PMID 15800627).
- **Numbers updated everywhere**: 22,473 · 21,568 · 11,605 · 11,743 · 8,863 · 3,063 · 6,170.
- **Figures regenerated**: Figure 1 (22,473), Figure 3 (21,568 pairs, 11,605 uncertain), Figure 4 (from V025).
- **Legends updated**: main FIGURE LEGENDS + Supplementary Information file.
- **Supplementary consolidated**: Notes S1–S3 + Supplementary Figures S1–S2 (front page in Calibri).
- **App updated**: loads V025 matrix; dome, Gene Catalog, and detail pages regenerated.
- **Traceability**: "V024 → V025 Amendment Log" added to the contract.

## Run
```
setwd(".../RCDome_Atlas/APP")
shiny::runApp(appDir = ".", port = 8890, launch.browser = TRUE)
```
'''

open(BASE + '/CHANGELOG_V025.md', 'w', encoding='utf-8').write(changelog)

# ---- ZIP ----
files = [
    'ui.R', 'server.R', 'global.R', 'run.R', 'build_signatures_cache.R',
    'data/pmid_title_lookup.rds', 'data/pmid_title_lookup.json',
    'data/about/see also/sigpolytope.svg',
    'www/landing_page.html', 'www/dome_prototype.html', 'www/detail_page_wireframe.html',
    'www/explore.html', 'www/module_placeholder.html', 'www/SigPolytope.html',
    'www/contact_intercept.js',
    'generate_dome.py', 'generate_detail_page.py', 'generate_explore.py',
    'CHANGELOG_V025.md',
]
files += ['R/' + f for f in os.listdir(BASE + '/R') if f.endswith('.R')]
files += ['modules/' + f for f in os.listdir(BASE + '/modules') if f.endswith('.R')]

out = BASE + '/RCDome_V025_update.zip'
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in files:
        p = os.path.join(BASE, f)
        if os.path.exists(p):
            z.write(p, f)
    z.write(MATRIX, 'data/unified_gene_rcd_matrix_V025.rds')

print('created RCDome_V025_update.zip with', len(files)+1, 'entries')
print('size:', round(os.path.getsize(out)/1024/1024, 2), 'MB')
