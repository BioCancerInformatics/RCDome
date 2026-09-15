# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

f = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/docs/RCDome_Traceability_Contract.md'
txt = open(f, encoding='utf-8').read()

repl = [
    ('| Current version | V011 |', '| Current version | V025 |'),
    ('unified_gene_rcd_matrix_V011.csv', 'unified_gene_rcd_matrix_V025.csv'),
    ('| Rows | 24,834 |', '| Rows | 22,473 |'),
    ('| Columns | 28 |', '| Columns | 67 |'),
    ('| Unique genes | 9,252 |', '| Unique genes | 9,265 |'),
    ('| Canonical RCD forms | 54 |', '| Canonical RCD forms | 53 |'),
    ('| Raw RCD form names | 61 |', '| Raw RCD form names | 62 |'),
    ('| MECHANISTIC pairs | 3,466 |', '| MECHANISTIC pairs | 3,063 |'),
    ('| DATABASE_ONLY pairs | 274 |', '| DATABASE_ONLY pairs | 442 |'),
    ('| Databases integrated | 18 |', '| Databases integrated | 20 |'),
]
for old, new in repl:
    txt = txt.replace(old, new)

note = '''
## V024 \u2192 V025 Amendment Log

1. **Orphan-row deletion** \u2014 removed the single retracted Elicit record (EPAS1 / Ammonia-induced cell death) whose provenance was empty (`source_databases` = NaN, `num_sources` = 0). Rows 22,474 \u2192 22,473; unique pairs 21,569 \u2192 21,568; corroboration rows unchanged (905).

2. **Mini-run pairs \u2014 Phase 2A/D two-call classification** \u2014 populated `mechanistic_class`, `llm_status`, `llm_pmids`, `llm_evidence_force` for the two late-added pairs (NLRX1 and PPIF, MPT-driven necrosis):
   - NLRX1 \u2192 **CONTEXT_GAP** (PubMed confirms via PMID 41739553; LLM training does not recognize the gene in this form).
   - PPIF \u2192 **MECHANISTIC** (LLM knowledge + PubMed both confirm via PMID 15800627).

   *Method deviation (transparency):* for these two pairs, call B used the known PMIDs from `pmid_list` instead of the standard esearch query, because the canonicalized form name "MPT-driven necrosis" does not match PubMed terminology ("mitochondrial permeability transition"). Call A used the clarified descriptor "MPT-driven necrosis (necrosis driven by the mitochondrial permeability transition, mPTP)".

'''
txt = txt.replace('\n## File Inventory', note + '\n## File Inventory')

open(f, 'w', encoding='utf-8').write(txt)
print('traceability contract updated (V025 + amendment log)')
