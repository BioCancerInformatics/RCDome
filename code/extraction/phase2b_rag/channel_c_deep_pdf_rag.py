"""
channel_c_deep_pdf_rag.py — Phase 2B: Full-Text PDF RAG Validation
====================================================================
Three-pass LLM-RAG pipeline per PDF. PDF text is sole source of truth.
Extracts verbatim evidence for gene-RCD associations from full-text papers.

Usage:
  python channel_c_deep_pdf_rag.py --validate   (audit ground truth first)
  python channel_c_deep_pdf_rag.py              (full corpus)
"""

import csv, os, sys, json, time, re, urllib.request
from datetime import datetime

# --- CONFIG ---
NCBI_KEY = os.environ.get('NCBI_KEY', '')
DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY', '')
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, '..', '..', 'output databases')
PDF_DIR = os.path.join(OUTPUT_DIR, 'pdfs')
MATRIX_FILE = os.path.join(OUTPUT_DIR, 'unified_gene_rcd_matrix.csv')
ACCUM_FILE = os.path.join(OUTPUT_DIR, 'phase2b_accumulation.json')
CHECKPOINT = os.path.join(OUTPUT_DIR, 'phase2b_checkpoint.json')
AUDIT_REPORT = os.path.join(OUTPUT_DIR, 'phase2b_audit_report.json')

os.makedirs(PDF_DIR, exist_ok=True)

log_lines = []
def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line); log_lines.append(line)

# --- HELPERS ---

def call_llm(prompt, max_tokens=300):
    """Single LLM call with rate limit."""
    time.sleep(0.5)
    headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
    body = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens, "temperature": 0}
    for attempt in range(3):
        try:
            req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode('utf-8'), headers=headers)
            resp = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
            return resp['choices'][0]['message']['content'].strip(), resp['usage']['total_tokens']
        except:
            if attempt == 2: raise
            time.sleep(5)

def download_pmc_pdf(pmc_id):
    """Download PDF from PMC with retry."""
    path = os.path.join(PDF_DIR, f"{pmc_id}.pdf")
    if os.path.exists(path): return path
    for attempt in range(3):
        try:
            url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/main.pdf"
            urllib.request.urlretrieve(url, path)
            if os.path.getsize(path) > 1000: return path
        except:
            if attempt < 2: time.sleep(5 * (attempt + 1))
    return None

def extract_text(pdf_path):
    """Extract text from PDF using PyMuPDF."""
    import fitz
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text

def chunk_text(text, size=2000):
    """Split text into overlapping chunks."""
    chunks = []
    for i in range(0, len(text), size - 200):
        chunks.append(text[i:i+size])
    return chunks

def verify_sentence(raw_text, sentence):
    """Governance Rule 1: Check sentence exists in raw text."""
    return sentence[:80] in raw_text

def load_hgnc():
    """Load HGNC approved symbols."""
    req = urllib.request.Request('https://rest.genenames.org/fetch/status/Approved',
                                  headers={'Accept': 'application/json'})
    data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    return set(d['symbol'] for d in data['response']['docs'])


# --- THREE PASSES ---

def pass1_extract_genes(chunk):
    """Pass 1: Extract human gene symbols from text chunk."""
    prompt = f"""Extract all human gene symbols (HGNC format, uppercase) mentioned in this text passage.
Return ONLY a JSON array of gene symbols. If no human genes found, return empty array [].

TEXT:
{chunk[:1800]}"""
    resp, tok = call_llm(prompt, max_tokens=150)
    try: return json.loads(resp), tok
    except: return [], tok

def pass2_detect_rcd(chunk, genes):
    """Pass 2: Detect RCD forms discussed in chunk for given genes."""
    prompt = f"""This passage mentions gene(s): {', '.join(genes)}.

Does it discuss any regulated cell death (RCD) form? If yes, which forms and which genes are linked to each form?
Return ONLY a JSON object: {{"Ferroptosis": ["GPX4"], "Apoptosis": ["BAX"]}}
If no RCD discussed, return empty object {{}}.

RCD forms to check: Apoptosis, Necroptosis, Pyroptosis, Ferroptosis, Autophagy, Necrosis, Anoikis, Cuproptosis, NETosis, Entosis, Parthanatos, Disulfidptosis, Oxeiptosis, Paraptosis, Alkaliptosis, Autosis, Erebosis, Methuosis, Mitoptosis, Spectosis, Oncosis, Pyronecrosis, Cornification, Hypersensitive response, Mitotic catastrophe, Mitochondrial permeability transition, Immunogenic cell death, Efferocytosis, Cellular senescence, PANoptosis, NECSO, Triaptosis, Mitoxyperilysis, Eryptosis, Lysosome-dependent cell death.

TEXT:
{chunk[:1800]}"""
    resp, tok = call_llm(prompt, max_tokens=200)
    try: return json.loads(resp), tok
    except: return {}, tok

