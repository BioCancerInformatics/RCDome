"""
VERBATIM AUDIT — Galluzzi 2018 (NCCD Box 1) and Rodrigues et al. 2025 (Dataset S1A)
definitions must be byte-identical to the source (modulo whitespace normalization).

Part 1: re-extract Galluzzi Box 1 from the PMC XML (not the saved JSON) and compare
        against the decoder's galluzzi_nccd_definition / operational_definition.
Part 2: re-read Rodrigues S1A "Operational Definition" from the xlsx and compare
        against the decoder's operational_definition (12) or complement (13).
"""
import re, json, sys, openpyxl, pandas as pd

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
DEC = BASE + r"/RCDome Decoder"

def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip()

df = pd.read_csv(DEC + "/RCDome_Decoder_53.csv")
PASS = FAIL = 0
def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1; print(f"  [PASS] {name}")
    else:
        FAIL += 1; print(f"  [FAIL] {name}  {detail}")

sys.stdout.reconfigure(encoding="utf-8")
print("=" * 72)
print("VERBATIM AUDIT — Galluzzi NCCD 2018 + Rodrigues S1A 2025")
print("=" * 72)

# ---------- Part 1: Galluzzi verbatim (re-extract from PMC XML) ----------
print("\n[Part 1] Galluzzi NCCD 2018 Box 1 (re-extracted from PMC5864239 XML)")
xml = open(DEC + "/galluzzi2018_nccd_pmc5864239.xml", encoding="utf-8").read()
i = xml.find("Box 1 Operational definitions")
j = xml.find("</boxed-text>", i)
if j < 0:
    j = i + 20000
seg = xml[i:j]
txt = re.sub(r"<[^>]+>", " ", seg)
txt = re.sub(r"\s+", " ", txt).strip()
cut = txt.find("Intrinsic apoptosis Intrinsic apoptosis")
if cut > 0:
    txt = txt[:cut].strip()
TERMS = ["Accidental cell death (ACD)", "Anoikis", "Autophagy-dependent cell death", "Autosis",
         "Cell death", "Cellular senescence", "Efferocytosis", "Entotic cell death",
         "Extrinsic apoptosis", "Ferroptosis", "Immunogenic cell death", "Intrinsic apoptosis",
         "Lysosome-dependent cell death", "Mitochondrial permeability transition (MPT)-driven necrosis",
         "Mitotic catastrophe", "Mitotic death", "Necroptosis", "NETotic cell death",
         "Parthanatos", "Programmed cell death (PCD)", "Pyroptosis", "Regulated cell death (RCD)"]
pos = [(txt.find(t), t) for t in TERMS]
pos.append((len(txt), "__END__"))
fresh_nccd = {}
for k in range(len(TERMS)):
    p0, name = pos[k]
    p1 = pos[k + 1][0]
    if p0 < 0:
        continue
    body = txt[p0 + len(name):p1].strip().lstrip(" .").strip()
    fresh_nccd[name] = re.sub(r"\s*\.\s*$", "", norm(body))

