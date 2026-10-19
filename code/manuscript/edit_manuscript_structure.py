# -*- coding: utf-8 -*-
import sys, docx, shutil, datetime, os
sys.stdout.reconfigure(encoding='utf-8')
p = 'manuscript_V027/RCDome_manuscript_governance_V026.docx'
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
os.makedirs('manuscript_V027/_archive_backups', exist_ok=True)
bak = f'manuscript_V027/_archive_backups/RCDome_manuscript_governance_V026_backup_{ts}.docx'
shutil.copy2(p, bak)
print('backup:', bak)

d = docx.Document(p)
P = d.paragraphs

def find(text, start=0, mode='exact'):
    for i in range(start, len(P)):
        t = P[i].text.strip()
        if mode == 'exact' and t == text:
            return i
        if mode == 'startswith' and t.startswith(text):
            return i
    return -1

# --- #1: surface the small execution core in early Results ---
idx = find('The RCD entity census and operational definitions')
assert idx > 0, 'entity census heading not found'
new1 = ("Read at the level of mechanism, the compendium reveals a remarkably small execution "
        "core: only 469 gene-RCD pairs (4.7% of the mechanistically-involved set) are executors "
        "\u2014 genes that directly pore, cleave, or permeabilize to kill the cell \u2014 while 9,489 "
        "pairs (94.7%) are regulators that promote or inhibit death without executing it "
        "(Figure 3A). Regulated cell death, therefore, is not a collection of lethal machines "
        "but a vast regulatory network built around a small core of executioners.")
P[idx].insert_paragraph_before(new1)
print('#1 OK')

# --- #2a: Phase 2G rationale ---
idx = find('A third, fully independent evidence channel', mode='startswith')
assert idx > 0, '2G body not found'
P[idx].insert_paragraph_before(
    "Phase 2G is reported here out of numerical order because the Consensus channel was added "
    "during manuscript revision, after the Phase 3 benchmark; its placement reflects "
    "implementation order rather than pipeline order.")
print('#2a OK')

# --- #2b: delete orphan heading ---
idx = find('RCD Form Name Normalization')
assert idx > 0, 'orphan heading not found'
P[idx]._element.getparent().remove(P[idx]._element)
print('#2b OK')

# --- #2c: differentiate duplicate accuracy headings ---
i1 = find('Independent Accuracy Assessment')
assert i1 > 0
P[i1].text = 'Independent Accuracy Assessment (Phase 2A/D)'
i2 = find('Independent Accuracy Assessment')
assert i2 > 0
P[i2].text = 'Independent Accuracy Assessment (Phase 2B)'
print('#2c OK')

# --- #2d: heading-level consistency (same document object) ---
idx = find('INTRODUCTION')
if idx >= 0:
    P[idx].style = d.styles['Heading 2']
    print('#2d OK')
else:
    print('#2d WARN: INTRODUCTION not found')

d.save(p)
print('saved:', p)
