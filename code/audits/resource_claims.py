# -*- coding: utf-8 -*-
"""Re-sourcing — for each paywalled-blocked claim, find a public open-access source (PMID/PMCID) that states it, then verify."""
import sys, os, re, json, urllib.request, urllib.parse, time
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Criação de cartoon representations for RCDome/RCD modulo revisao/verificacao_antihallucination'
OUT = os.path.join(BASE, '_resourced.jsonl')
KEY = ''
for line in open('D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_distribution/.Renviron', encoding='utf-8'):
    if line.startswith('DEEPSEEK_API_KEY='):
        KEY = line.split('=', 1)[1].strip().strip('"').strip("'")

TARGETS = ['Pyroptosis','Phagoptosis','Regulated Necrosis','Parthanatos','Pyronecrosis',
           'Senescence and Autophagy in Cancer','Spectosis','Triaptosis','Vacuolar cell death']

stage2 = { (r['entity'], r['sentence']) : r for r in [json.loads(l) for l in open(os.path.join(BASE, '_stage2_results.jsonl'), encoding='utf-8')] }
claims = [r for r in stage2.values() if r['entity'] in TARGETS and r.get('kind')=='none']
print(f'paywalled-blocked claims to re-source: {len(claims)}')

def ask(prompt, max_tokens=80):
    body = json.dumps({'model':'deepseek-chat','messages':[{'role':'user','content':prompt}],
                       'temperature':0,'max_tokens':max_tokens}).encode('utf-8')
    req = urllib.request.Request('https://api.deepseek.com/chat/completions', data=body,
                                 headers={'Content-Type':'application/json','Authorization':f'Bearer {KEY}'})
    for _ in range(3):
        try:
            d = json.loads(urllib.request.urlopen(req, timeout=90).read().decode('utf-8'))
            return d['choices'][0]['message']['content'].strip()
        except Exception:
            time.sleep(3)
    return ''

def suggest_pmid(claim):
    """Search Europe PMC for an open-access paper whose abstract mentions the claim's key terms."""
    words = [w for w in re.findall(r'[A-Za-z0-9-]{5,}', claim)
             if w.lower() not in ('that','with','from','this','these','their','were','have','been','through','between','within','which','other','such','also','does','into','while','during','upon','against','whereas','important','importantly','cell','cells','death','mechanism','pathway','rcd')]
    tokens = sorted(set(w.lower() for w in words), key=len, reverse=True)[:4]
    if not tokens:
        return ''
    q = ' AND '.join(tokens) + ' AND OPEN_ACCESS:Y'
    url = ('https://www.ebi.ac.uk/europepmc/webservices/rest/search?'
           + urllib.parse.urlencode({'query': q, 'format': 'json', 'pageSize': 3, 'resultType': 'core'}))
    try:
        d = json.loads(urllib.request.urlopen(url, timeout=40).read())
        for r in d.get('resultList', {}).get('result', []):
            if r.get('pmcid') and r.get('isOpenAccess') == 'Y':
                return str(r.get('pmid', ''))
    except Exception:
        return ''
    return ''

def has_pmcid(pmid):
    try:
        d = json.loads(urllib.request.urlopen(
            f'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={pmid}&format=json&tool=RCDome&email=quique@uenf.br', timeout=30).read())
        for r in d.get('records', []):
            return r.get('pmcid','')
    except Exception:
        return ''
    return ''

def fulltext(pmcid):
    try:
        xml = urllib.request.urlopen(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML', timeout=90).read().decode('utf-8','ignore')
        return re.sub(r'<[^>]+>',' ', re.sub(r'<script.*?</script>',' ',xml,flags=re.S|re.I)).strip()
    except Exception:
        return ''

def verify(claim, text):
    prompt = (f'A claim states: "{claim}".\nBelow is the full text of a candidate source.\n'
              f'Answer exactly SUPPORTED, NOT_SUPPORTED, or UNCERTAIN, then quote the supporting sentence if any.\n\n'
              f'SOURCE TEXT:\n{text[:8000]}')
    return ask(prompt, max_tokens=400)

n = 0
from collections import Counter
c = Counter()
out = open(OUT, 'a', encoding='utf-8')
for r in claims:
    pmid = suggest_pmid(r['sentence'])
    if not pmid:
        c['NO_PUBLIC_SOURCE'] += 1
        out.write(json.dumps({'entity':r['entity'],'sentence':r['sentence'],'verdict':'STILL_UNSUPPORTED','pmid':''}, ensure_ascii=False)+'\n')
    else:
        pc = has_pmcid(pmid)
        if not pc:
            c['NO_OPEN_ACCESS'] += 1
            out.write(json.dumps({'entity':r['entity'],'sentence':r['sentence'],'verdict':'STILL_UNSUPPORTED','pmid':pmid}, ensure_ascii=False)+'\n')
        else:
            txt = fulltext(pc)
            v = verify(r['sentence'], txt) if txt else 'UNCERTAIN'
            if 'SUPPORTED' in v.upper(): c['RE_ANCHORED'] += 1
            else: c['STILL_UNSUPPORTED'] += 1
            out.write(json.dumps({'entity':r['entity'],'sentence':r['sentence'],'verdict':'RE_ANCHORED' if 'SUPPORTED' in v.upper() else 'STILL_UNSUPPORTED','pmid':pmid,'pmcid':pc,'detail':v[:200]}, ensure_ascii=False)+'\n')
    n += 1
    if n % 10 == 0:
        out.flush()
        print(f'  {n}/{len(claims)}: {dict(c)}', flush=True)
out.close()
print(f'\nre-sourcing complete: {dict(c)}')
