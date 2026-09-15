"""
phase3b_p4_RegulatedNecrosis.py — Phase 3B P4 runner for the ONE missing form.

Mirrors phase3b_p1/p2/p3.py EXACTLY in spirit, context, content and deep search:
  - same channel_e_elicit_extract contract (maxResults=1000, 4 semantic searches)
  - same 6 extraction questions (generate: False, useFigures: False)
  - same governance: HGNC + allow-list (parse_elicit_response) + post-export rules
  - same 43-column matrix schema output (raw + governed CSVs)
  - same resume-safe progress + per-form audit

NEW (the fix that was missing before): a RECONCILIATION GUARD that asserts
every matrix form is covered by P1+P2+P3+P4 before spending a single API call.
"""
import csv, os, json, time, io, subprocess, urllib.request
from collections import Counter, defaultdict
from datetime import datetime

import channel_e_elicit_extract as ce   # production (maxResults=1000)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATRIX_FILE = '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/output databases/unified_gene_rcd_matrix_V014.csv'
OUTPUT_DIR = os.path.join(BASE_DIR, 'phase3b_p4_output')
PROGRESS_FILE = os.path.join(OUTPUT_DIR, 'phase3b_p4_progress.json')
COMBINED_FILE = os.path.join(OUTPUT_DIR, 'phase3b_p4_combined.csv')

# P4 = the single form missed by P1/P2/P3
P4_FORMS = ['Regulated Necrosis']

# Full reconciled universe of all 53 matrix forms (P1+P2+P3+P4)
ALL_FORMS = set([
    # P1 (20)
    'Apoptosis', 'Autophagy', 'Ferroptosis', 'Autosis', 'Necrosis',
    'Pyroptosis', 'Necroptosis', 'Immunogenic cell death', 'Anoikis',
    'Cellular senescence', 'Apoptosis (intrinsic)',
    'Lysosome-dependent cell death', 'Mitotic death',
    'Apoptosis (extrinsic)', 'Programmed cell death', 'Parthanatos',
    'Mitotic catastrophe', 'Autophagy-dependent cell death',
    'Senescence and Autophagy in Cancer', 'Disulfidptosis',
    # P2 (14)
    'Efferocytosis', 'Entosis', 'Cuproptosis', 'Phagoptosis',
    'MPT-driven necrosis', 'Aponecrosis', 'Mitochondrial permeability transition',
    'PANoptosis', 'Lysosomal cell death', 'NETosis', 'Metalloptosis',
    'Lysoptosis', 'Floatptosis', 'NECSO',
    # P3 (18)
    'Pyronecrosis', 'Methuosis', 'Spectosis', 'Triaptosis',
    'Cornification', 'Eryptosis', 'Mitoptosis', 'Paraptosis',
    'Erebosis', 'Linker cell-type death', 'Lysozincrosis',
    'Mitoxyperilysis', 'Oncosis', 'Oxeiptosis',
    'Ammonia-induced cell death', 'Hypersensitive response',
    'Alkaliptosis', 'Vacuolar cell death',
    # P4 (1)
    'Regulated Necrosis',
])

# 43-column schema (identical to P1/P2/P3)
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

FORM_LEVEL_COLS = [
    'rcdome_level', 'rcdome_level_name',
    'elic_onto_rcd_id', 'elic_onto_rcd_name', 'elic_onto_inventory',
    'elic_onto_rcd_type', 'elic_onto_parent_rcd_id', 'elic_onto_relationship',
    'elic_onto_ontology_status', 'elic_onto_operational_note',
    'rodr_category', 'rodr_core_mechanism', 'rodr_key_molecules',
    'rodr_primary_refs', 'rodr_secondary_refs',
]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def load_matrix():
    """Load V014 matrix: rows + form-level attribute lookup + allow-lists."""
    rows = list(csv.DictReader(open(MATRIX_FILE, encoding='utf-8-sig')))
    form_attrs = {}
    allow_lists = defaultdict(set)
    for r in rows:
        form = r['rcd_form_canonical']
        if form not in form_attrs:
            form_attrs[form] = {c: r.get(c, '') for c in FORM_LEVEL_COLS}
        allow_lists[form].add(r['gene_symbol'])
    return rows, form_attrs, allow_lists

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {'completed': {}, 'started_at': datetime.now().isoformat()}

def save_progress(progress):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def apply_post_export(records):
    """Role normalization + EXECUTOR validation (identical to P1/P2/P3)."""
    log_out = []
    for r in records:
        role = r.get('rcd_gene_type', '')
        if role in ('SENSITIZER', 'RESISTANCE', 'PROTECTIVE'):
            r['rcd_gene_type'] = 'REGULATOR'
            log_out.append(('NORMALIZED', role, r['gene_symbol']))
        if role == 'EXECUTOR' and r.get('required_for_death', '') != 'YES':
            r['rcd_gene_type'] = 'REGULATOR'
            log_out.append(('DOWNGRADED', 'EXECUTOR', r['gene_symbol']))
    return records, log_out

