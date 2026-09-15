"""
extract_governance_literature.py — DEEP RAG over the AI-video governance literature.

Deep RAG, matching the Phase 2B architecture (channel_c_deep_xml_rag.py):

  1. SEARCH    — Europe PMC queries over the governance topic (not a fixed 14).
  2. SNOWBALL  — expand via each paper's references + citations until saturation (capped).
  3. RETRIEVE  — full-text XML via NCBI efetch (db=pmc), abstract fallback for non-OA.
  4. EXTRACT   — combined-pass DeepSeek (deepseek-chat, temperature 0) with VERBATIM
                 anchoring: governance_principles / hallucination_control / benchmark_methods.
  5. SYNTHESIZE — recurring themes across the corpus, grounded and unranked.

Resume-safe: corpus.json (built once) + governance_progress.json (per paper).

Usage:
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  nohup python3 -u extract_governance_literature.py >> extract_governance_literature.log 2>&1 &
"""
import csv, os, json, re, time, urllib.request, urllib.parse, io, sys
from datetime import datetime

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

# Seed: 13 verified FULL-TEXT PMIDs (every anchor must be verbatim-anchorable;
# abstract-only papers were replaced by OA full-text equivalents).
SEED_PMIDS = ['42101962', '40910027', '40807833', '41198241', '41708802', '41429451',
              '41747768', '42326391', '41799471', '42000932', '42040517', '42222272',
              '42205634', '41969862']

# Deep-search queries over the governance topic.
# Narrow, governance-centered queries: every query requires a core term
# (hallucination / governance / fidelity / faithfulness) so the harvest stays
# on-topic and never explodes into broad 'video' or 'AI' hits.
SEARCH_QUERIES = [
    'hallucination AND (governance OR mitigation OR control OR detection)',
    'hallucination AND (benchmark OR evaluation) AND (video OR image OR multimodal OR vision)',
    'hallucination AND (faithfulness OR fidelity) AND (generative OR video OR image)',
    'governance AND (generative AI OR synthetic media OR deepfake) AND (risk OR ethics OR framework)',
    'deepfake AND (detection OR watermarking) AND (hallucination OR governance)',
    '(human oversight OR human-in-the-loop) AND (generative AI OR large language model) AND (hallucination OR verification)',
    'text-to-video AND (hallucination OR faithfulness)',
    'retrieval-augmented AND (faithful OR hallucination) AND citation',
]

MAX_PAPERS = 1500         # corpus cap (theme saturation reached well before this)
SNOWBALL_PER_PAPER = 30   # references+citations fetched per snowballed paper
PILOT_MODE = False         # False = full run (narrow search + snowball + corpus + themes)
THROTTLE = 0.3             # delay (s) between Europe PMC calls (rate-limit friendly)

# Topic relevance keywords (NARROW): a snowballed candidate is added only if its
# title matches one of these. Broad terms (video, image, AI, generative, etc.) were
# removed because they matched thousands of off-topic papers and hit the ceiling.
TOPIC_KEYWORDS = ['hallucination', 'hallucinations', 'governance', 'governing',
                  'fidelity', 'faithful', 'faithfulness', 'safeguard', 'safeguards',
                  'deepfake', 'deepfakes', 'synthetic media', 'oversight',
                  'human-in-the-loop', 'misinformation', 'authenticity', 'watermarking',
                  'text-to-video', 'text-to-image']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'governance_extraction')
# PILOT writes to pilot_* files so it NEVER overwrites the overnight results.
PFX = 'pilot_' if PILOT_MODE else ''
CORPUS_FILE = os.path.join(OUTPUT_DIR, PFX + 'corpus.json')
PROGRESS_FILE = os.path.join(OUTPUT_DIR, PFX + 'governance_progress.json')
EXTRACTIONS_FILE = os.path.join(OUTPUT_DIR, PFX + 'governance_extractions.json')
THEMES_FILE = os.path.join(OUTPUT_DIR, PFX + 'governance_themes.json')

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

