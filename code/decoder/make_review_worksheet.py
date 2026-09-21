"""
Generate the traceable two-call review worksheet for the RCDome definitions.

Every DRAFT field carries its provenance (source + reference) so that each human
decision (approve/edit/reject) is verifiable by traceability source.
Output: definition_review_worksheet.csv
"""
import pandas as pd, csv, sys

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder"
df = pd.read_csv(BASE + "/RCDome_Decoder_53.csv")

# provenance for each field, given an entity's status + founding PMID
def prov_opdef(r):
    st = r["definition_status"]
    if st == "DEFINED_RODRIGUES":
        if r["galluzzi_nccd_status"] == "NCCD_2018_INVARIANT":
            return "NCCD Box1 verbatim (INVARIANT) + Rodrigues S1A (complement)", "PMID 29362479"
        return "Rodrigues S1A (complement)", "Dataset S1_Rodrigues et al 2025.xlsx"
    if st in ("DRAFT_SOLID", "DRAFT_CANDIDATE"):
        return "founding-paper abstract", f"PMID {r['founding_pmid']}"
    if st == "PRE_PUBMED":
        return "pre-PubMed concept (committee primary source required)", "Stakman 1915"
    return "none (composite)", ""

def prov_molecules(r):
    st = r["definition_status"]
    if st == "DEFINED_RODRIGUES":
        return "RCD_25_Forms_Reference_Table_FINAL.docx", ""
    return "founding-paper abstract", f"PMID {r['founding_pmid']}"

def prov_field(r, field):
    if field in ("RS1", "RS2", "RS3", "RS4", "RS5", "RS6"):
        return "rubric-informed DRAFT (objective inputs + 25 anchors)", "entity_evidence_V025.csv"
    if field == "S":
        return "computed (verified formula 25/25)", "scoring_formulas.py"
    if field == "founding_pmid":
        if r["definition_status"] == "DEFINED_RODRIGUES":
            return "RCD_25_Forms_Reference_Table primary PMID", ""
        return "PubMed esearch (oldest hit)", "founding_pmid_lookup.py"
    if field == "operational_definition":
        s, ref = prov_opdef(r)
        return s, ref
    if field == "key_molecules":
        s, ref = prov_molecules(r)
        return s, ref
    if field in ("inflammatory", "overlaps"):
        if r["definition_status"] == "DEFINED_RODRIGUES":
            return "Rodrigues S1A / Reference Table", ""
        return "founding-paper abstract", f"PMID {r['founding_pmid']}"
    return "", ""

rows = []
FIELDS = ["operational_definition", "key_molecules", "inflammatory", "overlaps",
          "RS1", "RS2", "RS3", "RS4", "RS5", "RS6", "S", "founding_pmid"]
for _, r in df.iterrows():
    if r["definition_status"] == "DEFINED_RODRIGUES":
        continue  # 25 Rodrigues already locked (S1A + Reference Table; NCCD verbatim invariant)
    for f in FIELDS:
        src, ref = prov_field(r, f)
        rows.append({
            "entity": r["rcd_form"],
            "definition_status": r["definition_status"],
            "field": f,
            "draft_value": r[f],
            "provenance_source": src,
            "provenance_ref": ref,
            "reviewer_decision": "PENDING",   # APPROVE / EDIT / REJECT
            "reviewer_value": "",
            "justification": "",
            "crossvalidation_status": "",      # filled by consensus_crossvalidate.py
        })

with open(BASE + "/definition_review_worksheet.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["entity", "definition_status", "field", "draft_value",
                                      "provenance_source", "provenance_ref", "reviewer_decision",
                                      "reviewer_value", "justification", "crossvalidation_status"])
    w.writeheader()
    w.writerows(rows)

print("SAVED definition_review_worksheet.csv | rows:", len(rows))
# count reviewable entities
ents = {x["entity"] for x in rows}
print("reviewable entities:", len(ents))
