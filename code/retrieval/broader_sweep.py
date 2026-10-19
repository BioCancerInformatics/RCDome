# -*- coding: utf-8 -*-
"""Broader sweep — Semantic Scholar (+ Europe PMC fallback) to find a source for the remaining NOT_SUPPORTED claims."""
import sys, os, re, json, urllib.request, urllib.parse, time
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Criação de cartoon representations for RCDome/RCD modulo revisao/verificacao_antihallucination'
OUT = os.path.join(BASE, '_broader_sweep.jsonl')
KEY = ''
for line in open('D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_distribution/.Renviron', encoding='utf-8'):
    if line.startswith('DEEPSEEK_API_KEY='):
        KEY = line.split('=', 1)[1].strip().strip('"').strip("'")

rean = { (r['entity'], r['sentence']) : r for r in [json.loads(l) for l in open(os.path.join(BASE, '_reanchored.jsonl'), encoding='utf-8')] }
targets = [(r['entity'], r['sentence']) for r in rean.values() if r['verdict'] == 'STILL_UNSUPPORTED']
print(f'claims for broader sweep: {len(targets)}')

STOP = {'that','with','from','this','these','their','were','have','been','through','between','within','which','other','such','also','does','into','while','during','upon','against','whereas','important','importantly','cell','cells','death','mechanism','pathway','rcd','defined','established','form','modality','subtype'}
def key_terms(claim, n=4):
    return sorted(set(w.lower() for w in re.findall(r'[A-Za-z0-9-]{5,}', claim) if w.lower() not in STOP), key=len, reverse=True)[:n]

def ss_search(terms):
    q = ' '.join(terms)
    url = ('https://api.semanticscholar.org/graph/v1/paper/search?'
           + urllib.parse.urlencode({'query': q, 'fields': 'title,externalIds,isOpenAccess,openAccessPdf,abstract', 'limit': 5}))
    try:
        d = json.loads(urllib.request.urlopen(url, timeout=40).read())
        return d.get('data', [])
    except Exception:
        return []

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent':'RCDome-audit/1.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode('utf-8','ignore')

def europepmc_text(doi):
    try:
        d = json.loads(fetch('https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':f'DOI:{doi}','format':'json','pageSize':1,'resultType':'core'})))
        res = d.get('resultList',{}).get('result',[])
        if res and res[0].get('pmcid'):
            xml = fetch(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{res[0]["pmcid"]}/fullTextXML')
            return re.sub(r'<[^>]+>',' ', re.sub(r'<script.*?</script>',' ',xml,flags=re.S|re.I)).strip()
    except Exception:
        pass
    return ''

def verify_semantic(claim, text):
    if not KEY or not text:
        return 'UNCERTAIN'
    prompt = (f'A claim states: "{claim}". Below is a candidate source. The claim may be paraphrased. '
              f'Does the source SUPPORT the claim\'s meaning, CONTRADICT it, or is it SILENT? '
              f'Answer one of: SUPPORTED, NOT_SUPPORTED, UNCERTAIN.\n\nSOURCE TEXT:\n{text[:20000]}')
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
    verdict = 'STILL_UNSUPPORTED'
    source = ''
    for paper in ss_search(terms):
        doi = (paper.get('externalIds') or {}).get('DOI') or ''
        text = europepmc_text(doi) if doi else ''
        if not text:
            text = paper.get('abstract') or ''
        if text:
            v = verify_semantic(sentence, text)
            if v == 'SUPPORTED':
                verdict = 'RE_ANCHORED'
                source = doi or paper.get('title','')[:60]
                break
    c[verdict] += 1
    out.write(json.dumps({'entity':entity,'sentence':sentence,'verdict':verdict,'source':source}, ensure_ascii=False)+'\n')
    n += 1
    if n % 20 == 0:
        out.flush()
        print(f'  {n}/{len(targets)}: {dict(c)}', flush=True)
    time.sleep(1.2)  # Semantic Scholar rate limit
out.close()
print(f'\nbroader sweep complete: {dict(c)}')