def fill_43_columns(records, form, form_attrs):
    """Map parse output to the full 43-column schema."""
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

def process_form(form, form_attrs, hgnc_symbols, hgnc_enrich):
    """Full pipeline for one form (identical to P1/P2/P3)."""
    log(f"=== {form} ===")
    sid = ce.call_elicit(form)
    if not sid:
        log(f"  FAIL: no session"); return [], {'error': 'no_session'}
    log(f"  session={sid}")

    resp, csv_data = ce.poll_elicit(sid, max_wait=3600)
    if not csv_data:
        log(f"  FAIL: no CSV"); return [], {'error': 'no_csv'}

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    raw_path = os.path.join(OUTPUT_DIR, f'{form.replace(" ", "_").replace("(", "").replace(")", "")}_raw.csv')
    with open(raw_path, 'w', encoding='utf-8') as f:
        f.write(csv_data)

    rows = list(csv.DictReader(io.StringIO(csv_data)))
    papers = len(set(r.get('Title', '').strip() for r in rows if r.get('Title', '').strip()))

    records = ce.parse_elicit_response(csv_data, hgnc_symbols, hgnc_enrich, form)
    records, log_out = apply_post_export(records)
    records43 = fill_43_columns(records, form, form_attrs)

    form_path = os.path.join(OUTPUT_DIR, f'{form.replace(" ", "_").replace("(", "").replace(")", "")}_governed.csv')
    with open(form_path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=MATRIX_COLUMNS)
        w.writeheader(); w.writerows(records43)

    unique_genes = set(r['gene_symbol'] for r in records43)
    roles = Counter(r['rcd_gene_type'] for r in records43)

    audit = {
        'papers': papers,
        'rows': len(rows),
        'records': len(records43),
        'unique_genes': len(unique_genes),
        'roles': dict(roles),
        'post_export_actions': len(log_out),
        'raw_csv': os.path.basename(raw_path),
        'governed_csv': os.path.basename(form_path),
    }
    log(f"  papers={papers} records={len(records43)} genes={len(unique_genes)} actions={len(log_out)}")
    return records43, audit

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rows, form_attrs, allow_lists = load_matrix()
    log(f"Matrix loaded: {len(rows)} rows, {len(form_attrs)} forms")

    # ============ RECONCILIATION GUARD (the fix) ============
    uncovered = set(form_attrs) - ALL_FORMS
    extra = ALL_FORMS - set(form_attrs)
    if uncovered:
        log("=" * 70)
        log(f"FATAL: {len(uncovered)} matrix forms NOT covered by P1+P2+P3+P4:")
        for f in sorted(uncovered):
            log(f"  MISSING: {f}")
        log("ABORTING before any API spend.")
        log("=" * 70)
        return
    if extra:
        log(f"WARNING: {len(extra)} batch forms not present in matrix (ignored): {sorted(extra)}")
    log(f"Reconciliation OK: {len(ALL_FORMS)} batch forms == {len(set(form_attrs))} matrix forms")
    # ========================================================

    hgnc_symbols, hgnc_enrich = ce.load_hgnc()
    log(f"HGNC loaded: {len(hgnc_symbols)}")

    progress = load_progress()
    log(f"Already completed: {len(progress['completed'])} forms")

    all_records = []
    consecutive_failures = 0
    for form in P4_FORMS:
        prev = progress['completed'].get(form)
        if prev and 'error' not in prev and 'records' in prev:
            log(f"SKIP {form} (done: {prev.get('records', 0)} records)")
            continue
        if form not in form_attrs:
            log(f"SKIP {form} (not in matrix)"); continue
        try:
            records, audit = process_form(form, form_attrs, hgnc_symbols, hgnc_enrich)
        except Exception as e:
            audit = {'error': str(e)[:200]}
            records = []
            log(f"  ERROR {form}: {e}")
        if 'error' in audit:
            consecutive_failures += 1
            if consecutive_failures >= 3:
                log("RUN HALTED — 3 consecutive form failures.")
                break
        else:
            consecutive_failures = 0
        progress['completed'][form] = audit
        progress['completed'][form]['finished_at'] = datetime.now().isoformat()
        save_progress(progress)
        all_records.extend(records)
        log(f"  Saved progress ({len(progress['completed'])}/{len(P4_FORMS)})")

    if all_records:
        with open(COMBINED_FILE, 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=MATRIX_COLUMNS)
            w.writeheader(); w.writerows(all_records)
        log(f"Combined output: {COMBINED_FILE} ({len(all_records)} records)")

    log("\n=== PHASE 3B P4 AUDIT SUMMARY ===")
    for form in P4_FORMS:
        a = progress['completed'].get(form, {})
        if 'papers' in a:
            log(f"  {form}: papers={a['papers']} records={a['records']} genes={a['unique_genes']}")

if __name__ == '__main__':
    main()
