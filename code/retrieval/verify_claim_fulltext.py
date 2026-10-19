# -*- coding: utf-8 -*-
"""Programmatic anti-hallucination verification.
Claim -> citation -> reference -> full text (OA XML / green OA / preprint / abstract) -> DeepSeek verdict -> prose log entry.
"""
import sys, os, re, json, urllib.request, urllib.parse, datetime
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Criação de cartoon representations for RCDome/RCD modulo revisao'
LOG = os.path.join(BASE, 'log_validacao_antihallucination.md')

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'RCDome-audit/1.0 (mailto:quique@uenf.br)'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode('utf-8', 'ignore')

def load_refs(entity):
    refs = {}
    path = os.path.join(BASE, 'referencias', entity + '.txt')
    for line in open(path, encoding='utf-8'):
        m = re.search(r'^\[?(\d+)\]?\.?\s', line.strip())
        if not m:
            continue
        num = m.group(1)
        doi = re.search(r'(?:DOI|doi):\s*\**\s*(10\.[^\s*]+)', line)
        pmid = re.search(r'PMID:\s*(\d+)', line)
        pmcid = re.search(r'PMCID:\s*(PMC\d+)', line)
        refs[num] = {
            'doi': doi.group(1).rstrip('.').lower() if doi else '',
            'pmid': pmid.group(1) if pmid else '',
            'pmcid': pmcid.group(1) if pmcid else '',
        }
    return refs

def strip_html(s):
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S|re.I)
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.S|re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s

def retrieve_fulltext(ref):
    """Returns (text, route) for the first successful route."""
    # 1. Europe PMC OA XML
    if ref['pmcid']:
        try:
            xml = fetch(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{ref['pmcid']}/fullTextXML")
            return strip_html(xml), 'europepmc-fulltextxml'
        except Exception:
            pass
    # 2. OpenAlex green OA
    if ref['doi']:
        try:
            d = json.loads(fetch('https://api.openalex.org/works/https://doi.org/' + urllib.parse.quote(ref['doi'])))
            oa_url = (d.get('open_access') or {}).get('oa_url')
            if oa_url:
                # if it is a PMC article page, try the Europe PMC XML with the PMCID from the URL
                m = re.search(r'articles/(PMC\d+)', oa_url)
                if m:
                    try:
                        xml = fetch(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{m.group(1)}/fullTextXML")
                        return strip_html(xml), 'openalex->europepmc-fulltextxml'
                    except Exception:
                        pass
                txt = fetch(oa_url)
                return strip_html(txt), 'openalex-green-oa-html'
        except Exception:
            pass
        # 3. Unpaywall green OA
        try:
            d = json.loads(fetch('https://api.unpaywall.org/v2/' + urllib.parse.quote(ref['doi']) + '?email=quique@uenf.br'))
            loc = d.get('best_oa_location') or {}
            url = loc.get('url_for_pdf') or loc.get('url')
            if url:
                txt = fetch(url)
                return strip_html(txt), 'unpaywall-green-oa'
        except Exception:
            pass
    # 4. Abstract (PubMed)
    if ref['pmid']:
        try:
            txt = fetch(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ref['pmid']}&rettype=abstract&retmode=text")
            return txt, 'pubmed-abstract'
        except Exception:
            pass
    return None, 'no-route'

def deepseek_verdict(claim, text):
    """Ask DeepSeek whether the retrieved text supports the claim."""
    # read key from .Renviron
    key = ''
    renv = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_distribution/.Renviron'
    for line in open(renv, encoding='utf-8'):
        if line.startswith('DEEPSEEK_API_KEY='):
            key = line.split('=', 1)[1].strip().strip('"').strip("'")
    if not key:
        return 'UNCERTAIN (no API key)'
    snippet = text[:6000] if text else '(no full text)'
    prompt = (f"A claim in a cell-death description states: \"{claim}\".\n"
              f"Below is the source text of the cited article.\n"
              f"Answer with exactly one word: SUPPORTED, NOT_SUPPORTED, or UNCERTAIN.\n\n"
              f"SOURCE TEXT:\n{snippet}")
    body = json.dumps({
        'model': 'deepseek-chat',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0,
        'max_tokens': 20,
    }).encode('utf-8')
    req = urllib.request.Request('https://api.deepseek.com/chat/completions', data=body,
                                 headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {key}'})
    try:
        d = json.loads(urllib.request.urlopen(req, timeout=120).read().decode('utf-8'))
        verdict = d['choices'][0]['message']['content'].strip().upper()
        for v in ('SUPPORTED', 'NOT_SUPPORTED', 'UNCERTAIN'):
            if v in verdict:
                return v
        return verdict[:40]
    except Exception as e:
        return f'UNCERTAIN (API error: {e})'

def append_log(entry):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write('\n' + entry + '\n')

def verify_claim(entity, citations, claim):
    refs = load_refs(entity)
    c = citations[0]
    ref = refs.get(c)
    if ref is None:
        entry = (f"The claim \"{claim}\" in {entity}, cited as [{c}], could not be resolved to a "
                 f"reference line; the verdict is UNCERTAIN and the citation should be checked.")
        append_log(entry)
        print('  unresolved citation:', c)
        return
    text, route = retrieve_fulltext(ref)
    verdict = deepseek_verdict(claim, text)
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    entry = (f"[{ts}] The claim \"{claim}\" in {entity}, cited as [{c}] with PMID {ref['pmid']} "
             f"and PMCID {ref['pmcid'] or 'none'}, was resolved through {route}. "
             f"The independent verdict is {verdict}.")
    append_log(entry)
    print(f"  [{c}] PMID {ref['pmid']} PMCID {ref['pmcid'] or '-'} route={route} -> {verdict}")

if __name__ == '__main__':
    # the six detail-level targets from the Ferroptosis assessment
    targets = [
        ('Ferroptosis', ['19'], 'FSP1 is recruited to membranes through N-terminal myristoylation and acts as an NAD(P)H-dependent oxidoreductase'),
        ('Ferroptosis', ['7'], 'RSL3 covalently inhibits the catalytic selenocysteine-containing active site of GPX4'),
        ('Ferroptosis', ['22'], 'NRF2 controls iron homeostasis and ferroptosis through regulators including HERC2 and VAMP8'),
        ('Ferroptosis', ['17'], 'Acetylation of p53 is important for its tumor-suppressive ferroptotic activity'),
        ('Ferroptosis', ['21'], 'DHODH reduces ubiquinone to ubiquinol in the inner mitochondrial membrane'),
        ('Ferroptosis', ['28'], 'NINJ1 oligomerizes to promote plasma-membrane rupture during ferroptosis'),
    ]
    print('Verifying the six detail-level Ferroptosis claims...\n')
    for entity, cites, claim in targets:
        verify_claim(entity, cites, claim)
    print('\nDone. Entries appended to the log.')