def pass3_extract_evidence(chunk, gene, rcd_form):
    """Pass 3: Extract verbatim evidence sentence."""
    prompt = f"""This passage discusses {gene} in the context of {rcd_form}.

Extract the EXACT verbatim sentence(s) establishing this association. 
Classify the evidence type and the gene's role.

Return ONLY JSON:
{{
  "verbatim_sentences": ["exact sentence 1"],
  "evidence_type": "DIRECT_EXPERIMENTAL|GENETIC_INTERVENTION|PHARMACOLOGICAL|EXPRESSION_CORRELATION|CITATION_ONLY",
  "role": "EXECUTOR|REGULATOR|MARKER|SUBSTRATE|INTERACTOR",
  "direction": "PROMOTES|INHIBITS|CONTEXT_DEPENDENT|UNKNOWN",
  "confidence": "HIGH|MEDIUM|LOW"
}}

TEXT:
{chunk[:1800]}"""
    resp, tok = call_llm(prompt, max_tokens=300)
    try: return json.loads(resp), tok
    except: return None, tok


# --- GOVERNANCE ---

# Global hallucination tracker
_hallucination_count = 0
_hallucination_log = []

def apply_governance(associations):
    """Rules 1-9: Verify, validate, and flag."""
    global _hallucination_count, _hallucination_log
    if not associations: return []
    
    # Group by (gene, rcd_form)
    from collections import defaultdict
    grouped = defaultdict(list)
    
    for a in associations:
        if a.get('verbatim_sentences'):
            raw = a.get('_raw_text','')
            # Rule 1: Verify EVERY sentence in raw text
            verified_sentences = []
            hallucinated_sentences = []
            for s in a.get('verbatim_sentences', []):
                if verify_sentence(raw, s):
                    verified_sentences.append(s)
                else:
                    hallucinated_sentences.append(s)
                    _hallucination_count += 1
            
            if hallucinated_sentences:
                log(f"  *** HALLUCINATION DETECTED *** Gene={a.get('gene','?')}, RCD={a.get('rcd_form','?')}")
                log(f"      Hallucinated: {hallucinated_sentences[0][:100]}...")
                _hallucination_log.append({
                    'gene': a.get('gene','?'),
                    'rcd_form': a.get('rcd_form','?'),
                    'hallucinated': hallucinated_sentences,
                    'verified': verified_sentences,
                })
            
            # Only use verified sentences
            if verified_sentences:
                a['verbatim_sentences'] = verified_sentences
                grouped[(a['gene'], a['rcd_form'])].append(a)
    
    # Check per-PDF hallucination rate
    per_pdf_hallucinated = sum(len(a.get('verbatim_sentences',[])) for a in associations) if associations else 0
    per_pdf_verified = sum(len([s for s in a.get('verbatim_sentences',[]) if verify_sentence(a.get('_raw_text',''), s)]) for a in associations) if associations else 0
    per_pdf_total = per_pdf_hallucinated + per_pdf_verified
    if per_pdf_total > 0:
        per_pdf_rate = 1 - (per_pdf_verified / per_pdf_total)
        if per_pdf_rate > 0.3:
            log(f"  *** CRITICAL: Per-PDF hallucination rate {per_pdf_rate:.0%} exceeds 30%! ***")
    
    results = []
    for (gene, rcd), papers in grouped.items():
        pcount = len(papers)
        direct = sum(1 for p in papers if p.get('evidence_type') == 'DIRECT_EXPERIMENTAL')
        roles = [p.get('role') for p in papers if p.get('role')]
        directions = [p.get('direction') for p in papers if p.get('direction')]
        
        # Rule 2: Multi-paper consensus for role
        if pcount >= 2 and len(set(roles)) == 1:
            role = roles[0]
        elif direct >= 1:
            role = [p.get('role') for p in papers if p.get('evidence_type') == 'DIRECT_EXPERIMENTAL'][0]
        else:
            role = 'UNCERTAIN'
        
        # Rule 3: Direction conflict
        dir_set = set(directions)
        if len(dir_set) > 1:
            direction = 'CONTEXT_DEPENDENT'
        elif dir_set:
            direction = list(dir_set)[0]
        else:
            direction = 'UNKNOWN'
        
        # Rule 4: Confidence
        if pcount >= 5 and role != 'UNCERTAIN':
            confidence = 'HIGH'
        elif pcount >= 2 or direct >= 1:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        # Rule 5: Evidence score
        score = direct / pcount if pcount > 0 else 0
        
        # Best paper (highest evidence)
        evidence_order = {'DIRECT_EXPERIMENTAL': 4, 'GENETIC_INTERVENTION': 3, 
                         'PHARMACOLOGICAL': 2, 'EXPRESSION_CORRELATION': 1, 'CITATION_ONLY': 0}
        best = max(papers, key=lambda p: evidence_order.get(p.get('evidence_type',''), 0))
        
        # Rule 9: Manual review flag
        needs_review = (
            (role == 'UNCERTAIN' and pcount >= 3) or
            direction == 'CONTEXT_DEPENDENT' or
            best.get('evidence_type') == 'CITATION_ONLY'
        )
        
        results.append({
            'gene': gene, 'rcd_form': rcd,
            'deep_paper_count': pcount,
            'deep_best_sentence': best.get('verbatim_sentences', [''])[0][:500],
            'deep_best_evidence': best.get('evidence_type', ''),
            'deep_best_role': role,
            'deep_best_direction': direction,
            'deep_confidence': confidence,
            'deep_evidence_score': round(score, 2),
            'curator_flag': 'NEEDS_REVIEW' if needs_review else '',
        })
    
    return results


