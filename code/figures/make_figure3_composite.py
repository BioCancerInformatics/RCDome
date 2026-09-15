# -*- coding: utf-8 -*-
# Figure 3 — death core composite (2x2) — regenerated with V026 numbers.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import math

NAVY='#0b1020'; GOLD='#FFD700'; ORANGE='#FF9800'; BLUE='#00B0FF'; GREEN='#00E676'; PURPLE='#E040FB'; ORANGE5='#FF6D00'; GREY='#c8c4bf'; TEAL='#14b8a6'

fig, axes = plt.subplots(2, 2, figsize=(10.5, 8), dpi=600)
fig.patch.set_facecolor('white')

# (a) Role distribution
ax = axes[0,0]
roles=['Marker','Executor','Regulator','Uncertain']; vals=[5,469,9489,11605]
bars = ax.barh(roles, vals, color=['#e7e5e4', ORANGE, BLUE, GREY])
for b,v in zip(bars, vals):
    ax.text(b.get_width()+250, b.get_y()+b.get_height()/2, f'{v:,}', va='center', fontsize=9, color=NAVY, fontweight='bold')
ax.set_xlim(0,13500); ax.set_title('Role distribution (21,568 pairs)', fontsize=11, fontweight='bold', color=NAVY)
ax.text(-0.14, 1.02, 'A', transform=ax.transAxes, fontsize=15, fontweight='bold', color=NAVY)
ax.spines[['top','right']].set_visible(False); ax.tick_params(colors=NAVY, labelsize=8)

# (b) Mechanistic by level
ax = axes[0,1]
levels=['L1','L2','L3','L4','L5']; pcts=[64.7,40.5,33.3,23.6,31.4]
lcolors=[GOLD,BLUE,GREEN,PURPLE,ORANGE5]
bars = ax.bar(levels, pcts, color=lcolors, width=0.62)
for b,v in zip(bars,pcts):
    ax.text(b.get_x()+b.get_width()/2, v+1.2, f'{v}%', ha='center', fontsize=9, color=NAVY, fontweight='bold')
ax.set_ylim(0,70); ax.set_title('Mechanistically involved, by level (%)', fontsize=11, fontweight='bold', color=NAVY)
ax.text(-0.14, 1.02, 'B', transform=ax.transAxes, fontsize=15, fontweight='bold', color=NAVY)
ax.spines[['top','right']].set_visible(False); ax.tick_params(colors=NAVY, labelsize=8)

# (c) Direction
ax = axes[1,0]
dirs=['Protects','Promotes']; dvals=[4755,5070]
bars = ax.barh(dirs, dvals, color=[TEAL, ORANGE])
for b,v in zip(bars,dvals):
    ax.text(b.get_width()+110, b.get_y()+b.get_height()/2, f'{v:,}', va='center', fontsize=9, color=NAVY, fontweight='bold')
ax.set_xlim(0,6800); ax.set_title('Direction of regulation', fontsize=11, fontweight='bold', color=NAVY)
ax.text(-0.14, 1.02, 'C', transform=ax.transAxes, fontsize=15, fontweight='bold', color=NAVY)
ax.spines[['top','right']].set_visible(False); ax.tick_params(colors=NAVY, labelsize=8)

# (d) Bullseye — AREA-proportional rings
ax = axes[1,1]
TOTAL = 21568
R3 = 1.0
R2 = math.sqrt((9489+469)/TOTAL)
R1 = math.sqrt(469/TOTAL)
# outer grey ring (uncertain)
ax.add_patch(Wedge((0,0), R3, 0, 360, width=R3-R2, facecolor=GREY, alpha=0.9))
# middle blue ring (regulator)
ax.add_patch(Wedge((0,0), R2, 0, 360, width=R2-R1, facecolor=BLUE, alpha=0.9))
# inner orange core (executor)
ax.add_patch(plt.Circle((0,0), R1, color=ORANGE, alpha=0.95))
# labels
ax.text(0, (R2+R3)/2, 'UNCERTAIN\n11,605', ha='center', va='center', fontsize=8, color=NAVY, fontweight='bold')
ax.text(0, (R1+R2)/2, 'REGULATOR\n9,489', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
ax.text(0, 0, '469', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
ax.text(0, -0.24, 'EXECUTOR', ha='center', va='center', fontsize=8, color=ORANGE, fontweight='bold')
ax.set_xlim(-1.15,1.15); ax.set_ylim(-1.15,1.15); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('The core is small; the network is vast', fontsize=11, fontweight='bold', color=NAVY, pad=6)
ax.text(-0.14, 1.02, 'D', transform=ax.transAxes, fontsize=15, fontweight='bold', color=NAVY)

plt.tight_layout()
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
print('Figure 3 regenerated (V026 numbers)')
