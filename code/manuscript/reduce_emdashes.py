# -*- coding: utf-8 -*-
import sys, docx, shutil, datetime, os, re
sys.stdout.reconfigure(encoding='utf-8')
p = 'manuscript_V027/RCDome_manuscript_governance_V026.docx'
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
os.makedirs('manuscript_V027/_archive_backups', exist_ok=True)
shutil.copy2(p, f'manuscript_V027/_archive_backups/RCDome_manuscript_governance_V026_backup_{ts}.docx')
print('backup saved')

EM = '\u2014'  # em-dash
SP = ' ' + EM + ' '  # " — "

# specific overrides: colon where a list/definition follows
specific = [
    ('(i) definition \u2014 ', '(i) definition: '),
    ('(ii) quantified ranking \u2014 ', '(ii) quantified ranking: '),
    ('(iii) provenance \u2014 ', '(iii) provenance: '),
    ('Task 1 \u2014 Gene Symbol Extraction', 'Task 1: Gene Symbol Extraction'),
    ('Task 2 \u2014 RCD Form Detection', 'Task 2: RCD Form Detection'),
    ('Task 3 \u2014 Verbatim Evidence Extraction', 'Task 3: Verbatim Evidence Extraction'),
    ('(i) gene-RCD association validation \u2014 ', '(i) gene-RCD association validation: '),
    ('(ii) RCD modality status validation \u2014 ', '(ii) RCD modality status validation: '),
    ('20 entities \u2014 these 15 plus', '20 entities: these 15 plus'),
    ('criteria were retained \u2014 RS1', 'criteria were retained: RS1'),
    ('complete evaluation architecture \u2014 RCD entity classification', 'complete evaluation architecture: RCD entity classification'),
    ('quality gates \u2014 is summarized', 'quality gates: is summarized'),
    ('three evidence layers: (i) definition \u2014 ', 'three evidence layers: (i) definition: '),
]

d = docx.Document(p)
before = 0
after = 0
changed_paras = []
for pi, para in enumerate(d.paragraphs):
    if EM not in para.text:
        continue
    before += para.text.count(EM)
    for run in para.runs:
        t = run.text
        if not t:
            continue
        new = t
        # specific overrides first
        for old, repl in specific:
            if old in new:
                new = new.replace(old, repl)
        # global comma for the rest
        new = new.replace(SP, ', ')
        if new != t:
            run.text = new
    after += para.text.count(EM)
    if EM in para.text:
        changed_paras.append(pi)

d.save(p)
print(f'em-dash before: {before}')
print(f'em-dash after : {after}')
print(f'paragraphs still containing em-dash: {len(changed_paras)}')
for pi in changed_paras:
    print(f'  still has em-dash: ¶{pi}  {d.paragraphs[pi].text.strip()[:80]}')
