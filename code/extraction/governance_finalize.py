"""
governance_finalize.py — recover failed chunks + chunked final theme merge.

After governance_theme_synthesis.py:
  - chunks 116 and 138 FAILED (their ~300 items have no themes)
  - the final one-shot merge of 3,563 themes also failed (too large)

This script:
  1. re-condenses the extractions (same dedupe logic)
  2. re-processes the two failed chunks in 50-item subchunks
  3. merges all themes in ~300-theme batches, then merges the batch results

Run on Zima:
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  nohup python3 -u governance_finalize.py >> governance_finalize.log 2>&1 &
"""
import json, os, time, urllib.request, re, io, sys
from datetime import datetime

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTIONS_FILE = os.path.join(BASE_DIR, 'governance_extraction', 'governance_extractions.json')
THEMES_FILE = os.path.join(BASE_DIR, 'governance_extraction', 'governance_themes.json')
FAILED_CHUNKS = [115, 137]  # 0-indexed -> chunks 116 and 138 in the 1-indexed log

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def call_llm(prompt, max_tokens=2500):
    for attempt in range(3):
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
            body = {"model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens, "temperature": 0, "response_format": {"type": "json_object"}}
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req, timeout=120).read().decode('utf-8'))
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

SYNTH = ("Identify recurring AI-governance themes from the extracted items below. "
         "Merge near-duplicates. Output ONLY a JSON array, no markdown fences:\n"
         "[{\"theme\": \"short name\", \"description\": \"1-2 sentences grounded only in the items\", "
         "\"supporting_pmids\": [\"...\"]}]\n\nITEMS:\n")

MERGE = ("Merge these theme lists into one deduplicated set. Keep only themes grounded in the items. "
         "Output ONLY a JSON array, no markdown fences.\n\nTHEMES:\n")

def main():
    if not DEEPSEEK_KEY:
        log("ERROR: DEEPSEEK_KEY not set"); return

    # ---- 1. re-condense + recover failed chunks ----
    ext = json.load(open(EXTRACTIONS_FILE, encoding='utf-8'))
    seen = {}
    for e in ext:
        cat = e.get('category', '')
        item = (e.get('item') or '').strip()
        if not item:
            continue
        k = (cat, item.lower())
        if k not in seen:
            seen[k] = {'category': cat, 'item': item, 'pmids': set()}
        if e.get('pmid'):
            seen[k]['pmids'].add(e['pmid'])
    condensed = [{'category': v['category'], 'item': v['item'],
                  'pmids': sorted(v['pmids'])[:5]} for v in seen.values()]
    log(f"condensed: {len(condensed)}")

    recovered = []
    for idx in FAILED_CHUNKS:
        ch = condensed[idx * 150:(idx + 1) * 150]
        log(f"recovering chunk {idx + 1}: {len(ch)} items")
        for i in range(0, len(ch), 50):
            sub = ch[i:i + 50]
            out = call_llm(SYNTH + json.dumps(sub, ensure_ascii=False), max_tokens=1500)
            arr = safe_json(out)
            if isinstance(arr, list) and arr:
                recovered.extend(arr)
                log(f"  subchunk {i//50 + 1}: {len(arr)} themes")
            else:
                # retry 25 items
                out2 = call_llm(SYNTH + json.dumps(sub[:25], ensure_ascii=False), max_tokens=1500)
                arr2 = safe_json(out2)
                if isinstance(arr2, list):
                    recovered.extend(arr2)
                    log(f"  subchunk {i//50 + 1}: {len(arr2)} themes (25-item retry)")
                else:
                    log(f"  subchunk {i//50 + 1}: FAILED")
            time.sleep(0.5)
    log(f"recovered themes: {len(recovered)}")

    # ---- 2. load existing + recovered, chunked merge ----
    themes = json.load(open(THEMES_FILE, encoding='utf-8'))
    log(f"existing pre-merge themes: {len(themes)}")
    themes = themes + recovered
    log(f"total to merge: {len(themes)}")

    batch_merged = []
    for i in range(0, len(themes), 300):
        batch = themes[i:i + 300]
        out = call_llm(MERGE + json.dumps(batch, ensure_ascii=False), max_tokens=2000)
        arr = safe_json(out)
        if isinstance(arr, list) and arr:
            batch_merged.extend(arr)
            log(f"  merge batch {i//300 + 1}: {len(arr)} themes")
        else:
            out2 = call_llm(MERGE + json.dumps(batch[:150], ensure_ascii=False), max_tokens=2000)
            arr2 = safe_json(out2)
            if isinstance(arr2, list):
                batch_merged.extend(arr2)
                log(f"  merge batch {i//300 + 1}: {len(arr2)} themes (half-batch retry)")
            else:
                batch_merged.extend(batch)
                log(f"  merge batch {i//300 + 1}: FAILED (kept raw)")
        time.sleep(0.5)
    log(f"post-batch themes: {len(batch_merged)}")

    # ---- 3. final merge of batch results ----
    final = call_llm(MERGE + json.dumps(batch_merged, ensure_ascii=False), max_tokens=3000)
    arr = safe_json(final)
    if isinstance(arr, list):
        json.dump(arr, open(THEMES_FILE, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        log(f"final themes: {len(arr)} -> {THEMES_FILE}")
    else:
        json.dump(batch_merged, open(THEMES_FILE, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        log(f"final merge failed; saved {len(batch_merged)} post-batch themes")
    log("DONE.")

if __name__ == '__main__':
    main()
