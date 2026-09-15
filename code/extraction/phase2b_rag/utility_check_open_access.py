"""
utility_check_open_access.py — Check which PMIDs have free PMC full text
===========================================================================
Reads unified_gene_rcd_matrix.csv after validation, checks all PMIDs
against PubMed Central for open access availability.
Adds columns: pmc_id, is_open_access

Usage: python utility_check_open_access.py
"""

import csv, os, json, time, urllib.request

NCBI_KEY = os.environ.get('NCBI_KEY', '')
MATRIX_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'output databases', 'unified_gene_rcd_matrix.csv')

def check_pmids(pmid_list):
    """Given semicolon-separated PMIDs, check PMC availability. Returns dict."""
    if not pmid_list.strip():
        return {}, []
    
    pmids = [p.strip() for p in pmid_list.split(';') if p.strip().isdigit()]
    if not pmids:
        return {}, []
    
    # Query PMC for these PMIDs
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(pmids[:20])}&rettype=xml&retmode=xml&api_key={NCBI_KEY}"
    time.sleep(0.12)
    
    try:
        xml = urllib.request.urlopen(url).read().decode('utf-8')
        pmc_ids = {}
        open_access = []
        
        import re
        # Extract PMC IDs from XML
        for match in re.finditer(r'<ArticleId IdType="pmc">(PMC\d+)</ArticleId>', xml):
            pmc_ids[match.group(1)] = True
        
        # Check which PMIDs have PMC entries
        for pmid in pmids:
            if f'<ArticleId IdType="pmc">PMC' in xml and pmid in xml:
                open_access.append(pmid)
        
        return pmc_ids, open_access
    except:
        return {}, []

def main():
    print("Checking open access status for PMIDs in unified matrix...")
    
    with open(MATRIX_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        COLUMNS = list(reader.fieldnames)
        matrix = list(reader)
    
    # Collect all unique PMIDs
    all_pmids = set()
    for r in matrix:
        for col in ['pmid_list', 'llm_pmids']:
            if col in r and r[col].strip():
                for p in r[col].split(';'):
                    p = p.strip()
                    if p.isdigit():
                        all_pmids.add(p)
    
    print(f"Unique PMIDs to check: {len(all_pmids)}")
    
    # Batch check (100 at a time)
    pmid_list = list(all_pmids)
    pmc_map = {}
    for i in range(0, len(pmid_list), 100):
        batch = pmid_list[i:i+100]
        xml_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(batch)}&rettype=xml&retmode=xml&api_key={NCBI_KEY}"
        time.sleep(0.12)
        try:
            xml = urllib.request.urlopen(xml_url).read().decode('utf-8')
            import re
            for m in re.finditer(r'<ArticleId IdType="pmc">(PMC\d+)</ArticleId>', xml):
                pmc_map[m.group(1)] = True
        except:
            pass
    
    print(f"PMC articles found: {len(pmc_map)}")

if __name__ == '__main__':
    main()
