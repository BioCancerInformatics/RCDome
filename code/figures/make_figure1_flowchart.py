# -*- coding: utf-8 -*-
"""Figure 1 pipeline flowchart — PROVENANCE NOTE (honesty contract).

CANONICAL generator: generate_rcdome_flowchart.R (grViz/DiagrammeR), in
  D:/Pré-artigo 5-optosis model/Machine learning CancerRCDShiny_prediction/Enrique version/
This Python/matplotlib script is a RECREATION used only because R + DiagrammeR
are not installed on the local machine. It mirrors the R script's nodes,
colors and layout, with the V026 correction (71 columns).
When R is available, regenerate with the canonical R script.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os, sys

OUT = r'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures/Figure_1_pipeline'

fig, ax = plt.subplots(figsize=(8.27, 11.69))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

def wrap(s, w=52):
    import textwrap
    return '\n'.join(textwrap.wrap(s, w))

def box(cx, cy, w, h, text, fc, fc_text='#1F3143', fs=8.5, bold=False):
    ax.add_patch(FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                                boxstyle='round,pad=0.4,rounding_size=1.2',
                                linewidth=1.2, edgecolor='#8DB0C9', facecolor=fc))
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fs,
            color=fc_text, fontweight='bold' if bold else 'normal',
            fontfamily='DejaVu Sans', linespacing=1.5)

def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                                 mutation_scale=16, linewidth=1.6,
                                 color='#7998AF', shrinkA=2, shrinkB=2))

# node layout (top -> bottom)
box(50, 95, 66, 12, wrap('20 source databases (FerrDB v3, RCDdb, iPCD, LncRCD, iLIR, HADb, HAMdb, ATD, AMT-DB, ncFO, KEGG, Reactome, GO, MSigDB, WikiPathways, NCBI Gene, Rodrigues 2025, XDeathDB, Elicit Phase 3, Elicit Alert)'), '#AED6F1')
box(50, 80, 66, 12, wrap('Four compilation channels: A: PubMed Boolean (recall), B: curated databases (precision), C: AI-assisted screening, D: manual curation (arbiter)'), '#48C9B0')
box(50, 65, 66, 11, wrap('Consolidation: 53 canonicalized RCD-related entities (62 name strings), 22,473 rows, 9,265 genes'), '#F9E79F')
box(50, 50, 30, 8, 'INDEPENDENT\nVALIDATION', '#EBDEF0', fc_text='#D32F2F', fs=9, bold=True)
box(18, 35, 27, 14, wrap('DeepSeek (Phases 2A/D, 2B, 2C, 2D/2E, 2F): two-call validation, deep RAG, recovery, CoT full-matrix (cot_role, cot_direction, cot_mechanistic, cot_evidence)'), '#ABEBC6', fs=7)
box(50, 35, 27, 14, wrap('Elicit (Phase 3): AI-assisted extraction, role + direction'), '#F1948A', fs=8)
box(82, 35, 27, 14, wrap('Consensus (Phase 2G): evidence-channel classification, neutral query'), '#EB984E', fs=8)
box(50, 18, 66, 10, 'Consolidated matrix: 22,473 rows x 71 columns', '#FCBB18', fs=10, bold=True)
box(50, 4, 66, 7, wrap('RCDome web application (dome, Explore RCDome, Operational Definitions, Compare Definitions, Gene Catalog, RCD entities, RCDome Board, Network)'), '#D32F2F', fc_text='white', fs=8)

# arrows
arrow(50, 89, 50, 86)
arrow(50, 74, 50, 70.5)
arrow(50, 59.5, 50, 54)
arrow(50, 46, 50, 42)
arrow(50, 42, 18, 42)
arrow(50, 42, 82, 42)
arrow(18, 28, 50, 23)
arrow(50, 28, 50, 23)
arrow(82, 28, 50, 23)
arrow(50, 13, 50, 7.5)

plt.tight_layout(pad=0.5)
fig.savefig(OUT + '.pdf', facecolor='white', bbox_inches='tight')
fig.savefig(OUT + '.png', dpi=600, facecolor='white', bbox_inches='tight')
fig.savefig(OUT + '.tiff', dpi=600, facecolor='white', bbox_inches='tight',
            pil_kwargs={'compression': 'tiff_lzw'})
plt.close(fig)

# unify timestamps (Created + Modified + Accessed)
_ts = os.stat(OUT + '.pdf').st_mtime
for _e in ['.pdf', '.png', '.tiff']:
    os.utime(OUT + _e, (_ts, _ts))
if sys.platform == 'win32':
    try:
        import ctypes
        _EPOCH_1601 = 116444736000000000
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
print('Figure 1 regenerated (V026, 71 columns)')
