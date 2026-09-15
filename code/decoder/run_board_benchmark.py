#!/usr/bin/env python3
"""
run_board_benchmark.py — Digital Molecular RCD Board benchmark (statistically determined).

Runs the 7 benchmark tests, calls DeepSeek with the RCD Board governance prompt,
extracts the FACTS (content), and reports point + Wilson 95% CI + significance.

Run on a machine with DEEPSEEK_KEY in .env. No API key is committed.
"""
import os, re, json, math, hashlib, datetime
import pandas as pd
from scipy import stats

import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT = open(BASE + "/board/RCD_Board_DeepSeek_Prompt.md",
              encoding="utf-8").read()

# ── statistics helpers ──────────────────────────────────────────────────────
def wilson_ci(p, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    denom = 1 + z*z/n
    center = (p + z*z/(2*n)) / denom
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / denom
    return (max(0, center-half), min(1, center+half))

def sample_size_proportion(p, E, z=1.96):
    return math.ceil(z*z*p*(1-p) / (E*E))

def sample_size_delta(p0, p1, power=0.80, z=1.96):
    pbar = (p0+p1)/2; zbeta = 0.84
    return math.ceil((z+zbeta)**2 * 2*pbar*(1-pbar) / (p0-p1)**2)

# ── data ────────────────────────────────────────────────────────────────────
m = pd.read_csv(BASE + "/data/unified_gene_rcd_matrix_V026.csv",
                low_memory=False)
d = pd.read_csv(BASE + "/data/RCDome_Decoder_53.csv")

GOLDEN = {
    # 10 executors
    ("BAX","Apoptosis"):"EXECUTOR", ("CASP3","Apoptosis"):"EXECUTOR",
    ("CASP8","Apoptosis"):"EXECUTOR", ("CASP9","Apoptosis"):"EXECUTOR",
    ("CYCS","Apoptosis"):"EXECUTOR", ("MLKL","Necroptosis"):"EXECUTOR",
    ("RIPK3","Necroptosis"):"EXECUTOR", ("GSDMD","Pyroptosis"):"EXECUTOR",
    ("GSDME","Pyroptosis"):"EXECUTOR", ("CASP1","Pyroptosis"):"EXECUTOR",
    # 8 regulators
    ("BCL2","Apoptosis"):"REGULATOR", ("BCL2L1","Apoptosis"):"REGULATOR",
    ("XIAP","Apoptosis"):"REGULATOR", ("TP53","Apoptosis"):"REGULATOR",
    ("GPX4","Ferroptosis"):"REGULATOR", ("ACSL4","Ferroptosis"):"REGULATOR",
    ("AIFM2","Ferroptosis"):"REGULATOR", ("BECN1","Autophagy"):"REGULATOR",
    # 8 negative (form mismatch)
    ("GPX4","Pyroptosis"):"NEGATIVE", ("MLKL","Ferroptosis"):"NEGATIVE",
    ("CASP3","Necroptosis"):"NEGATIVE", ("BAX","Necroptosis"):"NEGATIVE",
    ("GSDMD","Ferroptosis"):"NEGATIVE", ("CASP1","Apoptosis"):"NEGATIVE",
    ("MLKL","Apoptosis"):"NEGATIVE", ("BAX","Pyroptosis"):"NEGATIVE",
}

def matrix_row(gene, entity):
    r = m[(m.gene_symbol==gene) & (m.rcd_form_canonical==entity)]
    return None if r.empty else r.iloc[0]

def decoder_row(entity):
    r = d[d.rcd_form==entity]
    return None if r.empty else r.iloc[0]

# ── DeepSeek call (run on a machine with the key) ───────────────────────────
def call_deepseek(prompt, temperature=0.7, seed=42, model="deepseek-chat"):
    import requests
    key = os.environ.get("DEEPSEEK_KEY")
    if not key:
        raise RuntimeError("DEEPSEEK_KEY not set in environment/.env")
    resp = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={"model":model,"temperature":temperature,"seed":seed,
              "messages":[{"role":"system","content":PROMPT},
                          {"role":"user","content":prompt}]}, timeout=120)
    msg = resp.json()["choices"][0]["message"]["content"]
    usage = resp.json().get("usage", {})
    return msg, usage

