"""
Add provenance chain to the RCDome decoder (P3 policy):
  - source_databases  (aggregated from V026 matrix)
  - source_channels   (aggregated from V026 matrix)
  - provenance_note   (matrix elic_onto_operational_note; explicit note for composites)
  - reference_pmid    for the composite = parent evidence PMIDs (P1 policy)

No entity is deleted (P0). The composite is KEPT and annotated, not wiped.
"""
import pandas as pd, sys

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
DEC = BASE + r"/RCDome Decoder"
M = pd.read_csv(BASE + r"/output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv")
ev = pd.read_csv(DEC + "/entity_evidence_V026.csv")
df = pd.read_csv(DEC + "/RCDome_Decoder_53.csv")

# aggregate source databases + channels per canonical entity
PROV = {}
for ent, g in M.groupby("rcd_form_canonical"):
    dbs = sorted({x for v in g["source_databases"].dropna() for x in str(v).split(";") if x.strip()})
    chs = sorted({x for v in g["source_channels"].dropna() for x in str(v).split(";") if x.strip()})
    PROV[ent] = {"source_databases": ";".join(dbs), "source_channels": ";".join(chs)}

note_map = {r["rcd_form_canonical"]: str(r["elic_onto_operational_note"]) for _, r in ev.iterrows()}

def prov_note(ent):
    if ent == "Senescence and Autophagy in Cancer":
        return ("WikiPathways pathway label (channel B) + Elicit_Phase3 (channel E); "
                "composite of Cellular senescence + Autophagy — NOT a distinct RCD entity. "
                "Retained per provenance policy P0/P1 (no deletion).")
    return note_map.get(ent, "")

df["source_databases"] = df["rcd_form"].map(lambda e: PROV.get(e, {}).get("source_databases", ""))
df["source_channels"] = df["rcd_form"].map(lambda e: PROV.get(e, {}).get("source_channels", ""))
df["provenance_note"] = df["rcd_form"].map(prov_note)

# P1: composite carries parent evidence PMIDs (never a fabricated one)
comp = df["rcd_form"] == "Senescence and Autophagy in Cancer"
df["reference_pmid"] = df["reference_pmid"].astype(object)
df["reference_citation"] = df["reference_citation"].astype(object)
df["primary_refs_pmids"] = df["primary_refs_pmids"].astype(object)
df.loc[comp, "reference_pmid"] = "29362479;36864290"
df.loc[comp, "reference_citation"] = "Composite of Cellular senescence (PMID 29362479) + Autophagy (PMID 36864290)"
df.loc[comp, "primary_refs_pmids"] = "29362479;36864290"

df.to_csv(DEC + "/RCDome_Decoder_53.csv", index=False)
print("SAVED RCDome_Decoder_53.csv | columns:", len(df.columns))
print()
print("=== provenance chain per entity (examples) ===")
for ent in ["Senescence and Autophagy in Cancer", "Apoptosis", "Floatptosis", "Necroptosis"]:
    r = df[df["rcd_form"] == ent].iloc[0]
    print(f"  {ent:36s}")
    print(f"    DBs: {r['source_databases'][:70]}")
    print(f"    ch : {r['source_channels'][:30]}")
    print(f"    ref: {r['reference_pmid']}")
    print(f"    note: {str(r['provenance_note'])[:90]}")
print()
print("entities with source_databases:", df["source_databases"].astype(str).str.len().gt(1).sum(), "/53")
print("entities with provenance_note:", df["provenance_note"].astype(str).str.len().gt(1).sum(), "/53")