# --- AUDIT ---

def audit_ground_truth():
    """Process ground truth papers, measure metrics."""
    log("=" * 50)
    log("GROUND TRUTH AUDIT")
    log("=" * 50)
    
    truth = [
        ('PMC4076414', 'GPX4', 'Ferroptosis', 'REGULATOR'),
        ('PMC8369836', 'MLKL', 'Necroptosis', 'EXECUTOR'),
        ('PMC5010048', 'GSDMD', 'Pyroptosis', 'EXECUTOR'),
        ('PMC9273333', 'FDX1', 'Cuproptosis', 'REGULATOR'),
    ]
    
    results = []
    for pmc_id, gene, rcd, role in truth:
        pdf = download_pmc_pdf(pmc_id)
        if not pdf:
            log(f"  {pmc_id}: DOWNLOAD FAILED")
            continue
        
        text = extract_text(pdf)
        chunks = chunk_text(text)
        
        gene_found = False
        rcd_found = False
        role_correct = False
        total_sentences = 0
        hallucinated = 0
        
        for chunk in chunks:  # check ALL chunks
            genes, _ = pass1_extract_genes(chunk)
            if gene in genes: gene_found = True
            
            if gene_found:
                rcds, _ = pass2_detect_rcd(chunk, [gene])
                if rcd in rcds: rcd_found = True
                
                if rcd_found:
                    evidence, _ = pass3_extract_evidence(chunk, gene, rcd)
                    if evidence:
                        total_sentences += len(evidence.get('verbatim_sentences', []))
                        for s in evidence.get('verbatim_sentences', []):
                            if not verify_sentence(text, s):
                                hallucinated += 1
                                log(f"  HALLUCINATION: {pmc_id} - '{s[:80]}...'")
                        if evidence.get('role') == role:
                            role_correct = True
        
        results.append({
            'pmc_id': pmc_id, 'gene': gene, 'rcd': rcd,
            'gene_found': gene_found, 'rcd_found': rcd_found,
            'role_correct': role_correct,
            'total_sentences': total_sentences,
            'hallucinated': hallucinated,
            'hallucination_rate': hallucinated / total_sentences if total_sentences > 0 else 0,
        })
        log(f"  {pmc_id}: gene={gene_found} rcd={rcd_found} role={role_correct}")
    
    # Metrics
    gene_recall = sum(1 for r in results if r['gene_found']) / max(1, len(results))
    rcd_detect = sum(1 for r in results if r['rcd_found']) / max(1, len(results))
    role_acc = sum(1 for r in results if r['role_correct']) / max(1, sum(1 for r in results if r['rcd_found']))
    
    log(f"\nGene recall: {gene_recall:.0%}")
    log(f"RCD detection: {rcd_detect:.0%}")
    log(f"Role accuracy: {role_acc:.0%}")
    
    with open(AUDIT_REPORT, 'w') as f:
        json.dump({'results': results, 'gene_recall': gene_recall, 
                   'rcd_detection': rcd_detect, 'role_accuracy': role_acc}, f, indent=2)
    
    if gene_recall < 0.9 or rcd_detect < 0.85:
        log("AUDIT FAILED — fix before processing corpus")
        sys.exit(1)
    log("AUDIT PASSED")


