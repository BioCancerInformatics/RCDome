"""
governance_collapse.py — final collapse of recurring themes to the core governance set.

Filters to themes supported by >=2 PMIDs (the true "recurring" themes, ~712),
then aggressively LLM-merges near-duplicates into a SMALL distinct set (~50-80).

Run on Zima:
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  nohup python3 -u governance_collapse.py >> governance_collapse.log 2>&1 &
"""
import json, os, time, urllib.request, re, io, sys
from datetime import datetime

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
THEMES_FILE = os.path.join(BASE_DIR, 'governance_extraction', 'governance_themes.json')
FINAL_FILE = os.path.join(BASE_DIR, 'governance_extraction', 'governance_framework.json')

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

COLLAPSE = ("You are consolidating recurring AI-governance themes into a SMALL set of distinct themes. "
            "Merge themes that express the SAME idea even if worded differently (for example, "
            "'Human oversight and accountability', 'Human oversight and intervention', and 'Human oversight and "
            "governance' are ONE theme). Be aggressive: aim for the smallest number of clearly distinct themes, "
            "ideally 40-60. Merge their supporting_pmids. "
            "Output ONLY a JSON array, no markdown fences:\n"
            "[{\"theme\": \"short name\", \"description\": \"1-2 sentences grounded in the items\", "
            "\"supporting_pmids\": [\"...\"]}]\n\nTHEMES:\n")

def main():
    if not DEEPSEEK_KEY:
        log("ERROR: DEEPSEEK_KEY not set"); return

    themes = json.load(open(THEMES_FILE, encoding='utf-8'))
    log(f"loaded themes: {len(themes)}")

    # filter recurring (>=2 supporting PMIDs), sort strongest first
    recurring = [t for t in themes if isinstance(t, dict) and len(t.get('supporting_pmids', [])) >= 2]
    recurring.sort(key=lambda t: -len(t.get('supporting_pmids', [])))
    log(f"recurring themes (>=2 PMIDs): {len(recurring)}")

    BATCH = 80
    batches = [recurring[i:i + BATCH] for i in range(0, len(recurring), BATCH)]
    log(f"batches: {len(batches)}")

    collapsed = []
    for bi, batch in enumerate(batches):
        out = call_llm(COLLAPSE + json.dumps(batch, ensure_ascii=False), max_tokens=4000)
        arr = safe_json(out)
        if isinstance(arr, list) and arr:
            collapsed.extend(arr)
            log(f"  batch {bi+1}/{len(batches)}: {len(arr)} themes (from {len(batch)})")
        else:
            half = batch[:len(batch)//2]
            out2 = call_llm(COLLAPSE + json.dumps(half, ensure_ascii=False), max_tokens=4000)
            arr2 = safe_json(out2)
            if isinstance(arr2, list):
                collapsed.extend(arr2)
                log(f"  batch {bi+1}/{len(batches)}: {len(arr2)} themes (half retry)")
            else:
                collapsed.extend(batch)
                log(f"  batch {bi+1}/{len(batches)}: FAILED (kept raw)")
        time.sleep(0.5)
    log(f"pre-final themes: {len(collapsed)}")

    # final collapse of the batch results
    if len(collapsed) > 300:
        final = []
        for i in range(0, len(collapsed), 300):
            sub = collapsed[i:i + 300]
            out = call_llm(COLLAPSE + json.dumps(sub, ensure_ascii=False), max_tokens=4000)
            arr = safe_json(out)
            if isinstance(arr, list):
                final.extend(arr)
            else:
                final.extend(sub)
            time.sleep(0.5)
    else:
        out = call_llm(COLLAPSE + json.dumps(collapsed, ensure_ascii=False), max_tokens=4000)
        arr = safe_json(out)
        final = arr if isinstance(arr, list) else collapsed

    json.dump(final, open(FINAL_FILE, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    log(f"final themes: {len(final)} -> {FINAL_FILE}")
    log("DONE.")

if __name__ == '__main__':
    main()
