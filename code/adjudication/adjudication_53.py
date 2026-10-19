# -*- coding: utf-8 -*-
import pandas as pd, sys, io
sys.stdout.reconfigure(encoding='utf-8')

BASE = "D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
import os
os.chdir(BASE)

dec = pd.read_csv("RCDome Decoder/RCDome_Decoder_53.csv", dtype=str)
m = pd.read_csv("output databases/Phase 2C output/unified_gene_rcd_matrix_V026.csv", dtype=str, low_memory=False)

# gene evidence per entity (to avoid "death signature" overstatement)
ev = m.groupby("rcd_form_canonical").agg(
    n_genes=("gene_symbol", "nunique"),
    n_exec=("cot_role", lambda s: (s == "EXECUTOR").sum()),
    n_mech=("mechanistic_class", lambda s: (s == "MECHANISTIC").sum()),
).reset_index()
ev.columns = ["rcd_form", "n_genes", "n_executor", "n_mechanistic"]

lv = m.drop_duplicates("rcd_form_canonical")[["rcd_form_canonical", "rcdome_level", "rcdome_level_name"]]
lv.columns = ["rcd_form", "level", "level_name"]

d = dec.merge(lv, on="rcd_form", how="left").merge(ev, on="rcd_form", how="left")

GROUP_G = {
    "L1": ["Executioner", "CORE_RCD_FORM", "CORE_PENDING"],
    "L2": ["SUBTYPE", "SYNONYM"],
    "L3": ["Trigger"],
    "L4": ["Functional", "CONTEXTUAL", "CELL_TYPE", "DIFFERENTIATION", "MORPHOLOGY", "CLEARANCE_PROCESS", "INTEGRATED_PROGRAM"],
    "L5": ["CELLULAR_PROCESS", "UMBRELLA", "LEGACY", "TAXON", "EMERGING", "COMPOSITE"],
}
cat2lvl = {c: l for l, cats in GROUP_G.items() for c in cats}

G0 = {"L1": "YES", "L2": "YES", "L3": "NO (initiating event, not death itself)", "L4": "PARTIAL", "L5": "PARTIAL/NO"}
G1 = {"L1": "YES (execution machinery)", "L2": "PARTIAL (inherits parent)", "L3": "NO", "L4": "NO", "L5": "NO"}
G2 = {"L1": "YES", "L2": "PARTIAL", "L3": "NO", "L4": "NO", "L5": "NO"}
G3 = {"L1": "YES", "L2": "YES", "L3": "YES (trigger)", "L4": "YES (phenotype)", "L5": "VARIABLE"}

rows = []
for _, r in d.iterrows():
    ent = r["rcd_form"]; cat = str(r["category"]); lvl = r["level"]
    lvl_name = r["level_name"] if pd.notna(r["level_name"]) else ""
    hard = str(r["hard_gate_status"]); maturity = str(r["evidence_maturity"]); species = str(r["species_scope"])
    rel = str(r["relationship_type"]); repl = str(r["independent_replication"])
    defn = str(r["operational_definition"]); fpmid = str(r["founding_pmid"]); refpmid = str(r["reference_pmid"])
    refcit = str(r["reference_citation"])
    n_g = int(r["n_genes"]) if pd.notna(r["n_genes"]) else 0
    n_exec = int(r["n_executor"]) if pd.notna(r["n_executor"]) else 0
    n_mech = int(r["n_mechanistic"]) if pd.notna(r["n_mechanistic"]) else 0

    # flags
    flags = []
    def_low = defn.lower()
    if "modality" in def_low and hard != "L1-ELIGIBLE":
        flags.append("FORM_MODALITY_CONFLATION")
    # category -> level consistency
    exp = cat2lvl.get(cat)
    if exp and exp != lvl:
        flags.append(f"CATEGORY_LEVEL_MISMATCH({cat}->{exp})")
    if species == "cross_species" and cat in ("TAXON", "CELL_TYPE"):
        flags.append("SPECIES_SCOPE_REVIEW")
    if repl.lower() in ("pending", "no", ""):
        # G5 independent_replication is a GLOBAL deferred field (uniform 'pending' until curated)
        pass
    if maturity.lower() == "supported" and n_g < 50 and n_mech == 0:
        flags.append("MATURITY_REVIEW")
    if maturity.lower() == "established" and n_mech == 0:
        flags.append("MATURITY_REVIEW")

    modality = "bona fide RCD modality" if hard == "L1-ELIGIBLE" else "NOT a modality"
    human = ("HUMAN/ESTABLISHED" if lvl == "L1" else
             ("HUMAN-CONTEXT" if species == "human" else ("NON-HUMAN/TAXON" if cat in ("TAXON","CELL_TYPE") else "MIXED/UNSPECIFIED")))

    action = "KEEP_AS_IS"
    if flags:
        action = "KEEP_BUT_REWORD" if "FORM_MODALITY_CONFLATION" in flags else "KEEP_AND_FLAG"
        if "CATEGORY_LEVEL_MISMATCH" in flags:
            action = "RECLASSIFY_LEVEL"
    status = "FLAGGED" if flags else "STABLE"
    review = "TRUE" if flags else "FALSE"

    # priority
    prio = "D"
    if "FORM_MODALITY_CONFLATION" in flags or "CATEGORY_LEVEL_MISMATCH" in flags or "SPECIES_SCOPE_REVIEW" in flags:
        prio = "A"
    elif "MATURITY_REVIEW" in flags:
        prio = "B"
    # (G5 independent_replication is tracked globally, not per entity)

    rows.append({
        "entity": ent, "level": lvl, "level_name": lvl_name, "category": cat,
        "hard_gate_status": hard, "definition": defn, "definition_source": str(r["operational_definition_source"]),
        "founding_pmid": fpmid, "reference_pmid": refpmid, "reference_citation": refcit,
        "species_scope": species, "evidence_maturity": maturity, "relationship_type": rel,
        "independent_replication": repl, "n_genes": n_g, "n_executor": n_exec, "n_mechanistic": n_mech,
        "G0": G0[lvl], "G1": G1[lvl], "G2": G2[lvl], "G3": G3[lvl],
        "modality_status": modality, "human_RCD_status": human,
        "terminology_flags": "; ".join(flags) if flags else "none",
        "proposed_action": action, "expert_adjudication_status": status,
        "expert_review_required": review, "priority": prio,
    })

