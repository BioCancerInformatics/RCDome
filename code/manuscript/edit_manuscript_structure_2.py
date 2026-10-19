# -*- coding: utf-8 -*-
import sys, docx, shutil, datetime, os
sys.stdout.reconfigure(encoding='utf-8')
p = 'manuscript_V027/RCDome_manuscript_governance_V026.docx'
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
os.makedirs('manuscript_V027/_archive_backups', exist_ok=True)
shutil.copy2(p, f'manuscript_V027/_archive_backups/RCDome_manuscript_governance_V026_backup_{ts}.docx')
print('backup saved')

d = docx.Document(p)
P = d.paragraphs

def find(text, mode='exact'):
    for i, para in enumerate(P):
        t = para.text.strip()
        if mode == 'exact' and t == text:
            return i
        if mode == 'startswith' and t.startswith(text):
            return i
        if mode == 'contains' and text in t:
            return i
    return -1

def set_text(i, new):
    P[i].text = new

# --- #3a: remove redundant 53-entity breakdown from compendium paragraph ---
i = find('The compendium contains 22,473', mode='startswith')
assert i >= 0
old = P[i].text
sentence = " These comprise 19 RCD modalities, 7 subtypes, 2 triggers, 13 functional/contextual categories, and 12 generic/umbrella/taxon concepts (Supplementary Table S3)."
assert sentence in old, 'redundant sentence not found'
set_text(i, old.replace(sentence, ''))
print('#3a OK: redundant 53-entity breakdown removed from compendium paragraph')

# --- #3b: trim duplicate utility passage ---
i = find('The interface is built for extraction as much as for browsing', mode='startswith')
assert i >= 0
set_text(i, ("The interface is built for extraction as much as for browsing: in a single session, "
             "a researcher can filter to a mechanism of interest, download the underlying matrix, "
             "and trace any claim back to its source, with every association PMID resolving to a "
             "verified article title."))
print('#3b OK: duplicate utility passage condensed')

# --- #4: expand Limitations ---
i = find('Two limitations are explicitly acknowledged', mode='startswith')
assert i >= 0
addition = (" Third, the automated classifications rely on LLM calls whose residual error rate "
            "cannot be guaranteed across all 21,568 pairs; we repaired 84 self-inconsistent rows "
            "and retained 231 as explicitly uncertain, but some fraction of the remaining automated "
            "verdicts will be wrong and is open to community correction. Fourth, 442 DATABASE_ONLY "
            "pairs (2.0%) lack any verifiable paper trail in the indexed literature, and 86.3% of "
            "validated rows are not mechanistically confirmed \u2014 limits of the published record "
            "itself rather than of the platform.")
set_text(i, P[i].text + addition)
print('#4 OK: Limitations expanded (LLM residual error + DATABASE_ONLY + non-mechanistic share)')

d.save(p)
print('saved:', p)
