# -*- coding: utf-8 -*-
"""Stage 2 — DeepSeek classification of every covered claim (no-key retrieval + DeepSeek verdict)."""
import sys, os, re, json, urllib.request, urllib.parse, datetime, time
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Criação de cartoon representations for RCDome/RCD modulo revisao'
DESC = os.path.join(BASE, 'descricao RCDs')
REF = os.path.join(BASE, 'referencias')
RESULTS = os.path.join(BASE, '_stage2_results.jsonl')
REPORT = os.path.join(BASE, 'relatorio_validacao_antihallucination.md')

pcache = json.load(open(os.path.join(BASE, '_fulltext_cache.json')))
dcache = json.load(open(os.path.join(BASE, '_doi_cache.json')))

# read DeepSeek key
KEY = ''
for line in open('D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_distribution/.Renviron', encoding='utf-8'):
    if line.startswith('DEEPSEEK_API_KEY='):
        KEY = line.split('=', 1)[1].strip().strip('"').strip("'")

def load_refs(entity):
    refs = {}
    p = os.path.join(REF, entity + '.txt')
    if not os.path.exists(p):
        return refs
    for line in open(p, encoding='utf-8'):
        m = re.search(r'^\[?(\d+)\]?\.?\s+', line.strip())
        if not m:
            continue
        pmid = re.search(r'PMID:\s*(\d+)', line)
        doi = re.search(r'(?:DOI|doi):\s*\**\s*(10\.[^\s*]+)', line)
        refs[m.group(1)] = {'pmid': pmid.group(1) if pmid else '', 'doi': doi.group(1).rstrip('.').lower() if doi else ''}
    return refs

def split_cites(s):
    out = []
    for m in re.finditer(r'\[([0-9,\s\u2013\-]+)\]', s):
        for tok in m.group(1).split(','):
            tok = tok.strip()
            if not tok:
                continue
            rng = re.match(r'^(\d+)\s*[\u2013-]\s*(\d+)$', tok)
            if rng:
                out.extend(str(x) for x in range(int(rng.group(1)), int(rng.group(2)) + 1))
            elif tok.isdigit():
                out.append(tok)
    return sorted(set(out))

def resolve_source(ref):
    if ref['pmid']:
        t = pcache.get(ref['pmid'], '')
        if t.strip():
            return t, ('full' if len(t) >= 2000 else 'abstract'), ref['pmid']
    if ref['doi']:
        t = dcache.get(ref['doi'], '')
        if t.strip():
            return t, ('full' if len(t) >= 2000 else 'abstract'), ref['doi']
    return '', 'none', ''

def deepseek(claim, source):
    if not KEY:
        return 'UNCERTAIN'
    snippet = source[:6000]
    prompt = (f'A claim in a cell-death description states: "{claim}".\n'
              f'Below is the source text of the cited reference.\n'
              f'Answer with exactly one word: SUPPORTED, NOT_SUPPORTED, or UNCERTAIN.\n\n'
              f'SOURCE TEXT:\n{snippet}')
    body = json.dumps({'model': 'deepseek-chat', 'messages': [{'role': 'user', 'content': prompt}],
                       'temperature': 0, 'max_tokens': 20}).encode('utf-8')
    req = urllib.request.Request('https://api.deepseek.com/chat/completions', data=body,
                                 headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {KEY}'})
    for _ in range(3):
        try:
            d = json.loads(urllib.request.urlopen(req, timeout=90).read().decode('utf-8'))
            v = d['choices'][0]['message']['content'].strip().upper()
            for ok in ('SUPPORTED', 'NOT_SUPPORTED', 'UNCERTAIN'):
                if ok in v:
                    return ok
            return v[:30]
        except Exception as e:
            time.sleep(3)
    return 'UNCERTAIN (API error)'

# ---- collect claims ----
claims = []
for fn in sorted(os.listdir(DESC)):
    if not fn.endswith('.txt'):
        continue
    entity = os.path.splitext(fn)[0]
    refs = load_refs(entity)
    text = open(os.path.join(DESC, fn), encoding='utf-8', errors='ignore').read()
    for s in re.split(r'(?<=[.!?])\s+', text):
        cites = split_cites(s)
        if not cites or len(s) <= 30:
            continue
        # resolve the best source among cited refs
        best = ('', 'none', '', '')
        for c in cites:
            if c in refs:
                src, kind, key = resolve_source(refs[c])
                if kind == 'full':
                    best = (src, 'full', key, ','.join(cites)); break
                if kind == 'abstract' and best[1] != 'full':
                    best = (src, 'abstract', key, ','.join(cites))
        claims.append({'entity': entity, 'sentence': s.strip(), 'cites': ','.join(cites),
                       'source': best[0], 'kind': best[1], 'key': best[2]})

print(f'total claims: {len(claims)}')
print(f'  full-text: {sum(1 for c in claims if c["kind"]=="full")}')
print(f'  abstract: {sum(1 for c in claims if c["kind"]=="abstract")}')
print(f'  no-source (UNCERTAIN): {sum(1 for c in claims if c["kind"]=="none")}')

# ---- classify ----
done = set()
if os.path.exists(RESULTS):
    for line in open(RESULTS, encoding='utf-8'):
        r = json.loads(line)
        done.add(r['entity'] + '||' + r['sentence'][:80])

counts = {'SUPPORTED': 0, 'NOT_SUPPORTED': 0, 'UNCERTAIN': 0}
out = open(RESULTS, 'a', encoding='utf-8')
n = 0
for c in claims:
    key = c['entity'] + '||' + c['sentence'][:80]
    if key in done:
        continue
    if c['kind'] == 'none':
        verdict = 'UNCERTAIN'
    else:
        verdict = deepseek(c['sentence'], c['source'])
    if verdict.startswith('SUPPORTED'):
        verdict = 'SUPPORTED'
    elif verdict.startswith('NOT_SUPPORTED'):
        verdict = 'NOT_SUPPORTED'
    else:
        verdict = 'UNCERTAIN'
    counts[verdict] += 1
    out.write(json.dumps({'entity': c['entity'], 'sentence': c['sentence'], 'cites': c['cites'],
                          'kind': c['kind'], 'key': c['key'], 'verdict': verdict}, ensure_ascii=False) + '\n')
    n += 1
    if n % 100 == 0:
        out.flush()
        print(f'  {n} classified... SUPPORTED={counts["SUPPORTED"]} NOT_SUPPORTED={counts["NOT_SUPPORTED"]} UNCERTAIN={counts["UNCERTAIN"]}', flush=True)
out.close()
print('\nclassification complete:', counts)
print(f'results: {RESULTS}')
