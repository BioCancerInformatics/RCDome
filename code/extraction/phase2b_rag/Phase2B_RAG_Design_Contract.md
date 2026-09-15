# LLM-RAG PDF Pipeline — Design Contract

## SHOULD DO

1. **PDF as sole source of truth** — only extract what's IN the text, never use LLM knowledge
2. **Sequential, one PDF at a time** — no parallel processing of PDFs
3. **Extract ALL human genes** from full text → cross-ref with our 9,037 list
4. **Three-pass per PDF:**
   - Pass 1: gene extraction from chunks
   - Pass 2: RCD form detection for matched genes
   - Pass 3: verbatim evidence extraction + classification
5. **Save progress per PDF** — resumable if interrupted
6. **Accumulate in separate JSON** — only merge into matrix at end
7. **Rate-limit LLM calls** — 0.5s gap between calls
8. **Track tokens and cost** — per PDF and cumulative
9. **Log everything** — timestamped audit trail
10. **Output evidence with exact source** — PMC ID, passage location, verbatim sentence

## SHOULD NOT DO

1. **NEVER modify the matrix during processing** — only at final merge
2. **NEVER use LLM knowledge** — only what's IN the PDF text
3. **NEVER invent gene-RCD associations** — only extract, never create
4. **NEVER skip a PDF** — process all, even if no evidence found (log it)
5. **NEVER exceed API limits** — hard-coded rate limiter
6. **NEVER hardcode API keys** — always from environment

## MUST HAVE

1. **Retry logic** — 3 attempts with exponential backoff for API failures
2. **Progress persistence** — JSON checkpoint after every PDF
3. **Cost tracking** — cumulative token count logged
4. **Audit log** — every decision, every extraction, every failure
5. **Output schema** matching matrix column format
6. **.env file** for API keys, never in code
7. **PDF cleanup** — delete after processing (storage management)
8. **Graceful shutdown** — Ctrl+C saves progress before exit

## OUTPUT SCHEMA (per PDF, accumulated)

```json
{
  "pmc_id": "PMC12345",
  "pmid": "12345678", 
  "title": "Paper title",
  "year": 2025,
  "status": "PROCESSED" | "NO_GENES_FOUND" | "NO_RCD_FOUND" | "FAILED",
  "genes_found": ["GPX4", "ACSL4"],
  "rcd_forms_found": ["Ferroptosis"],
  "associations": [
    {
      "gene": "GPX4",
      "rcd_form": "Ferroptosis",
      "verbatim_sentence": "GPX4 is the central repressor of ferroptosis...",
      "evidence_type": "DIRECT_EXPERIMENTAL",
      "role": "EXECUTOR",
      "direction": "INHIBITS",
      "confidence": "HIGH",
      "passage_location": "Results section, paragraph 3"
    }
  ],
  "tokens_used": 95000,
  "processing_time_seconds": 45.2
}
```

## MATRIX COLUMNS ADDED (after merge)

| Column | Type | Example |
|--------|------|---------|
| `deep_pmc_ids` | text | PMC12345;PMC67890 |
| `deep_paper_count` | int | 12 |
| `deep_best_sentence` | text | "GPX4 is the central repressor..." |
| `deep_best_evidence` | text | DIRECT_EXPERIMENTAL |
| `deep_best_role` | text | EXECUTOR |
| `deep_best_direction` | text | INHIBITS |
| `deep_confidence` | text | HIGH |
| `deep_evidence_score` | float | 0.92 |

## WHAT MAKES THIS DIFFERENT FROM PHASE 2A

| Phase 2A (Abstract) | Phase 2B (Full-Text RAG) |
|---------------------|--------------------------|
| LLM reads abstracts only | LLM reads complete PDF body |
| "Is gene X in RCD Y?" per pair | Extract ALL genes, then ALL RCD forms |
| Misses evidence in body text | Catches everything in full text |
| One LLM call per pair | 40 LLM calls per PDF |
| $0.20 total | $190 total |
| ~25 hours | ~55 hours |


## GOVERNANCE RULES

### Rule 1: Verbatim-Only Verification
Every `deep_best_sentence` MUST be verifiable. The LLM returns the exact sentence from the PDF.
Before storing, the code verifies the sentence appears in the extracted text.
If the sentence is NOT found in the raw text → REJECTED (hallucination detected).

### Rule 2: Multi-Paper Consensus Required for Role Classification
A gene's role (EXECUTOR/REGULATOR/MARKER) is only assigned if:
- ≥ 2 papers agree on the same role, OR
- 1 paper with DIRECT_EXPERIMENTAL evidence
Otherwise → role = "UNCERTAIN"

