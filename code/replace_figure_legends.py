# -*- coding: utf-8 -*-
import docx, sys
sys.stdout.reconfigure(encoding='utf-8')

PATH = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_manuscript_governance_V024.docx'

fig1 = ("Figure 1. RCDome compilation and validation pipeline. RCDome is a human gene atlas of regulated "
"cell death (RCD) assembled in a single top-to-bottom workflow. Twenty source databases constitute the "
"input layer: ten RCD-specific curated resources (FerrDB version 3, RCDdb, iPCD, LncRCD, iLIR, HADb, "
"HAMdb, ATD, AMT-DB and ncFO), five pathway and molecular databases (KEGG, Reactome, Gene Ontology, the "
"Molecular Signatures Database and WikiPathways), the NCBI Gene resource, the Rodrigues et al. (2025) "
"pan-cancer gene set, XDeathDB, and two Elicit literature channels (the Phase 3 systematic review and the "
"Alert review). These resources are compiled through four complementary channels: Channel A (programmatic "
"PubMed Boolean searches) maximizes recall; Channel B (topic-specific database extraction) provides "
"precision; Channel C (generative-AI-assisted literature screening) captures recent discoveries; and "
"Channel D (manual expert curation) serves as the final arbiter. Consolidation normalizes the 62 original "
"database name strings into 53 canonical RCD entities, yielding 22,474 gene\u2013RCD association rows across "
"9,265 unique human genes. The consolidated matrix then enters an independent validation stage in which "
"three mutually independent analyses are applied in execution order. The first is the DeepSeek "
"chain-of-thought classifier (Phases 2A through 2F), which performs two-call abstract validation, "
"full-text recovery, deep retrieval-augmented generation and a full-matrix chain-of-thought classification "
"that annotates every pair with four columns (cot_role, cot_direction, cot_mechanistic, cot_evidence) "
"encoding chain-of-thought role, direction, mechanistic verdict and evidence. The second is the Elicit "
"systematic-review extraction (Phase 3), which assigns functional role and direction of regulation. The "
"third is the Consensus evidence-channel classification (Phase 2G), which queries each pair with a neutral "
"formulation \u2014 the gene symbol followed only by \u201ccell death\u201d \u2014 so that evidence is retrieved without "
"form-name priming. The three analyses are preserved in separate columns and are never conflated. The "
"resulting consolidated matrix (22,474 rows and 67 columns) powers the RCDome web application, whose "
"interface comprises the interactive dome, the Explore RCDome guide, the Gene Catalog, the RCD entities "
"browser, the Network module and RCDchat. Boxes are colour-coded for visual distinction, and arrows "
"indicate the flow of data through the pipeline.")

fig2 = ("Figure 2. Benchmark evaluation of the three independent analyses. (A) DeepSeek model-selection "
"benchmark against a fixed 26-pair ground-truth set comprising 18 positive executor and regulator pairs "
"and 8 form-mismatch negative controls: the baseline deepseek-chat model reached 81% combined accuracy "
"with 38% false positives; chain-of-thought deepseek-reasoner reached 73% with 25% false positives; and "
"the governance-augmented tool-call loop with a hand-curated reference, together with the self-provided "
"chain-of-thought loop, each reached 100% combined accuracy with zero false positives \u2014 the self-provided "
"loop was adopted because it requires no external reference. (B) Elicit post-export governance benchmark "
"on the 784 records extracted across three forms (393 ferroptosis, 390 cuproptosis and 1 triaptosis): "
"allow-list compliance improved from 75.4% to 100%, executor precision from 47% to 100% (through 192 "
"EXECUTOR-to-REGULATOR downgrades), and publication traceability from 24% to 98%. (C) Consensus "
"query-formulation benchmark against the same 26-pair ground-truth set: the form-biased query reached 92% "
"combined accuracy with 12% false positives, whereas the neutral query \u2014 the gene symbol followed only "
"by \u201ccell death\u201d \u2014 reached 100% combined accuracy with zero false positives. Green bars denote "
"combined accuracy (panels A and C) or post-governance values (panel B); salmon bars denote false "
"positives (panels A and C) or pre-governance values (panel B).")

doc = docx.Document(PATH)
replaced = {}
for p in doc.paragraphs:
    if p.text.startswith('Figure 1.'):
        p.runs[0].text = fig1
        replaced['Figure 1'] = True
    elif p.text.startswith('Figure 2.'):
        p.runs[0].text = fig2
        replaced['Figure 2'] = True

doc.save(PATH)
print('Replaced:', replaced)
