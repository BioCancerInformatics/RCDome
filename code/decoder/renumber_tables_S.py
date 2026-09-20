"""
Renumber supplementary tables S1-S14 by FIRST-CALLOUT order across:
  - manuscript (RCDome_manuscript_governance_V026.docx)
  - workbook (RCDome_manuscript_V026_supplementary_tables.xlsx: sheets + INDEX)
  - supplementary info (RCDome_manuscript_V026_supplementary_information.docx)

Mapping (old -> new), by first callout order:
  S1->S1, S12->S2, S2->S3, S3->S4, S13->S5, S4->S6, S5->S7,
  S8->S8, S6->S9, S7->S10, S14->S11, S9->S12, S10->S13, S11->S14
"""
import re, shutil, sys, docx, openpyxl

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
MAP = {1: 1, 12: 2, 2: 3, 3: 4, 13: 5, 4: 6, 5: 7, 8: 8, 6: 9, 7: 10, 14: 11, 9: 12, 10: 13, 11: 14}

def renum_text(t):
    return re.sub(r"Table S(\d+)", lambda m: f"Table S{MAP[int(m.group(1))]}", t)

sys.stdout.reconfigure(encoding="utf-8")

# ---------- 1. manuscript ----------
man = BASE + "/RCDome_manuscript_governance_V026.docx"
shutil.copy(man, man.replace(".docx", "_backup_preRenumber.docx"))
doc = docx.Document(man)
n_changed = 0
for p in doc.paragraphs:
    full = p.text
    new = renum_text(full)
    if new != full:
        # keep first run formatting, put whole new text in first run
        if p.runs:
            p.runs[0].text = new
            for r in p.runs[1:]:
                r.text = ""
        n_changed += 1
doc.save(man)
print(f"manuscript: {n_changed} paragraphs renumbered")

# ---------- 2. workbook (sheets + INDEX) ----------
wb_path = BASE + "/RCDome_manuscript_V026_supplementary_tables.xlsx"
shutil.copy(wb_path, wb_path.replace(".xlsx", "_backup_preRenumber.xlsx"))
wb = openpyxl.load_workbook(wb_path)
# two-phase sheet rename (avoid collisions)
for ws in wb.worksheets:
    if ws.title.startswith("Table S"):
        ws.title = "ZZ" + ws.title
for ws in wb.worksheets:
    if ws.title.startswith("ZZTable S"):
        old = int(re.search(r"S(\d+)", ws.title).group(1))
        ws.title = f"Table S{MAP[old]}"
# reorder sheets by new number
order = sorted([ws for ws in wb.worksheets if ws.title.startswith("Table S")],
               key=lambda w: int(re.search(r"S(\d+)", w.title).group(1)))
# move Table sheets after INDEX (they already are, just ensure order)
# update INDEX table column
idx = wb["INDEX"]
for row in idx.iter_rows(min_row=2):
    if row[0].value and str(row[0].value).startswith("Table S"):
        row[0].value = renum_text(str(row[0].value))
wb.save(wb_path)
print("workbook: sheets + INDEX renumbered ->", [ws.title for ws in wb.worksheets if ws.title.startswith("Table S")])

# ---------- 3. supplementary info ----------
sup = BASE + "/RCDome_manuscript_V026_supplementary_information.docx"
if __import__("os").path.exists(sup):
    shutil.copy(sup, sup.replace(".docx", "_backup_preRenumber.docx"))
    d2 = docx.Document(sup)
    c2 = 0
    for p in d2.paragraphs:
        full = p.text
        new = renum_text(full)
        if new != full:
            if p.runs:
                p.runs[0].text = new
                for r in p.runs[1:]:
                    r.text = ""
            c2 += 1
    d2.save(sup)
    print(f"supplementary info: {c2} paragraphs renumbered")
else:
    print("supplementary info: not found (skip)")