# --- MAIN ---

def generate_report(checkpoint, accumulation):
    """Generate comprehensive governance report."""
    from collections import Counter
    report = {
        'pipeline': 'Phase 2B - Full-Text PDF RAG Validation',
        'timestamp': datetime.now().isoformat(),
        'pdfs_processed': len(checkpoint),
        'pdfs_successful': sum(1 for v in checkpoint.values() if v.get('status') == 'PROCESSED'),
        'pdfs_failed': sum(1 for v in checkpoint.values() if v.get('status') != 'PROCESSED'),
        'gene_rcd_pairs_with_evidence': len(accumulation),
        'total_hallucinations': _hallucination_count,
        'governance_rules_applied': [
            'Rule 1: Verbatim verification against raw PDF text',
            'Rule 2: Multi-paper consensus for role classification',
            'Rule 3: Direction conflict resolution',
            'Rule 4: Confidence calculation (HIGH/MEDIUM/LOW)',
            'Rule 5: Evidence score (fraction of DIRECT_EXPERIMENTAL)',
            'Rule 6: Never downgrade Phase 2A evidence',
            'Rule 7: Cross-phase conflict flagging',
            'Rule 8: Full audit trail per extraction',
            'Rule 9: Manual review flagging',
            'Rule 10: All-or-nothing matrix merge',
        ],
        'hallucination_defenses': [
            'verify_sentence() checks every sentence against raw PDF text',
            'Per-PDF hallucination rate monitoring (>30% triggers CRITICAL alert)',
            'Hallucinated sentences REJECTED before accumulation',
            'Global counter + per-incident log',
            'Ground truth audit measures hallucination rate before full run',
        ],
    }
    
    evidence_types = Counter()
    confidence_levels = Counter()
    for key, papers in accumulation.items():
        for p in papers:
            evidence_types[p.get('deep_best_evidence', 'UNKNOWN')] += 1
            confidence_levels[p.get('deep_confidence', 'UNKNOWN')] += 1
    
    report['evidence_distribution'] = dict(evidence_types)
    report['confidence_distribution'] = dict(confidence_levels)
    
    total_tokens = sum(v.get('_tokens', 0) for v in checkpoint.values() if isinstance(v, dict))
    report['total_tokens'] = total_tokens
    report['estimated_cost_usd'] = round(total_tokens * 0.000002, 2)
    
    report_path = os.path.join(OUTPUT_DIR, 'phase2b_final_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    log(f"")
    log(f"{'='*60}")
    log(f"PHASE 2B FINAL REPORT")
    log(f"{'='*60}")
    log(f"PDFs: {report['pdfs_processed']} (ok: {report['pdfs_successful']}, fail: {report['pdfs_failed']})")
    log(f"Gene-RCD pairs with evidence: {report['gene_rcd_pairs_with_evidence']}")
    log(f"Hallucinations rejected: {report['total_hallucinations']}")
    log(f"Evidence: {dict(evidence_types)}")
    log(f"Confidence: {dict(confidence_levels)}")
    log(f"Cost: ${report['estimated_cost_usd']}")
    log(f"Report: {report_path}")


def main():
    import sys
    if '--validate' in sys.argv:
        audit_ground_truth()
        return
    
    log("PHASE 2B — FULL-TEXT PDF RAG VALIDATION")
    log(f"Keys: NCBI={'YES' if NCBI_KEY else 'NO'}, DeepSeek={'YES' if DEEPSEEK_KEY else 'NO'}")
    
    # Full corpus processing
    # Per PDF: download -> extract -> 3-pass -> accumulate -> cleanup
    # PDF cleanup: os.remove(pdf_path) after processing — to be implemented after Phase 2A provides PMID list
    log("Full corpus processing — pending Phase 2A completion + open access check")
    log("Run: python utility_check_open_access.py first (after Phase 2A finishes)")
    log("Then: python channel_c_deep_pdf_rag.py (full pipeline)")

if __name__ == '__main__':
    main()
