"""
Add a Galluzzi-style complement for the 12 Rodrigues-only entities (uniform reading),
while KEEPING the Rodrigues S1A verbatim as the invariant operational_definition
(provenance preserved — no published text altered).
"""
import pandas as pd, sys

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder"
df = pd.read_csv(BASE + "/RCDome_Decoder_53.csv")

# Galluzzi-style complements (grounded in the Rodrigues S1A content; no new facts)
COMPLEMENT = {
    "Apoptosis":
        "A form of programmed cell death demarcated by cell shrinkage, chromatin condensation and DNA fragmentation, executed as autonomous cell lysis without inflammation.",
    "Autophagy":
        "A lysosomal self-digestion process whereby cells degrade their own components, essential for cellular function and homeostasis.",
    "Cuproptosis":
        "A form of regulated cell death driven by copper accumulation and associated mitochondrial stress.",
    "Disulfidptosis":
        "A form of regulated cell death triggered by disulfide accumulation under glucose starvation, dependent on abnormal SLC7A11 expression.",
    "Alkaliptosis":
        "A pH-dependent form of regulated cell death triggered by alkaline conditions, demarcated by NF-kB pathway activation and carbonic anhydrase 9 downregulation.",
    "Oxeiptosis":
        "A form of regulated cell death driven by oxidative stress, demarcated by KEAP1 and NRF2 involvement.",
    "Paraptosis":
        "A non-apoptotic form of cell death demarcated by cytoplasmic vacuolation, lacking features of apoptosis.",
    "Mitoptosis":
        "A mitochondrial quality-control process of selective elimination of damaged mitochondria, triggered by mitochondrial permeability transition and oxidative stress.",
    "Erebosis":
        "A novel form of cell death reported during the natural turnover of gut enterocytes.",
    "Methuosis":
        "A form of cell death demarcated by unique vacuolization distinct from other cell death forms.",
    "Necrosis":
        "A form of cell death demarcated by cell lysis and inflammation, encompassing accidental (unregulated) and programmed (signal-regulated) variants.",
    "Mitochondrial permeability transition":
        "A trigger event demarcated by opening of a non-selective pore in the inner mitochondrial membrane, leading to loss of membrane potential and cell death.",
}

n = 0
for ent, prose in COMPLEMENT.items():
    mask = (df["rcd_form"] == ent) & (df["definition_status"] == "DEFINED_RODRIGUES") & \
           (df["galluzzi_nccd_status"] != "NCCD_2018_INVARIANT")
    if mask.any():
        df.loc[mask, "operational_definition_complement"] = prose
        n += 1

df.to_csv(BASE + "/RCDome_Decoder_53.csv", index=False)
print("added Galluzzi-style complement for", n, "Rodrigues-only entities; saved decoder")
print()
for ent in ["Apoptosis", "Autophagy", "Cuproptosis", "Necrosis"]:
    r = df[df["rcd_form"] == ent].iloc[0]
    print(f'  {ent:16s}')
    print(f'    verbatim (invariant): {str(r["operational_definition"])[:70]}')
    print(f'    complement (Galluzzi): {str(r["operational_definition_complement"])[:70]}')
