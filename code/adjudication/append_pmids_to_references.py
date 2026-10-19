# -*- coding: utf-8 -*-
"""Append PMID (from the audit CSV) to each cited reference in referencias/*.txt."""
import sys, os, csv, re, shutil, datetime
sys.stdout.reconfigure(encoding='utf-8')
base = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Criação de cartoon representations for RCDome/RCD modulo revisao'
ref_dir = os.path.join(base, 'referencias')

# backup
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
bak = os.path.join(base, f'_backup_referencias_{ts}')
shutil.copytree(ref_dir, bak)
print('backup:', bak)

# load lookup (entity, doi) -> pmid
lookup = {}
with open(os.path.join(base, 'tabela_referencias_doi_pmid.csv'), encoding='utf-8-sig') as f:
    for r in csv.reader(f, delimiter=';'):
        if len(r) >= 4 and r[0] != 'Entidade RCD':
            ent, doi, pmid = r[0].strip().lower(), r[2].strip().lower(), r[3].strip()
            if doi:
                lookup[(ent, doi)] = pmid

doi_pat = re.compile(r'DOI:\s*(10\.[^\s*]+)', re.I)

total_doi = 0
appended = 0
not_available = 0
skipped_pmid = 0
no_id = 0

for fn in sorted(os.listdir(ref_dir)):
    if not fn.endswith('.txt'):
        continue
    ent = os.path.splitext(fn)[0]
    path = os.path.join(ref_dir, fn)
    lines = open(path, encoding='utf-8').read().splitlines(keepends=True)
    out = []
    for line in lines:
        stripped = line.rstrip('\n')
        if 'PMID:' in stripped:
            out.append(line)
            skipped_pmid += 1
            continue
        m = doi_pat.search(stripped)
        if m:
            total_doi += 1
            doi = m.group(1).lower()
            pmid = lookup.get((ent.lower(), doi))
            if pmid:
                newline = stripped + f' **PMID: {pmid}**'
                appended += 1
            else:
                newline = stripped + ' **PMID: not available**'
                not_available += 1
            out.append(newline + '\n')
        elif 'DOI: not available' in stripped:
            out.append(line)
            no_id += 1
        else:
            # no DOI, no PMID -> keep + flag
            out.append(line)
            no_id += 1
    open(path, 'w', encoding='utf-8').write(''.join(out))

print(f'\nreferences with DOI processed: {total_doi}')
print(f'PMID appended: {appended}')
print(f'PMID "not available": {not_available}')
print(f'already had PMID (skipped): {skipped_pmid}')
print(f'no DOI/PMID (left as-is): {no_id}')
