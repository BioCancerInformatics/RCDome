# -*- coding: utf-8 -*-
import sys, docx, shutil, datetime, os, copy
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

# --- Edit 1: add Phase 2C heading before its content ---
i_2c_content = find('Output and Traceability. Phase 2C adds', mode='startswith')
assert i_2c_content > 0, '2C content not found'
# reference heading to copy style/bold from (Phase 2D and 2E)
i_ref = find('Phase 2D and 2E: Extended Literature Validation', mode='startswith')
assert i_ref > 0

new_p = P[i_2c_content].insert_paragraph_before()
new_p.style = P[i_ref].style
run = new_p.add_run('Phase 2C: Full-Text Europe PMC Recovery')
run.bold = True
# mirror the reference heading's bold state on its first run if any
if P[i_ref].runs and P[i_ref].runs[0].bold is not None:
    run.bold = P[i_ref].runs[0].bold
print('#1 OK: Phase 2C heading inserted')

# --- Edit 2: rename the vocabulary-expansion heading ---
i_heading = find('Phase 2 and 3: Expansion, External Audit, and Governance')
assert i_heading > 0, 'expansion heading not found'
P[i_heading].text = 'RCD Form Vocabulary Expansion, External Audit, and Governance'
print('#2 OK: expansion heading renamed')

d.save(p)
print('saved:', p)

# verify
d2 = docx.Document(p)
seq = [q.text.strip() for q in d2.paragraphs if q.text.strip()]
for i, t in enumerate(seq):
    if t.startswith('Phase 2C:') or t.startswith('RCD Form Vocabulary Expansion') or t.startswith('Phase 2D'):
        print(f'  {i:3d}  {t[:60]}')
