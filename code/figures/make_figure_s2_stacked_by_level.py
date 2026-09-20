# -*- coding: utf-8 -*-
"""Figure S2 (improved): mechanistic associations per source, stacked by
RCD entity ontological level (L1-L5), concordant RCDome palette + legend."""
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

BASE = r'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript'
m = pd.read_csv(BASE + '/output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv',
                low_memory=False)

# build source x level mechanistic counts
rows = []
for _, r in m.iterrows():
    ss = str(r.source_databases)
    if not ss or ss == 'nan':
        continue
    mech = str(r.cot_mechanistic).upper() == 'YES'
    if not mech:
        continue
    lvl = r.rcdome_level
    for s in ss.split(';'):
        s = s.strip()
        if s:
            rows.append((s, lvl))

t = pd.DataFrame(rows, columns=['source', 'level'])
ct = t.groupby(['source', 'level']).size().unstack(fill_value=0)
levels = ['L1', 'L2', 'L3', 'L4', 'L5']
ct = ct.reindex(columns=levels, fill_value=0)

# clean source names
clean = {'Rodrigues2025': 'Rodrigues et al. 2025', 'NCBI_Gene': 'NCBI Gene',
         'Elicit_Phase3': 'Elicit Phase 3', 'Elicit_Alert': 'Elicit Alert'}
ct.index = [clean.get(s, s) for s in ct.index]

# sort ascending by total (bottom -> top)
ct['_total'] = ct.sum(axis=1)
ct = ct.sort_values('_total')
totals = ct.pop('_total')

# concordant RCDome palette + names
palette = {'L1': '#FCBB18', 'L2': '#5DADE2', 'L3': '#58D68D',
           'L4': '#AF7AC5', 'L5': '#F1948A'}
lvl_names = {'L1': 'L1 Modalities (19)', 'L2': 'L2 Subtypes (7)',
             'L3': 'L3 Triggers (2)', 'L4': 'L4 Functional/contextual (13)',
             'L5': 'L5 Generic/umbrella/taxon (12)'}
dark = '#1F2937'

OUT = BASE + '/Figures/Figure_S2_source_classification'

fig, ax = plt.subplots(figsize=(8.27, 11.69))
left = 0
for lv in levels:
    vals = ct[lv].values
    ax.barh(ct.index, vals, left=left, color=palette[lv], edgecolor=dark,
            linewidth=0.5, height=0.72)
    left = left + vals

# total count label on the right
for i, (src, tot) in enumerate(totals.items()):
    ax.text(tot + 40, i, f'{tot:,}', va='center', ha='left',
            fontsize=6.5, color=dark)

ax.set_xlim(0, totals.max() * 1.16)
ax.tick_params(axis='y', labelsize=7, colors=dark)
ax.tick_params(axis='x', labelsize=8, colors=dark)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
ax.spines['left'].set_color(dark)
ax.spines['bottom'].set_color(dark)
ax.set_xlabel('Mechanistic associations (cot_mechanistic = YES)', fontsize=9, color=dark)
ax.set_title('Mechanistic associations per source, stacked by RCD entity ontological level',
             fontsize=10.5, color=dark, fontweight='bold', pad=12)

handles = [plt.Rectangle((0, 0), 1, 1, color=palette[lv]) for lv in levels]
ax.legend(handles, [lvl_names[lv] for lv in levels], loc='lower right',
          fontsize=7, frameon=False, title='Ontological level', title_fontsize=7.5)

plt.tight_layout()

# save PDF + PNG + 600 DPI TIFF
fig.savefig(OUT + '.pdf', format='pdf')
fig.savefig(OUT + '.png', dpi=300)
fig.savefig(OUT + '.tiff', dpi=600, format='tiff', pil_kwargs={'compression': 'tiff_lzw'})
plt.close(fig)

# data CSV
ct.to_csv(OUT + '_data.csv')

# unify ALL output timestamps for provenance (Created + Modified + Accessed)
import os, sys
_ts = os.stat(OUT + '.pdf').st_mtime
for _e in ['.pdf', '.png', '.tiff']:
    os.utime(OUT + _e, (_ts, _ts))
if sys.platform == 'win32':
    try:
        import ctypes
        _EPOCH_1601 = 116444736000000000  # 100ns intervals since 1601
        _ft = int(_ts * 10_000_000) + _EPOCH_1601
        _k32 = ctypes.windll.kernel32
        for _e in ['.pdf', '.png', '.tiff']:
            _h = _k32.CreateFileW(OUT + _e, 0x0100, 0, None, 3, 0, None)
            if _h != -1:
                _cft = ctypes.c_ulonglong(_ft)
                _k32.SetFileTime(_h, ctypes.byref(_cft),
                                  ctypes.byref(_cft), ctypes.byref(_cft))
                _k32.CloseHandle(_h)
    except Exception:
        pass

print('saved Figure_S2_source_classification (stacked by ontological level)')
print(ct)
