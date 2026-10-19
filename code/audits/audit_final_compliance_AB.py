# -*- coding: utf-8 -*-
"""Final ocean-deep compliance audit: Group A + Group B vs Figure S1 truth."""
import sys, os, re, zipfile
sys.stdout.reconfigure(encoding='utf-8')
import openpyxl

MAIN = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
MV = os.path.join(MAIN, 'manuscript_V027')

def docx_text(p):
    z = zipfile.ZipFile(p)
    x = z.read('word/document.xml').decode('utf-8','ignore')
    return re.sub(r'<[^>]+>', '', re.sub(r'</w:p>', '\n', x))

mt = docx_text(os.path.join(MV, 'RCDome_manuscript_governance_V026.docx'))
si = docx_text(os.path.join(MV, 'RCDome_manuscript_V027_supplementary_information.docx'))
wb = openpyxl.load_workbook(os.path.join(MV, 'RCDome_manuscript_V027_supplementary_tables.xlsx'), read_only=True, data_only=True)
xt = '\n'.join(str(c) for ws in wb.worksheets for row in ws.iter_rows(values_only=True) for c in row if c is not None)

def classify_gene(ctx):
    """Heuristic: gene-symbol noise (family/member/protein/subunit etc.) vs naming token."""
    return bool(re.search(r'family|member|protein|subunit|switch|phase|cardiac|skeletal|pseudogene|domain|binding protein|kinase|reductase|troponin|complement|apolipoprotein|plexin|kinesin|homeobox|host cell factor|cyclin|forkhead|ribonuclease|checkpoint|expressed|homolog', ctx))

STALE_PATTERNS = [
    ('evidence-tier T1-T4 (stale)', re.compile(r'(?<![CE])\bT[1-4]\b')),
    ('biol-gate G0-G6 (stale)',      re.compile(r'(?<!B)\bG[0-6]\b')),
    ('modality C2/C3 (stale)',       re.compile(r'\bC[23]\s+(trigger|morpholog)')),
    ('modality C1-C5 (stale)',       re.compile(r'C1-C5')),
    ('quality QG1-QG5 (stale)',      re.compile(r'\bQG[1-5]\b')),
    ('ranking C1-C6 (stale)',        re.compile(r'(?<!M)\bC[1-6]\b')),
]
CANON = ['ET1-ET4','CT1-CT4','BG0-BG6','MC1-MC5','EG1-EG5','RS1-RS6','Q1-Q13','L1-L5']

report = []
for name, txt in [('manuscript', mt), ('supp info', si), ('supp tables', xt)]:
    print("="*70)
    print(f"ARTIFACT: {name}")
    for label, pat in STALE_PATTERNS:
        hits = list(pat.finditer(txt))
        genuine = []
        for m in hits:
            s = max(0, m.start()-35); e = min(len(txt), m.end()+35)
            ctx = txt[s:e].replace('\n',' ')
            if not classify_gene(ctx):
                genuine.append((m.group(0), ctx))
        status = 'OK (0 genuine)' if not genuine else 'FAIL'
        print(f"  {label}: {len(genuine)} genuine stale  [{status}]")
        for g, ctx in genuine[:8]:
            print(f"      {g!r} …{ctx}…")
        report.append((name, label, len(genuine), status))
    for c in CANON:
        n = len(re.findall(re.escape(c.replace('1-4','[1-4]').replace('1-5','[1-5]').replace('0-6','[0-6]').replace('1-6','[1-6]').replace('1-13','[1-9]')), txt))
    print("  canonical present:", {c: (re.search(re.escape(c), txt) is not None) for c in ['ET1','CT1','BG0','MC1','EG1','RS1','Q1']})

print("\n" + "="*70)
print("SUMMARY")
fails = [r for r in report if r[3] == 'FAIL']
print(f"  total checks: {len(report)} | FAIL: {len(fails)}")
for r in fails:
    print(f"    FAIL {r[0]} :: {r[1]} ({r[2]} stale)")