### Rule 3: Direction Conflict Resolution
If papers disagree on direction (PROMOTES vs INHIBITS):
- Both directions recorded in `deep_direction` as "CONTEXT_DEPENDENT"
- Individual paper directions stored in accumulation JSON for audit
- Flagged for manual review

### Rule 4: Confidence Calculation
```
deep_confidence = HIGH   if deep_paper_count ≥ 5 AND role ≠ UNCERTAIN
deep_confidence = MEDIUM if deep_paper_count ≥ 2 OR deep_best_evidence = DIRECT_EXPERIMENTAL
deep_confidence = LOW    if deep_paper_count = 1 AND evidence ≠ DIRECT_EXPERIMENTAL
```

### Rule 5: Evidence Score
```
deep_evidence_score = papers_with_direct_experimental / deep_paper_count
```
Ranges 0–1.0. Higher = more papers with direct experimental evidence.

### Rule 6: Never Downgrade
Phase 2B evidence only UPGRADES or CONFIRMS — never downgrades.
If Phase 2A said CONFIRMED and Phase 2B finds no PDF evidence → Phase 2A status preserved.
Rationale: absence of PDF evidence ≠ absence of evidence (paper may not be open access).

### Rule 7: Conflict with Phase 2A
If Phase 2A said UNCLEAR but Phase 2B finds strong evidence → upgraded.
If Phase 2A said CONFIRMED but Phase 2B finds contradictory evidence → flagged for manual review.
The `deep_confidence` column records the Phase 2B verdict independently.

### Rule 8: Audit Trail
Every evidence extraction stores:
- PMC ID, passage number, verbatim sentence
- Whether sentence was verified in raw text (Rule 1)
- LLM response (raw JSON) for reproducibility
- Timestamp and token count

### Rule 9: Manual Review Flag
Rows meeting ANY of these criteria are flagged `curator_flag = NEEDS_REVIEW`:
- Role = UNCERTAIN but deep_paper_count ≥ 3
- Direction conflict (CONTEXT_DEPENDENT)
- Phase 2A vs Phase 2B contradiction
- deep_best_evidence = "CITATION_ONLY" (paper just cites another paper)

### Rule 10: Matrix Merge — All or Nothing
Phase 2B results accumulated in JSON. Only merged into matrix when ALL PDFs processed.
If pipeline interrupted → partial results preserved, no matrix corruption.


## INDEPENDENT AUDIT & VALIDATION

### Ground Truth Set
Before processing the full corpus, 10 well-established papers are processed through the exact same pipeline. These papers are selected because their gene-RCD associations are definitively known:

| Paper | Gene | RCD Form | Expected Role | Expected Sentence |
|-------|------|----------|---------------|-------------------|
| Dixon et al. 2012 (PMC3367386) | GPX4 | Ferroptosis | EXECUTOR | "GPX4 is an essential regulator of ferroptotic cancer cell death" |
| Sun et al. 2012 (PMC3308724) | RIPK3 | Necroptosis | EXECUTOR | Contains direct experimental evidence |
| Shi et al. 2015 (PMC4660266) | GSDMD | Pyroptosis | EXECUTOR | Contains direct experimental evidence |
| Tsvetkov et al. 2022 (PMC9273333) | FDX1 | Cuproptosis | EXECUTOR | Contains direct experimental evidence |
| Liu et al. 2023 | SLC7A11 | Disulfidptosis | REGULATOR | Contains direct experimental evidence |

### Audit Metrics

| Metric | What it measures | Target |
|--------|-----------------|--------|
| **Gene recall** | % of known genes correctly extracted from PDF | ≥ 90% |
| **RCD detection** | % of RCD forms correctly identified | ≥ 85% |
| **Role accuracy** | % of correct role classification | ≥ 80% |
| **Sentence verifiability** | % of extracted sentences found in raw text (Rule 1) | 100% |
| **Hallucination rate** | % of sentences NOT found in raw text | 0% |

### Audit Mode
```
python channel_c_deep_pdf_rag.py --validate
```
Processes only the ground truth papers, reports all 5 metrics.
Pipeline does NOT proceed to full corpus until audit passes.

### Reproducibility
- Ground truth papers cached locally (PMC IDs fixed)
- Raw LLM responses saved for each ground truth paper
- Audit report generated as `phase2b_audit_report.json`
- Same code, same prompts, same PDFs → same results (deterministic with temperature=0)


## EXECUTION SEQUENCE