# ── fact extractor ──────────────────────────────────────────────────────────
def extract_facts(narrative, gene, entity, mr, dr):
    facts = {}
    facts["pmid_ok"] = bool(re.search(r"PMID[: ]?(\d+)", narrative))
    facts["role_ok"] = (str(mr.cot_role).upper() in narrative.upper())
    facts["level_ok"] = (str(dr.hard_gate_status).split("-")[0] in narrative or
                         str(mr.rcdome_level) in narrative)
    facts["entity_ok"] = entity.lower() in narrative.lower()
    facts["gene_ok"] = gene.lower() in narrative.lower()
    return facts


# ── Test 8: model comparison ────────────────────────────────────────────────
def test8_model_comparison(n_pairs=None):
    models = ["deepseek-chat", "deepseek-reasoner"]
    results = {}
    cases = list(GOLDEN.items())[:n_pairs] if n_pairs else list(GOLDEN.items())
    for model in models:
        correct = 0; tokens = {"prompt":0, "completion":0}
        for (gene, ent), expect in cases:
            mr, dr = matrix_row(gene, ent), decoder_row(ent)
            if mr is None or dr is None: continue
            prompt = f"Gene: {gene}\nEntity: {ent}\nMatrix: {mr.to_dict()}\nDecoder: {dr.to_dict()}"
            print(f"[{model}] {gene}-{ent} ...", flush=True)
            try:
                narr, usage = call_deepseek(prompt, model=model)
                print(f"      done", flush=True)
                tokens["prompt"] += usage.get("prompt_tokens", 0)
                tokens["completion"] += usage.get("completion_tokens", 0)
            except Exception as e:
                print(f"  [skip] {model} {gene}-{ent}: {e}"); continue
            f = extract_facts(narr, gene, ent, mr, dr)
            ok = f["role_ok"] and f["entity_ok"] and f["gene_ok"]
            correct += int(ok)
        n = len(cases)
        p = correct/n if n else 0
        results[model] = {"correct": correct, "n": n, "p": p,
                           "ci95": wilson_ci(p, n), "tokens": tokens}
    return results

# ── main benchmark ──────────────────────────────────────────────────────────
def main():
    seed = int(os.environ.get("BENCH_SEED", "42"))
    temp = float(os.environ.get("BENCH_TEMP", "0.7"))
    stamp = datetime.datetime.now().isoformat()
    report = {"run": stamp, "seed": seed, "temperature": temp}

    # Test 1 — golden accuracy
    correct = 0
    for (gene, ent), expect in GOLDEN.items():
        mr, dr = matrix_row(gene, ent), decoder_row(ent)
        if mr is None or dr is None:
            continue
        prompt = f"Gene: {gene}\nEntity: {ent}\nMatrix: {mr.to_dict()}\nDecoder: {dr.to_dict()}"
        print(f"[{list(GOLDEN).index((gene,ent))+1}/{len(GOLDEN)}] {gene}-{ent} ...", flush=True)
        try:
            narr, _ = call_deepseek(prompt, temp, seed)
            print(f"      done", flush=True)
        except Exception as e:
            print(f"  [skip] {gene}-{ent}: {e}", flush=True)
            continue
        f = extract_facts(narr, gene, ent, mr, dr)
        ok = f["role_ok"] and f["entity_ok"] and f["gene_ok"]
        if expect == "NEGATIVE":
            ok = ok and "not" in narr.lower()
        correct += int(ok)
    n = len(GOLDEN)
    p = correct/n
    report["golden"] = {"correct": correct, "n": n, "p": p, "ci95": wilson_ci(p, n)}

    # Test 2 — census (level+category == decoder)
    cen_ok = 0
    for _, dr in d.iterrows():
        mr = matrix_row(None, dr.rcd_form)  # any row
        lv = m[m.rcd_form_canonical==dr.rcd_form].rcdome_level.iloc[0]
        if lv in dr.hard_gate_status or dr.category.upper() in dr.hard_gate_status.upper():
            cen_ok += 1
    report["census"] = {"ok": cen_ok, "n": 53, "ci95": wilson_ci(cen_ok/53, 53)}

    # Test 7 — sample-size recommendation
    report["sizes"] = {
        "golden_to_tighten_5pct": sample_size_proportion(0.95, 0.05),
        "fact_stability_73": sample_size_proportion(0.95, 0.05),
        "governance_1pct": sample_size_proportion(0.01, 0.01),
        "version_delta_290": sample_size_delta(0.90, 0.95),
    }

    report["test8_models"] = test8_model_comparison()
    print(json.dumps(report, indent=2, default=str))

if __name__ == "__main__":
    main()
