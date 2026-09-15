"""
Build the consolidated RCDome Decoder (53 entities) from:
  - Rodrigues Dataset S1A (25): prose, year, overlaps, C1-C6, S
  - RCD_25_Forms_Reference_Table_FINAL (25): category, key molecules, inflammatory, PMIDs
  - the 28 pending DRAFT records (inline, produced this session)
Output: RCDome_Decoder_53.csv + RCDome_Decoder_53.md
"""
import openpyxl, docx, csv, re, sys, json

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
DEC = BASE + r"/RCDome Decoder"

def clean(v):
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""

# ---------- 0. Galluzzi 2018 NCCD invariant definitions (verbatim Box 1) ----------
with open(DEC + "/galluzzi2018_nccd_definitions.json", encoding="utf-8") as f:
    NCCD = json.load(f)

NCCD_MAP = {
    "Anoikis": "Anoikis",
    "Autophagy-dependent cell death": "Autophagy-dependent cell death",
    "Autosis": "Autosis",
    "Cellular senescence": "Cellular senescence",
    "Efferocytosis": "Efferocytosis",
    "Entotic cell death": "Entosis",
    "Extrinsic apoptosis": "Apoptosis (extrinsic)",
    "Ferroptosis": "Ferroptosis",
    "Immunogenic cell death": "Immunogenic cell death",
    "Intrinsic apoptosis": "Apoptosis (intrinsic)",
    "Lysosome-dependent cell death": "Lysosome-dependent cell death",
    "Mitochondrial permeability transition (MPT)-driven necrosis": "MPT-driven necrosis",
    "Mitotic catastrophe": "Mitotic catastrophe",
    "Mitotic death": "Mitotic death",
    "Necroptosis": "Necroptosis",
    "NETotic cell death": "NETosis",
    "Parthanatos": "Parthanatos",
    "Programmed cell death (PCD)": "Programmed cell death",
    "Pyroptosis": "Pyroptosis",
    # synonym maps to the same NCCD definition
    "Lysosomal cell death": "Lysosomal cell death",
}

def nccd_fields(entity_name):
    for nccd_term, dec_name in NCCD_MAP.items():
        if dec_name == entity_name:
            if nccd_term == "Lysosomal cell death":
                nccd_term = "Lysosome-dependent cell death"
            return NCCD.get(nccd_term, ""), "NCCD_2018_INVARIANT"
    return "", "NOT_IN_NCCD_2018"

# ---------- 1. Read S1A (25) ----------
wb = openpyxl.load_workbook(BASE + r"/output databases/Dataset S1_Rodrigues et al 2025.xlsx", read_only=True)
ws = wb["Dataset S1A"]
s1a = {}
for r in ws.iter_rows(min_row=2, values_only=True):
    if r[1] is None:
        continue
    s1a[clean(r[1])] = {
        "year": clean(r[2]),
        "prose": clean(r[3]),
        "C": [clean(x) for x in r[4:10]],
        "S": clean(r[10]),
        "overlaps": clean(r[11]),
    }

# ---------- 2. Read Reference Table (25) ----------
doc = docx.Document(BASE + r"/RCDome Decoder/RCD_25_Forms_Reference_Table_FINAL.docx")
tb = doc.tables[0]
ref = {}
for row in tb.rows[1:]:
    c = [clean(x.text) for x in row.cells]
    name = c[1]
    pmids = re.findall(r"\b\d{7,8}\b", c[7])   # primary references column
    spmids = re.findall(r"\b\d{7,8}\b", c[8])  # secondary references column
    ref[name] = {
        "category": c[2],
        "core_mechanism": c[3],
        "key_molecules": c[4],
        "inflammatory": c[5],
        "primary_pmids": ";".join(pmids),
        "secondary_pmids": ";".join(spmids),
    }

