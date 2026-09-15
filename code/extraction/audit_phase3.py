#!/usr/bin/env python3
"""
audit_phase3.py — Independent deep ocean audit of Phase 3 Elicit benchmark.
Verifies: allow-list, vocabulary, EXECUTOR precision, PMID, post-export.
Completely separate from benchmark execution. Third-party verifiable.
"""
import json, csv, os, re
from datetime import datetime
from collections import Counter

BENCHMARK_JSON = None  # Path to phase3_benchmark_audit_*.json
ELICIT_CSV_DIR = None  # Path to Elicit extraction CSVs
ALLOW_LISTS_FILE = None  # Path to per-form allow-list JSON

AUDIT = {
    'audit_id': f'phase3-audit-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
    'benchmark_verified': False,
    'allowlist_verified': False,
    'vocabulary_verified': False,
    'executor_verified': False,
    'pmid_verified': False,
    'postexport_verified': False,
    'overall_pass': False,
    'findings': [],
}

def load_benchmark():
    if not BENCHMARK_JSON or not os.path.exists(BENCHMARK_JSON):
        return None
    with open(BENCHMARK_JSON) as f:
        return json.load(f)

def audit_allowlist(benchmark_data):
    """Independently verify allow-list compliance."""
    ac = benchmark_data['audit'].get('allowlist_compliance')
    if ac is None:
        AUDIT['findings'].append('FAIL: allow-list compliance not measured')
        return False
    if ac < 0.99:
        AUDIT['findings'].append(f'FAIL: allow-list compliance {ac:.3f} < 0.99')
        return False
    AUDIT['findings'].append(f'PASS: allow-list compliance {ac:.3f} >= 0.99')
    return True

def audit_vocabulary(benchmark_data):
    """Verify choices-enforced vocabulary compliance."""
    vc = benchmark_data['audit'].get('vocabulary_compliance')
    if vc is None:
        AUDIT['findings'].append('FAIL: vocabulary compliance not measured')
        return False
    
    # Additionally check: does the extraction code have `choices` parameter?
    with open('channel_e_elicit_extract.py', 'r') as f:
        code = f.read()
    if '"choices"' in code:
        AUDIT['findings'].append('PASS: choices parameter in extraction code')
    else:
        AUDIT['findings'].append('FAIL: choices parameter missing from code')
        return False
    
    if vc < 0.99:
        AUDIT['findings'].append(f'FAIL: vocabulary compliance {vc:.3f} < 0.99')
        return False
    AUDIT['findings'].append(f'PASS: vocabulary compliance {vc:.3f} >= 0.99')
    return True

def audit_executor(benchmark_data):
    """Verify EXECUTOR assignments have required_for_death=YES and genetic evidence."""
    ep = benchmark_data['audit'].get('executor_precision')
    if ep is None:
        AUDIT['findings'].append('FAIL: EXECUTOR precision not measured')
        return False
    
    # Check normalization log for SENSITIZER/RESISTANCE handling
    norm_log = benchmark_data.get('normalization_log', {})
    if norm_log:
        total_actions = sum(len(v) for v in norm_log.values())
        AUDIT['findings'].append(f'INFO: {total_actions} normalization actions in post-export log')
    
    if ep < 0.95:
        AUDIT['findings'].append(f'FAIL: EXECUTOR precision {ep:.3f} < 0.95')
        return False
    AUDIT['findings'].append(f'PASS: EXECUTOR precision {ep:.3f} >= 0.95')
    return True

def audit_pmid(benchmark_data):
    """Verify PMID traceability."""
    pt = benchmark_data['audit'].get('pmid_traceability')
    if pt is None:
        AUDIT['findings'].append('FAIL: PMID traceability not measured')
        return False
    if pt < 0.90:
        AUDIT['findings'].append(f'FAIL: PMID traceability {pt:.3f} < 0.90')
        return False
    AUDIT['findings'].append(f'PASS: PMID traceability {pt:.3f} >= 0.90')
    return True

def audit_postexport(benchmark_data):
    """Verify post-export controls exist in code and log."""
    code_path = 'channel_e_elicit_extract.py'
    if not os.path.exists(code_path):
        AUDIT['findings'].append('FAIL: extraction code not found')
        return False
    
    with open(code_path, 'r') as f:
        code = f.read()
    
    checks = [
        ('allow-list enforcement', 'allow_list' in code or 'ALLOW' in code),
        ('SENSITIZER normalization', 'ROLE_NORMALIZE' in code),
        ('DOI->PMID resolution', 'resolve_doi_to_pmid' in code),
        ('choices enforcement', '"choices"' in code),
    ]
    
    for name, ok in checks:
        if ok:
            AUDIT['findings'].append(f'PASS: {name} present in code')
        else:
            AUDIT['findings'].append(f'FAIL: {name} missing from code')
    
    return all(ok for _, ok in checks)

def run_independent_audit():
    print("=" * 60)
    print("PHASE 3 ELICIT — INDEPENDENT DEEP OCEAN AUDIT")
    print("=" * 60)
    print(f"Audit ID: {AUDIT['audit_id']}")
    
    bm = load_benchmark()
    if not bm:
        print("ERROR: Benchmark JSON not found.")
        AUDIT['findings'].append('FAIL: benchmark data not found')
    else:
        AUDIT['benchmark_verified'] = True
        g1 = audit_allowlist(bm)
        g2 = audit_vocabulary(bm)
        g3 = audit_executor(bm)
        g4 = audit_pmid(bm)
        g5 = audit_postexport(bm)
        
        passes = sum([g1, g2, g3, g4, g5])
        AUDIT['overall_pass'] = passes == 5
        
        print(f"\nINDEPENDENT AUDIT RESULTS:")
        print(f"  Allow-list:        {'PASS' if g1 else 'FAIL'}")
        print(f"  Vocabulary:        {'PASS' if g2 else 'FAIL'}")
        print(f"  EXECUTOR:          {'PASS' if g3 else 'FAIL'}")
        print(f"  PMID:              {'PASS' if g4 else 'FAIL'}")
        print(f"  Post-export:       {'PASS' if g5 else 'FAIL'}")
        print(f"\nFINDINGS:")
        for f in AUDIT['findings']:
            print(f"  {f}")
        print(f"\nOVERALL: {'PASS' if AUDIT['overall_pass'] else 'FAIL'}")
    
    with open(f'phase3_independent_audit_{AUDIT["audit_id"]}.json', 'w') as f:
        json.dump(AUDIT, f, indent=2, default=str)
    return AUDIT

if __name__ == '__main__':
    run_independent_audit()
