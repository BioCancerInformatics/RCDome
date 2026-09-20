# -*- coding: utf-8 -*-
import docx, io, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = "D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
import os; os.chdir(BASE)

f = "manuscript_V026/RCDome_manuscript_supplementary_information.docx"
d = docx.Document(f)
paras = d.paragraphs

# locate boundaries
i_notes = i_figs = None
for i,p in enumerate(paras):
    t = p.text.strip()
    if t == "Supplementary Notes": i_notes = i
    if t.startswith("Supplementary Figure Legends"): i_figs = i
print("notes heading:", i_notes, "| figure legends:", i_figs)

# capture benchmark blocks by heading text (¶ i_notes+1 .. i_figs-1)
def block_texts():
    blocks = {}
    cur = None
    for i in range(i_notes+1, i_figs):
        t = paras[i].text.strip()
        if t.startswith("RCDome: AI Usage"): cur = "S5"
        elif t.startswith("RCDome: Model-Selection"): cur = "S2"
        elif t.startswith("RCDome: Consensus API"): cur = "S3"
        elif t.startswith("RCDome: Digital Molecular"): cur = "S6"
        elif t.startswith("Supplementary Note S"): cur = None  # scrambled inserted content, skip
        if cur:
            blocks.setdefault(cur, []).append(t if t else "")
    return blocks

blocks = block_texts()
print("captured benchmark blocks:", {k: len(v) for k,v in blocks.items()})

# read S1 + S4 markdown (correct content, forward order)
def md_lines(path):
    out = []
    for line in io.open(path, encoding="utf-8").read().split("\n"):
        line = line.strip()
        if not line: continue
        if line.startswith("|"): continue  # skip tables
        line = line.lstrip("#").strip()
        line = line.replace("**","")
        if line.startswith("- "): line = "• " + line[2:]
        out.append(line)
    return out

s1_lines = md_lines("Expert Nomenclature and Ontological Adjudication Audit/Supplementary_Note_S1_Terminology_Ontological_Adjudication_Governance.md")
s4_lines = md_lines("Expert Nomenclature and Ontological Adjudication Audit/Supplementary_Note_S4_Canonicalization_Logic.md")
print("S1 lines:", len(s1_lines), "| S4 lines:", len(s4_lines))

# delete the whole notes content (i_notes+1 .. i_figs-1)
for i in range(i_notes+1, i_figs):
    paras[i]._element.getparent().remove(paras[i]._element)

# rebuild in serial order: S1, S2, S3, S4, S5, S6
anchor = d.paragraphs[i_notes]  # "Supplementary Notes"
target_para = d.paragraphs[i_notes+1] if i_notes+1 < len(d.paragraphs) else None  # "Supplementary Figure Legends"

ordered = s1_lines + blocks.get("S2", []) + blocks.get("S3", []) + s4_lines + blocks.get("S5", []) + blocks.get("S6", [])

if target_para is None:
    # append at end
    for line in ordered:
        p = d.add_paragraph(line)
else:
    # insert before the figure legends, in reverse so order is preserved
    for line in ordered:
        np = target_para.insert_paragraph_before(line)
        np.style = target_para.style

d.save(f)
print("rebuilt notes in serial order S1-S6; total lines:", len(ordered))
