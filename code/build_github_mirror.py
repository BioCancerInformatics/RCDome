# -*- coding: utf-8 -*-
"""build_github_mirror.py — copy the V025 TRUTH into a clean GitHub staging folder,
generate .gitignore, .env.example, mirror_manifest.txt (sha256), and LICENSE."""
import os, sys, glob, hashlib, shutil
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript'
MIRROR = 'D:/RCDome_github'
DRY_RUN = False

MAPPING = [
    # docs
    ('RCDome_manuscript_governance_V025.docx', 'docs/manuscript'),
    ('RCDome_manuscript_V025_supplementary_information.docx', 'docs/supplementary'),
    ('RCDome_manuscript_V025_supplementary_tables.xlsx', 'docs/supplementary'),
    ('RCDome_manuscript_V025_matrix_variables.xlsx', 'docs/supplementary'),
    ('docs/RCDome_Traceability_Contract.md', 'docs/traceability'),
    ('Medinas_AI_Governance_Rules_in_Writing_Scientific_Manuscripts.docx', 'docs/governance'),
    # figures
    ('Figures/Figure_1_pipeline.tiff', 'docs/figures'),
    ('Figures/Figure_1_pipeline.png', 'docs/figures'),
    ('Figures/Figure_2_benchmarks.tiff', 'docs/figures'),
    ('Figures/Figure_2_benchmarks.png', 'docs/figures'),
    ('Figures/Figure 3.tiff', 'docs/figures'),
    ('Figures/Figure 3.png', 'docs/figures'),
    ('Figures/Figure_4_entity_coverage.tiff', 'docs/figures'),
    ('Figures/Figure_4_entity_coverage.png', 'docs/figures'),
    ('Figures/Figure_S1_database_contribution.tiff', 'docs/figures'),
    ('Figures/Figure_S1_database_contribution.png', 'docs/figures'),
    ('Figures/Figure_S2_source_classification.tiff', 'docs/figures'),
    ('Figures/Figure_S2_source_classification.png', 'docs/figures'),
    # data
    ('output databases/Phase 2C output/unified_gene_rcd_matrix_V025.csv', 'data'),
    ('Shiny app/RCDome_Atlas/APP/data/pmid_title_lookup.json', 'data'),
    # code — extraction (channels A/B/E only)
    ('extraction code snippets/channel_a_*.py', 'code/extraction'),
    ('extraction code snippets/channel_b_*.py', 'code/extraction'),
    ('extraction code snippets/channel_e_*.py', 'code/extraction'),
    ('extraction code snippets/channel_2e_zero_pmid_recovery.py', 'code/extraction'),
    # code — validation (channels C + DeepSeek + Consensus + phase2ad)
    ('Consensus API/consensus_cot_full.py', 'code/validation'),
    ('extraction code snippets/deepseek_cot_v11_full.py', 'code/validation'),
    ('extraction code snippets/channel_c_evidence_tier.py', 'code/validation'),
    ('extraction code snippets/channel_c_recovery_europe_pmc.py', 'code/validation'),
    ('extraction code snippets/phase2ad_msigdb_1832.py', 'code/validation'),
    ('extraction code snippets/phase2ad_residual.py', 'code/validation'),
    # code — benchmarks
    ('extraction code snippets/cot_benchmark*.py', 'code/benchmarks'),
    ('Consensus API/consensus_benchmark*.py', 'code/benchmarks'),
    # code — merge
    ('extraction code snippets/merge_*.py', 'code/merge'),
    # code — figures
    ('make_figure3_composite.py', 'code/figures'),
    ('make_figure_entity_coverage.R', 'code/figures'),
    ('make_figure_db_contribution.R', 'code/figures'),
    ('make_figure_source_classification.R', 'code/figures'),
    # app (code only)
    ('Shiny app/RCDome_Atlas/APP/ui.R', 'app'),
    ('Shiny app/RCDome_Atlas/APP/server.R', 'app'),
    ('Shiny app/RCDome_Atlas/APP/global.R', 'app'),
    ('Shiny app/RCDome_Atlas/APP/run.R', 'app'),
    ('Shiny app/RCDome_Atlas/APP/build_signatures_cache.R', 'app'),
    ('Shiny app/RCDome_Atlas/APP/generate_*.py', 'app'),
    ('Shiny app/RCDome_Atlas/APP/modules/*.R', 'app/modules'),
    ('Shiny app/RCDome_Atlas/APP/R/*.R', 'app/R'),
    ('Shiny app/RCDome_Atlas/APP/www/*.html', 'app/www'),
    ('Shiny app/RCDome_Atlas/APP/www/*.js', 'app/www'),
    ('Shiny app/RCDome_Atlas/APP/www/*.svg', 'app/www'),
    # changelog
    ('Shiny app/RCDome_Atlas/APP/CHANGELOG_V025.md', 'results/changelogs'),
]

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

# resolve
planned = []
for glob_src, mirror_dir in MAPPING:
    for m in sorted(glob.glob(os.path.join(BASE, glob_src))):
        fname = os.path.basename(m)
        planned.append((m, os.path.join(MIRROR, mirror_dir, fname)))

seen = set(); unique = []
for s, d in planned:
    if s not in seen:
        seen.add(s); unique.append((s, d))
planned = unique

# ---- copy ----
manifest_lines = ['# RCDome GitHub mirror manifest — version V025 (truth snapshot)',
                  '# sha256  |  size  |  mirror path  <-  source path', '']
copied = []
for src, dst in planned:
    if not DRY_RUN:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    copied.append((src, dst, os.path.getsize(src), sha256(src)))

# ---- manifest ----
for src, dst, size, h in copied:
    manifest_lines.append(f'{h}  {size:>10}  {os.path.relpath(dst, MIRROR)}  <-  {os.path.relpath(src, BASE)}')

# ---- .gitignore ----
gitignore = '''# secrets — NEVER commit
.env

# python
__pycache__/
*.pyc

# R
.Rproj.user/
.Rhistory

# runtime artifacts
*.log
*_progress.json
*.tmp
'''
# ---- .env.example ----
env_example = '''# RCDome — environment variables (fill with YOUR keys; never commit real values)
# Copy this file to .env and add your credentials.

NCBI_KEY=
DEEPSEEK_KEY=
ELICIT_API_KEY=
CONSENSUS_API_KEY=

# email notification (optional)
NOTIFY_TO=
NOTIFY_FROM=
NOTIFY_PASS=
'''
# ---- LICENSE (MIT) ----
license_txt = '''MIT License

Copyright (c) 2026 LBTGenomica / BioCancerInformatics

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

if not DRY_RUN:
    open(os.path.join(MIRROR, 'mirror_manifest.txt'), 'w', encoding='utf-8').write('\n'.join(manifest_lines))
    open(os.path.join(MIRROR, '.gitignore'), 'w', encoding='utf-8').write(gitignore)
    open(os.path.join(MIRROR, '.env.example'), 'w', encoding='utf-8').write(env_example)
    open(os.path.join(MIRROR, 'LICENSE'), 'w', encoding='utf-8').write(license_txt)

total = sum(c[2] for c in copied)
print(f'{"DRY-RUN" if DRY_RUN else "COPIED"} {len(copied)} files -> {MIRROR} ({total/1024/1024:.1f} MB)')
print('generated: .gitignore, .env.example, LICENSE, mirror_manifest.txt')
