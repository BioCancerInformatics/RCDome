# -*- coding: utf-8 -*-
import docx, sys
sys.stdout.reconfigure(encoding='utf-8')

PATH = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_manuscript_governance_V024.docx'
doc = docx.Document(PATH)

edits = [
    # (old, new, description)
    ("encompassing all described forms of RCD.",
     "encompassing all described forms of RCD (Figure 1).",
     "PARA 39: cite Figure 1 (overall pipeline)"),
    ("and manual curation) (Figure 2).",
     "and manual curation) (Figure 1).",
     "PARA 51: four channels -> Figure 1 (was stale Figure 2)"),
    ("for functional-role classification (Supplementary Note S2)",
     "for functional-role classification (Supplementary Note S2; Figure 2A)",
     "PARA 162: cite Figure 2A (DeepSeek benchmark)"),
    ("zero false positives (Supplementary Note S3)",
     "zero false positives (Supplementary Note S3; Figure 2C)",
     "PARA 175: cite Figure 2C (Consensus benchmark)"),
    ("traceability from 24% to 98% (+310%).",
     "traceability from 24% to 98% (+310%) (Figure 2B).",
     "Elicit governance impact: cite Figure 2B"),
]

for old, new, desc in edits:
    done = False
    for p in doc.paragraphs:
        if old not in p.text:
            continue
        for r in p.runs:
            if old in r.text:
                r.text = r.text.replace(old, new)
                done = True
                break
        if not done:
            # rebuild: first run carries full text, others cleared
            full = p.text.replace(old, new)
            p.runs[0].text = full
            for r in p.runs[1:]:
                r.text = ''
            done = True
        break
    print(('OK  ' if done else 'FAIL'), '-', desc)

doc.save(PATH)
print('saved')
