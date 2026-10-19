# -*- coding: utf-8 -*-
import os, zipfile, sys
sys.stdout.reconfigure(encoding='utf-8')

ROOT = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript'
BASE = ROOT + '/Shiny app/RCDome_Atlas/APP'
MATRIX = ROOT + '/output databases/Phase 2C output/unified_gene_rcd_matrix_V026.rds'
DECODER = ROOT + '/RCDome Decoder/RCDome_Decoder_53.csv'

# ---- CHANGELOG ----
changelog = '''# RCDome — CHANGELOG V026_4

**Download (zip):** https://drive.google.com/drive/folders/1J8NO3U88GpAeIkdG2Bfo7lXLqu-aHykl?usp=sharing

## V026_4 — Governance + RCD Network ontology layer
- **RCD Network ontology layer** (`modules/mod_network.R`): RCD entity nodes colored by ontological level (L1–L5 level colors, ring on logos / fill on dots); gene nodes colored by dominant mechanistic role (EXECUTOR / REGULATOR / MARKER / UNCERTAIN); compact legend (entity levels + gene roles + edge direction badges); rich hover — gene → symbol + HGNC name, entity → name + level + first sentence of the operational definition, edge → role · direction · tier · PMID count; per-edge evidence attributes aggregated from the V026 matrix (role/direction prefer the strongest value, tier, unique PMID count).
- **Response Protocol** (`governance/Protocolo_de_Resposta.md/.docx`): enumerated-response protocol sent to Emanuell, Victor and Higor. Preamble sets the standard (my e-mails are structured, itemized and carefully edited; responses must match that level); item-by-item format (copy each item, then "Resposta:"); 7 rules — no generic/ambiguous responses (with concrete rejected examples), no grouping of items (verified solutions in the record, not guesswork), declare what is missing, real item-by-item progress, substandard responses rejected, no student-to-advisor role reversal (with offensive-phrase example; use statistical data and benchmark instead), cited evidence traceable via a Google Drive folder holding all codes/prompts/comparative analyses + its URL.
- **Reply to Emanuell's quantitative report** (`governance/resposta_emanuell_relatorio.md/.docx`): firm traceability ruling — running the app zip is the core traceability instrument (asked yes/no); mechanistic prose must be anchored in full text via DeepSeek Chat + RAG + code + benchmark; the article source is already deposited in the V26 matrix (300k PMIDs/PMCs explored, 10k selected with proof references); per-artifact validation record; absolute dates; incremental delivery to Enrique (who syncs GitHub); closing principle — everything in the app must be circumstantiated by traceability, honesty, reproducibility and documented provenance, or be excluded.
- **Traceability solicitation** (`governance/solicitacao_rastreabilidade_modulo_entities.md` + `solicitacao_atualizacao_modulo_entities.md`): RCD Entities + RCD Network scoped to Emanuell — 5 requirements (code+logic, benchmark, provenance, per-figure Methods/Supplementary, GitHub deposit + non-compliance exclusion).
- **Governance artifacts shipped**: `governance/RCDome_Code_Amendment_Contract.md`, `governance/audit_before_run.sh`.

## V026_3 — Operational Definitions + Comparator + landing-page menu
- **Operational Definitions module** (`modules/mod_od.R`): new navbar tab, list+detail browser over the 53-form decoder, source databases as wrapping pills, reference citations hyperlinked to PMIDs, didactic ontology-level legend.
- **Operational Definition Comparator** (`modules/mod_od_compare.R`): side-by-side comparison of 2-4 entities, difference highlighting, 3 display modes (all / differing / identical), top-aligned cells, NCCD badges, Download Comparison (HTML) with entity names in the filename.
- **Landing page lower panel**: now mirrors the full bar menu (Home, Explore RCDome, Operational Definitions, Compare Definitions, RCD entities, Gene Catalog, RCDome Board, Network, About, Contact), each linked to its tab.
- **Not-found pop-up**: universal on all scroll-downs via the verified create callback (returns false, value never added) + centered modal.
- **Gene Catalog**: click a gene opens the gene page in-app (navbar stays).
- **Detail page**: stable jump bar with type-ahead gene/entity search + not-found pop-ups.
- **Governance**: pre-run audit contract (`docs/RCDome_Code_Amendment_Contract.md`) + executable audit (`code/audit_before_run.sh`).

## V026 — Digital Molecular RCD Board + governed Q&A AI
- **Board module** (`modules/mod_board.R`): prose synthesis of any RCD entity (and optional gene) strictly from the matrix and decoder, with governance scrub, payload table, and HTML download.
- **Q&A submodule** (`modules/mod_board_qa.R`): retrieval-augmented (RAG) free-form Q&A across all 53 entities and all 9,265 genes; static full gene-entity index (22,473 associations) plus dynamic four-dimension records (class | role | direction | tier | PMID); no gene capping, no funneling; hyphenated gene-entity tokens split (XIAP-Apoptosis -> XIAP).
- **Governance**: zero hallucination (never invent gene/PMID/fact), exact refusal sentence, exact disclaimer, RCDome database/decoder terminology only, hedging, PMID discipline.
- **Benchmark**: board 9 tests (golden 26/26, census 53/53, fact-stability 73/73, governance 0.047% violation, anti-hallucination 4/4, articulation 98.7%); Q&A 2 tests (T10 positive + T11 negative, n=100 each, 100/100, Wilson 95% CI 96.3-100%, two-sided binomial p=0.010).
- **Logo**: `www/rcdome_logo.svg` (dome-only) and `www/rcdome_logo_full.svg` (full emblem with wordmark) - cupola dome + 53 ontology-colored entity nodes + rust gene constellation.
- **UI**: "Try an example query" relocated after the Q&A; footer processing-time darkened for visibility.
- **Supplementary Note S4** and manuscript paragraph 324 updated with the board and Q&A benchmarks.
- **Board benchmarks shipped**: `board/run_board_benchmark.py`, `board/run_qa_benchmark.py`, `board/qa_benchmark_report.json`.

## V026 -> V026 — Victor's biological curation (7/7 groups)
- **GROUP A**: MPT-driven necrosis -> L1 (modality); MPT -> L3 (trigger, `triggered_by`); Vacuolar cell death -> L4 (cross-species morphology).
- **GROUP B**: 7 ontological fields added to the decoder (species_scope, evidence_maturity, relationship_type, parent_entity, ontology_curator_verified, independent_replication, primary_discovery_reference) -> decoder 31 -> 39 columns.
- **GROUP C**: hard gates G0-G6 (addition, not replacement) + `hard_gate_status` column (L1-ELIGIBLE 16 / NOT-L1 37).
- **GROUP D**: D1 Ontology Adjudication Table (Table S12, 53 x 26, Q1-Q13 + C1-C5) + D2 two-validation separation in Methods.
- **GROUP E**: ontological recalibration - 23 level changes (L1 12,366 -> 10,300 · L2 2,111 -> 2,354 · L3 172 · L4 1,219 -> 2,684 · L5 6,605 -> 6,963); specific adjudications (Anoikis -> L2 subtype_of Intrinsic apoptosis; Mitotic death -> L4 driven_by Mitotic catastrophe; direction fix).
- **GROUP F**: Methods/Results/Discussion framing - 5 insertions.
- **GROUP G**: 9 ontological relationships registered (12-value relationship vocabulary + outcome_of).
- **Matrix**: V026 (22,473 x 71; levels recalibrated per G0-G6).
- **Decoder**: 39 columns; hard_gate_status 16/37.
- **Manuscript**: version-free content; matrix named **Database S1**; 381 paragraphs.
- **Supplementary**: S1-S15 + Database S1.
- **Figure 4**: regenerated with V026 level colors.
- **App**: loads V026 matrix.

## Run
```
setwd(".../RCDome_Atlas/APP")
shiny::runApp(appDir = ".", port = 8890, launch.browser = TRUE)
```
'''

