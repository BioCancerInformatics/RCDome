#!/usr/bin/env python3
"""Smoke test — ONE gene-RCD pair. Prints the FINAL production report:
AI synthesis + deterministic audit trail (timing, governance audit, raw payload)."""
import os, json, sys, time
import requests, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_canonical import (scrub_governance_violations, audit_report,
                             audit_negative, build_audit_trail,
                             MATRIX_KEYS, DECODER_KEYS)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT = open(BASE + "/board/RCD_Board_DeepSeek_Prompt.md", encoding="utf-8").read()
m = pd.read_csv(BASE + "/data/unified_gene_rcd_matrix_V026.csv", low_memory=False)
d = pd.read_csv(BASE + "/data/RCDome_Decoder_53.csv")

gene, entity = "GPX4", "Ferroptosis"
mr = m[(m.gene_symbol == gene) & (m.rcd_form_canonical == entity)].iloc[0]
dr = d[d.rcd_form == entity].iloc[0]
key = os.environ.get("DEEPSEEK_KEY", "")

mfields = {k: str(mr[k]) for k in MATRIX_KEYS}
dfields = {k: str(dr[k]) for k in DECODER_KEYS}
prompt = (f"Gene: {gene}\nEntity: {entity}\n"
          f"RCDome database: {mfields}\nRCDome decoder: {dfields}")

print(f"SMOKE TEST: {gene} - {entity} (calling DeepSeek...)", flush=True)
t0 = time.time()
r = requests.post(
    "https://api.deepseek.com/chat/completions",
    headers={"Authorization": "Bearer " + key},
    json={"model": "deepseek-chat", "temperature": 0.7, "seed": 42,
          "messages": [{"role": "system", "content": PROMPT},
                       {"role": "user", "content": prompt}]},
    timeout=180)
latency = time.time() - t0
data = r.json()

if "choices" not in data:
    print("ERRO DA API:")
    print(json.dumps(data, indent=2)[:800])
    sys.exit(1)

raw_narr = data["choices"][0]["message"]["content"]
narr, actions = scrub_governance_violations(raw_narr)
res = audit_report(narr, mr, dr)
final = narr + build_audit_trail(narr, gene, entity, mr, dr, res,
                                 latency=latency, actions=actions)

print()
print(final)
print()
print("--- TOKENS ---")
print(data.get("usage", {}))
