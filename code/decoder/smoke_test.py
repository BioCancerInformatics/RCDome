#!/usr/bin/env python3
"""Smoke test — ONE gene-RCD pair, prints the FULL narrative + facts + tokens."""
import os, json, requests, pandas as pd, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT = open(BASE + "/board/RCD_Board_DeepSeek_Prompt.md", encoding="utf-8").read()
m = pd.read_csv(BASE + "/data/unified_gene_rcd_matrix_V026.csv", low_memory=False)
d = pd.read_csv(BASE + "/data/RCDome_Decoder_53.csv")

gene, entity = "GPX4", "Ferroptosis"
mr = m[(m.gene_symbol == gene) & (m.rcd_form_canonical == entity)].iloc[0]
dr = d[d.rcd_form == entity].iloc[0]
key = os.environ.get("DEEPSEEK_KEY", "")

print("=" * 60)
print(f"SMOKE TEST: {gene} - {entity}")
print("=" * 60)
print()
print("--- MATRIX (evidencia) ---")
for c in ["mechanistic_class", "cot_role", "cot_direction", "cot_mechanistic", "pmid_list"]:
    print(f"  {c}: {mr[c]}")
print()
print("--- DECODER (referencia) ---")
for c in ["category", "hard_gate_status", "relationship_type", "parent_entity", "operational_definition"]:
    print(f"  {c}: {dr[c]}")
print()
print("--- CALLING DEEPSEEK (aguarde ~15s) ---", flush=True)

prompt = f"Gene: {gene}\nEntity: {entity}\nMatrix: {mr.to_dict()}\nDecoder: {dr.to_dict()}"
r = requests.post(
    "https://api.deepseek.com/chat/completions",
    headers={"Authorization": "Bearer " + key},
    json={"model": "deepseek-chat", "temperature": 0.7, "seed": 42,
          "messages": [{"role": "system", "content": PROMPT},
                       {"role": "user", "content": prompt}]},
    timeout=120)
data = r.json()
print("HTTP status:", r.status_code)
print()
if "choices" in data:
    narr = data["choices"][0]["message"]["content"]
    print("--- NARRATIVE (a saida do board) ---")
    print(narr)
    print()
    print("--- TOKENS ---")
    print(data.get("usage", {}))
else:
    print("ERRO DA API:")
    print(json.dumps(data, indent=2)[:800])
