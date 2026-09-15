"""
Inject the M&M and Results OD subsections into the manuscript V25 (additive,
no existing text removed).
  - M&M    -> after the 5-criteria paragraph (before "Multi-Channel Gene Compilation")
  - Results -> after the compendium-composition paragraph (before "Compendium Completeness")
"""
import docx, re, shutil, sys

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
DEC = BASE + r"/RCDome Decoder"
MAN = BASE + r"/RCDome_manuscript_governance_V026.docx"

def parse_md(path):
    """Return list of (text, is_header) from a .md file."""
    txt = open(path, encoding="utf-8").read()
    blocks = [b.strip() for b in re.split(r"\n\s*\n", txt) if b.strip()]
    out = []
    for b in blocks:
        b = re.sub(r"\n", " ", b)  # join wrapped lines
        if b.startswith("# "):
            out.append((b[2:].strip(), True))
        elif b.startswith("**") and b.endswith("**") and b.count("**") == 2:
            out.append((b.strip("*"), True))
        else:
            # strip inline markdown
            t = b.replace("**", "").replace("·", "·").strip()
            out.append((t, False))
    return out

def insert_after(doc, before_idx, items):
    """Insert paragraphs (in order) before paragraph 'before_idx'."""
    anchor = doc.paragraphs[before_idx]
    for text, is_header in items:
        p = anchor.insert_paragraph_before()
        run = p.add_run(text)
        run.bold = is_header
        p.style = doc.styles["Normal"]

sys.stdout.reconfigure(encoding="utf-8")
# backup
shutil.copy(MAN, MAN.replace(".docx", "_backup_preOD.docx"))
print("backup:", MAN.replace(".docx", "_backup_preOD.docx"))

doc = docx.Document(MAN)
n0 = len(doc.paragraphs)

# locate anchors
mm_idx = next(i for i, p in enumerate(doc.paragraphs) if p.text.strip() == "Multi-Channel Gene Compilation Architecture")
res_idx = next(i for i, p in enumerate(doc.paragraphs) if p.text.strip() == "Compendium Completeness")

# inject
mm_items = parse_md(DEC + "/MandM_operational_definitions.md")
res_items = parse_md(DEC + "/Results_OD_census.md")
insert_after(doc, mm_idx, mm_items)
# after the first insertion, indices shift; re-locate the Results anchor
res_idx = next(i for i, p in enumerate(doc.paragraphs) if p.text.strip() == "Compendium Completeness")
insert_after(doc, res_idx, res_items)

doc.save(MAN)
n1 = len(doc.paragraphs)
print(f"paragraphs: {n0} -> {n1}  (+{n1-n0})")
print(f"M&M inserted {len(mm_items)} blocks before '{doc.paragraphs[mm_idx].text.strip()}'")
print(f"Results inserted {len(res_items)} blocks before 'Compendium Completeness'")
