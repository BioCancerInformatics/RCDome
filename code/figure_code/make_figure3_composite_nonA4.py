# -*- coding: utf-8 -*-
# Figure 3 — death core composite (2x2) — regenerated with V026 numbers.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import math

NAVY='#0b1020'; GOLD='#FFD700'; ORANGE='#FF9800'; BLUE='#00B0FF'; GREEN='#00E676'; PURPLE='#E040FB'; ORANGE5='#FF6D00'; GREY='#c8c4bf'; TEAL='#14b8a6'

# ── Read the truth matrix (unique pairs) so Figure 3 always matches the frozen data ──
import csv as _csv
_UNIQ = set(); _ROLE = {'MARKER':0,'EXECUTOR':0,'REGULATOR':0,'UNCERTAIN':0}; _DIR = {'PROMOTES':0,'PROTECTS':0,'UNCLEAR':0}
_MAT = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_distribution/data/unified_gene_rcd_matrix_V027.csv'
with open(_MAT, encoding='utf-8-sig', newline='') as _f:
    for _r in _csv.DictReader(_f):
        _k = (_r['gene_symbol'], _r['rcd_form_canonical'])
        if _k in _UNIQ: continue
        _UNIQ.add(_k)
        _r_role = _r.get('final_role','')
        _r_dir = _r.get('final_direction','')
        if _r_role in _ROLE: _ROLE[_r_role] += 1
        if _r_dir in _DIR: _DIR[_r_dir] += 1
_ROLE_VALS = [_ROLE['MARKER'], _ROLE['EXECUTOR'], _ROLE['REGULATOR'], _ROLE['UNCERTAIN']]
_DIR_VALS = [_DIR['PROTECTS'], _DIR['PROMOTES']]

fig, axes = plt.subplots(2, 2, figsize=(10.5, 8), dpi=600)
fig.patch.set_facecolor('white')

# (a) Role distribution
ax = axes[0,0]
roles=['Marker','Executor','Regulator','Uncertain']; vals=_ROLE_VALS
bars = ax.barh(roles, vals, color=['#e7e5e4', ORANGE, BLUE, GREY])
for b,v in zip(bars, vals):
    ax.text(b.get_width()+250, b.get_y()+b.get_height()/2, f'{v:,}', va='center', fontsize=9, color=NAVY, fontweight='bold')
ax.set_xlim(0,13500); ax.set_title('Role distribution (21,568 pairs)', fontsize=11, fontweight='bold', color=NAVY)
ax.spines[['top','right']].set_visible(False); ax.tick_params(colors=NAVY, labelsize=8)

# (b) Mechanistic by level
ax = axes[0,1]
levels=['L1','L2','L3','L4','L5']; pcts=[37.3,14.1,14.2,6.3,10.9]
lcolors=[GOLD,BLUE,GREEN,PURPLE,ORANGE5]
bars = ax.bar(levels, pcts, color=lcolors, width=0.62)
for b,v in zip(bars,pcts):
    ax.text(b.get_x()+b.get_width()/2, v+1.2, f'{v}%', ha='center', fontsize=9, color=NAVY, fontweight='bold')
ax.set_ylim(0,70); ax.set_title('Mechanistically involved, by level (%)', fontsize=11, fontweight='bold', color=NAVY)
ax.spines[['top','right']].set_visible(False); ax.tick_params(colors=NAVY, labelsize=8)

# (c) Direction
ax = axes[1,0]
dirs=['Protects','Promotes']; dvals=_DIR_VALS
bars = ax.barh(dirs, dvals, color=[TEAL, ORANGE])
for b,v in zip(bars,dvals):
    ax.text(b.get_width()+110, b.get_y()+b.get_height()/2, f'{v:,}', va='center', fontsize=9, color=NAVY, fontweight='bold')
ax.set_xlim(0,6800); ax.set_title('Direction of regulation', fontsize=11, fontweight='bold', color=NAVY)
ax.spines[['top','right']].set_visible(False); ax.tick_params(colors=NAVY, labelsize=8)

# (d) Bullseye — AREA-proportional rings
ax = axes[1,1]
TOTAL = 21568
R3 = 1.0
R2 = math.sqrt((4604+225)/TOTAL)
R1 = math.sqrt(225/TOTAL)
# outer grey ring (uncertain)
ax.add_patch(Wedge((0,0), R3, 0, 360, width=R3-R2, facecolor=GREY, alpha=0.9))
# middle blue ring (regulator)
ax.add_patch(Wedge((0,0), R2, 0, 360, width=R2-R1, facecolor=BLUE, alpha=0.9))
# inner orange core (executor)
ax.add_patch(plt.Circle((0,0), R1, color=ORANGE, alpha=0.95))
# labels
ax.text(0, (R2+R3)/2, 'UNCERTAIN\n16,641', ha='center', va='center', fontsize=8, color=NAVY, fontweight='bold')
ax.text(0, (R1+R2)/2, 'REGULATOR\n4,604', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
ax.text(0, 0, '225', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
ax.text(0, -0.24, 'EXECUTOR', ha='center', va='center', fontsize=8, color=ORANGE, fontweight='bold')
ax.set_xlim(-1.15,1.15); ax.set_ylim(-1.15,1.15); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('The core is small; the network is vast', fontsize=11, fontweight='bold', color=NAVY, pad=6)

plt.tight_layout()

# Panel labels in FIGURE coordinates so (A)/(C) and (B)/(D) align vertically
_posA = axes[0,0].get_position(); _posB = axes[0,1].get_position(); _posC = axes[1,0].get_position()
_labels = [('A', _posA.x0, _posA.y1), ('B', _posB.x0, _posB.y1),
           ('C', _posC.x0, _posC.y1), ('D', _posB.x0, _posC.y1)]
for _l, _x, _y in _labels:
    fig.text(_x - 0.015, _y + 0.008, f'({_l})', fontsize=15, fontweight='bold',
             color=NAVY, va='bottom', ha='left', transform=fig.transFigure)

out = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures/Figure_3'
plt.savefig(out + '.pdf', facecolor='white', bbox_inches='tight')
plt.savefig(out + '.png', dpi=600, facecolor='white', bbox_inches='tight')
plt.savefig(out + '.tiff', dpi=600, facecolor='white', bbox_inches='tight', pil_kwargs={'compression': 'tiff_lzw'})
plt.close()

import os, sys
_ts = os.stat(out + '.pdf').st_mtime
for _e in ['.pdf', '.png', '.tiff']:
    os.utime(out + _e, (_ts, _ts))
if sys.platform == 'win32':
    try:
        import ctypes
        _EPOCH_1601 = 116444736000000000
        _ft = int(_ts * 10_000_000) + _EPOCH_1601
        _k32 = ctypes.windll.kernel32
        for _e in ['.pdf', '.png', '.tiff']:
            _h = _k32.CreateFileW(out + _e, 0x0100, 0, None, 3, 0, None)
            if _h != -1:
                _cft = ctypes.c_ulonglong(_ft)
                _k32.SetFileTime(_h, ctypes.byref(_cft), ctypes.byref(_cft), ctypes.byref(_cft))
                _k32.CloseHandle(_h)
    except Exception:
        pass
print('Figure 3 regenerated (V027 numbers)')
