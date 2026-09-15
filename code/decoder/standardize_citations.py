"""
Standardize citation style: strip trailing inline "(Author Year)" citations from the
prose so ALL 53 ODs are citation-free in prose (like the NCCD verbatim and Rodrigues).
The citation is already carried uniformly in reference_pmid + reference_citation.
Then regenerate the review worksheet from the updated decoder.
"""
import pandas as pd, re, sys

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder"
df = pd.read_csv(BASE + "/RCDome_Decoder_53.csv")

CITE = re.compile(r"\s*\([^()]*\b(?:18|19|20|21)\d{2}[^()]*\)\.?\s*$")

def strip(v):
    s = str(v)
    return CITE.sub("", s).strip()

for col in ["operational_definition", "operational_definition_complement"]:
    df[col] = df[col].map(lambda x: strip(x) if pd.notna(x) else x)

df.to_csv(BASE + "/RCDome_Decoder_53.csv", index=False)
print("stripped inline citations; saved decoder")
print()

# regenerate the worksheet
import make_review_worksheet  # reruns and saves the worksheet from the updated decoder
print()

# verify consistency: any remaining inline citations in OD prose?
rem = df["operational_definition"].astype(str).str.contains(r"\((?:18|19|20|21)\d{2}\)", regex=True)
print("ODs still with inline citation:", int(rem.sum()), "/53")
print()
for ent in ["Eryptosis", "Floatptosis", "Necroptosis", "Cuproptosis", "Phagoptosis"]:
    r = df[df["rcd_form"] == ent].iloc[0]
    print(f'  {ent:18s} OD: {str(r["operational_definition"])[:70]}')
    print(f'  {"":18s} ref: {str(r["reference_pmid"])[:24]} | {str(r["reference_citation"])[:36]}')