# ---------------- DEEPSEEK ----------------
def call_llm(prompt, max_tokens=1600):
    time.sleep(0.5)
    headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
    body = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens, "temperature": 0}
    for attempt in range(3):
        try:
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=90).read().decode('utf-8'))
            return resp['choices'][0]['message']['content'].strip()
        except Exception:
            if attempt == 2:
                return None
            time.sleep(10 * (attempt + 1))

def safe_json_loads(s):
    if not s:
        return None
    s = s.strip()
    s = re.sub(r'^```(json)?\s*', '', s)
    s = re.sub(r'\s*```$', '', s)
    s = s[s.find('['):s.rfind(']') + 1] if '[' in s and ']' in s else s
    try:
        return json.loads(s)
    except Exception:
        return None

# ---------------- EUROPE PMC: SEARCH + SNOWBALL ----------------
def epmc_search(query, page_size=50):
    """Return list of PMIDs for a query."""
    time.sleep(THROTTLE)
    url = ('https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='
           + urllib.parse.quote(query) + f'&format=json&pageSize={page_size}&resultType=lite')
    try:
        data = json.loads(urllib.request.urlopen(url, timeout=30).read().decode('utf-8'))
        return [r.get('pmid') for r in data.get('resultList', {}).get('result', []) if r.get('pmid')]
    except Exception:
        return []

def get_titles(pmids):
    """Batch title lookup via NCBI esummary. Returns {pmid: title}."""
    if not pmids:
        return {}
    out = {}
    for i in range(0, len(pmids), 200):
        batch = pmids[i:i + 200]
        url = ('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id='
               + ','.join(batch))
        try:
            d = json.loads(urllib.request.urlopen(url, timeout=30).read().decode('utf-8'))
            for p in batch:
                r = d.get('result', {}).get(p, {})
                if r:
                    out[p] = r.get('title', '')
        except Exception:
            pass
    return out

def filter_relevant(pmids):
    """Keep only papers whose title matches the governance topic keywords."""
    titles = get_titles(pmids)
    keep = []
    for p in pmids:
        t = titles.get(p, '').lower()
        if t and any(k in t for k in TOPIC_KEYWORDS):
            keep.append(p)
    return keep

def epmc_linked(pmid, kind, page_size=30):
    """kind = 'references' or 'citations'. Returns list of PMIDs.
    Europe PMC response: referenceList.reference / citationList.citation, field 'id'."""
    time.sleep(THROTTLE)
    url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/MED/{pmid}/{kind}?format=json&pageSize={page_size}'
    key = 'referenceList' if kind == 'references' else 'citationList'
    subkey = 'reference' if kind == 'references' else 'citation'
    try:
        data = json.loads(urllib.request.urlopen(url, timeout=30).read().decode('utf-8'))
        return [r.get('id') for r in data.get(key, {}).get(subkey, []) if r.get('id')]
    except Exception:
        return []

def build_corpus():
    corpus = set(SEED_PMIDS)
    # 1. SEARCH
    for q in SEARCH_QUERIES:
        hits = epmc_search(q)
        before = len(corpus)
        corpus.update(hits)
        log(f"  search '{q[:55]}...': +{len(corpus) - before} (total {len(corpus)})")
        if len(corpus) >= MAX_PAPERS:
            break
    # 2. SNOWBALL until saturation, relevance-filtered: breadth-first over the
    #    citation graph. A candidate is added ONLY if its title matches the topic
    #    keywords (never drifts off-topic). Stops when the frontier is exhausted
    #    (saturation) or the safety ceiling is hit.
    frontier = list(corpus)
    snowballed = set()
    rounds = 0
    while frontier and len(corpus) < MAX_PAPERS:
        rounds += 1
        pmid = frontier.pop(0)
        if pmid in snowballed:
            continue
        snowballed.add(pmid)
        candidates = []
        for kind in ('references', 'citations'):
            candidates.extend(epmc_linked(pmid, kind, SNOWBALL_PER_PAPER))
        for p in filter_relevant([c for c in candidates if c not in corpus]):
            if len(corpus) < MAX_PAPERS:
                corpus.add(p)
                frontier.append(p)
        if rounds % 50 == 0:
            log(f"  snowball: {len(snowballed)} crawled, corpus {len(corpus)}, frontier {len(frontier)}")
    corpus = sorted(corpus)[:MAX_PAPERS]
    log(f"  corpus built: {len(corpus)} papers (snowball crawled {len(snowballed)}, rounds {rounds})")
    return corpus

