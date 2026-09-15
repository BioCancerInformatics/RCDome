"""Fix the progress file structure: move recovered forms under 'completed'."""
import json, csv, os
from collections import Counter

OUT_DIR = '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/extraction code snippets/phase3b_p1_output'
PROGRESS = os.path.join(OUT_DIR, 'phase3b_p1_progress.json')

# Rebuild from the governed CSVs (actual counts, no hardcoding)
FORMS = ['Apoptosis', 'Autophagy', 'Ferroptosis']

completed = {}
for form in FORMS:
    gov = os.path.join(OUT_DIR, f'{form.replace(" ", "_")}_governed.csv')
    if os.path.exists(gov):
        rows = list(csv.DictReader(open(gov, encoding='utf-8-sig')))
        genes = set(r['gene_symbol'] for r in rows)
        roles = Counter(r['rcd_gene_type'] for r in rows)
        completed[form] = {
            'records': len(rows),
            'unique_genes': len(genes),
            'roles': dict(roles),
            'governed_csv': os.path.basename(gov),
            'finished_at': 'recovered',
        }
        print(f'{form}: records={len(rows)} genes={len(genes)}')
    else:
        print(f'{form}: {gov} NOT FOUND')

progress = {'completed': completed}
json.dump(progress, open(PROGRESS, 'w'), indent=2)
print(f'\nProgress fixed: {len(completed)} forms under "completed"')
