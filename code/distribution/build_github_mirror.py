# -*- coding: utf-8 -*-
"""build_github_mirror.py — copy the V027 truth into the GitHub mirror
(D:/RCDome_github): app code, manuscript deliverables, and the matrix.

The mirror is PRIVATE until submission. This script only adds/updates files;
it never deletes, so legacy files remain for git history. It regenerates
mirror_manifest.txt (sha256 provenance) but does NOT touch .gitignore,
LICENSE, or .env.example (those are already correct in the mirror).
"""
import os, glob, hashlib, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript'
MIRROR = 'D:/RCDome_github'
DRY_RUN = False

# (source glob relative to BASE, target dir relative to MIRROR)
MAPPING = [
    # ── manuscript deliverables → mirror root ──────────────────────────
    ('manuscript_V027/RCDome_manuscript_governance_V027.docx', ''),
    ('manuscript_V027/RCDome_manuscript_V027_supplementary_information.docx', ''),
    ('manuscript_V027/RCDome_manuscript_V027_supplementary_tables.xlsx', ''),
    ('manuscript_V027/RCDome_53_canonical_entities.docx', ''),

    # ── app code → app/ ────────────────────────────────────────────────
    ('RCDome_distribution/global.R', 'app'),
    ('RCDome_distribution/server.R', 'app'),
    ('RCDome_distribution/ui.R', 'app'),
    ('RCDome_distribution/run.R', 'app'),
    ('RCDome_distribution/explore.html', 'app'),
    ('RCDome_distribution/detail_page_wireframe.html', 'app'),
    ('RCDome_distribution/CHANGELOG_V027.md', 'app'),
    ('RCDome_distribution/README_DISTRIBUTION.md', 'app'),
    ('RCDome_distribution/generate_detail_page.py', 'app'),
    ('RCDome_distribution/generate_dome_3d.py', 'app'),
    ('RCDome_distribution/extract_pdfs_to_overall.py', 'app'),
    ('RCDome_distribution/modules/*.R', 'app/modules'),
    ('RCDome_distribution/R/*.R', 'app/R'),
    ('RCDome_distribution/www/*.html', 'app/www'),
    ('RCDome_distribution/www/*.js', 'app/www'),
    ('RCDome_distribution/www/*.svg', 'app/www'),
    ('RCDome_distribution/board/*', 'app/board'),

    # ── app data (key files; RCD modulo static assets are already mirrored) ──
    ('RCDome_distribution/data/unified_gene_rcd_matrix_V027.csv', 'app/data'),
    ('RCDome_distribution/data/unified_gene_rcd_matrix_V027.rds', 'app/data'),
    ('RCDome_distribution/data/RCDome_Decoder_53.csv', 'app/data'),
    ('RCDome_distribution/data/hgnc_complete_set.txt', 'app/data'),
    ('RCDome_distribution/data/gene_info_lookup.json', 'app/data'),
    ('RCDome_distribution/data/pmid_title_lookup.json', 'app/data'),
    ('RCDome_distribution/data/adjudication/disc_df.rds', 'app/data/adjudication'),
    ('RCDome_distribution/data/adjudication/disc_html.rds', 'app/data/adjudication'),

    # ── matrix also under mirror data/ (root) ──────────────────────────
    ('output databases/Phase 2C output/unified_gene_rcd_matrix_V027.csv', 'data'),
    ('output databases/Phase 2C output/unified_gene_rcd_matrix_V027.rds', 'data'),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


# resolve globs
planned = []
for glob_src, mirror_dir in MAPPING:
    for m in sorted(glob.glob(os.path.join(BASE, glob_src))):
        fname = os.path.basename(m)
        planned.append((m, os.path.join(MIRROR, mirror_dir, fname)))

# dedupe by source
seen = set()
unique = []
for s, d in planned:
    if s not in seen:
        seen.add(s)
        unique.append((s, d))
planned = unique

# copy
manifest_lines = ['# RCDome GitHub mirror manifest — V027 (truth snapshot)',
                  '# sha256  |  size  |  mirror path  <-  source path', '']
copied = []
for src, dst in planned:
    if not DRY_RUN:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    copied.append((src, dst, os.path.getsize(src), sha256(src)))

for src, dst, size, h in copied:
    manifest_lines.append(f'{h}  {size:>10}  {os.path.relpath(dst, MIRROR)}  <-  {os.path.relpath(src, BASE)}')

if not DRY_RUN:
    open(os.path.join(MIRROR, 'mirror_manifest.txt'), 'w', encoding='utf-8').write('\n'.join(manifest_lines))

total = sum(c[2] for c in copied)
print(f'{"DRY-RUN" if DRY_RUN else "COPIED"} {len(copied)} files -> {MIRROR} ({total/1024/1024:.1f} MB)')
print('regenerated mirror_manifest.txt (sha256 provenance)')
