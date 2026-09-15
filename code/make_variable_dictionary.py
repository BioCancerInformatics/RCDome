import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

COLS = [
    ("gene_symbol", "Identifiers", "Official HGNC gene symbol for the gene in the association.", "HGNC-approved symbol"),
    ("rcd_form", "Identifiers", "The RCD form name exactly as recorded by the source database (original, unnormalized).", "free text"),
    ("rcd_form_canonical", "Identifiers", "The canonicalized RCD-related form name (one of 53 canonicalized forms).", "53 canonicalized forms"),
    ("rcdome_level", "Identifiers", "The ontological level code of the RCD entity: L1 Modalities, L2 Subtypes, L3 Triggers, L4 Functional/conceptual, L5 Generic/composite.", "L1->Modalities, L2->Subtypes, L3->Triggers, L4->Functional/conceptual, L5->Generic/composite"),
    ("rcdome_level_name", "Identifiers", "The label of the ontological level the RCD entity belongs to (paired with the rcdome_level code).", "L1 Modalities, L2 Subtypes, L3 Triggers, L4 Functional/conceptual, L5 Generic/composite"),
    ("source_databases", "Source provenance", "Semicolon-separated list of the source databases that contributed this association (joined provenance, not a single base ID).", "combinations of the 19 base database identifiers (828 distinct combinations)"),
    ("source_channels", "Source provenance", "The compilation channel(s) that produced the association. Channels C (AI-assisted) and D (manual curation) are validation/annotation layers, not row-producing.", "A, B, E and combinations (A;B, B;E, A;B;E, A;E)"),
    ("num_sources", "Source provenance", "The number of independent source databases contributing this association.", "integer"),
    ("evidence_quality", "Source provenance", "The nature of the source evidence (curated / mixed / ai_extracted / keyword).", "curated, mixed, ai_extracted, keyword"),
    ("evidence_types", "Source provenance", "The type(s) of evidence supporting the association (e.g. database, LLM, PMID).", "free text"),
    ("pmid_list", "PMIDs", "PubMed identifiers collected by the original database/compilation.", "semicolon-separated PMIDs"),
    ("llm_pmids", "PMIDs", "PubMed identifiers retrieved by Phase 2A/D Call B (abstract evidence).", "semicolon-separated PMIDs"),
    ("epmc_pmids", "PMIDs", "PubMed identifiers recovered by the Europe PMC full-text pipeline (Phase 2C).", "semicolon-separated PMIDs"),
    ("elicit_pmids", "PMIDs", "PubMed identifiers from the Elicit systematic review (Phase 3B).", "semicolon-separated PMIDs"),
    ("confidence_score", "Confidence", "Weighted sum of source channels (Channel D=4, B=3, A=1, C=1).", "1-5 observed (0-10 theoretical)"),
    ("confidence_tier", "Confidence", "Confidence tier derived from the weighted score (T1 strongest).", "T2, T3, T4 (T1 theoretical, none observed)"),
    ("uniprot_id", "Gene metadata", "UniProt accession for the gene product.", "UniProt ID"),
    ("ensembl_id", "Gene metadata", "Ensembl gene identifier.", "ENSG..."),
    ("cancer_gene_type", "Gene metadata", "Cancer gene role from Rodrigues2025, distinct from the RCD functional role.", "suppressor, driver, unclassified, mixed"),
    ("rcd_gene_type", "Gene metadata", "Functional role of the gene in the RCD form: EXECUTOR (executes death), REGULATOR (controls death), MARKER (associated but not causal), UNCERTAIN.", "EXECUTOR, REGULATOR, MARKER, UNCERTAIN, CANDIDATE_MODULE"),
    ("gene_symbol_status", "Gene metadata", "Result of HGNC validation of the gene symbol.", "valid (invalid/not_found excluded during HGNC validation)"),
    ("gene_biotype", "Gene metadata", "The gene biotype.", "protein_coding, miRNA, lncRNA, pseudogene, other, other_RNA"),
    ("evidence_tier", "Evidence & validation", "The final evidence tier (T1-T4) combining source count and LLM validation.", "T1, T2, T3, T4"),
    ("evidence_basis", "Evidence & validation", "Human-readable justification of the evidence tier assignment.", "free text"),
    ("llm_status", "Evidence & validation", "The Phase 2A/D two-call verdict (CONFIRMED / NEEDS_LITERATURE / NEEDS_CONTEXT / UNCLEAR).", "CONFIRMED, NEEDS_LITERATURE, NEEDS_CONTEXT, UNCLEAR"),
    ("llm_evidence_force", "Evidence & validation", "The total PubMed paper count returned for the gene-form query (evidence force).", "integer"),
    ("mechanistic_class", "Evidence & validation", "The mechanistic classification of the association.", "MECHANISTIC, LITERATURE_GAP, CONTEXT_GAP, CO_OCCURRENCE, INSUFFICIENT_DATA, DATABASE_ONLY (TECHNICAL_FAILURE = 0 observed)"),
    ("epmc_hits", "Evidence & validation", "The Europe PMC full-text hit count for the gene-form pair (Phase 2C).", "integer"),
    ("epmc_status", "Evidence & validation", "The Phase 2C full-text LLM verdict.", "CONFIRMED, NEEDS_CONTEXT, NEEDS_LITERATURE, UNCLEAR, MECHANISTIC_SKIPPED"),
    ("phase2c_mechanistic_class", "Evidence & validation", "The combined mechanistic classification after Europe PMC full-text recovery.", "MECHANISTIC, CO_OCCURRENCE, CONTEXT_GAP, LITERATURE_GAP, INSUFFICIENT_DATA, DATABASE_ONLY"),
    ("elic_onto_rcd_id", "RCD ontology", "The RCD entity identifier in the Elicit-derived ontology.", "ID"),
    ("elic_onto_rcd_name", "RCD ontology", "The RCD entity name in the ontology.", "free text"),
    ("elic_onto_inventory", "RCD ontology", "The gene inventory/coverage of the RCD entity.", "free text"),
    ("elic_onto_rcd_type", "RCD ontology", "The RCD entity type (modality, subtype, trigger, category, concept).", "type"),
    ("elic_onto_parent_rcd_id", "RCD ontology", "The parent RCD entity identifier in the ontology hierarchy.", "ID"),
    ("elic_onto_relationship", "RCD ontology", "The relationship of this entity to its parent.", "relationship"),
    ("elic_onto_ontology_status", "RCD ontology", "The ontology status of the entity (e.g. established, emerging).", "status"),
    ("elic_onto_operational_note", "RCD ontology", "Literature-justified operational note defining the entity.", "free text"),
    ("rodr_category", "RODR operational definitions", "The Rodrigues2025 category of the RCD form.", "category"),
    ("rodr_core_mechanism", "RODR operational definitions", "The core molecular mechanism of the RCD form (Rodrigues2025).", "free text"),
    ("rodr_key_molecules", "RODR operational definitions", "The key molecules of the RCD form (Rodrigues2025).", "free text"),
    ("rodr_primary_refs", "RODR operational definitions", "Primary PMID references for the RCD form definition.", "semicolon-separated PMIDs"),
    ("rodr_secondary_refs", "RODR operational definitions", "Secondary PMID references for the RCD form definition.", "semicolon-separated PMIDs"),
    ("role_direction", "Elicit extraction", "Direction of the gene's effect: PROMOTES (pro-death) / PROTECTS (pro-survival) / ASSOCIATED / BIDIRECTIONAL / UNCLEAR.", "PROMOTES, PROTECTS, ASSOCIATED, BIDIRECTIONAL, UNCLEAR"),
    ("required_for_death", "Elicit extraction", "Whether the gene is required for the death process (NCCD criterion).", "YES, PARTIAL, NO, NOT_TESTED, UNCLEAR"),
    ("evidence_type", "Elicit extraction", "The type of evidence from the Elicit extraction.", "GENETIC_PERTURBATION, EXPRESSION_CORRELATION, PHARMACOLOGICAL, CITATION_ONLY"),
    ("elicit_verbatim_sentence", "Elicit extraction", "The verbatim sentence from the source paper supporting the association.", "verbatim text"),
    ("elicit_doi", "Elicit extraction", "The DOI of the supporting paper.", "DOI"),
    ("elicit_title", "Elicit extraction", "The title of the supporting paper.", "free text"),
    ("elicit_authors", "Elicit extraction", "The authors of the supporting paper.", "free text"),
    ("elicit_venue", "Elicit extraction", "The journal/venue of the supporting paper.", "free text"),
    ("elicit_year", "Elicit extraction", "The publication year of the supporting paper.", "year"),
    ("elicit_evidence_status", "Elicit extraction", "The triage status of the Elicit association (genuine / association_only / retracted / none).", "genuine, association_only, retracted, none"),
    ("deep_pmids_total", "Phase 2B deep evidence", "Total PMIDs examined for the pair in the deep full-text RAG (Phase 2B).", "integer"),
    ("deep_pmids_free", "Phase 2B deep evidence", "Open-access PMIDs (free full text) among the examined PMIDs.", "integer"),
    ("deep_pmids_skipped", "Phase 2B deep evidence", "Paywalled/skipped PMIDs among the examined PMIDs.", "integer"),
    ("deep_paper_count", "Phase 2B deep evidence", "The number of unique papers with deep evidence for the pair.", "integer"),
    ("deep_best_sentence", "Phase 2B deep evidence", "The strongest verbatim body sentence supporting the pair.", "verbatim text"),
    ("deep_best_evidence", "Phase 2B deep evidence", "The evidence type of the strongest deep sentence.", "DIRECT_EXPERIMENTAL, GENETIC_INTERVENTION, PHARMACOLOGICAL, EXPRESSION_CORRELATION, CITATION_ONLY"),
    ("deep_best_role", "Phase 2B deep evidence", "The functional role from the deepest full-text evidence.", "EXECUTOR, REGULATOR, MARKER, INTERACTOR, SUBSTRATE"),
    ("deep_best_direction", "Phase 2B deep evidence", "The direction of effect from the deepest full-text evidence.", "PROMOTES, INHIBITS, CONTEXT_DEPENDENT, UNKNOWN"),
    ("deep_confidence", "Phase 2B deep evidence", "The multi-paper consensus confidence of the deep evidence.", "HIGH, MEDIUM, LOW"),
    ("deep_evidence_score", "Phase 2B deep evidence", "The proportion of papers with direct experimental support (0-1).", "float 0-1"),
]

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Variable Dictionary"
ws['A1'] = "RCDome Matrix V022 - Variable Dictionary (63 columns)"
ws['A1'].font = Font(bold=True, size=14)

for ci, h in enumerate(['#', 'Variable', 'Category', 'Comprehensive description', 'Values / enum'], 1):
    c = ws.cell(row=3, column=ci, value=h)
    c.font = Font(bold=True)
    c.fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')

for ri, (var, cat, desc, enum) in enumerate(COLS, start=4):
    ws.cell(row=ri, column=1, value=ri-3)
    ws.cell(row=ri, column=2, value=var).font = Font(bold=True)
    ws.cell(row=ri, column=3, value=cat)
    ws.cell(row=ri, column=4, value=desc).alignment = Alignment(wrap_text=True, vertical='top')
    ws.cell(row=ri, column=5, value=enum)

ws.column_dimensions['A'].width = 5
ws.column_dimensions['B'].width = 28
ws.column_dimensions['C'].width = 24
ws.column_dimensions['D'].width = 75
ws.column_dimensions['E'].width = 40

wb.save('RCDome_manuscript_V022_matrix_variables.xlsx')
print(f"saved: {len(COLS)} variables")