open(BASE + '/CHANGELOG_V026_4.md', 'w', encoding='utf-8').write(changelog)

# ---- ZIP ----
files = [
    'ui.R', 'server.R', 'global.R', 'run.R', 'build_signatures_cache.R',
    'data/pmid_title_lookup.rds', 'data/pmid_title_lookup.json',
    'data/about/see also/sigpolytope.svg',
    'www/landing_page.html', 'www/dome_prototype.html', 'www/detail_page_wireframe.html',
    'www/explore.html', 'www/module_placeholder.html', 'www/SigPolytope.html',
    'www/contact_intercept.js', 'www/rcdome_logo.svg', 'www/rcdome_logo_full.svg',
    'generate_dome.py', 'generate_detail_page.py', 'generate_explore.py',
    'CHANGELOG_V026_4.md',
]
files += ['R/' + f for f in sorted(os.listdir(BASE + '/R')) if f.endswith('.R')]
files += ['modules/' + f for f in sorted(os.listdir(BASE + '/modules')) if f.endswith('.R')]
# board folder (benchmark scripts + S4 note + report + examples)
for f in sorted(os.listdir(BASE + '/board')):
    if f.endswith(('.py', '.md', '.json', '.html', '.txt')):
        files.append('board/' + f)

# governance folder (V026_4 additions)
governance = [
    ('comms/emails_coautores/Protocolo_de_Resposta.md', 'governance/Protocolo_de_Resposta.md'),
    ('comms/emails_coautores/Protocolo_de_Resposta.docx', 'governance/Protocolo_de_Resposta.docx'),
    ('comms/emails_coautores/resposta_emanuell_relatorio.md', 'governance/resposta_emanuell_relatorio.md'),
    ('comms/emails_coautores/resposta_emanuell_relatorio.docx', 'governance/resposta_emanuell_relatorio.docx'),
    ('comms/emails_coautores/resposta_emanuell_rastreabilidade.md', 'governance/resposta_emanuell_rastreabilidade.md'),
    ('comms/emails_coautores/resposta_emanuell_rastreabilidade.docx', 'governance/resposta_emanuell_rastreabilidade.docx'),
    ('comms/emails_coautores/solicitacao_rastreabilidade_modulo_entities.md', 'governance/solicitacao_rastreabilidade_modulo_entities.md'),
    ('comms/emails_coautores/solicitacao_rastreabilidade_modulo_entities.docx', 'governance/solicitacao_rastreabilidade_modulo_entities.docx'),
    ('comms/emails_coautores/solicitacao_atualizacao_modulo_entities.md', 'governance/solicitacao_atualizacao_modulo_entities.md'),
    ('comms/emails_coautores/solicitacao_atualizacao_modulo_entities.docx', 'governance/solicitacao_atualizacao_modulo_entities.docx'),
    ('docs/RCDome_Code_Amendment_Contract.md', 'governance/RCDome_Code_Amendment_Contract.md'),
    ('code/audit_before_run.sh', 'governance/audit_before_run.sh'),
]

out = BASE + '/RCDome_V026_update_4.zip'
added = 0
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in files:
        p = os.path.join(BASE, f)
        if os.path.exists(p):
            z.write(p, f)
    for src, arc in governance:
        p = os.path.join(ROOT, src)
        if os.path.exists(p):
            z.write(p, arc)
            added += 1
    z.write(MATRIX, 'data/unified_gene_rcd_matrix_V026.rds')
    z.write(DECODER, 'data/RCDome_Decoder_53.csv')

print('created RCDome_V026_update_4.zip with', len(files) + added + 2, 'entries')
print('size:', round(os.path.getsize(out)/1024/1024, 2), 'MB')
