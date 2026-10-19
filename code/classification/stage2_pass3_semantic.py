# -*- coding: utf-8 -*-
"""Pass 3 (semantic) — re-verify the NOT_SUPPORTED claims by MEANING (paraphrase allowed), not verbatim identity."""
import sys, os, json, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Criação de cartoon representations for RCDome/RCD modulo revisao/verificacao_antihallucination'
OUT = os.path.join(BASE, '_stage2_pass3_semantic.jsonl')
KEY = ''
for line in open('D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_distribution/.Renviron', encoding='utf-8'):
    if line.startswith('DEEPSEEK_API_KEY='):
        KEY = line.split('=', 1)[1].strip().strip('"').strip("'")

pcache = json.load(open(os.path.join(BASE, '_fulltext_full.json'))) if os.path.exists(os.path.join(BASE, '_fulltext_full.json')) else json.load(open(os.path.join(BASE, '_fulltext_cache.json')))
dcache = json.load(open(os.path.join(BASE, '_doi_cache.json')))

stage2 = { (r['entity'], r['sentence']) : r for r in [json.loads(l) for l in open(os.path.join(BASE, '_stage2_results.jsonl'), encoding='utf-8')] }
pass2 = { (r['entity'], r['sentence']) : r for r in [json.loads(l) for l in open(os.path.join(BASE, '_stage2_pass2_results.jsonl'), encoding='utf-8')] }
targets = [(r['entity'], r['sentence'], r['key']) for key, r in stage2.items()
           if (pass2[key]['verdict'] if key in pass2 else r['verdict']) == 'NOT_SUPPORTED']
print(f'NOT_SUPPORTED to re-verify semantically: {len(targets)}')

def source_of(key):
    return pcache.get(key) or dcache.get(key) or ''

def semantic_verdict(claim, text):
    if not KEY or not text:
        return 'UNCERTAIN', ''
    prompt = (f'A claim in a cell-death description states: "{claim}".\n'
              f'Below is the complete text of the cited source. The claim may be paraphrased, not verbatim.\n'
              f'Answer whether the source SUPPORTS the claim\'s meaning (even if wording differs), '
              f'CONTRADICTS it, or is SILENT on it. Answer one of: SUPPORTED, NOT_SUPPORTED, UNCERTAIN. '
              f'Then cite the closest passage if any.\n\n'
              f'SOURCE TEXT:\n{text[:40000]}')
    body = json.dumps({'model':'deepseek-chat','messages':[{'role':'user','content':prompt}],
                       'temperature':0,'max_tokens':400}).encode('utf-8')
    req = urllib.request.Request('https://api.deepseek.com/chat/completions', data=body,
                                 headers={'Content-Type':'application/json','Authorization':f'Bearer {KEY}'})
    for _ in range(3):
        try:
            d = json.loads(urllib.request.urlopen(req, timeout=180).read().decode('utf-8'))
            raw = d['choices'][0]['message']['content'].strip()
            verdict = 'UNCERTAIN'
            for ok in ('NOT_SUPPORTED', 'SUPPORTED', 'UNCERTAIN'):
                if ok in raw.upper():
                    verdict = ok
                    break
            parts = raw.split('\n', 1)
            evidence = parts[1].strip() if len(parts) > 1 else ''
            return verdict, evidence
        except Exception:
            time.sleep(3)
    return 'UNCERTAIN', ''

out = open(OUT, 'w', encoding='utf-8')
from collections import Counter
c = Counter()
n = 0
for entity, sentence, key in targets:
    text = source_of(key)
    v, ev = semantic_verdict(sentence, text) if text else ('UNCERTAIN', '')
    c[v] += 1
    out.write(json.dumps({'entity':entity,'sentence':sentence,'key':key,'verdict':v,'evidence':ev}, ensure_ascii=False)+'\n')
    n += 1
    if n % 50 == 0:
        out.flush()
        print(f'  {n}/{len(targets)}: {dict(c)}', flush=True)
out.close()
print(f'\nsemantic pass complete: {dict(c)}')
