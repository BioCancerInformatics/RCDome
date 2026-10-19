# -*- coding: utf-8 -*-
import pandas as pd, io, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = "D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
import os; os.chdir(BASE)

dec = pd.read_csv("RCDome Decoder/RCDome_Decoder_53.csv", dtype=str)
m = pd.read_csv("output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv", dtype=str, low_memory=False)

# per-entity mechanistic-gene count (proxy for replication strength)
mech = m.groupby("rcd_form_canonical").agg(
    n_genes=("gene_symbol","nunique"),
    n_mech=("mechanistic_class", lambda s: (s=="MECHANISTIC").sum()),
    n_exec=("cot_role", lambda s: (s=="EXECUTOR").sum()),
).reset_index().rename(columns={"rcd_form_canonical":"rcd_form"})

lv = m.drop_duplicates("rcd_form_canonical")[["rcd_form_canonical","rcdome_level"]].rename(columns={"rcd_form_canonical":"rcd_form"})

d = dec.merge(lv, on="rcd_form", how="left").merge(mech, on="rcd_form", how="left")
d = d.sort_values(["rcdome_level","rcd_form"])

rows = []
for _, r in d.iterrows():
    rows.append({
        "entity": r["rcd_form"],
        "level": r["rcdome_level"],
        "category": r["category"],
        "founding_pmid": r["founding_pmid"],
        "founding_citation": r["reference_citation"],
        "key_molecules": r["key_molecules"],
        "current_maturity": r["evidence_maturity"],
        "mechanistic_genes_proxy": int(r["n_mech"]) if pd.notna(r["n_mech"]) else 0,
        "executor_genes": int(r["n_exec"]) if pd.notna(r["n_exec"]) else 0,
        "total_genes": int(r["n_genes"]) if pd.notna(r["n_genes"]) else 0,
        "replication_verdict (none/limited/multiple)": "",
        "independent_replication_pmids": "",
        "reviewer_notes": "",
    })

out = pd.DataFrame(rows)
out.to_excel("Expert Nomenclature and Ontological Adjudication Audit/G5_REPLICATION_WORKSHEET.xlsx", index=False)

md = io.StringIO()
md.write("# G5 — Independent-replication worksheet (53 entities)\n\n")
md.write("**Verdict standard:** none = only founding paper · limited = 1–2 independent reproductions · multiple = ≥3 independent groups.\n")
md.write("Fill the three open columns; I will then propagate `independent_replication` through decoder/app/Table S11/matrix and verify.\n\n")
md.write("| entity | level | founding PMID | founding citation | key molecules | maturity | mech-genes (proxy) | executors | verdict | independent PMIDs | notes |\n|---|---|---|---|---|---|---|---|---|---|---|\n")
for _, r in out.iterrows():
    md.write(f"| {r['entity']} | {r['level']} | {r['founding_pmid']} | {r['founding_citation']} | {r['key_molecules']} | {r['current_maturity']} | {r['mechanistic_genes_proxy']} | {r['executor_genes']} |  |  |  |\n")
io.open("Expert Nomenclature and Ontological Adjudication Audit/G5_REPLICATION_WORKSHEET.md","w",encoding="utf-8").write(md.getvalue())

print("entities:", len(out))
print("saved xlsx + md")
print("\nL1 entities (16):", len(out[out.level=="L1"]))
