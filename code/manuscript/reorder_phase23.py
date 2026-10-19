# -*- coding: utf-8 -*-
import docx, sys
sys.stdout.reconfigure(encoding='utf-8')

PATH = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_manuscript_governance_V024.docx'
doc = docx.Document(PATH)
paras = doc.paragraphs

start_idx  = next(i for i, p in enumerate(paras) if p.text.strip().startswith('Phase 3 Benchmark'))
results_idx = next(i for i, p in enumerate(paras) if p.text.strip() == 'RESULTS')
insert_idx  = next(i for i, p in enumerate(paras) if p.text.strip().startswith('Phase 2G:'))

print('start (Phase 3 Benchmark):', start_idx)
print('results (RESULTS):', results_idx)
print('insert before (Phase 2G):', insert_idx)

# block = Phase 3 section paragraphs (start_idx .. results_idx-2 inclusive)
block = [paras[i]._element for i in range(start_idx, results_idx - 1)]
insert_el = paras[insert_idx]._element

for el in block:
    insert_el.addprevious(el)

doc.save(PATH)
print('moved', len(block), 'paragraphs -> Phase 3 (Elicit) now before Phase 2G (Consensus)')
