# -*- coding: utf-8 -*-
"""Re-anchoring — for each NOT_SUPPORTED claim, search for a public source that states the specific assertion, then verify semantically."""
import sys, os, re, json, urllib.request, urllib.parse, time
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Criação de cartoon representations for RCDome/RCD modulo revisao/verificacao_antihallucination'
OUT = os.path.join(BASE, '_reanchored.jsonl')
KEY = ''
for line in open('D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_distribution/.Renviron', encoding='utf-8'):
    if line.startswith('DEEPSEEK_API_KEY='):
        KEY = line.split('=', 1)[1].strip().strip('"').strip("'")

stage2 = { (r['entity'], r['sentence']) : r for r in [json.loads(l) for l in open(os.path.join(BASE, '_stage2_results.jsonl'), encoding='utf-8')] }
pass3 = { (r['entity'], r['sentence']) : r for r in [json.loads(l) for l in open(os.path.join(BASE, '_stage2_pass3_semantic.jsonl'), encoding='utf-8')] }
resrc = { (r['entity'], r['sentence']) : r for r in [json.loads(l) for l in open(os.path.join(BASE, '_resourced.jsonl'), encoding='utf-8')] }
# the 428 NOT_SUPPORTED: pass3 NOT_SUPPORTED (215) + resrc STILL_UNSUPPORTED with pmcid (213)
targets = []
for key, r in stage2.items():
    if key in pass3 and pass3[key]['verdict'] == 'NOT_SUPPORTED':
        targets.append((r['entity'], r['sentence']))
    elif key in resrc and resrc[key].get('pmcid') and resrc[key]['verdict'] == 'STILL_UNSUPPORTED':
        targets.append((r['entity'], r['sentence']))
print(f'NOT_SUPPORTED to re-anchor: {len(targets)}')

STOP = {'that','with','from','this','these','their','were','have','been','through','between','within','which','other','such','also','does','into','while','during','upon','against','whereas','important','importantly','cell','cells','death','mechanism','pathway','rcd','defined','established','form','modality','subtype'}
def key_terms(claim, n=4):
    words = [w for w in re.findall(r'[A-Za-z0-9-]{5,}', claim) if w.lower() not in STOP]
    return sorted(set(w.lower() for w in words), key=len, reverse=True)[:n]

def search_open_access(terms):
    if not terms:
        return []
    q = ' AND '.join(terms) + ' AND OPEN_ACCESS:Y'
    url = ('https://www.ebi.ac.uk/europepmc/webservices/rest/search?'
           + urllib.parse.urlencode({'query': q, 'format': 'json', 'pageSize': 3, 'resultType': 'core'}))
    try:
        d = json.loads(urllib.request.urlopen(url, timeout=40).read())
        return [r for r in d.get('resultList', {}).get('result', []) if r.get('pmcid') and r.get('isOpenAccess') == 'Y']
    except Exception:
        return []

def fulltext(pmcid):
    try:
        xml = urllib.request.urlopen(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML', timeout=90).read().decode('utf-8','ignore')
        return re.sub(r'<[^>]+>',' ', re.sub(r'<script.*?</script>',' ',xml,flags=re.S|re.I)).strip()
    except Exception:
        return ''

def verify_semantic(claim, text):
    if not KEY or not text:
        return 'UNCERTAIN'
    prompt = (f'A claim states: "{claim}". Below is the full text of a candidate source. '
              f'The claim may be paraphrased. Does the source SUPPORT the claim\'s meaning, CONTRADICT it, or is it SILENT? '
              f'Answer one of: SUPPORTED, NOT_SUPPORTED, UNCERTAIN.\n\nSOURCE TEXT:\n{text[:30000]}')
    body = json.dumps({'model':'deepseek-chat','messages':[{'role':'user','content':prompt}],
                       'temperature':0,'max_tokens':40}).encode('utf-8')
    req = urllib.request.Request('https://api.deepseek.com/chat/completions', data=body,
                                 headers={'Content-Type':'application/json','Authorization':f'Bearer {KEY}'})
    for _ in range(3):
        try:
            d = json.loads(urllib.request.urlopen(req, timeout=90).read().decode('utf-8'))
            v = d['choices'][0]['message']['content'].strip().upper()
            for ok in ('NOT_SUPPORTED','SUPPORTED','UNCERTAIN'):
                if ok in v:
                    return ok
            return 'UNCERTAIN'
        except Exception:
            time.sleep(3)
    return 'UNCERTAIN'

out = open(OUT, 'w', encoding='utf-8')
from collections import Counter
c = Counter()
n = 0
for entity, sentence in targets:
    terms = key_terms(sentence)
    cands = search_open_access(terms)
    verdict = 'STILL_UNSUPPORTED'
    pmid = ''
    for cand in cands:
        txt = fulltext(cand['pmcid'])
        v = verify_semantic(sentence, txt) if txt else 'UNCERTAIN'
        if v == 'SUPPORTED':
            verdict = 'RE_ANCHORED'
            pmid = cand.get('pmid','')
            break
    c[verdict] += 1
    out.write(json.dumps({'entity':entity,'sentence':sentence,'verdict':verdict,'pmid':pmid}, ensure_ascii=False)+'\n')
    n += 1
    if n % 25 == 0:
        out.flush()
        print(f'  {n}/{len(targets)}: {dict(c)}', flush=True)
out.close()
print(f'\nre-anchoring complete: {dict(c)}')
