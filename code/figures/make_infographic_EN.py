# -*- coding: utf-8 -*-
"""Generate the ENGLISH version of Victor's nomenclature-architecture infographic (4K)."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

NAVY = '#0b1020'; GOLD = '#FFD700'; ORANGE = '#FF9800'; BLUE = '#00B0FF'
GREEN = '#00E676'; PURPLE = '#E040FB'; ORANGE5 = '#FF6D00'; GREY = '#6b7280'
CARD = '#ffffff'; BORDER = '#e5e7eb'; TEXT = '#1c1917'; MUT = '#57534e'

fig, ax = plt.subplots(figsize=(20, 28), dpi=200)  # 4000 x 5600 px
ax.set_xlim(0, 20); ax.set_ylim(0, 28); ax.axis('off')
fig.patch.set_facecolor('white')

def box(x, y, w, h, fc=CARD, ec=BORDER, lw=1.5, r=0.02):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=1))

def txt(x, y, s, size=12, color=TEXT, weight='normal', ha='center', va='center', zorder=3):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, zorder=zorder)

# ── Title ──
txt(10, 26.8, "Evaluation Architecture of RCDome V026", size=34, color=NAVY, weight='bold')
txt(10, 25.6, "Proposed framework for conceptual organization and nomenclature harmonization",
    size=16, color=MUT)

# ── Three columns ──
col_x = [0.7, 7.0, 13.3]; col_w = 6.0
col_titles = ["RCD entity", "Gene–RCD association", "Pipeline quality"]
col_subs = ["Biological / ontological\nclassification", "Strength and type of the\nrelationship", "Reliability of automated\nextraction"]
col_colors = [GOLD, BLUE, GREEN]

for i in range(3):
    x = col_x[i]
    box(x, 15.0, col_w, 9.0)
    txt(x + col_w/2, 23.3, col_titles[i], size=17, color=NAVY, weight='bold')
    txt(x + col_w/2, 21.9, col_subs[i], size=11, color=MUT)
    # header underline
    ax.plot([x+0.4, x+col_w-0.4], [21.2, 21.2], color=col_colors[i], lw=3, zorder=2)

# Column A content (RCD entity)
x = col_x[0] + col_w/2
txt(x, 20.3, "MC1–MC5", size=15, color=GOLD, weight='bold')
txt(x, 19.5, "Modality criteria\n(machinery, trigger, morphology,\nnomenclature, distinguishability)", size=10.5, color=TEXT)
txt(x, 17.9, "Q1–Q13", size=15, color=GOLD, weight='bold')
txt(x, 17.1, "Evidence checklist", size=10.5, color=TEXT)
txt(x, 16.4, "BG0–BG6", size=15, color=GOLD, weight='bold')
txt(x, 15.6, "Biological gates", size=10.5, color=TEXT)
txt(x, 18.7, "→", size=14, color=GREY)
txt(x, 18.0, "L1–L5", size=15, color=GOLD, weight='bold')
txt(x, 17.2, "Final ontological level", size=10.5, color=TEXT)

# Column B content (Gene-RCD association)
x = col_x[1] + col_w/2
txt(x, 20.3, "ET1–ET4", size=15, color=BLUE, weight='bold')
txt(x, 19.5, "Evidence tier", size=10.5, color=TEXT)
txt(x, 18.6, "confidence_score\nor CT1–CT4", size=10.5, color=TEXT)
txt(x, 17.6, "Mechanistic role & direction", size=12, color=NAVY, weight='bold')
txt(x, 16.6, "EXECUTOR, REGULATOR, MARKER;\npositive / negative / mixed", size=10.5, color=TEXT)

# Column C content (Pipeline quality)
x = col_x[2] + col_w/2
txt(x, 20.3, "EG1–EG5", size=15, color=GREEN, weight='bold')
txt(x, 19.5, "Elicit governance gates", size=10.5, color=TEXT)
txt(x, 18.6, "• Input validation\n• Allow-list compliance\n• Vocabulary compliance\n• EXECUTOR precision\n• Traceability", size=10.5, color=TEXT, ha='center')

# Goals
txt(col_x[0]+col_w/2, 14.4, "Goal", size=12, color=MUT, weight='bold')
txt(col_x[0]+col_w/2, 13.7, "Determine what the entity is,\nbiologically.", size=10.5, color=TEXT)
txt(col_x[1]+col_w/2, 14.4, "Goal", size=12, color=MUT, weight='bold')
txt(col_x[1]+col_w/2, 13.7, "Qualify the strength and type of the\ngene–RCD association.", size=10.5, color=TEXT)
txt(col_x[2]+col_w/2, 14.4, "Goal", size=12, color=MUT, weight='bold')
txt(col_x[2]+col_w/2, 13.7, "Assess the reliability of the\nautomated extraction.", size=10.5, color=TEXT)

# Key message
box(0.7, 10.4, 18.6, 2.2, fc='#f8fafc', ec=BORDER)
txt(10, 12.0, "Key message", size=14, color=NAVY, weight='bold')
txt(10, 11.2, "Three distinct objects are being evaluated: (A) the RCD entity, (B) the gene–RCD association, and (C) pipeline quality.",
    size=12, color=TEXT)

# ── Nomenclature harmonization table ──
txt(10, 9.2, "Suggested nomenclature harmonization", size=18, color=NAVY, weight='bold')
rows = [
    ("Current", "Suggested"),
    ("C1–C5 (biological classification)", "MC1–MC5"),
    ("C1–C6 (scoring)", "RS1–RS6"),
    ("G0–G6 (biological gates)", "BG0–BG6"),
    ("G1–G5 (Elicit)", "EG1–EG5"),
    ("T1–T4 (evidence)", "ET1–ET4"),
    ("T1–T4 (confidence)", "CT1–CT4 or confidence_score"),
]
ty = 8.0
row_h = 0.85
col_w2 = 8.6
tx1, tx2 = 5.4, 15.2
# header
box(tx1-4.0, ty+0.1, col_w2, row_h-0.1, fc=NAVY, ec=NAVY)
box(tx2-4.0, ty+0.1, col_w2, row_h-0.1, fc=NAVY, ec=NAVY)
txt(tx1-0.3, ty+0.5, "Current", size=13, color='white', weight='bold', ha='center')
txt(tx2-0.3, ty+0.5, "Suggested", size=13, color='white', weight='bold', ha='center')
ty -= row_h
for i, (a, b) in enumerate(rows[1:]):
    c = '#ffffff' if i % 2 == 0 else '#f1f5f9'
    box(tx1-4.0, ty+0.05, col_w2, row_h-0.05, fc=c, ec=BORDER, lw=0.8)
    box(tx2-4.0, ty+0.05, col_w2, row_h-0.05, fc=c, ec=BORDER, lw=0.8)
    txt(tx1-0.3, ty+0.45, a, size=11.5, color=TEXT, ha='center')
    txt(tx2-0.3, ty+0.45, b, size=11.5, color=NAVY, weight='bold', ha='center')
    ty -= row_h

# closing note
txt(10, ty - 0.3, "The proposed harmonization reduces ambiguity and facilitates reading, reproduction and biological curation of the atlas.",
    size=11.5, color=MUT)

plt.tight_layout(pad=0.5)
out = r'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/analysis/Victor_analysis/Auditoria_V26-20260912T123815Z-1-001/Auditoria_V26/Versões do infográfico nomeclatura/Nomeclatura_4K_EN.png'
plt.savefig(out, dpi=200, facecolor='white', bbox_inches='tight')
print("saved:", out)
