# -*- coding: utf-8 -*-
"""Phase 2A/D two-call — CORRECTED: uses the known PMIDs (from pmid_list) for call B,
and a clarified form descriptor so DeepSeek recognizes the entity."""
import json, os, time, urllib.request, sys
sys.stdout.reconfigure(encoding='utf-8')

ENV = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/extraction code snippets/.env'
keys = {}
for line in open(ENV, encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        keys[k.strip()] = v.strip().strip('"').strip("'")
DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY') or keys.get('DEEPSEEK_KEY', '')
NCBI_KEY = os.environ.get('NCBI_KEY') or keys.get('NCBI_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

PAIRS = [
    ('NLRX1', 'MPT-driven necrosis', '41739553'),
    ('PPIF',  'MPT-driven necrosis', '15800627'),
]
FORM_DESC = 'MPT-driven necrosis (necrosis driven by the mitochondrial permeability transition, mPTP)'

def call_llm(prompt, max_tokens=20):
    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
            body = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0}
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=30).read().decode('utf-8'))
            return resp['choices'][0]['message']['content'].strip(), resp['usage']['total_tokens']
        except Exception:
            if attempt == 2: return (None, 0)
            time.sleep(5 * (attempt + 1))

def fetch_pmid_abstract(pmid):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&rettype=abstract&retmode=text&api_key={NCBI_KEY}"
    try:
        return urllib.request.urlopen(url, timeout=30).read().decode('utf-8')[:20000]
    except Exception:
        return ''

def llm_verify(gene, form, pmid):
    time.sleep(0.1)
    prompt_a = f"Is gene {gene} mechanistically involved in {FORM_DESC}? Answer only CONFIRMED or UNCLEAR."
    resp_a, _ = call_llm(prompt_a)
    call_a = resp_a and resp_a.startswith('CONFIRMED')

    abstract = fetch_pmid_abstract(pmid)
    if abstract:
        prompt_b = f"Based on this PubMed abstract, is gene {gene} genuinely involved in {FORM_DESC}? Answer only CONFIRMED or UNCLEAR.\n\nABSTRACT (PMID {pmid}):\n{abstract}"
        resp_b, _ = call_llm(prompt_b, max_tokens=20)
        call_b = resp_b.startswith('CONFIRMED') if resp_b else None
    else:
        call_b = None

    if call_a and call_b: status = 'CONFIRMED'; basis = 'LLM knowledge + PubMed both confirm'
    elif call_a and call_b is False: status = 'NEEDS_LITERATURE'; basis = 'LLM confirms; PubMed does not'
    elif call_a and call_b is None: status = 'CONFIRMED'; basis = 'LLM confirms; no PubMed data'
    elif call_a is False and call_b: status = 'NEEDS_CONTEXT'; basis = 'PubMed confirms; LLM uncertain'
    elif call_a is None and call_b: status = 'CONFIRMED'; basis = 'PubMed confirms'
    elif call_a is False and call_b is False: status = 'UNCLEAR'; basis = 'Neither confirms'
    elif call_a is False and call_b is None: status = 'UNCLEAR'; basis = 'LLM uncertain; no PubMed'
    else: status = 'UNVERIFIED'; basis = 'Both calls failed'

    def cls(s):
        if s == 'CONFIRMED': return 'MECHANISTIC'
        if s == 'NEEDS_LITERATURE': return 'LITERATURE_GAP'
        if s == 'NEEDS_CONTEXT': return 'CONTEXT_GAP'
        return 'INSUFFICIENT_DATA'
    return {'gene': gene, 'llm_status': status, 'llm_basis': basis, 'llm_pmids': pmid,
            'mechanistic_class': cls(status), 'call_a': resp_a, 'call_b': call_b}

results = []
for gene, form, pmid in PAIRS:
    r = llm_verify(gene, form, pmid)
    results.append(r)
    print(f"\n=== {gene} / {form} (PMID {pmid}) ===")
    print(f"  call_a           : {r['call_a']}")
    print(f"  call_b (abstract): {r['call_b']}")
    print(f"  llm_status       : {r['llm_status']}  ({r['llm_basis']})")
    print(f"  mechanistic_class: {r['mechanistic_class']}")

json.dump(results, open('phase2ad_mini_2pairs_result_corrected.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('\nsaved phase2ad_mini_2pairs_result_corrected.json')