# name alignment (S1A -> Reference Table)
ALIAS = {
    "Mitotic Catastrophe": "Mitotic catastrophe",
    "Immunogenic Cell Death": "Immunogenic cell death (ICD)",
    "Lysosome-Dependent Cell Death": "Lysosome-dependent cell death",
    "Lysosome-Dependent Cell Death (LDCD)": "Lysosome-dependent cell death",
    "Cellular Senescence": "Cellular senescence",
    "Mitochondrial Permeability Transition": "Mitochondrial permeability transition (MPT)",
}

def cat_of(name):
    return "Executioner" if name == "Autosis" else ref.get(name, {}).get("category", "")

# ---------- 3. 28 pending DRAFT records (inline) ----------
# name: (category, year, prose, key_molecules, inflammatory, overlaps, C1..C6, S, pmid, status)
P = {
 "Programmed cell death": ("UMBRELLA", 1965, "Umbrella term for genetically encoded, developmentally scheduled cell death, first defined by Lockshin & Williams (1965) from intersegmental-muscle degeneration during insect metamorphosis; parent of the specific RCD programs.", "", "member-dependent", "parent of all programmed RCD forms", 10,3,9,5,10,8, "14287218", "DRAFT_SOLID"),
 "Mitotic death": ("UMBRELLA", 1967, "Delayed cell death following aberrant mitosis after radiation or drug exposure (Jacobson & Lee 1967); umbrella overlapping mitotic catastrophe.", "", "not specified", "mitotic catastrophe; apoptosis/necrosis downstream", 5,3,5,4,5,4, "6027879", "DRAFT_SOLID"),
 "Aponecrosis": ("LEGACY", 2000, "Syncretic cell death sharing apoptotic and necrotic features, induced by high-dose mitochondrial insult; an incomplete apoptotic program that degenerates into necrosis (Formigli 2000).", "caspase-3; respiratory chain complex III", "Yes", "apoptosis + necrosis", 4,4,4,4,5,3, "10567915", "DRAFT_SOLID"),
 "Phagoptosis": ("CONTEXTUAL", 2012, "Cell death caused by phagocytosis of viable cells (primary phagocytosis), provoked by 'eat-me' signals or loss of 'don't-eat-me' signals (Brown & Neher 2012).", "eat-me signals (PS); CD47", "No", "distinct from efferocytosis", 5,5,5,5,6,5, "22682109", "DRAFT_SOLID"),
 "PANoptosis": ("INTEGRATED", 2019, "Integrated inflammatory death engaging Pyroptosis, Apoptosis and Necroptosis via the RIPK1/RIPK3-FADD-caspase-8 complex, orchestrated by ZBP1 and TAK1 (Malireddi 2019).", "ZBP1, TAK1, RIPK1, RIPK3, FADD, caspase-8, NLRP3", "Yes", "pyroptosis + apoptosis + necroptosis", 5,6,5,7,6,6, "31850239", "DRAFT_SOLID"),
 "Lysoptosis": ("LEGACY", 2022, "Lysosome-dependent cell death defined by LMP and cathepsin-dependent proteolysis, predominating when serpin inhibitors (SERPINB3/srp-6) are absent (Luke 2022).", "cathepsins (L); SERPINB3", "Yes", "subtype of LDCD", 4,5,4,5,5,4, "35022507", "DRAFT_SOLID"),
 "Floatptosis": ("EMERGING", 2025, "Cytoplasmic vacuolization death induced by Bergeyella cardium in macrophages; Fused LysOsome-Associated Termination, inhibited by amiloride (Mao 2025).", "SLC9A9; sodium channels", "not specified", "lysosome-associated vacuolar death", 3,4,3,7,5,3, "41115953", "DRAFT_SOLID"),
 "Ammonia-induced cell death": ("CONTEXTUAL", 2002, "Dose-dependent death with vacuolation induced by ammonia, detoxified via arginase and protected by L-glutamine (Nakamura & Hagen 2002).", "arginase; L-glutamine", "not specified", "vacuolar/necrotic features", 4,3,3,4,4,4, "12388179", "DRAFT_SOLID"),
 "Oncosis": ("MORPHOLOGY", 1995, "Accidental cell death with swelling from plasma-membrane ionic-pump failure (ischemia); leads to necrosis with karyolysis (Majno & Joris 1995).", "Na+/K+-ATPase", "Yes", "leads to necrosis; contrasts with apoptosis", 4,4,4,3,4,4, "7856735", "DRAFT_SOLID"),
 "Mitoxyperilysis": ("EMERGING", 2025, "Lytic death from synergism of innate-immune and metabolic signals; BAX/BAK1/BID-dependent mitochondrial oxidative stress at the plasma membrane causes lysis (Wang 2025).", "BAX, BAK1, BID, mTORC2", "Yes", "independent of pyroptosis/PANoptosis/necroptosis/ferroptosis/oxeiptosis", 3,4,3,8,5,4, "41317732", "DRAFT_SOLID"),
 "Linker cell-type death": ("TAXON", 2007, "Caspase-independent (ced-3-independent) non-apoptotic developmental death of the C. elegans linker cell (Abraham 2007).", "let-7; LIN-29", "No", "non-apoptotic developmental death", 3,4,3,4,5,3, "17199042", "DRAFT_SOLID"),
 "Cornification": ("DIFFERENTIATION", 2005, "A terminal differentiation program of keratinocytes producing the cornified (keratinized) barrier and culminating in a specialized form of programmed cell death.", "", "No", "terminal differentiation", 4,3,4,3,4,3, "15803139", "DRAFT_SOLID"),
 "Triaptosis": ("EMERGING", 2025, "An endosome-dependent cell death modality (Tang, Kang & Kroemer 2025).", "endosomal machinery", "not specified", "distinct from lysosome-dependent death", 3,3,2,7,4,2, "39638924", "DRAFT_SOLID"),
 "Spectosis": ("EMERGING", 2025, "Programmed death of red blood cells where complement initiates (mini)NLRP3-caspase-8 complexes culminating in hemolysis.", "complement; NLRP3; caspase-8", "Yes", "NLRP3-caspase-8 machinery in mature RBCs", 3,4,3,7,4,3, "40252640", "DRAFT_SOLID"),
 "Pyronecrosis": ("LEGACY", 2007, "Necrosis-like, caspase-1-independent, ASC- and cathepsin B-dependent inflammatory macrophage death with HMGB1 spillage (Willingham 2007).", "NLRP3, ASC, cathepsin B, HMGB1", "Yes", "inflammasome components; caspase-1/IL-1b-independent", 3,4,3,4,4,3, "18005730", "DRAFT_SOLID"),
 # CANDIDATE
 "Apoptosis (intrinsic)": ("SUBTYPE", 2002, "Mitochondrial (Bcl-2-regulated) apoptotic pathway, blocked by Bcl-2/Bcl-xL (Chen 2002).", "Bcl-2, Bcl-xL, Bax", "No", "subtype of Apoptosis", 6,7,7,4,8,7, "12186923", "DRAFT_CANDIDATE"),
 "Apoptosis (extrinsic)": ("SUBTYPE", 2004, "Death-receptor apoptotic pathway via CD95/Fas oligomerization, FADD recruitment and caspase-8 activation (Chatfield & Eastman 2004).", "CD95/Fas, FADD, caspase-8", "No", "subtype of Apoptosis", 6,7,6,4,7,7, "15451440", "DRAFT_CANDIDATE"),
 "Autophagy-dependent cell death": ("CORE_PENDING", 2009, "Death executed through autophagy; autophagosome inhibition prevents death; blockade of basal autophagic flux (Mora 2009).", "autophagy machinery", "not specified", "autophagy; 'autophagic cell death' predates", 5,5,4,5,6,4, "18942750", "DRAFT_CANDIDATE"),
 "Regulated Necrosis": ("UMBRELLA", 2011, "Umbrella for genetically controlled non-apoptotic necrosis; founding usage = RIP3-driven regulated necrosis controlled by FADD (Galluzzi 2011).", "RIP3, FADD", "Yes", "parent of necroptosis/pyroptosis/MPT-driven necrosis", 6,4,6,5,7,6, "21894190", "DRAFT_CANDIDATE"),
 "MPT-driven necrosis": ("CORE_PENDING", 2016, "Regulated necrosis from abrupt loss of inner-mitochondrial-membrane osmotic homeostasis via the PTPC (Izzo 2016).", "permeability transition pore complex (PTPC)", "Yes", "downstream of MPT (Trigger)", 5,5,5,4,5,5, "27161573", "DRAFT_CANDIDATE"),
 "Lysosomal cell death": ("SYNONYM", 2004, "Cysteine-cathepsin (B/L) lysosomal death pathway (Fehrenbacher 2004); synonym of Lysosome-dependent cell death.", "cathepsin B, L", "Yes", "synonym of LDCD", 4,5,4,4,5,4, "15289336", "DRAFT_CANDIDATE"),
 "Metalloptosis": ("UMBRELLA", 2025, "Umbrella for metal-ion-based RCD encompassing ferroptosis, cuproptosis, lysozincrosis, manganism, calcicoptosis and NECSO (Wang 2025).", "metal ions (Fe, Cu, Zn, Mn, Ca, Na)", "member-dependent", "umbrella of metal-RCD forms", 4,4,4,6,5,5, "41094656", "DRAFT_CANDIDATE"),
 "Lysozincrosis": ("EMERGING", 2021, "Regulated non-apoptotic, lysosomal zinc-dependent death; primary mechanism from Du et al. 2021.", "lysosomal zinc", "not specified", "metalloptosis umbrella", 3,3,3,7,4,3, "34686351", "DRAFT_CANDIDATE"),
 "NECSO": ("LEGACY", 2025, "Necrosis by sodium overload; necrocide 1 (NC1) persistently activates TRPM4 promoting Na+ influx and necrosis (Fu 2025).", "TRPM4, Na+, NC1", "Yes", "metalloptosis umbrella (sodium)", 3,4,3,6,4,3, "39915626", "DRAFT_CANDIDATE"),
 "Vacuolar cell death": ("MORPHOLOGY", 2004, "Death with conspicuous cytoplasmic vacuolization; atg1 disruption reveals a hidden non-vacuolar pathway (Kosta 2004).", "atg1", "not specified", "autophagic vacuolar death", 3,3,3,4,4,3, "15358773", "DRAFT_CANDIDATE"),
 "Eryptosis": ("CELL_TYPE", 2006, "Suicidal erythrocyte death: shrinkage, blebbing, calpain activation and PS exposure via PGE2/Ca2+ and PLA2/ceramide pathways (Lang 2006).", "Ca2+ channels, ceramide, calpain, erythropoietin", "No", "PS-exposure clearance (apoptosis/efferocytosis-like)", 4,4,4,4,5,5, "16910766", "DRAFT_CANDIDATE"),
 "Senescence and Autophagy in Cancer": ("COMPOSITE", "", "No single definition - Elicit-derived composite of senescence + autophagy in the cancer context.", "", "not applicable", "senescence + autophagy (both defined)", 4,3,4,4,4,4, "", "COMPOSITE"),
 "Hypersensitive response": ("TAXON", 1969, "Rapid localized programmed death of plant cells at infection sites restricting pathogen spread; concept predates PubMed (Stakman 1915).", "", "No", "plant innate-immunity death", 4,4,4,3,5,3, "4977772", "PRE_PUBMED"),
}

