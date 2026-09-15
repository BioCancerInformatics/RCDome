"""
governance_theme_synthesis.py — chunked re-run of the governance theme synthesis.

The original one-shot synthesis failed because all 27,852 extractions were
packed into a single prompt (~700K tokens > 128K context). This version:
  1. condenses + dedupes items by (category, item)
  2. splits into 150-item chunks
  3. synthesizes themes per chunk
  4. merges the per-chunk theme lists into a final set

Run on Zima (DEEPSEEK_KEY + governance_extractions.json already there):
  export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY .env | cut -d= -f2)
  nohup python3 -u governance_theme_synthesis.py >> governance_theme_synthesis.log 2>&1 &
"""
import json, os, time, urllib.request, re, io, sys
from datetime import datetime

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTIONS_FILE = os.path.join(BASE_DIR, 'governance_extraction', 'governance_extractions.json')
THEMES_FILE = os.path.join(BASE_DIR, 'governance_extraction', 'governance_themes.json')

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

def main():
    if not DEEPSEEK_KEY:
        log("ERROR: DEEPSEEK_KEY not set"); return
    ext = json.load(open(EXTRACTIONS_FILE, encoding='utf-8'))
    log(f"extractions loaded: {len(ext)}")

    # condense + dedupe by (category, item)
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
    log(f"condensed unique items: {len(condensed)}")

    CHUNK = 150
    chunks = [condensed[i:i + CHUNK] for i in range(0, len(condensed), CHUNK)]
    log(f"chunks: {len(chunks)}")

    SYNTH = ("Identify recurring AI-governance themes from the extracted items below. "
             "Merge near-duplicates. A theme must derive ONLY from the items. Do not rank. "
             "Output ONLY a JSON array, no markdown fences:\n"
             "[{\"theme\": \"short name\", \"description\": \"1-2 sentences grounded only in the items\", "
             "\"supporting_pmids\": [\"...\"]}]\n\nITEMS:\n")

    all_themes = []
    for ci, ch in enumerate(chunks):
        prompt = SYNTH + json.dumps(ch, ensure_ascii=False)
        out = call_llm(prompt, max_tokens=2000)
        arr = safe_json(out)
        if isinstance(arr, list) and arr:
            all_themes.extend(arr)
            log(f"  chunk {ci+1}/{len(chunks)}: {len(arr)} themes")
        else:
            # retry with the first half of the chunk
            half = ch[:max(1, len(ch) // 2)]
            out2 = call_llm(SYNTH + json.dumps(half, ensure_ascii=False), max_tokens=2000)
            arr2 = safe_json(out2)
            if isinstance(arr2, list):
                all_themes.extend(arr2)
                log(f"  chunk {ci+1}/{len(chunks)}: {len(arr2)} themes (half-chunk retry)")
            else:
                log(f"  chunk {ci+1}/{len(chunks)}: FAILED")
        time.sleep(0.5)

    log(f"pre-merge themes: {len(all_themes)}")

    # final merge of per-chunk theme lists
    MERGE = ("Merge these theme lists into one deduplicated set. Keep only themes grounded "
             "in the items. Output ONLY a JSON array, no markdown fences.\n\nTHEMES:\n")
    out = call_llm(MERGE + json.dumps(all_themes, ensure_ascii=False), max_tokens=3000)
    final = safe_json(out)
    if isinstance(final, list):
        json.dump(final, open(THEMES_FILE, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        log(f"final themes: {len(final)} -> {THEMES_FILE}")
    else:
        json.dump(all_themes, open(THEMES_FILE, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        log(f"merge failed; saved {len(all_themes)} pre-merge themes -> {THEMES_FILE}")
    log("DONE.")

if __name__ == '__main__':
    main()
