# -*- coding: utf-8 -*-
"""Recompute every Results count from the V026 matrix and compare with the
manuscript's current (stale) numbers. Output: before->after table (md + xlsx)."""
import pandas as pd, io, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = "D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
import os; os.chdir(BASE)

m = pd.read_csv("output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv",
                dtype=str, low_memory=False)

rows = len(m)
pairs = m.drop_duplicates(['gene_symbol','rcd_form_canonical']).shape[0]
genes = m.gene_symbol.nunique()
entities = m.rcd_form_canonical.nunique()
corrob = rows - pairs

role = m.cot_role.value_counts().to_dict()
dirn = m.cot_direction.value_counts().to_dict()
tier = m.evidence_tier.value_counts().to_dict()
role_dir = pd.crosstab(m.cot_role, m.cot_direction)

# manuscript's current (stale) values, quoted by Higor
before = {
 "matrix_rows": 22473,
 "unique_pairs": 21568,
 "unique_genes": 9265,
 "entities": 53,
 "EXECUTOR": 469,
 "REGULATOR": 9489,
 "MARKER": 5,
 "UNCERTAIN": 11605,
 "PROMOTES": 5070,
 "PROTECTS": 4755,
 "UNCLEAR": 11743,
 "T1": 2862, "T2": 5686, "T3": 8213, "T4": 5711,
}
after = {
 "matrix_rows": rows,
 "unique_pairs": pairs,
 "unique_genes": genes,
 "entities": entities,
 "EXECUTOR": int(role.get("EXECUTOR",0)),
 "REGULATOR": int(role.get("REGULATOR",0)),
 "MARKER": int(role.get("MARKER",0)),
 "UNCERTAIN": int(role.get("UNCERTAIN",0)),
 "PROMOTES": int(dirn.get("PROMOTES",0)),
 "PROTECTS": int(dirn.get("PROTECTS",0)),
 "UNCLEAR": int(dirn.get("UNCLEAR",0)),
 "T1": int(tier.get("T1",0)), "T2": int(tier.get("T2",0)),
 "T3": int(tier.get("T3",0)), "T4": int(tier.get("T4",0)),
}

rows_out = []
for k in before:
    rows_out.append((k, before[k], after[k], after[k]-before[k]))

df = pd.DataFrame(rows_out, columns=["metric","manuscript(before)","matrix(after)","delta"])
df.to_excel("Expert Nomenclature and Ontological Adjudication Audit/RESULTS_COUNT_RECOMPUTE.xlsx", index=False)

md = io.StringIO()
md.write("# Results count recompute — manuscript vs V026 matrix\n\n")
md.write("| metric | manuscript (before) | matrix (after) | delta |\n|---|---|---|---|\n")
for k,b,a,d in rows_out:
    md.write(f"| {k} | {b:,} | {a:,} | {d:+d} |\n")
md.write(f"\nTier sum (before): {before['T1']+before['T2']+before['T3']+before['T4']:,}\n")
md.write(f"Tier sum (after):  {after['T1']+after['T2']+after['T3']+after['T4']:,}\n")
md.write(f"\nDirection (after) = PROMOTES {after['PROMOTES']:,} + PROTECTS {after['PROTECTS']:,} = {after['PROMOTES']+after['PROTECTS']:,}\n")
md.write(f"Role (after) = EXECUTOR {after['EXECUTOR']:,} + REGULATOR {after['REGULATOR']:,} + MARKER {after['MARKER']:,} + UNCERTAIN {after['UNCERTAIN']:,} = {after['EXECUTOR']+after['REGULATOR']+after['MARKER']+after['UNCERTAIN']:,}\n")
md.write("\n## Role x direction (matrix)\n\n")
md.write("| role | PROMOTES | PROTECTS | UNCLEAR |\n|---|---|---|---|\n")
for r in role_dir.index:
    md.write(f"| {r} | {role_dir.loc[r,'PROMOTES']} | {role_dir.loc[r,'PROTECTS']} | {role_dir.loc[r,'UNCLEAR']} |\n")
io.open("Expert Nomenclature and Ontological Adjudication Audit/RESULTS_COUNT_RECOMPUTE.md","w",encoding="utf-8").write(md.getvalue())

print("saved RESULTS_COUNT_RECOMPUTE.md/.xlsx")
print(df.to_string(index=False))
