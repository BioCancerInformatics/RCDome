"""
utility_preflight_check.py — Pre-Flight Check for Phase 2B
============================================================
Verifies all prerequisites before the deep PDF RAG pipeline runs.
Run before channel_c_deep_pdf_rag.py
"""

import os, sys, shutil

def check(msg, condition):
    status = "PASS" if condition else "FAIL"
    print(f"  {status:6s} {msg}")
    return condition

def main():
    print("=" * 60)
    print("PHASE 2B PRE-FLIGHT CHECK")
    print("=" * 60)
    
    all_pass = True
    
    # 1. Python packages
    print("\n1. DEPENDENCIES")
    try:
        import fitz; all_pass &= check("PyMuPDF (fitz)", True)
    except ImportError:
        all_pass &= check("PyMuPDF (fitz) — install: pip install PyMuPDF", False)
    
    try:
        import openpyxl; all_pass &= check("openpyxl", True)
    except ImportError:
        all_pass &= check("openpyxl", False)
    
    try:
        import urllib.request; all_pass &= check("urllib", True)
    except:
        all_pass &= check("urllib", False)
    
    # 2. API keys
    print("\n2. API KEYS")
    ncbi = os.environ.get('NCBI_KEY', '')
    ds = os.environ.get('DEEPSEEK_KEY', '')
    all_pass &= check("NCBI_KEY set", bool(ncbi))
    all_pass &= check("DEEPSEEK_KEY set", bool(ds))
    
    # 3. Input files
    print("\n3. INPUT FILES")
    base = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base, '..', '..', 'output databases')
    
    matrix = os.path.join(output_dir, 'unified_gene_rcd_matrix.csv')
    all_pass &= check(f"Unified matrix: {matrix}", os.path.exists(matrix))
    
    if os.path.exists(matrix):
        import csv
        with open(matrix) as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames
            rows = sum(1 for _ in reader)
        all_pass &= check(f"  Rows: {rows:,}, Columns: {len(cols)}", True)
        needed = ['evidence_tier', 'llm_status', 'pmid_list', 'llm_pmids']
        for col in needed:
            all_pass &= check(f"  Column '{col}' present", col in cols)
    
    # 4. Output directory
    print("\n4. OUTPUT DIRECTORY")
    pdf_dir = os.path.join(output_dir, 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    all_pass &= check(f"PDF directory: {pdf_dir}", os.path.exists(pdf_dir))
    
    accum = os.path.join(output_dir, 'phase2b_accumulation.json')
    all_pass &= check(f"Accumulation file will be: {accum}", True)
    
    # 5. Disk space
    print("\n5. DISK SPACE")
    free_gb = shutil.disk_usage(output_dir).free / (1024**3)
    all_pass &= check(f"Free space: {free_gb:.1f} GB (need ~5 GB)", free_gb >= 5)
    
    # 6. Ground truth PDFs
    print("\n6. GROUND TRUTH PDFs")
    ground_truth = {
        'PMC4076414': 'Yang 2014 — GPX4/Ferroptosis',
        'PMC8369836': 'Cai 2014 — MLKL/Necroptosis',
        'PMC5010048': 'Sborgi 2016 — GSDMD/Pyroptosis',
        'PMC9273333': 'Tsvetkov 2022 — FDX1/Cuproptosis',
    }
    for pmc_id, desc in ground_truth.items():
        pdf_path = os.path.join(pdf_dir, f'{pmc_id}.pdf')
        exists = os.path.exists(pdf_path)
        if not exists:
            # Try to download
            try:
                import urllib.request as ur
                url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/main.pdf"
                ur.urlretrieve(url, pdf_path)
                exists = os.path.exists(pdf_path)
            except:
                pass
        all_pass &= check(f"{desc} ({pmc_id})", exists)
    
    # 7. HGNC data
    print("\n7. HGNC DATA")
    try:
        import urllib.request as ur, json
        req = ur.Request('https://rest.genenames.org/fetch/status/Approved', 
                         headers={'Accept': 'application/json'})
        data = json.loads(ur.urlopen(req).read().decode('utf-8'))
        count = len(data['response']['docs'])
        all_pass &= check(f"HGNC symbols loaded: {count:,}", count > 40000)
    except Exception as e:
        all_pass &= check(f"HGNC API: {str(e)[:60]}", False)
    
    # 8. DeepSeek connectivity
    print("\n8. DEEPSEEK API")
    try:
        import urllib.request as ur, json
        headers = {"Authorization": f"Bearer {ds}", "Content-Type": "application/json"}
        body = {"model": "deepseek-chat", "messages": [{"role": "user", "content": "Say OK"}], "max_tokens": 5}
        req = ur.Request("https://api.deepseek.com/chat/completions", 
                        data=json.dumps(body).encode('utf-8'), headers=headers)
        resp = json.loads(ur.urlopen(req).read().decode('utf-8'))
        ok = resp['choices'][0]['message']['content'].strip() == 'OK'
        all_pass &= check(f"DeepSeek test: {resp['choices'][0]['message']['content'].strip()}", ok)
    except Exception as e:
        all_pass &= check(f"DeepSeek API: {str(e)[:60]}", False)
    
    # Summary
    print(f"\n{'='*60}")
    if all_pass:
        print("ALL CHECKS PASSED — Ready for Phase 2B")
    else:
        print("SOME CHECKS FAILED — Fix before running Phase 2B")
    print(f"{'='*60}")
    return all_pass

if __name__ == '__main__':
    main()