# ---------------- RETRIEVAL ----------------
def pmid_to_pmcid(pmids):
    """Batch PMID->PMCID via Europe PMC, 100 PMIDs per query (avoids URL length limits)."""
    results = {p: '' for p in pmids}
    for i in range(0, len(pmids), 100):
        batch = pmids[i:i + 100]
        query = ' OR '.join(f'EXT_ID:{p}' for p in batch)
        url = ('https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='
               + urllib.parse.quote(query) + f'&format=json&pageSize={len(batch)}&resultType=core')
        try:
            data = json.loads(urllib.request.urlopen(url, timeout=30).read().decode('utf-8'))
            for r in data.get('resultList', {}).get('result', []):
                pmid = r.get('pmid', '')
                if pmid in results:
                    results[pmid] = r.get('pmcid', '')
        except Exception:
            pass  # one batch fails; keep going
    return results

def fetch_fulltext(pmcid):
    if not pmcid or not pmcid.startswith('PMC'):
        return None
    num = pmcid.replace('PMC', '')
    url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={num}&rettype=xml'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'RCDome/1.0'})
        xml = urllib.request.urlopen(req, timeout=40).read().decode('utf-8')
        m = re.search(r'<body[^>]*>(.*?)</body>', xml, re.DOTALL)
        if m:
            clean = re.sub(r'<[^>]+>', ' ', m.group(1))
            return re.sub(r'\s+', ' ', clean).strip()
    except Exception:
        pass
    return None

def fetch_abstract(pmid):
    url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&rettype=abstract&retmode=text'
    try:
        return urllib.request.urlopen(url, timeout=30).read().decode('utf-8')
    except Exception:
        return None

def chunk_text(text, size=3000):
    return [text[i:i + size] for i in range(0, len(text), size - 300)]

# ---------------- PROMPTS ----------------
EXTRACT_PROMPT = """You extract GOVERNANCE content from a scientific paper about controlling AI hallucination in generated content (text, images, or video).

From the text, extract:
1. governance_principles: explicit rules or principles the paper states for governing AI-generated content.
2. hallucination_control: methods to detect, prevent, or mitigate hallucination.
3. benchmark_methods: evaluation or benchmark approaches used or proposed.

STRICT RULES:
- Every item MUST carry a verbatim_sentence copied character-for-character from the text.
- Do NOT paraphrase, do NOT invent. If no verbatim sentence exists, omit the item.
- relevance_to_rcdome: one short sentence on how it applies to RCDome's evidence-anchored scientific videos.
- Output ONLY a JSON array. No markdown fences, no commentary.

TEXT:
{text}

OUTPUT (JSON array):
[{"category": "governance_principles|hallucination_control|benchmark_methods",
  "item": "short label",
  "verbatim_sentence": "exact sentence from text",
  "relevance_to_rcdome": "..."}]"""

