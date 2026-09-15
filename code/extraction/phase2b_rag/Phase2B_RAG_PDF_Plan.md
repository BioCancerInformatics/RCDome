# RCDome — Phase 2B: Comprehensive PDF Cross-Reference Plan
## Full-Text as Source of Truth for ALL Gene-RCD Pairs

**Date:** 2026-07-23
**Principle:** The abstract screen (Phase 2A) misses evidence buried in full text. The PDF corpus is the definitive source. Cross-reference all 18,221 gene-RCD pairs against all ~10,000 open-access PDFs.

---

## 1. THE APPROACH: Inverted Search

Instead of asking "is gene X in RCD Y?" per pair (18K queries × 10K PDFs = impossible), we invert:

```
For each PDF:
  1. Extract all gene symbols mentioned in the full text
  2. Cross-reference with our 9,037 gene symbols
  3. For matched genes, check which RCD forms the paper discusses
  4. Record every gene-RCD pair found in the paper
  5. Extract verbatim sentences as evidence
```

This is O(10K PDFs × gene extraction per PDF) instead of O(18K pairs × 10K PDFs).

---

## 2. PIPELINE PER PDF

```
PDF → text extraction → split into passages (~2000 chars) →
  Pass 1: Extract ALL human gene symbols from passage →
  Pass 2: For matched genes, determine which RCD forms are discussed →
  Pass 3: Extract verbatim evidence sentences →
  Store in accumulation database
```

### 2.1 Pass 1: Gene Symbol Extraction

```
PROMPT:
Extract all human gene symbols mentioned in this passage. 
Return ONLY a JSON array of HGNC gene symbols. 
If none, return empty array.

PASSAGE:
{chunk}

OUTPUT: ["GPX4", "TP53", "BAX", ...]
```

### 2.2 Pass 2: RCD Form Detection

For passages containing matched genes:

```
PROMPT:
This passage mentions gene(s): {matched_genes}.

Does this passage discuss any form of regulated cell death (RCD)?
If yes, which forms? Return JSON:
{
  "rcd_forms": ["Ferroptosis", "Apoptosis"],
  "genes_by_form": {"Ferroptosis": ["GPX4"], "Apoptosis": ["BAX"]}
}
If no RCD forms discussed, return {"rcd_forms": []}.
```

### 2.3 Pass 3: Evidence Extraction

For confirmed gene-RCD pairs:

```
PROMPT:
This passage discusses {gene} in the context of {rcd_form}.

Extract the verbatim sentence(s) establishing this association.
Classify the evidence type and the gene's role.

PASSAGE:
{chunk}

OUTPUT (JSON):
{
  "verbatim_sentences": ["exact sentence 1", "exact sentence 2"],
  "evidence_type": "DIRECT_EXPERIMENTAL|GENETIC_INTERVENTION|PHARMACOLOGICAL|EXPRESSION_CORRELATION|CITATION_ONLY",
  "role": "EXECUTOR|REGULATOR|MARKER|SUBSTRATE|INTERACTOR",
  "direction": "PROMOTES|INHIBITS|CONTEXT_DEPENDENT|UNKNOWN",
  "confidence": "HIGH|MEDIUM|LOW"
}
```

---

## 3. COST ANALYSIS

Per PDF (~30 pages, ~15,000 words, ~25 passages):

| Pass | Queries per PDF | Tokens per query | Total tokens/PDF |
|------|----------------|-----------------|------------------|
| Pass 1: Gene extraction | 25 | ~2,500 | 62,500 |
| Pass 2: RCD detection | ~10 (passages with genes) | ~2,000 | 20,000 |
| Pass 3: Evidence extraction | ~5 (passages with RCD) | ~2,500 | 12,500 |
| **Total per PDF** | **~40** | | **~95,000** |

**Total: 10,000 PDFs × 95,000 tokens = 950M tokens × $0.000002 = ~$1,900**

---

## 4. COST OPTIMIZATION

| Strategy | PDFs | Cost |
|----------|------|------|
| All 10K PDFs, all 3 passes | 10,000 | ~$1,900 |
| Pass 1 only (gene extraction), Pass 2-3 only if genes found | 10,000 | ~$1,200 |
| Top 5,000 PDFs by citation count | 5,000 | ~$950 |
| Phase 2A pre-filter: only PDFs for CONFIRMED pairs | ~5,000 | ~$950 |

---

## 5. OUTPUT: ACCUMULATION DATABASE

Not modifying the matrix per PDF — accumulate in a separate database, then merge at the end:

```json
{
  "pmc_id": "PMC12345",
  "pmid": "12345678",
  "title": "Ferroptosis in cancer...",
  "year": 2025,
  "genes_found": ["GPX4", "ACSL4", "TP53"],
  "rcd_forms_discussed": ["Ferroptosis", "Apoptosis"],
  "associations": [
    {
      "gene": "GPX4",
      "rcd_form": "Ferroptosis",
      "verbatim_sentence": "GPX4 is the central repressor of ferroptosis...",
      "evidence_type": "DIRECT_EXPERIMENTAL",
      "role": "EXECUTOR",
      "direction": "INHIBITS",
      "confidence": "HIGH"
    }
  ]
}
```

---

## 6. NEW MATRIX COLUMNS (After Merge)

| Column | Description |
|--------|-------------|
| `deep_pmc_ids` | PMC IDs containing evidence for this pair |
| `deep_paper_count` | Number of papers supporting this pair |
| `deep_verbatim_sentence` | Best evidence sentence from full-text |
| `deep_evidence_type` | DIRECT_EXPERIMENTAL / etc. |
| `deep_role` | EXECUTOR / REGULATOR / MARKER |
| `deep_direction` | PROMOTES / INHIBITS |
| `deep_confidence` | HIGH / MEDIUM / LOW |
| `deep_evidence_score` | Weighted score from multiple papers |

---

## 7. TIER UPGRADE LOGIC

After Phase 2B merge:

| Before | Upgrade Condition | After |
|--------|-------------------|-------|
| T2 | deep_evidence = HIGH + role = EXECUTOR | **T1** |
| T3 | deep_evidence = HIGH + deep_paper_count ≥ 3 | **T2** |
| T4 | deep_evidence = HIGH | **T3** |

---

## 8. IMPLEMENTATION NOTES

- **Sequential** — one PDF at a time, ~40 LLM queries per PDF
- **Rate limit** — 0.5s between LLM calls = 2 calls/sec = 120 RPM (safe for DeepSeek)
- **Time** — 10,000 PDFs × 40 queries × 0.5s = ~55 hours
- **Cost** — ~$1,900 (or ~$950 with pre-filtering)
- **Resumable** — save progress per PDF in JSON

---

*For discussion: scope (all PDFs vs pre-filtered), cost tolerance, priority ordering.*
