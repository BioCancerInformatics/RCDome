#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deepseek_cot_mini_2pairs.py — classify ONLY the 2 V023-only pairs (NLRX1, PPIF).

These 2 pairs were added to V023 AFTER the full DeepSeek v11 run (which used V022),
so their cot_* columns are empty. This mini-run reuses the EXACT same logic
(prompt, verify_role governance loop, 3-vote majority) for just these 2 pairs.

USAGE (on Zima, where DEEPSEEK_KEY is already exported):
    python3 deepseek_cot_mini_2pairs.py

OUTPUT: prints each vote + the final 3-field verdict; writes mini_2pairs_result.json.
"""
import os, json, time, urllib.request
from collections import Counter
from datetime import datetime

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

PAIRS = [
    ("NLRX1", "MPT-driven necrosis"),
]

PROPS = {
    "mechanistic": {"type": "string", "enum": ["YES", "NO"]},
    "role": {"type": "string", "enum": ["EXECUTOR", "REGULATOR", "MARKER", "UNCERTAIN"]},
    "direction": {"type": "string", "enum": ["PROMOTES", "PROTECTS", "UNCLEAR"]},
    "mechanism": {"type": "string"},
    "known_forms": {"type": "string"},
    "role_form": {"type": "string"},
}
REQUIRED = ["mechanistic", "role", "direction", "mechanism", "known_forms", "role_form"]

TOOLS = [
    {"type": "function", "function": {
        "name": "verify_role",
        "description": "Check a preliminary classification against the governance rules",
        "parameters": {"type": "object", "properties": PROPS, "required": REQUIRED}}},
    {"type": "function", "function": {
        "name": "classify_gene_rcd",
        "description": "Submit the final classification",
        "parameters": {"type": "object", "properties": PROPS, "required": REQUIRED}}},
]


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def check_rules(args, form=None):
    role = (args.get('role') or '').upper()
    mech = (args.get('mechanistic') or '').upper()
    direction = (args.get('direction') or '').upper()
    mechanism = (args.get('mechanism') or '').lower()
    known_forms = (args.get('known_forms') or '').lower()
    role_form = (args.get('role_form') or '').lower()
    issues = []
    if role == 'EXECUTOR' and direction != 'PROMOTES':
        issues.append("an EXECUTOR must have direction PROMOTES")
    if role == 'REGULATOR' and direction not in ('PROMOTES', 'PROTECTS'):
        issues.append("a REGULATOR must have direction PROMOTES or PROTECTS")
    if role == 'MARKER' and direction in ('PROMOTES', 'PROTECTS'):
        issues.append("a MARKER should not claim a causal direction")
    if mech == 'NO' and role in ('EXECUTOR', 'REGULATOR', 'MARKER'):
        issues.append("mechanistic NO should not carry a confident role (use UNCERTAIN)")
    if mech == 'YES' and role == 'UNCERTAIN':
        issues.append("mechanistic YES should have a confident role")
    if mech == 'NO' and direction != 'UNCLEAR':
        issues.append("mechanistic NO should have direction UNCLEAR")
    EXEC_WORDS = ('execute', 'execution', 'pore', 'cleav', 'permeabil', 'caspase', 'kinase', 'directly exec',
                  'cytochrome', 'apoptosome', 'release', 'initiat', 'activates the caspase')
    if role == 'REGULATOR' and any(w in mechanism for w in EXEC_WORDS):
        issues.append("your stated mechanism indicates execution, so the role should be EXECUTOR")
    if form and known_forms and mech == 'YES' and known_forms not in ('unknown', 'unclear', 'various', 'not sure'):
        if form.lower() not in known_forms:
            issues.append(f"you stated the gene is known for '{known_forms}', not '{form}' — mark NO/UNCERTAIN")
    VAGUE = ('unknown', 'unclear', 'various', 'not sure', 'multiple', 'cell death', 'general', 'rcd')
    if mech == 'YES':
        if not role_form or any(v in role_form for v in VAGUE):
            issues.append("state the SPECIFIC RCD form this role belongs to")
        elif form and form.lower() not in role_form:
            issues.append(f"this gene's role belongs to '{role_form}', not '{form}' — mark NO/UNCERTAIN")
    return {"status": "consistent"} if not issues else {"status": "inconsistent", "issues": issues}


def call_llm(messages, max_tokens=32000, timeout=900):
    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
            body = {"model": "deepseek-v4-pro", "messages": messages,
                    "max_tokens": max_tokens, "thinking": {"type": "enabled"},
                    "reasoning_effort": "max", "tools": TOOLS}
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8'))
            if 'error' in resp:
                log(f"  API error: {str(resp['error'].get('message',''))[:100]}")
                time.sleep(15 * (attempt + 1))
                continue
            return resp['choices'][0]['message']
        except Exception:
            if attempt == 2:
                return None
            time.sleep(10 * (attempt + 1))
    return None


def run_loop(prompt, form, max_rounds=6):
    messages = [{"role": "user", "content": prompt}]
    for _ in range(max_rounds):
        msg = call_llm(messages)
        if msg is None:
            return {}
        assistant = {"role": "assistant", "content": msg.get('content', '') or '',
                     "reasoning_content": msg.get('reasoning_content', '') or ''}
        tool_calls = msg.get('tool_calls')
        if tool_calls:
            assistant['tool_calls'] = tool_calls
        messages.append(assistant)
        if not tool_calls:
            return {}
        for tc in tool_calls:
            fn = tc['function']['name']
            try:
                args = json.loads(tc['function'].get('arguments') or '{}')
            except Exception:
                args = {}
            if fn == 'classify_gene_rcd':
                return args
            elif fn == 'verify_role':
                messages.append({"role": "tool", "tool_call_id": tc['id'],
                                 "content": json.dumps(check_rules(args, form))})
    return {}


def prompt_loop(gene, form):
    return (f"Gene {gene}, regulated cell death form {form}. "
            f"DEFINITIONS: EXECUTOR = the gene DIRECTLY executes death (pore-forming, cleavage, permeabilization). "
            f"REGULATOR = the gene CONTROLS death (promotes or inhibits it) but does NOT execute it. "
            f"MARKER = associated but not causal. "
            f"In every tool call you MUST also state: (a) mechanism — the gene's molecular action, "
            f"(b) known_forms — which RCD form(s) the gene is primarily known for, and "
            f"(c) role_form — the SINGLE RCD form this gene's role belongs to. "
            f"A gene's role is FORM-SPECIFIC: if the role belongs to a DIFFERENT form, it is NOT involved in this form. "
            f"First call verify_role, then call classify_gene_rcd with your final answer. "
            f"Classify: mechanistic (YES/NO), role (EXECUTOR/REGULATOR/MARKER/UNCERTAIN), "
            f"direction (PROMOTES/PROTECTS/UNCLEAR), mechanism (string), known_forms (string), role_form (string).")


def classify_pair(gene, form, n=5):
    """Run up to n loops, RE-QUEUEING empty votes (like the full run), until n non-empty votes."""
    votes = []
    attempts = 0
    while len(votes) < n and attempts < n + 6:
        attempts += 1
        log(f"  vote {len(votes)+1}/{n} ...")
        v = run_loop(prompt_loop(gene, form), form)
        if v.get('role') or v.get('mechanistic'):
            votes.append(v)
            log(f"  vote {len(votes)}/{n} done")
        else:
            log(f"  empty result — re-queuing (attempt {attempts})")

    def maj(key):
        vals = [v.get(key, '') for v in votes if v.get(key)]
        return Counter(vals).most_common(1)[0][0] if vals else ''

    final = {'role': maj('role'), 'direction': maj('direction'), 'mechanistic': maj('mechanistic')}
    return votes, final


def main():
    if not DEEPSEEK_KEY:
        log("ERROR: DEEPSEEK_KEY not set — export it first."); return

    out = {}
    for gene, form in PAIRS:
        log(f"classifying {gene} | {form} ...")
        votes, final = classify_pair(gene, form, n=5)
        print()
        print(f"===== {gene} | {form} =====")
        for i, v in enumerate(votes, 1):
            print(f"  vote {i}: role={v.get('role','')} direction={v.get('direction','')} "
                  f"mechanistic={v.get('mechanistic','')}")
            print(f"           mechanism={v.get('mechanism','')[:140]!r}")
            print(f"           known_forms={v.get('known_forms','')!r} role_form={v.get('role_form','')!r}")
        print(f"  >>> FINAL: role={final['role']} direction={final['direction']} mechanistic={final['mechanistic']}")
        out[f"{gene}|{form}"] = final

    with open('mini_2pairs_result.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)
    log("saved mini_2pairs_result.json")
    log("to apply: fill cot_role/cot_direction/cot_mechanistic for NLRX1 + PPIF in V023_cot_repaired.csv")


if __name__ == '__main__':
    main()
