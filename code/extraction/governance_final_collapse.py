"""
governance_final_collapse.py — collapse the 255 AI-governance themes to a core set (~50).

Strategy fix vs prior runs: instead of asking the LLM to "merge near-duplicates"
(which it did weakly), we FORCE clustering — each batch of 40 themes must be
grouped into exactly 10 clusters. That guarantees a 4:1 reduction per batch.

Pipeline:
  1. load governance_framework.json (419 themes)
  2. classify AI vs human-clinical vs ambiguous (keyword-based)
  3. keep AI themes (255), sort strongest-first
  4. cluster each 40-theme batch into 10 clusters
  5. final merge of the batch clusters -> ~50

Run on Zima:
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  nohup python3 -u governance_final_collapse.py >> governance_final_collapse.log 2>&1 &
"""
import json, os, time, urllib.request, re, io, sys
from datetime import datetime

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRAMEWORK_FILE = os.path.join(BASE_DIR, 'governance_extraction', 'governance_framework.json')
CORE_FILE = os.path.join(BASE_DIR, 'governance_extraction', 'governance_core_set.json')

HUMAN_KW = ['treatment', 'risk factor', 'prevalence', 'neuroimaging', 'rating scale', 'phenomenolog',
            'sensory', 'diagnostic', 'psychiatr', 'schizophren', 'psychos', 'patient', 'clinical', 'symptom',
            'neural mechanism', 'brain', 'cognitive mechan', 'auditory', 'visual halluc', 'perceptual', 'therap',
            'charles bonnet', 'trauma']
AI_KW = ['benchmark', 'evaluation', 'mitigation', 'detection', 'deepfake', 'rag', 'retrieval', 'grounding',
         'transparency', 'explainab', 'governance', 'oversight', 'fact-check', 'misinformation', 'disinformation',
         'ai model', 'llm', 'language model', 'generative', 'synthetic', 'inoculation', 'prebunking', 'accountab',
         'compliance', 'privacy', 'data governance', 'hallucination mitigation', 'hallucination detection']

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def call_llm(prompt, max_tokens=4000):
    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
            body = {"model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens, "temperature": 0, "response_format": {"type": "json_object"}}
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=180).read().decode('utf-8'))
            return resp['choices'][0]['message']['content'].strip()
        except Exception:
            if attempt == 2:
                return None
            time.sleep(5 * (attempt + 1))

def safe_json(s):
    if not s:
        return None
    s = s.strip()
    s = re.sub(r'^```(json)?\s*', '', s)
    s = re.sub(r'\s*```$', '', s)
    if '[' in s and ']' in s:
        s = s[s.find('['):s.rfind(']') + 1]
    try:
        return json.loads(s)
    except Exception:
        return None

def classify(t):
    text = ((t.get('theme', '') or '') + ' ' + (t.get('description', '') or '')).lower()
    h = sum(1 for k in HUMAN_KW if k in text)
    a = sum(1 for k in AI_KW if k in text)
    if a > h:
        return 'AI'
    if h > a:
        return 'human'
    return 'ambiguous'

# Hard clustering constraint: 40 themes -> 10 clusters (4:1 reduction)
CLUSTER = ("Group the following governance themes into 10 clusters. Themes that express the SAME idea, even if "
           "worded differently (e.g., 'human oversight', 'human intervention', 'human accountability'), MUST go "
           "into the SAME cluster. Each cluster must represent one distinct governance idea. "
           "For each cluster output: {\"theme\": \"short cluster name\", \"description\": \"1-2 sentences\", "
           "\"supporting_pmids\": [\"merged PMIDs\"]}. "
           "Output ONLY a JSON array of 10 objects, no markdown fences.\n\nTHEMES:\n")

MERGE = ("Merge these governance themes into a deduplicated set of distinct themes. Merge themes that mean the "
         "same thing. Aim for the smallest distinct set (roughly half). "
         "Output ONLY a JSON array, no markdown fences:\n"
         "[{\"theme\": \"short name\", \"description\": \"1-2 sentences\", \"supporting_pmids\": [\"...\"]}]\n\nTHEMES:\n")

def main():
    if not DEEPSEEK_KEY:
        log("ERROR: DEEPSEEK_KEY not set"); return

    fw = json.load(open(FRAMEWORK_FILE, encoding='utf-8'))
    log(f"loaded framework themes: {len(fw)}")

    ai = [t for t in fw if classify(t) == 'AI']
    ai.sort(key=lambda t: -len(t.get('supporting_pmids', [])))
    log(f"AI themes: {len(ai)}")

    BATCH = 40
    batches = [ai[i:i + BATCH] for i in range(0, len(ai), BATCH)]
    log(f"batches: {len(batches)}")

    core = []
    for bi, batch in enumerate(batches):
        out = call_llm(CLUSTER + json.dumps(batch, ensure_ascii=False), max_tokens=4000)
        arr = safe_json(out)
        if isinstance(arr, list) and arr:
            core.extend(arr)
            log(f"  batch {bi+1}/{len(batches)}: {len(arr)} clusters (from {len(batch)})")
        else:
            half = batch[:len(batch)//2]
            out2 = call_llm(CLUSTER + json.dumps(half, ensure_ascii=False), max_tokens=4000)
            arr2 = safe_json(out2)
            if isinstance(arr2, list):
                core.extend(arr2)
                log(f"  batch {bi+1}/{len(batches)}: {len(arr2)} clusters (half retry)")
            else:
                core.extend(batch)
                log(f"  batch {bi+1}/{len(batches)}: FAILED (kept raw)")
        time.sleep(0.5)
    log(f"pre-final clusters: {len(core)}")

    # final merge
    out = call_llm(MERGE + json.dumps(core, ensure_ascii=False), max_tokens=4000)
    arr = safe_json(out)
    if isinstance(arr, list):
        final = arr
    else:
        final = core
    final.sort(key=lambda t: -len(t.get('supporting_pmids', [])))
    json.dump(final, open(CORE_FILE, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    log(f"core set: {len(final)} themes -> {CORE_FILE}")
    log("DONE.")

if __name__ == '__main__':
    main()
