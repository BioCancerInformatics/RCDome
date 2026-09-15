# -*- coding: utf-8 -*-
import docx, sys
sys.stdout.reconfigure(encoding='utf-8')

PATH = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_manuscript_governance_V024.docx'
doc = docx.Document(PATH)

fig4 = ("Figure 4. The RCDome web application. (A) The interactive Home dome, the primary entry point, "
"which renders the 53 canonicalized RCD-related entities, 9,265 genes and 21,568 association pairs as an explorable dome "
"with animated counters. (B) The Explore RCDome guide, an educational overview of the modules, the "
"benchmark results and the governance principles. (C) The Gene Catalog, the searchable 22,474-row matrix "
"browser with a Direction/Role source selector that switches the displayed annotation between the DeepSeek "
"chain-of-thought classification and the Elicit extraction, together with a one-click Death-core preset "
"that filters to the 469 executor pairs. (D) The gene detail page, which provides the entity jump "
"selector, the four chain-of-thought columns (role, direction, mechanistic verdict and evidence), the "
"required-for-death flag and verified publication titles. All views use the RCDome navy-and-gold theme.")

# insert before the References heading
ref = None
for p in doc.paragraphs:
    if p.text.strip() == 'References':
        ref = p
        break

if ref is None:
    print('ERROR: References not found'); sys.exit(1)

new_p = ref.insert_paragraph_before()
run = new_p.add_run(fig4)
run.bold = True

doc.save(PATH)
print('Figure 4 legend inserted before References (bold).')
