"""
governance_merge_v2.py — robust final merge of governance themes.

Why v2: the one-shot and 300-theme-batch merges failed. The 3,623 themes are
mostly exact-name duplicates across chunks. This script:
  1. programmatically dedupes by normalized theme name (no LLM)
  2. LLM-merges the unique themes in 80-theme batches (max_tokens=4000)
  3. final LLM merge of the batch results

Run on Zima:
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  nohup python3 -u governance_merge_v2.py >> governance_merge_v2.log 2>&1 &
"""
import json, os, time, urllib.request, re, io, sys
from datetime import datetime

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
THEMES_FILE = os.path.join(BASE_DIR, 'governance_extraction', 'governance_themes.json')

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

def norm(name):
    return re.sub(r'[^a-z0-9]+', ' ', (name or '').lower()).strip()

MERGE = ("Merge these governance themes into a deduplicated set. Merge themes that mean the same thing. "
         "Output ONLY a JSON array, no markdown fences:\n"
         "[{\"theme\": \"short name\", \"description\": \"1-2 sentences\", \"supporting_pmids\": [\"...\"]}]\n\nTHEMES:\n")

def main():
    if not DEEPSEEK_KEY:
        log("ERROR: DEEPSEEK_KEY not set"); return

    themes = json.load(open(THEMES_FILE, encoding='utf-8'))
    log(f"loaded themes: {len(themes)}")

    # ---- 1. programmatic dedupe by normalized theme name ----
    seen = {}
    for t in themes:
        name = t.get('theme', '') if isinstance(t, dict) else ''
        if not name:
            continue
        key = norm(name)
        if key not in seen:
            seen[key] = {'theme': name,
                         'description': t.get('description', ''),
                         'supporting_pmids': t.get('supporting_pmids', [])}
        else:
            # merge pmids
            cur = seen[key]
            cur['supporting_pmids'] = list(dict.fromkeys(
                (cur.get('supporting_pmids') or []) + (t.get('supporting_pmids') or [])))
    unique = list(seen.values())
    log(f"unique after programmatic dedupe: {len(unique)}")

    # ---- 2. LLM merge in 40-theme batches ----
    BATCH = 40
    batches = [unique[i:i + BATCH] for i in range(0, len(unique), BATCH)]
    log(f"batches: {len(batches)}")

    merged = []
    for bi, batch in enumerate(batches):
        out = call_llm(MERGE + json.dumps(batch, ensure_ascii=False), max_tokens=4000)
        arr = safe_json(out)
        if isinstance(arr, list) and arr:
            merged.extend(arr)
            log(f"  batch {bi+1}/{len(batches)}: {len(arr)} themes")
        else:
            # retry half
            half = batch[:len(batch)//2]
            out2 = call_llm(MERGE + json.dumps(half, ensure_ascii=False), max_tokens=4000)
            arr2 = safe_json(out2)
            if isinstance(arr2, list):
                merged.extend(arr2)
                log(f"  batch {bi+1}/{len(batches)}: {len(arr2)} themes (half retry)")
            else:
                merged.extend(batch)
                log(f"  batch {bi+1}/{len(batches)}: FAILED (kept raw)")
        time.sleep(0.5)
    log(f"post-batch themes: {len(merged)}")

    # ---- 3. final merge ----
    if len(merged) > 500:
        # chunk the final merge too
        final_out = []
        for i in range(0, len(merged), 400):
            sub = merged[i:i + 400]
            out = call_llm(MERGE + json.dumps(sub, ensure_ascii=False), max_tokens=4000)
            arr = safe_json(out)
            if isinstance(arr, list):
                final_out.extend(arr)
            else:
                final_out.extend(sub)
            time.sleep(0.5)
        final = final_out
    else:
        out = call_llm(MERGE + json.dumps(merged, ensure_ascii=False), max_tokens=4000)
        arr = safe_json(out)
        final = arr if isinstance(arr, list) else merged

    json.dump(final, open(THEMES_FILE, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    log(f"final themes: {len(final)} -> {THEMES_FILE}")
    log("DONE.")

if __name__ == '__main__':
    main()
