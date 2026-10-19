# -*- coding: utf-8 -*-
"""Group A reconciliation: supp-tables cell (T->CT) + decoder + distribution board/docs.
Approved by curator. Careful: only G0-G6->BG0-BG6, C1-C5->MC1-MC5, ~C#->~MC#, T1-T4->ET1-ET4.
Ranking C1-C6 (Group B) left untouched."""
import sys, os, re, glob, json, datetime
sys.stdout.reconfigure(encoding='utf-8')
import openpyxl

MAIN = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
log = {'date': datetime.datetime.now().isoformat(), 'changes': []}

# ---- 1. supp tables: one cell T->CT (confidence context) ----
XLSX = os.path.join(MAIN, 'manuscript_V027/RCDome_manuscript_V027_supplementary_tables.xlsx')
wb = openpyxl.load_workbook(XLSX)
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and 'Confidence tier derived from the weighted score (T1 strongest)' in str(cell.value):
                old = cell.value
                cell.value = str(cell.value).replace('(T1 strongest)', '(CT1 strongest)')
                log['changes'].append({'artifact':'supp_tables','sheet':ws.title,'cell':cell.coordinate,'old':'(T1 strongest)','new':'(CT1 strongest)'})
wb.save(XLSX)
print("[supp tables] cell fixed")

# ---- 2. text files (decoder + distribution board/docs) ----
TEXT_FILES = [
  'RCDome Decoder/MandM_operational_definitions.md',
  'RCDome Decoder/RCDome_Definition_Governance.md',
  'RCDome Decoder/GROUP_G_canonical_mapping.md',
  'RCDome Decoder/GROUP_C_compliance_declaration.md',
  'RCDome_distribution/README_DISTRIBUTION.md',
  'RCDome_distribution/CHANGELOG_V026_4.md',
  'RCDome_distribution/board/run_qa_benchmark.py',
  'RCDome_distribution/board/run_board_benchmark.py',
  'RCDome_distribution/board/qa_benchmark_report.json',
] + glob.glob('RCDome_distribution/board/qa_t*.json') + glob.glob('RCDome_distribution/board/Example_RCDome_Board_*.html')

def apply_text(p, rules):
    s = open(p, encoding='utf-8', errors='ignore').read()
    orig = s
    for pat, rep, label in rules:
        s, n = re.subn(pat, rep, s)
        if n:
            log['changes'].append({'artifact':'text','file':p,'label':label,'count':n})
    if s != orig:
        open(p, 'w', encoding='utf-8').write(s)
        return True
    return False

# ordered rules: C->MC first, then G->BG, then T->ET
rules = [
    (r'C1-C5', 'MC1-MC5', 'C1-C5 -> MC1-MC5'),
    (r'~ C([1-5])', r'~ MC\1', '~ C# -> ~ MC#'),
    (r'tier_T([1-4])', r'tier_ET\1', 'tier_T# -> tier_ET#'),
    (r'\bG([0-6])\b', r'BG\1', 'G0-G6 -> BG0-BG6'),
    (r'\bT([1-4])\b', r'ET\1', 'T1-T4 -> ET1-ET4'),
]
n_files = 0
for rel in TEXT_FILES:
    p = os.path.join(MAIN, rel)
    if os.path.exists(p) and apply_text(p, rules):
        n_files += 1
print(f"[text] files changed: {n_files}")

open('D:/_groupA_decoder_board_changes.json','w',encoding='utf-8').write(json.dumps(log, indent=2, ensure_ascii=False))
print("log: D:/_groupA_decoder_board_changes.json")
