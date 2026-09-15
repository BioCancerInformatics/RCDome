"""Complete the recovery: parse + govern the 3 recovered CSVs, save, update progress."""
import csv, io, os, json, sys
from collections import Counter, defaultdict

sys.path.insert(0, '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/extraction code snippets')
import channel_e_elicit_extract as ce

ENV = '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/extraction code snippets/.env'
for line in open(ENV):
    if line.startswith('ELICIT_API_KEY='):
        os.environ['ELICIT_API_KEY'] = line.split('=', 1)[1].strip()
        break
ce.ELICIT_KEY = os.environ['ELICIT_API_KEY']

# Matrix (V014) for form-level ontology columns
MATRIX = '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/output databases/unified_gene_rcd_matrix_V014.csv'
FORM_LEVEL_COLS = [
    'rcdome_level', 'rcdome_level_name',
    'elic_onto_rcd_id', 'elic_onto_rcd_name', 'elic_onto_inventory',
    'elic_onto_rcd_type', 'elic_onto_parent_rcd_id', 'elic_onto_relationship',
    'elic_onto_ontology_status', 'elic_onto_operational_note',
    'rodr_category', 'rodr_core_mechanism', 'rodr_key_molecules',
    'rodr_primary_refs', 'rodr_secondary_refs',
]
MATRIX_COLUMNS = [
    'gene_symbol', 'rcd_form', 'rcd_form_canonical', 'rcdome_level',
    'rcdome_level_name', 'source_databases', 'source_channels', 'num_sources',
    'evidence_quality', 'evidence_types', 'pmid_list', 'confidence_score',
    'confidence_tier', 'uniprot_id', 'ensembl_id', 'cancer_gene_type',
    'rcd_gene_type', 'role_direction', 'required_for_death', 'evidence_type',
    'gene_symbol_status', 'gene_biotype', 'evidence_tier',
    'evidence_basis', 'llm_status', 'llm_pmids', 'llm_evidence_force',
    'mechanistic_class', 'epmc_hits', 'epmc_status', 'epmc_pmids',
    'phase2c_mechanistic_class', 'elicit_pmids', 'elic_onto_rcd_id',
    'elic_onto_rcd_name', 'elic_onto_inventory', 'elic_onto_rcd_type',
    'elic_onto_parent_rcd_id', 'elic_onto_relationship',
    'elic_onto_ontology_status', 'elic_onto_operational_note',
    'rodr_category', 'rodr_core_mechanism', 'rodr_key_molecules',
    'rodr_primary_refs', 'rodr_secondary_refs',
]

OUT_DIR = '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/extraction code snippets/phase3b_p1_output'
PROGRESS = os.path.join(OUT_DIR, 'phase3b_p1_progress.json')

# Load matrix form attrs
mat = list(csv.DictReader(open(MATRIX, encoding='utf-8-sig')))
form_attrs = {}
for r in mat:
    f = r['rcd_form_canonical']
    if f not in form_attrs:
        form_attrs[f] = {c: r.get(c, '') for c in FORM_LEVEL_COLS}

hgnc_symbols, hgnc_enrich = ce.load_hgnc()
print(f"HGNC: {len(hgnc_symbols)}")

FORMS = ['Apoptosis', 'Autophagy', 'Ferroptosis']

def apply_post_export(records):
    out = []
    for r in records:
        role = r.get('rcd_gene_type', '')
        if role in ('SENSITIZER', 'RESISTANCE', 'PROTECTIVE'):
            r['rcd_gene_type'] = 'REGULATOR'
        if role == 'EXECUTOR' and r.get('required_for_death', '') != 'YES':
            r['rcd_gene_type'] = 'REGULATOR'
        out.append(r)
    return out

def fill_43(records, form):
    out = []
    for r in records:
        row = {c: '' for c in MATRIX_COLUMNS}
        for k, v in r.items():
            if k in MATRIX_COLUMNS:
                row[k] = v
        for c in FORM_LEVEL_COLS:
            row[c] = form_attrs.get(form, {}).get(c, '')
        row['rcd_form'] = form
        row['rcd_form_canonical'] = form
        row['elicit_pmids'] = row['pmid_list']
        out.append(row)
    return out

# Load existing progress
progress = {}
if os.path.exists(PROGRESS):
    progress = json.load(open(PROGRESS))

for form in FORMS:
    raw = f'{form.replace(" ", "_")}_recovered.csv'
    if not os.path.exists(raw):
        print(f'{form}: {raw} not found'); continue
    csv_data = open(raw, encoding='utf-8').read()
    rows = list(csv.DictReader(io.StringIO(csv_data)))
    papers = len(set(r.get('Title', '').strip() for r in rows if r.get('Title', '').strip()))
    records = ce.parse_elicit_response(csv_data, hgnc_symbols, hgnc_enrich, form)
    records = apply_post_export(records)
    rec43 = fill_43(records, form)
    genes = set(r['gene_symbol'] for r in rec43)
    roles = Counter(r['rcd_gene_type'] for r in rec43)

    gov = os.path.join(OUT_DIR, f'{form.replace(" ", "_")}_governed.csv')
    with open(gov, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=MATRIX_COLUMNS)
        w.writeheader(); w.writerows(rec43)

    progress[form] = {
        'papers': papers, 'rows': len(rows), 'records': len(rec43),
        'unique_genes': len(genes), 'roles': dict(roles),
        'post_export_actions': 0, 'governed_csv': os.path.basename(gov),
        'finished_at': 'recovered',
    }
    print(f'{form}: papers={papers} records={len(rec43)} genes={len(genes)} -> {os.path.basename(gov)}')

json.dump(progress, open(PROGRESS, 'w'), indent=2)
print(f'\nProgress updated: {len(progress)} forms done')
