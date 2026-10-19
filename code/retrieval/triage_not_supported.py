# -*- coding: utf-8 -*-
"""Tier 1 — triage the 538 NOT_SUPPORTED claims into ESTABLISHED / SPECIFIC / INTERPRETIVE."""
import sys, os, json, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Criação de cartoon representations for RCDome/RCD modulo revisao/verificacao_antihallucination'
OUT = os.path.join(BASE, '_triage_not_supported.jsonl')

KEY = ''
for line in open('D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_distribution/.Renviron', encoding='utf-8'):
    if line.startswith('DEEPSEEK_API_KEY='):
        KEY = line.split('=', 1)[1].strip().strip('"').strip("'")

stage2 = { (r['entity'], r['sentence']) : r for r in [json.loads(l) for l in open(os.path.join(BASE, '_stage2_results.jsonl'), encoding='utf-8')] }
pass2 = { (r['entity'], r['sentence']) : r for r in [json.loads(l) for l in open(os.path.join(BASE, '_stage2_pass2_results.jsonl'), encoding='utf-8')] }
ns = [(r['entity'], r['sentence']) for key, r in stage2.items()
      if (pass2[key]['verdict'] if key in pass2 else r['verdict']) == 'NOT_SUPPORTED']
print(f'NOT_SUPPORTED to triage: {len(ns)}')

def classify(claim):
    prompt = (f'Classify this single claim from a cell-death description into exactly one category:\n'
              f'ESTABLISHED — a broadly accepted, textbook-level fact citable to a general review;\n'
              f'SPECIFIC — a particular molecular or experimental detail requiring a specific primary source;\n'
              f'INTERPRETIVE — a synthetic or generalizing statement composed by the writer.\n\n'
              f'CLAIM: "{claim}"\n\nAnswer with one word only.')
    body = json.dumps({'model':'deepseek-chat','messages':[{'role':'user','content':prompt}],
                       'temperature':0,'max_tokens':20}).encode('utf-8')
    req = urllib.request.Request('https://api.deepseek.com/chat/completions', data=body,
                                 headers={'Content-Type':'application/json','Authorization':f'Bearer {KEY}'})
    for _ in range(3):
        try:
            d = json.loads(urllib.request.urlopen(req, timeout=90).read().decode('utf-8'))
            v = d['choices'][0]['message']['content'].strip().upper()
            for ok in ('ESTABLISHED','SPECIFIC','INTERPRETIVE'):
                if ok in v:
                    return ok
            return 'UNCLEAR'
        except Exception:
            time.sleep(3)
    return 'UNCLEAR'

done = set()
if os.path.exists(OUT):
    for line in open(OUT, encoding='utf-8'):
        done.add(json.loads(line)['sentence'][:80] + json.loads(line)['entity'])
from collections import Counter
c = Counter()
n = 0
out = open(OUT, 'a', encoding='utf-8')
for entity, sentence in ns:
    if sentence[:80] + entity in done:
        continue
    v = classify(sentence)
    c[v] += 1
    out.write(json.dumps({'entity':entity,'sentence':sentence,'type':v}, ensure_ascii=False) + '\n')
    n += 1
    if n % 50 == 0:
        out.flush()
        print(f'  {n} done: {dict(c)}', flush=True)
out.close()
print(f'\ntriage complete: {dict(c)}')