```
channel_c_deep_pdf_rag.py
│
├── STEP 0: Load .env, HGNC symbols, unified matrix
│
├── STEP 1: --validate MODE (ground truth audit)
│   ├── Process 5 ground-truth PDFs
│   ├── Measure: gene recall, RCD detection, role accuracy, 
│   │           sentence verifiability, hallucination rate
│   ├── Generate phase2b_audit_report.json
│   └── If any metric < target → ABORT (do not process corpus)
│
├── STEP 2: Load open-access PMID list (from utility_check_open_access.py output)
│
├── STEP 3: Process ALL PDFs (sequential, one at a time)
│   ├── Per PDF loop:
│   │   ├── Download PDF from PMC
│   │   ├── Extract text (PyMuPDF)
│   │   ├── Chunk into ~2000-char passages
│   │   ├── Pass 1: Gene extraction (25 LLM calls)
│   │   ├── Pass 2: RCD detection (only chunks with genes)
│   │   ├── Pass 3: Evidence extraction (only chunks with gene+RCD)
│   │   ├── Apply Governance Rules 1-10
│   │   ├── Accumulate in phase2b_accumulation.json
│   │   ├── Delete PDF (storage management)
│   │   └── Save checkpoint
│   └── Log progress every 100 PDFs
│
├── STEP 4: Merge accumulation → unified matrix
│   ├── For each gene-RCD pair in matrix:
│   │   ├── Aggregate evidence from all PDFs
│   │   ├── Compute deep_confidence, deep_evidence_score
│   │   ├── Apply tier upgrade logic
│   │   └── Flag manual review rows
│   └── Write updated matrix
│
├── STEP 5: Generate audit report
│   ├── Summary statistics
│   ├── Manual review flags
│   ├── Cost report (tokens, dollars)
│   └── Processing time
│
└── DONE
```

## CODE STRUCTURE

```python
# channel_c_deep_pdf_rag.py

def audit_ground_truth():        # STEP 1
def download_pmc_pdf(pmc_id):    # STEP 3 helper
def extract_text(pdf_path):      # STEP 3 helper  
def chunk_text(text):            # STEP 3 helper
def pass1_extract_genes(chunk):  # STEP 3 - Pass 1
def pass2_detect_rcd(chunk, genes):  # STEP 3 - Pass 2
def pass3_extract_evidence(chunk, gene, rcd):  # STEP 3 - Pass 3
def verify_sentence(raw_text, sentence):  # Governance Rule 1
def apply_governance(accumulation):       # Governance Rules 2-9
def merge_to_matrix(accumulation):        # STEP 4
def generate_report():                    # STEP 5

def main():
    if '--validate' in sys.argv:
        audit_ground_truth()
        return
    # Full pipeline...
```


## GAPS RESOLVED

### 1. Tier Upgrade Table

| Phase 2A Tier | Phase 2B Evidence | Upgraded Tier |
|---------------|-------------------|---------------|
| T2 | deep_confidence = HIGH + role = EXECUTOR | **T1** |
| T2 | deep_confidence = HIGH + role ≠ EXECUTOR | **T2+** |
| T2 | deep_confidence = MEDIUM | **T2** (unchanged) |
| T3 | deep_confidence = HIGH | **T2** |
| T3 | deep_confidence = MEDIUM + deep_paper_count ≥ 3 | **T2** |
| T4 | deep_confidence = HIGH | **T3** |
| T4 | deep_confidence = MEDIUM | **T3** |
| Any | deep_confidence = LOW | Unchanged |
| Any | No Phase 2B coverage (not open access) | Unchanged (Rule 6) |

### 2. PMC ID List Source

PMC IDs come from `utility_check_open_access.py` output:
- Input: `unified_gene_rcd_matrix.csv` (columns: `pmid_list`, `llm_pmids`)
- Queries PubMed E-utilities for PMC availability
- Output: `pmc_open_access_list.json` → `{pmid: pmc_id, is_oa: true/false}`
- Phase 2B reads this JSON to get downloadable PMC IDs

### 3. PDF Download Retry Logic

```python
def download_pmc_pdf(pmc_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/main.pdf"
            urllib.request.urlretrieve(url, f"pdfs/{pmc_id}.pdf")
            return f"pdfs/{pmc_id}.pdf"
        except:
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))  # 5s, 10s, 15s backoff
    return None  # failed after 3 retries
```

### 4. Disk Space Check

```python
import shutil
def check_disk_space(required_mb=5000):
    free = shutil.disk_usage(".").free / (1024**2)
    if free < required_mb:
        raise RuntimeError(f"Insufficient disk space: {free:.0f}MB free, {required_mb}MB required")
```
Checked at startup and every 500 PDFs.
