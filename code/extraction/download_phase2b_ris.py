#!/usr/bin/env python3
"""Batch RIS + free PDF download for Phase 2B processed articles (~100K/batch for Endnote)."""
import json, urllib.request, os, time

CHECKPOINT = '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/output databases/phase2b_checkpoint.json'
CACHE = '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/output databases/phase2b_pmid_cache.json'
BASE_OUT = '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/output databases/phase2b_references'
BATCH_SIZE = 100000

os.makedirs(BASE_OUT, exist_ok=True)

def build_ris(metadata):
    """Build RIS string with full biblio including PMID + PMCID."""
    lines = []
    if metadata.get('title'): lines.append(f'TI  - {metadata["title"]}')
    for a in metadata.get('authorString', '').split(', '):
        if a.strip(): lines.append(f'AU  - {a.strip()}')
    if metadata.get('journalTitle'): lines.append(f'JO  - {metadata["journalTitle"]}')
    if metadata.get('pubYear'): lines.append(f'PY  - {metadata["pubYear"]}')
    if metadata.get('journalVolume'): lines.append(f'VL  - {metadata["journalVolume"]}')
    if metadata.get('issue'): lines.append(f'IS  - {metadata["issue"]}')
    if metadata.get('pageInfo'): lines.append(f'SP  - {metadata["pageInfo"]}')
    if metadata.get('doi'): lines.append(f'DO  - {metadata["doi"]}')
    if metadata.get('pmid'): lines.append(f'AN  - {metadata["pmid"]}')
    if metadata.get('pmcid'): lines.append(f'C1  - PMCID: {metadata["pmcid"]}')
    lines.append('ER  - ')
    return '\n'.join(lines)

def download_pdf(pmcid, folder):
    """Download free PDF from Europe PMC. Returns True on success."""
    pdf_path = os.path.join(folder, f'{pmcid}.pdf')
    if os.path.exists(pdf_path):
        return True
    url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextPDF'
    try:
        pdf_data = urllib.request.urlopen(url, timeout=60).read()
        if len(pdf_data) > 1000:  # Valid PDF
            with open(pdf_path, 'wb') as f:
                f.write(pdf_data)
            return True
    except:
        pass
    return False

# Load state
with open(CHECKPOINT) as f: cp = json.load(f)
with open(CACHE) as f: cache = json.load(f)

# Build PMCID->PMID reverse lookup
pmcid_to_pmid = {}
for pmid, info in cache.items():
    if isinstance(info, dict) and info.get('pmcid'):
        pmcid_to_pmid[info['pmcid']] = pmid

pmcids = [p for p in cp.get('processed_pmcids', []) if p.startswith('PMC')]
batches = (len(pmcids) + BATCH_SIZE - 1) // BATCH_SIZE
print(f"Processing {len(pmcids):,} PMCIDs in {batches} batch(es) of ~{BATCH_SIZE:,}")

total_ris = 0
total_pdf = 0

for batch_num in range(batches):
    start = batch_num * BATCH_SIZE
    batch_pmcids = pmcids[start:start + BATCH_SIZE]
    batch_dir = os.path.join(BASE_OUT, f'batch_{batch_num+1:02d}')
    os.makedirs(batch_dir, exist_ok=True)
    
    # Create combined RIS file for this batch
    batch_ris_path = os.path.join(batch_dir, f'batch_{batch_num+1:02d}.ris')
    
    if not os.path.exists(batch_ris_path):
        ris_entries = []
        batch_built = 0
        
        for i, pmcid in enumerate(batch_pmcids):
            pmid = pmcid_to_pmid.get(pmcid, '')
            if not pmid:
                continue
            
            url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:{pmid}&format=json&resultType=core'
            try:
                data = json.loads(urllib.request.urlopen(url, timeout=10).read().decode('utf-8'))
                results = data.get('resultList', {}).get('result', [])
                if results:
                    metadata = results[0]
                    metadata['pmcid'] = pmcid
                    ris_entries.append(build_ris(metadata))
                    batch_built += 1
            except:
                pass
            
            if (i+1) % 500 == 0:
                pdf_so_far = total_pdf + sum(1 for p in batch_pmcids[:i+1] if os.path.exists(os.path.join(batch_dir, f'{p}.pdf')))
                print(f"  Batch {batch_num+1}: {i+1:,}/{len(batch_pmcids):,} | {batch_built:,} RIS | PDFs: {pdf_so_far:,}")
            time.sleep(0.1)
        
        if ris_entries:
            with open(batch_ris_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(ris_entries))
            total_ris += batch_built
            print(f"  Batch {batch_num+1} RIS saved: {batch_built:,} entries -> {batch_ris_path}")
    
    # Download PDFs for this batch (only new ones)
    pdf_count = 0
    for i, pmcid in enumerate(batch_pmcids):
        if download_pdf(pmcid, batch_dir):
            pdf_count += 1
        if (i+1) % 200 == 0:
            print(f"  Batch {batch_num+1} PDFs: {i+1:,}/{len(batch_pmcids):,} | {pdf_count:,} downloaded")
    
    total_pdf += pdf_count
    print(f"Batch {batch_num+1}: {pdf_count:,} PDFs downloaded")

print(f"\nDone: {total_ris:,} RIS entries | {total_pdf:,} PDFs | {batches} batches in {BASE_OUT}")
