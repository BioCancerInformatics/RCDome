"""
Fix the 7 NCCD-invariant pending complements: rewrite in Galluzzi style,
citation-free (the old draft prose with citations was left in the complement).
"""
import pandas as pd, re, sys

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder"
df = pd.read_csv(BASE + "/RCDome_Decoder_53.csv")
df["operational_definition_complement"] = df["operational_definition_complement"].astype(object)

COMP = {
    "Programmed cell death": "A genetically encoded, developmentally scheduled form of cell death, first defined from intersegmental-muscle degeneration during insect metamorphosis.",
    "Mitotic death": "A variant of regulated cell death driven by mitotic catastrophe, demarcated by delayed death following aberrant mitosis after radiation or drug exposure.",
    "Autophagy-dependent cell death": "A form of regulated cell death that depends on the autophagic machinery, demarcated by autophagosome accumulation and blockade of basal autophagic flux.",
    "Lysosomal cell death": "A lysosome-dependent cell death demarcated by primary lysosomal membrane permeabilization and cysteine-cathepsin (B/L) proteolysis; a synonym of lysosome-dependent cell death.",
    "Apoptosis (intrinsic)": "A subtype of apoptosis demarcated by mitochondrial outer-membrane permeabilization and regulated by Bcl-2/Bcl-xL.",
    "Apoptosis (extrinsic)": "A subtype of apoptosis initiated by death-receptor oligomerization, propagated by FADD and caspase-8.",
    "MPT-driven necrosis": "A regulated necrosis triggered by abrupt loss of inner-mitochondrial-membrane osmotic homeostasis via the permeability transition pore complex.",
}
for ent, prose in COMP.items():
    m = df["rcd_form"] == ent
    if m.any():
        df.loc[m, "operational_definition_complement"] = prose

df.to_csv(BASE + "/RCDome_Decoder_53.csv", index=False)
cited = df["operational_definition_complement"].astype(str).str.contains(r"\((?:18|19|20|21)\d{2}\)", regex=True)
sys.stdout.reconfigure(encoding="utf-8")
print("7 NCCD-invariant complements fixed (Galluzzi-style, citation-free)")
print("complements still with inline citation:", int(cited.sum()), "/53")
for ent in COMP:
    r = df[df["rcd_form"] == ent].iloc[0]
    print(f'  {ent:32s} {str(r["operational_definition_complement"])[:75]}')