# ---------- 4. Build 53 records ----------
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
rows = []
# 25 Rodrigues
for name, d in s1a.items():
    canon = CANON.get(name, name)
    rname = ALIAS.get(name, name)
    r = ref.get(rname, {})
    nccd, nccd_status = nccd_fields(canon)
    fpmid = r.get("primary_pmids", "").split(";")[0] if r.get("primary_pmids") else ""
    if nccd_status == "NCCD_2018_INVARIANT":
        opdef, complement, opdef_src = nccd, d["prose"], "NCCD_2018_VERBATIM"
        ref_pmid, ref_cit = "29362479", "Galluzzi et al. 2018 (NCCD Box 1)"
    else:
        opdef, complement, opdef_src = d["prose"], "", "RODRIGUES_S1A"
        ref_pmid, ref_cit = "41048343", "Rodrigues et al. 2025 (Dataset S1A)"
    rows.append({
        "rcd_form": canon, "category": r.get("category", ""), "year": d["year"],
        "operational_definition": opdef, "operational_definition_complement": complement,
        "operational_definition_source": opdef_src,
        "reference_pmid": ref_pmid, "reference_citation": ref_cit,
        "primary_refs_pmids": r.get("primary_pmids", ""),
        "secondary_refs_pmids": r.get("secondary_pmids", ""),
        "core_mechanism": r.get("core_mechanism", ""),
        "key_molecules": r.get("key_molecules", ""), "inflammatory": r.get("inflammatory", ""),
        "overlaps": d["overlaps"], "C1": d["C"][0], "C2": d["C"][1], "C3": d["C"][2],
        "C4": d["C"][3], "C5": d["C"][4], "C6": d["C"][5], "S": d["S"],
        "founding_pmid": fpmid,
        "definition_status": "DEFINED_RODRIGUES",
        "galluzzi_nccd_definition": nccd, "galluzzi_nccd_status": nccd_status,
    })
