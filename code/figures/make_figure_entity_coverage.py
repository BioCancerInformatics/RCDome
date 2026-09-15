# RCDome Figure 4: 53-entity coverage — log2 bars + real gene count labels (V026)
# Python equivalent of make_figure_entity_coverage.R (R unavailable in CI)
import csv, sys, math
csv.field_size_limit(10**9)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict

CSV = 'D:/RCDome_github/data/unified_gene_rcd_matrix_V026.csv'
OUT = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures/Figure_4_entity_coverage'

lvl_color = {'L1': '#FCBB18', 'L2': '#5DADE2', 'L3': '#58D68D', 'L4': '#AF7AC5', 'L5': '#F1948A'}
lvl_name = {'L1': 'L1 Modalities', 'L2': 'L2 Subtypes', 'L3': 'L3 Triggers',
            'L4': 'L4 Functional/contextual', 'L5': 'L5 Generic/umbrella/legacy/taxon/emerging'}
dark = '#1F2937'

genes = defaultdict(set)
with open(CSV, encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        genes[(row['rcd_form_canonical'], row['rcdome_level'])].add(row['gene_symbol'])

agg = sorted(((e, lv, len(g)) for (e, lv), g in genes.items()), key=lambda x: x[2])
entities = [f'{e} ({lv})' for e, lv, _ in agg]
counts = [c for _, _, c in agg]
levels = [lv for _, lv, _ in agg]
lg = [math.log2(c) for c in counts]
cols = [lvl_color[lv] for lv in levels]

ticks = [1, 4, 16, 64, 256, 1024, 4096]

fig, ax = plt.subplots(figsize=(8.27, 11.69))
y = range(len(agg))
ax.barh(list(y), lg, color=cols, edgecolor=dark, height=0.7)
ax.set_yticks(list(y))
ax.set_yticklabels(entities, fontsize=6.5, color=dark)
ax.set_xlim(0, 13.8)
ax.set_xticks([math.log2(t) for t in ticks])
ax.set_xticklabels([str(t) for t in ticks], color=dark, fontsize=8)
ax.set_xlabel('Genes associated with the entity  (log2 scale)', color=dark, fontsize=9)
ax.set_title('Gene coverage of the 53 canonicalized RCD-related entities', color=dark, fontweight='bold', fontsize=13)
for yy, l, c in zip(y, lg, counts):
    ax.text(l + 0.06, yy, f'{c:,}', va='center', fontsize=6.5, color=dark)
handles = [plt.Rectangle((0, 0), 1, 1, color=lvl_color[k], ec=dark) for k in ['L1', 'L2', 'L3', 'L4', 'L5']]
ax.legend(handles, [lvl_name[k] for k in ['L1', 'L2', 'L3', 'L4', 'L5']],
          loc='lower right', fontsize=7, title='Ontological level', title_fontsize=8,
          frameon=False, labelcolor=dark)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(dark)
ax.spines['bottom'].set_color(dark)
ax.tick_params(colors=dark)
plt.tight_layout()
fig.savefig(OUT + '.png', dpi=600, facecolor='white')
fig.savefig(OUT + '.pdf', facecolor='white')
# data CSV (same as R writes)
with open(OUT + '_data.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['rcd_form_canonical', 'rcdome_level', 'genes'])
    for e, lv, c in agg:
        w.writerow([e, lv, c])
print('Figure 4 regenerated (Python equivalent, V026)')