SYNTHESIS_PROMPT = """You synthesize a themed AI-governance framework from governance content extracted across scientific papers.

From the extractions below, identify the RECURRING THEMES (governance principles that appear across papers). Merge near-duplicates.

STRICT RULES:
- A theme must derive ONLY from the extracted items. Do NOT add knowledge from outside the extractions.
- Do NOT invent themes that are not present in the extractions.
- Do NOT rank themes by importance.
- supporting_pmids must be PMIDs actually present in the data.

For each theme provide:
- theme: a short name
- description: a 1-2 sentence synthesis, grounded only in the extracted items
- supporting_pmids: the PMIDs supporting this theme (from the data)

OUTPUT ONLY a JSON array. No markdown fences.

EXTRACTIONS:
{extractions}

OUTPUT (JSON array):
[{"theme": "...", "description": "...", "supporting_pmids": ["..."]}]"""

# ---------------- STATE ----------------
def load_json(path, default):
    if os.path.exists(path):
        try:
            return json.load(open(path, encoding='utf-8'))
        except Exception:
            return default
    return default

def save_json(path, obj):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

# ---------------- MAIN ----------------
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not DEEPSEEK_KEY:
        log("ERROR: DEEPSEEK_KEY not set. Export it from .env and re-run.")
        return

    # Phase 1: corpus
    if PILOT_MODE:
        corpus = list(SEED_PMIDS)
        log(f"PILOT MODE: processing only the {len(corpus)} seeds (no search/snowball)")
    else:
        corpus = load_json(CORPUS_FILE, None)
        if not corpus:
            log("=== BUILDING CORPUS (search + snowball) ===")
            corpus = build_corpus()
            save_json(CORPUS_FILE, corpus)
        else:
            log(f"corpus loaded: {len(corpus)} papers")

    # Phase 2: extract (resume-safe)
    progress = load_json(PROGRESS_FILE, {'done': {}})
    all_extractions = load_json(EXTRACTIONS_FILE, [])
    done_pmids = {e['pmid'] for e in all_extractions}
    pmcid_map = pmid_to_pmcid([p for p in corpus if p not in progress['done']])

    for pmid in corpus:
        if pmid in progress['done'] or pmid in done_pmids:
            continue
        pmcid = pmcid_map.get(pmid, '')
        text = fetch_fulltext(pmcid)
        source = 'fulltext'
        if not text:
            text = fetch_abstract(pmid)
            source = 'abstract'
        if not text:
            progress['done'][pmid] = {'source': 'none', 'n_items': 0}
            save_json(PROGRESS_FILE, progress)
            continue
        items = []
        for ci, chunk in enumerate(chunk_text(text)):
            out = call_llm(EXTRACT_PROMPT.replace('{text}', chunk))
            arr = safe_json_loads(out)
            if isinstance(arr, list):
                items.extend(arr)
        seen, dedup = set(), []
        for e in items:
            v = e.get('verbatim_sentence', '')
            if v and v not in seen:
                seen.add(v)
                e['pmid'] = pmid
                e['source'] = source
                dedup.append(e)
        progress['done'][pmid] = {'source': source, 'n_items': len(dedup)}
        save_json(PROGRESS_FILE, progress)
        all_extractions.extend(dedup)
        save_json(EXTRACTIONS_FILE, all_extractions)
        log(f"PMID {pmid} ({source}): {len(dedup)} items | total {len(all_extractions)}")

    log(f"Total extractions: {len(all_extractions)} -> {EXTRACTIONS_FILE}")

    # Phase 3: synthesize themes (grounded, unranked)
    log("=== SYNTHESIZING THEMES ===")
    condensed = [{'category': e.get('category', ''), 'item': e.get('item', ''), 'pmid': e.get('pmid', '')}
                 for e in all_extractions]
    summary = json.dumps(condensed, ensure_ascii=False)
    themes = call_llm(SYNTHESIS_PROMPT.replace('{extractions}', summary), max_tokens=2500)
    arr = safe_json_loads(themes)
    if isinstance(arr, list):
        save_json(THEMES_FILE, arr)
        log(f"Themed governance: {len(arr)} themes -> {THEMES_FILE}")
    else:
        log("  theme synthesis failed (no valid JSON)")
    log("DONE.")

if __name__ == '__main__':
    main()