# 28 pending
for name, t in P.items():
    (cat, yr, prose, mol, infl, ov, c1, c2, c3, c4, c5, c6, pmid, st) = t
    W = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
    S = round(sum(w*x for w, x in zip(W, [c1, c2, c3, c4, c5, c6])), 2)
    nccd, nccd_status = nccd_fields(name)
    if nccd_status == "NCCD_2018_INVARIANT":
        opdef, complement, opdef_src = nccd, prose, "NCCD_2018_VERBATIM"
        ref_pmid, ref_cit = "29362479", "Galluzzi et al. 2018 (NCCD Box 1)"
    else:
        opdef, complement, opdef_src = prose, "", ("FOUNDING_DRAFT" if st in ("DRAFT_SOLID", "DRAFT_CANDIDATE") else st)
        ref_pmid, ref_cit = str(pmid), ""
    rows.append({
        "rcd_form": name, "category": cat, "year": (str(yr) if yr else "n/a"), "operational_definition": opdef,
        "operational_definition_complement": complement, "operational_definition_source": opdef_src,
        "reference_pmid": ref_pmid, "reference_citation": ref_cit,
        "primary_refs_pmids": str(pmid), "secondary_refs_pmids": "",
        "core_mechanism": "", "key_molecules": mol, "inflammatory": infl, "overlaps": ov,
        "C1": c1, "C2": c2, "C3": c3, "C4": c4, "C5": c5, "C6": c6, "S": S,
        "founding_pmid": pmid, "definition_status": st,
        "galluzzi_nccd_definition": nccd, "galluzzi_nccd_status": nccd_status,
    })

rows.sort(key=lambda x: x["rcd_form"].lower())
FIELDS = ["rcd_form", "category", "year", "operational_definition",
          "operational_definition_complement", "operational_definition_source",
          "reference_pmid", "reference_citation", "primary_refs_pmids", "secondary_refs_pmids",
          "core_mechanism",
          "key_molecules", "inflammatory", "overlaps", "C1", "C2", "C3", "C4", "C5", "C6",
          "S", "founding_pmid", "definition_status", "galluzzi_nccd_definition",
          "galluzzi_nccd_status"]
with open(DEC + "/RCDome_Decoder_53.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)

print("SAVED RCDome_Decoder_53.csv | records:", len(rows))
from collections import Counter
print("status:", dict(Counter(r["definition_status"] for r in rows)))
