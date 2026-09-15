"""
Rewrite the non-NCCD pending ODs in Galluzzi et al. 2018 format:
  "[Term]. [CLASSIFICATION] [initiated by / triggered by / demarcated by / depends on /
   precipitated by / executed by] [mechanism]."
Grounded content is preserved (no new facts); only the FORM is changed.
The 20 NCCD-verbatim entities are untouched (invariant).
"""
import pandas as pd, sys

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder"
df = pd.read_csv(BASE + "/RCDome_Decoder_53.csv")

GALLUZZI = {
    "Ammonia-induced cell death":
        "A contextual cell death modality triggered by ammonia, demarcated by cytoplasmic vacuolation, and detoxified via arginase-mediated urea production with L-glutamine protection.",
    "Aponecrosis":
        "A syncretic cell death variant sharing features of apoptosis and necrosis, triggered by high-dose mitochondrial insult and demarcated by incomplete execution of the apoptotic program, with intracellular ATP as a determinant.",
    "Cornification":
        "A terminal differentiation program of keratinocytes producing the cornified (keratinized) barrier and culminating in a specialized form of programmed cell death.",
    "Eryptosis":
        "A cell-type-specific form of regulated cell death of erythrocytes, demarcated by cell shrinkage, membrane blebbing, calpain activation and phosphatidylserine exposure, and triggered by oxidative stress via prostaglandin E2/Ca2+ and phospholipase A2/ceramide pathways.",
    "Floatptosis":
        "A form of regulated cell death demarcated by cytoplasmic vacuolization with fused-lysosome-associated termination, triggered by Bergeyella cardium infection and inhibited by sodium-channel blockade.",
    "Linker cell-type death":
        "A taxon-specific, caspase-independent (ced-3-independent) non-apoptotic developmental cell death of the Caenorhabditis elegans linker cell, demarcated by nuclear crenellation and organelle swelling, and controlled by let-7 and LIN-29.",
    "Lysoptosis":
        "A lysosome-dependent cell death modality demarcated by lysosomal membrane permeabilization and cathepsin-dependent cytoplasmic proteolysis, executed when serpin inhibition is absent.",
    "Lysozincrosis":
        "A regulated non-apoptotic, lysosomal zinc-dependent cell death modality.",
    "Metalloptosis":
        "An umbrella term for metal-ion-based regulated cell death, encompassing ferroptosis, cuproptosis, lysozincrosis, manganism, calcicoptosis and necrosis by sodium overload.",
    "Mitoxyperilysis":
        "A lytic cell death modality triggered by the synergism of innate-immune and metabolic signals, demarcated by BAX/BAK1/BID-dependent mitochondrial oxidative stress at the plasma membrane and culminating in membrane lysis.",
    "NECSO":
        "A necrotic cell death modality caused by sodium overload, executed via persistent activation of the TRPM4 cation channel by necrocide 1.",
    "Oncosis":
        "An accidental cell death modality demarcated by cell swelling from failure of plasma-membrane ionic pumps, leading to necrosis with karyolysis.",
    "PANoptosis":
        "An integrated inflammatory cell death modality engaging pyroptosis, apoptosis and necroptosis through the RIPK1/RIPK3-FADD-caspase-8 complex, orchestrated by ZBP1 and TAK1.",
    "Phagoptosis":
        "A form of cell death caused by phagocytosis of viable cells, triggered by exposure of 'eat-me' signals or loss of 'don't-eat-me' signals.",
    "Pyronecrosis":
        "A necrosis-like inflammatory cell death of macrophages, executed in a caspase-1-independent manner via ASC and cathepsin B, with release of HMGB1.",
    "Regulated Necrosis":
        "An umbrella term for genetically controlled, non-apoptotic necrotic cell death.",
    "Spectosis":
        "A programmed cell death of erythrocytes in which complement activation initiates (mini)NLRP3-caspase-8 complexes culminating in hemolysis.",
    "Triaptosis":
        "An endosome-dependent cell death modality.",
    "Vacuolar cell death":
        "A cell death modality demarcated by conspicuous cytoplasmic vacuolization, with a hidden non-vacuolar pathway revealed by autophagy-gene disruption.",
    "Hypersensitive response":
        "A taxon-specific programmed cell death of plant cells at infection sites, restricting pathogen spread.",
}

n = 0
for ent, prose in GALLUZZI.items():
    mask = df["rcd_form"] == ent
    if mask.any():
        df.loc[mask, "operational_definition"] = prose
        n += 1

df.to_csv(BASE + "/RCDome_Decoder_53.csv", index=False)
print("rewrote", n, "ODs in Galluzzi format; saved decoder")
print()
# verify: NCCD verbatim untouched (20), and the 20 rewrites present
inv = df[df["galluzzi_nccd_status"] == "NCCD_2018_INVARIANT"]
print("NCCD-invariant entities (verbatim untouched):", len(inv))
print()
for ent in ["Eryptosis", "PANoptosis", "Oncosis", "Necroptosis", "Floatptosis"]:
    r = df[df["rcd_form"] == ent].iloc[0]
    print(f'  {ent:16s} {str(r["operational_definition"])[:85]}')
