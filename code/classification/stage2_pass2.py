# -*- coding: utf-8 -*-
"""Pass 2 (rigorous) — full source text, evidence-citing verdict. No text cap, no one-word simplification."""
import sys, os, re, json, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Criação de cartoon representations for RCDome/RCD modulo revisao/verificacao_antihallucination'
RESULTS = os.path.join(BASE, '_stage2_results.jsonl')
PASS2 = os.path.join(BASE, '_stage2_pass2_results.jsonl')

pcache = json.load(open(os.path.join(BASE, '_fulltext_cache.json')))
dcache = json.load(open(os.path.join(BASE, '_doi_cache.json')))
KEY = ''
for line in open('D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_distribution/.Renviron', encoding='utf-8'):
    if line.startswith('DEEPSEEK_API_KEY='):
        KEY = line.split('=', 1)[1].strip().strip('"').strip("'")

full_cache = json.load(open(os.path.join(BASE, '_fulltext_full.json'))) if os.path.exists(os.path.join(BASE, '_fulltext_full.json')) else {}
def source_of(key):
    return full_cache.get(key) or pcache.get(key) or dcache.get(key) or ''

def deepseek(claim, text):
    """Returns (verdict, cited_evidence)."""
    if not KEY or not text:
        return 'UNCERTAIN', ''
    prompt = (f'A claim in a cell-death description states: "{claim}".\n'
              f'Below is the complete text of the cited source.\n'
              f'First answer exactly one of: SUPPORTED, NOT_SUPPORTED, or UNCERTAIN.\n'
              f'Then, on the next line, quote verbatim the exact sentence(s) from the source that '
              f'support or contradict the claim. If no sentence does, write NO_SENTENCE.\n\n'
              f'SOURCE TEXT:\n{text}')
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
            # the cited evidence = everything after the verdict word
            parts = re.split(r'(SUPPORTED|NOT_SUPPORTED|UNCERTAIN)', raw, maxsplit=1, flags=re.I)
            evidence = parts[-1].strip() if len(parts) > 1 else ''
            return verdict, evidence
        except Exception:
            time.sleep(3)
    return 'UNCERTAIN', ''

rows = [json.loads(l) for l in open(RESULTS, encoding='utf-8')]
targets = [r for r in rows if r['verdict']=='UNCERTAIN' and r['kind']!='none']
print(f're-verifying {len(targets)} unconfirmed claims (full text, evidence-citing)...')
out = open(PASS2, 'w', encoding='utf-8')
from collections import Counter
c = Counter()
n = 0
for r in targets:
    text = source_of(r['key'])
    verdict, evidence = deepseek(r['sentence'], text) if text else ('UNCERTAIN', '')
    c[verdict] += 1
    out.write(json.dumps({'entity':r['entity'],'sentence':r['sentence'],'cites':r['cites'],
                          'key':r['key'],'verdict':verdict,'evidence':evidence}, ensure_ascii=False) + '\n')
    n += 1
    if n % 50 == 0:
        out.flush()
        print(f'  {n} done: {dict(c)}', flush=True)
out.close()
print(f'\npass 2 complete: {dict(c)}')
