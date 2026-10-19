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
    return -1

# locate the elements
i_heading = find('Phase 2G: Consensus Evidence-Channel Classification')
i_rationale = find('Phase 2G is reported here out of numerical order', mode='startswith')
i_body = find('A third, fully independent evidence channel', mode='startswith')
i_phase3 = find('Phase 3 Benchmark: Elicit Systematic Review Governance Validation')

assert i_heading > 0 and i_rationale > 0 and i_body > 0 and i_phase3 > 0, 'not all found'

heading_el = P[i_heading]._element
rationale_el = P[i_rationale]._element
body_el = P[i_body]._element
phase3_el = P[i_phase3]._element

# 1. delete the workaround rationale
rationale_el.getparent().remove(rationale_el)
print('deleted workaround rationale')

# 2. detach heading + body from their current position
heading_el.getparent().remove(heading_el)
body_el.getparent().remove(body_el)
print('detached 2G heading + body')

# 3. insert before Phase 3 heading (body first, then heading so heading precedes body)
phase3_el.addprevious(body_el)
phase3_el.addprevious(heading_el)
print('inserted 2G before Phase 3')

d.save(p)
print('saved:', p)

# verify the new order
d2 = docx.Document(p)
seq = [para.text.strip()[:60] for para in d2.paragraphs if para.text.strip()]
keys = ['Post-hoc reconciliation repaired 84', 'Phase 2G: Consensus', 'A third, fully independent', 'Phase 3 Benchmark', 'RCDome Platform Architecture']
idxs = []
for k in keys:
    for i, t in enumerate(seq):
        if t.startswith(k):
            idxs.append((k, i))
            break
print('\nnew order check:')
for k, i in sorted(idxs, key=lambda x: x[1]):
    print(f'  {i:3d}  {k}')
print('\nrationale still present:', any('out of numerical order' in t for t in seq))
