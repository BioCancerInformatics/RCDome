# -*- coding: utf-8 -*-
"""Ocean-deep Group A consistency audit (3 artifacts) + project-wide stale-name sweep."""
import sys, os, re, zipfile
sys.stdout.reconfigure(encoding='utf-8')
import openpyxl

MAIN = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
GH   = r"D:/RCDome_github"
MV   = os.path.join(MAIN, 'manuscript_V027')

def docx_text(p):
    z = zipfile.ZipFile(p)
    x = z.read('word/document.xml').decode('utf-8','ignore')
    return re.sub(r'<[^>]+>', '', re.sub(r'</w:p>', '\n', x))

# Group A tokens (stale vs canonical)
STALE = {
  'evidence-tier T1-T4 (stale)': re.compile(r'\bT[1-4]\b'),
  'biol-gate G0-G6 (stale)':      re.compile(r'\bG[0-6]\b'),
  'modality C2/C3 (stale)':       re.compile(r'\bC[23]\s+(trigger|morpholog)'),
  'modality C1-C5 (stale)':       re.compile(r'C1-C5'),
}
CANON = {
  'ET1-ET4': re.compile(r'ET[1-4]'),
  'BG0-BG6': re.compile(r'BG[0-6]'),
  'MC1-MC5': re.compile(r'MC[1-5]'),
}

print("="*80)
print("TASK 1 — OCEAN-DEEP AUDIT OF THE THREE ARTIFACTS")
print("="*80)

# 1a. manuscript
mt = docx_text(os.path.join(MV,'RCDome_manuscript_governance_V026.docx'))
# 1b. supplementary info
si = docx_text(os.path.join(MV,'RCDome_manuscript_V027_supplementary_information.docx'))
# 1c. supplementary tables (all cells)
wb = openpyxl.load_workbook(os.path.join(MV,'RCDome_manuscript_V027_supplementary_tables.xlsx'), read_only=True, data_only=True)
xt = '\n'.join(str(c) for ws in wb.worksheets for row in ws.iter_rows(values_only=True) for c in row if c is not None)

for name, txt in [('manuscript', mt), ('supp info', si), ('supp tables', xt)]:
    print(f"\n--- {name} ---")
    for label, pat in STALE.items():
        hits = [m for m in pat.finditer(txt)]
        # filter: keep only "gate-like" or genuine; report all with context
        keep = []
        for m in hits:
            s = max(0,m.start()-25); e = min(len(txt),m.end()+25)
            ctx = txt[s:e].replace('\n',' ')
            keep.append((m.group(0), ctx))
        print(f"  {label}: {len(keep)}")
        for g, ctx in keep[:6]:
            print(f"     {g!r} …{ctx}…")
    for label, pat in CANON.items():
        print(f"  [canonical] {label}: {len(pat.findall(txt))}")

print("\n" + "="*80)
print("TASK 2 — PROJECT-WIDE STALE-NAME SWEEP (files that may need Group A)")
print("="*80)

EXTS = {'.py','.R','.md','.txt','.html','.json','.csv','.yml','.yaml'}
SKIP_DIRS = {'_archive','_archive_backups','.git','Emergency backup file','__pycache__','RCDome_distribution/data'}

# which files contain stale names (with word-boundary care)
report = []
for root in (MAIN, GH):
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if os.path.splitext(fn)[1].lower() not in EXTS: continue
            p = os.path.join(dirpath, fn)
            try:
                s = open(p, encoding='utf-8', errors='ignore').read()
            except Exception:
                continue
            findings = []
            for m in re.finditer(r'\bG[0-6]\b', s):
                ctx = s[max(0,m.start()-20):m.end()+20].replace('\n',' ')
                # only flag gate-like (not gene symbols)
                if re.search(r'gate|machinery|necessity|phenotype|replication|species scope|hard[- ]gate|G[0-6][- ]G[0-6]', ctx):
                    findings.append(('G0-G6', ctx))
            for m in re.finditer(r'\bT[1-4]\b', s):
                ctx = s[max(0,m.start()-20):m.end()+20].replace('\n',' ')
                if re.search(r'evidence|tier|T[1-4] multi|multi-tier|Gold Standard|Strong Evidence|Moderate Evidence|Weak Evidence', ctx):
                    findings.append(('T1-T4', ctx))
            for m in re.finditer(r'\bC[23]\s+(trigger|morpholog)', s):
                ctx = s[max(0,m.start()-20):m.end()+20].replace('\n',' ')
                findings.append(('C2/C3', ctx))
            for m in re.finditer(r'C1-C5', s):
                ctx = s[max(0,m.start()-20):m.end()+20].replace('\n',' ')
                findings.append(('C1-C5', ctx))
            if findings:
                report.append((os.path.relpath(p, MAIN) if p.startswith(MAIN) else os.path.relpath(p, GH), findings))

print(f"\nfiles with Group-A stale names (outside the 3 artifacts + archives): {len(report)}")
for p, findings in report:
    print(f"\n  {p}")
    for kind, ctx in findings[:5]:
        print(f"     [{kind}] …{ctx}…")