NCCD_MAP = {
    "Anoikis": "Anoikis", "Autophagy-dependent cell death": "Autophagy-dependent cell death",
    "Autosis": "Autosis", "Cellular senescence": "Cellular senescence",
    "Efferocytosis": "Efferocytosis", "Entotic cell death": "Entosis",
    "Extrinsic apoptosis": "Apoptosis (extrinsic)", "Ferroptosis": "Ferroptosis",
    "Immunogenic cell death": "Immunogenic cell death", "Intrinsic apoptosis": "Apoptosis (intrinsic)",
    "Lysosome-dependent cell death": "Lysosome-dependent cell death",
    "Mitochondrial permeability transition (MPT)-driven necrosis": "MPT-driven necrosis",
    "Mitotic catastrophe": "Mitotic catastrophe", "Mitotic death": "Mitotic death",
    "Necroptosis": "Necroptosis", "NETotic cell death": "NETosis",
    "Parthanatos": "Parthanatos", "Programmed cell death (PCD)": "Programmed cell death",
    "Pyroptosis": "Pyroptosis",
}
ok = 0; total = 0
for nccd_term, ent in NCCD_MAP.items():
    if nccd_term not in fresh_nccd:
        continue
    total += 1
    row = df[df["rcd_form"] == ent]
    if not len(row):
        continue
    r = row.iloc[0]
    g = norm(r["galluzzi_nccd_definition"])
    op = norm(r["operational_definition"])
    expected = fresh_nccd[nccd_term]
    if g == expected and op == expected:
        ok += 1
    else:
        print(f"  MISMATCH {ent}:")
        print(f"    decoder galluzzi : {g[:80]}")
        print(f"    decoder OD       : {op[:80]}")
        print(f"    source           : {expected[:80]}")
check(f"Galluzzi verbatim: {ok}/{total} byte-identical (galluzzi_nccd_definition == OD == source)", ok == total, f"{ok}/{total}")

# ---------- Part 2: Rodrigues S1A verbatim (re-read from xlsx) ----------
print("\n[Part 2] Rodrigues et al. 2025 Dataset S1A (re-read from xlsx)")
wb = openpyxl.load_workbook(BASE + r"/output databases/Dataset S1_Rodrigues et al 2025.xlsx", read_only=True)
ws = wb["Dataset S1A"]
s1a_fresh = {}
for r in ws.iter_rows(min_row=2, values_only=True):
    if r[1] is None:
        continue
    s1a_fresh[norm(r[1])] = norm(r[3])  # Operational Definition column

# S1A name -> decoder canonical name
CANON = {
    "Apoptosis": "Apoptosis", "Necroptosis": "Necroptosis", "Pyroptosis": "Pyroptosis",
    "Ferroptosis": "Ferroptosis", "Autophagy": "Autophagy", "Cuproptosis": "Cuproptosis",
    "Mitotic Catastrophe": "Mitotic catastrophe", "Parthanatos": "Parthanatos",
    "Immunogenic Cell Death": "Immunogenic cell death", "Autosis": "Autosis",
    "NETosis": "NETosis", "Disulfidptosis": "Disulfidptosis", "Alkaliptosis": "Alkaliptosis",
    "Lysosome-Dependent Cell Death (LDCD)": "Lysosome-dependent cell death",
    "Entosis": "Entosis", "Anoikis": "Anoikis", "Oxeiptosis": "Oxeiptosis",
    "Paraptosis": "Paraptosis", "Cellular Senescence": "Cellular senescence",
    "Mitoptosis": "Mitoptosis", "Erebosis": "Erebosis", "Efferocytosis": "Efferocytosis",
    "Mitochondrial Permeability Transition": "Mitochondrial permeability transition",
    "Methuosis": "Methuosis", "Necrosis": "Necrosis",
}
ok = 0; total = 0
for s1a_name, prose in s1a_fresh.items():
    ent = CANON.get(s1a_name)
    if ent is None:
        continue
    row = df[df["rcd_form"] == ent]
    if not len(row):
        continue
    total += 1
    r = row.iloc[0]
    in_op = norm(r["operational_definition"])
    in_comp = norm(r["operational_definition_complement"])
    match = (in_op == prose) or (in_comp == prose)
    if match:
        ok += 1
    else:
        print(f"  MISMATCH {ent}:")
        print(f"    OD        : {in_op[:80]}")
        print(f"    complement: {in_comp[:80]}")
        print(f"    source    : {prose[:80]}")
check(f"Rodrigues S1A verbatim: {ok}/{total} found verbatim (in OD or complement)", ok == total, f"{ok}/{total}")

print("\n" + "=" * 72)
print(f"VERBATIM AUDIT RESULT: {PASS} PASS, {FAIL} FAIL")
print("=" * 72)