out = pd.DataFrame(rows)
out = out.sort_values(["level", "entity"], key=lambda s: s.str.lower() if s.dtype == object else s)

# Save Excel
xlsx_path = "Expert Nomenclature and Ontological Adjudication Audit/ADJUDICATION_53_entities.xlsx"
out.to_excel(xlsx_path, index=False)

# Priority counts
prio = out.priority.value_counts().to_dict()

# Save markdown summary
md = io.StringIO()
md.write("# RCDome 53-Entity Expert Nomenclature and Ontological Adjudication Audit\n\n")
md.write("Provisional, data-driven adjudication (proposal + flag). Read-only. Final biological calls deferred to the human expert.\n\n")
md.write("## Level distribution\n\n")
md.write(f"| Level | Entities |\n|---|---|\n")
for l in ["L1", "L2", "L3", "L4", "L5"]:
    n = (out.level == l).sum()
    md.write(f"| {l} | {n} |\n")
md.write("\n## Priority ranking\n\n")
md.write(f"- **Priority A (deep review):** {(out.priority=='A').sum()} entities\n")
md.write(f"- **Priority B (ontology/terminology review):** {(out.priority=='B').sum()}\n")
md.write(f"- **Priority C (minor):** {(out.priority=='C').sum()}\n")
md.write(f"- **Priority D (stable):** {(out.priority=='D').sum()}\n\n")
md.write("## Flagged entities (Priority A)\n\n")
a = out[out.priority == "A"]
for _, r in a.iterrows():
    md.write(f"- **{r['entity']}** ({r['level']}, {r['category']}): {r['terminology_flags']}\n")
md.write("\n## Global deferred items (not per-entity flags)\n\n")
md.write("- **G5 / independent_replication** — uniform value 'pending' across all 53 entities (deferred until curated; allowed values: none / limited / multiple). Recorded for the 53-entity audit, NOT used as a per-entity flag.\n")
md.write("\n## Full table\n\n")
md.write("See `ADJUDICATION_53_entities.xlsx` (33 columns). Columns: entity, level, level_name, category, hard_gate_status, definition, definition_source, founding_pmid, reference_pmid, reference_citation, species_scope, evidence_maturity, relationship_type, independent_replication, n_genes, n_executor, n_mechanistic, G0, G1, G2, G3, modality_status, human_RCD_status, terminology_flags, proposed_action, expert_adjudication_status, expert_review_required, priority.\n")
io.open("Expert Nomenclature and Ontological Adjudication Audit/ADJUDICATION_53_entities.md", "w", encoding="utf-8").write(md.getvalue())

print("entities:", len(out))
print("priority:", prio)
print("saved:", xlsx_path)
print()
print(out[out.priority.isin(['A'])][['entity','level','category','terminology_flags']].to_string(index=False))
