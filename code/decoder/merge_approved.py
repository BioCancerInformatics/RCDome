"""
Merge approved two-call review decisions into the FINAL locked RCDome decoder.

Reads definition_review_worksheet.csv (reviewer_decision + reviewer_value),
applies the deterministic merge rules, and writes:
  - RCDome_Decoder_53.csv   (locked decoder)
  - merge_log.csv                 (traceability: every decision applied)

Merge rules:
  APPROVE   -> keep the draft value
  EDIT      -> use reviewer_value
  REJECT    -> mark REJECTED (keeps draft pending re-draft)
  PENDING   -> keep draft, mark PENDING_REVIEW
  INVARIANT -> operational_definition of NCCD_2018_INVARIANT entities is NEVER
               altered; any EDIT/REJECT on it is REFUSED and logged.
  S recompute -> after any C1-C6 edit, S = 0.25C1+0.25C2+0.20C3+0.15C4+0.10C5+0.05C6
"""
import pandas as pd, csv, sys

BASE = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder"
W = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
CCOLS = ["C1", "C2", "C3", "C4", "C5", "C6"]

df = pd.read_csv(BASE + "/RCDome_Decoder_53.csv")
try:
    ws = pd.read_csv(BASE + "/definition_review_worksheet.csv")
except Exception:
    ws = pd.DataFrame(columns=["entity", "field", "reviewer_decision", "reviewer_value"])

log = []
refused = 0

# index worksheet decisions by (entity, field)
decisions = {}
for _, r in ws.iterrows():
    key = (r["entity"], r["field"])
    dec = str(r.get("reviewer_decision", "PENDING")).strip().upper()
    val = r.get("reviewer_value", "")
    decisions[key] = (dec, val)

def apply(entity, field, current):
    """Return (new_value, action) per merge rules."""
    global refused
    dec, val = decisions.get((entity, field), ("PENDING", ""))
    # NCCD invariance guard
    row = df[df["rcd_form"] == entity].iloc[0]
    invariant = (row["galluzzi_nccd_status"] == "NCCD_2018_INVARIANT")
    if invariant and field == "operational_definition" and dec in ("EDIT", "REJECT"):
        log.append({"entity": entity, "field": field, "decision": dec,
                    "action": "REFUSED_INVARIANT", "note": "NCCD verbatim cannot be altered"})
        refused += 1
        return current, "REFUSED_INVARIANT"
    if dec == "APPROVE":
        log.append({"entity": entity, "field": field, "decision": dec,
                    "action": "APPROVED", "note": ""})
        return current, "APPROVED"
    if dec == "EDIT":
        log.append({"entity": entity, "field": field, "decision": dec,
                    "action": "EDITED", "note": f"was: {current}"})
        return val, "EDITED"
    if dec == "REJECT":
        log.append({"entity": entity, "field": field, "decision": dec,
                    "action": "REJECTED", "note": "needs re-draft"})
        return current, "REJECTED"
    # PENDING
    return current, "PENDING"

# apply decisions row-wise to the decoder (all 53 rows)
for i, row in df.iterrows():
    ent = row["rcd_form"]
    for field in ["operational_definition", "key_molecules", "inflammatory", "overlaps",
                  "C1", "C2", "C3", "C4", "C5", "C6", "founding_pmid"]:
        if field in df.columns:
            newval, action = apply(ent, field, row[field])
            df.at[i, field] = newval
    # recompute S from (possibly edited) C1-C6
    c = [float(df.at[i, col]) for col in CCOLS]
    df.at[i, "S"] = round(sum(w * x for w, x in zip(W, c)), 2)

# review status per entity
def review_status(ent):
    rows = [d for d in log if d["entity"] == ent]
    if not rows:
        return "PENDING"
    acts = {d["action"] for d in rows}
    if "REFUSED_INVARIANT" in acts and acts <= {"REFUSED_INVARIANT", "PENDING", "APPROVED"}:
        return "APPROVED" if acts <= {"REFUSED_INVARIANT", "APPROVED"} else "PENDING"
    if "REJECTED" in acts:
        return "REJECTED"
    if "EDITED" in acts or "APPROVED" in acts:
        return "APPROVED" if not any(d["action"] == "PENDING" for d in rows) else "PARTIAL"
    return "PENDING"

df["review_status"] = df["rcd_form"].apply(review_status)

# write outputs
df.to_csv(BASE + "/RCDome_Decoder_53.csv", index=False)
with open(BASE + "/merge_log.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["entity", "field", "decision", "action", "note"])
    w.writeheader()
    w.writerows(log)

print("SAVED RCDome_Decoder_53.csv")
print("SAVED merge_log.csv | decisions logged:", len(log), "| refused (invariant):", refused)
print()
print("review_status distribution:")
print(df["review_status"].value_counts().to_string())
print()
print("S integrity after merge (bitwise vs formula):")
import math
mism = sum(abs(float(df.iloc[i]["S"]) - round(sum(w*float(df.iloc[i][c]) for w,c in zip(W,CCOLS)), 2)) > 0.005 for i in range(len(df)))
print(f"  {len(df)-mism}/{len(df)} match")
