# RCDome — Phase 2: Gene-RCD Association Validation Plan
## Literature-Based Evidence Validation for the Compilation Matrix

**Date:** 2026-07-23
**Goal:** Validate every gene-RCD association in `unified_gene_rcd_matrix.csv` (18,327 rows) against published literature, extracting mechanistic evidence, experimental support, and distinguishing true associations from mere co-occurrence.

---

## 1. THE PROBLEM

The Phase 1 compilation matrix tells us **which databases** support a gene-RCD association. It does NOT tell us:

| Question | Current Answer |
|----------|---------------|
| Is gene X mechanistically involved in RCD form Y? | Unknown — databases may record co-occurrence |
| Has the association been experimentally validated? | Unknown |
| What is the specific role (executor, regulator, marker)? | Only FerrDB rows have this |
| Which PMIDs provide the strongest evidence? | Only RCDdb has per-gene PMIDs (12%) |
| Is the association spurious (correlation, not causation)? | Unknown |

---

## 2. THE APPROACH: Multi-Layer Evidence Extraction

```
                    ┌────────────────────────────────────┐
                    │   COMPILATION MATRIX (18,327 rows) │
                    └──────────────┬─────────────────────┘
                                   │
                    ┌──────────────▼─────────────────────┐
                    │  LAYER 1: Consensus.app             │
                    │  Semantic search per gene-RCD pair  │
                    │  Claim extraction + citation count  │
                    └──────────────┬─────────────────────┘
                                   │
                    ┌──────────────▼─────────────────────┐
                    │  LAYER 2: LLM RAG (DeepSeek/GPT)   │
                    │  Full-text analysis of top papers   │
                    │  Mechanistic classification         │
                    └──────────────┬─────────────────────┘
                                   │
                    ┌──────────────▼─────────────────────┐
                    │  LAYER 3: PubMed E-utilities        │
                    │  Boolean co-occurrence verification │
                    │  PMID harvesting                    │
                    └──────────────┬─────────────────────┘
                                   │
                    ┌──────────────▼─────────────────────┐
                    │  LAYER 4: Evidence Tier Assignment  │
                    │  Automated scoring → tier           │
                    │  Flag top PMIDs for manual review   │
                    └──────────────┬─────────────────────┘
                                   │
                    ┌──────────────▼─────────────────────┐
                    │  ENRICHED MATRIX                    │
                    │  + pmids, + evidence_tier,          │
                    │  + mechanistic_role, + curator_flag │
                    └────────────────────────────────────┘
```

---

## 3. LAYER 1: Consensus.app — Semantic Literature Search

### What it does
Consensus.app searches 200M+ papers semantically (not just keyword matching). Returns claim-level extractions with citation context and consensus meter.

### Per gene-RCD pair query
```
"What is the role of [GENE] in [RCD_FORM]?"
"Is [GENE] mechanistically involved in [RCD_FORM]?"
"Does [GENE] regulate or execute [RCD_FORM]?"
```

### Output per query
| Field | Description |
|-------|-------------|
| `consensus_pmids` | Top N PMIDs returned |
| `consensus_claims` | Extracted claim sentences |
| `consensus_meter` | % of papers supporting the association |
| `consensus_paper_count` | Total papers found |
| `consensus_top_year` | Most recent publication year |

### Automation
- Consensus API (if available) or browser automation (Selenium/Playwright)
- Batch queries: 18,327 rows → group by unique (gene, rcd_form_canonical) ≈ ~30,000 queries
- Rate limit: ~100 queries/day on free tier → needs API key or distributed execution

---

## 4. LAYER 2: LLM RAG — Deep Literature Analysis

### What it does
For each gene-RCD pair, the LLM reads the top N papers (from Consensus or PubMed) and classifies the association.

### Prompt template
```
You are a molecular biology expert evaluating gene-RCD associations.

GENE: {gene_symbol}
RCD FORM: {rcd_form}

Based on the following paper abstracts, classify this association:

PAPERS:
{paper_abstracts}

OUTPUT (JSON):
{
  "verified": true/false,
  "mechanistic_role": "EXECUTOR|REGULATOR|MARKER|SUBSTRATE|INTERACTOR|UNRELATED",
  "evidence_level": "DIRECT_EXPERIMENTAL|INDIRECT|CORRELATION_ONLY|NO_EVIDENCE",
  "direction": "PROMOTES|INHIBITS|CONTEXT_DEPENDENT|UNKNOWN",
  "confidence": "HIGH|MEDIUM|LOW",
  "key_pmid": "most relevant PMID",
  "key_sentence": "verbatim sentence establishing the association",
  "notes": "brief explanation"
}
```

### Implementation
- Use DeepSeek API (cost-effective for 30K queries) or GPT-4o
- Batch papers in context window (up to 128K tokens)
- Cost estimate: ~30,000 queries × ~1,000 tokens/query ≈ 30M tokens ≈ $15-30 (DeepSeek)

---

## 5. LAYER 3: PubMed E-utilities — PMID Harvesting

### What it does
For gene-RCD pairs NOT covered by RCDdb (88% of matrix), harvest PMIDs via Boolean search.

### Query template
```
("[GENE]"[Gene]) AND ("[RCD_TERM]"[Title/Abstract]) AND (humans[Filter])
```

### Output
- `pubmed_pmids`: PMIDs where gene and RCD term co-occur
- `pubmed_count`: Number of articles
- Already partially done: our Channel A (Rodrigues2025) used this approach

### Distinction from Phase 1
Phase 1 Boolean search was at the compendium level. Phase 2 does it per gene-RCD pair with human filter and retrieves actual PMIDs.

---

## 6. LAYER 4: Evidence Tier Assignment

### Automated scoring algorithm

For each gene-RCD pair, evidence tier is calculated from:

| Source | Points | Condition |
|--------|--------|-----------|
| Consensus meter ≥ 70% | +3 | High agreement in literature |
| Consensus meter 40-69% | +1 | Moderate agreement |
| LLM classifies as EXECUTOR/REGULATOR | +3 | Mechanistic role confirmed |
| LLM classifies as MARKER | +1 | Readout, not regulator |
| LLM evidence = DIRECT_EXPERIMENTAL | +3 | Knockout/knockdown/inhibitor data |
| LLM evidence = INDIRECT | +1 | Expression correlation |
| PubMed co-occurrence count ≥ 10 | +2 | Well-published association |
| PubMed co-occurrence count 1-9 | +1 | Some literature support |
| Multi-database support (num_sources ≥ 3) | +2 | Independent database confirmation |

### Evidence tiers

| Tier | Score | Label | Meaning |
|------|-------|-------|---------|
| **T1** | ≥ 10 | Gold Standard | Mechanistically validated, multiple independent sources |
| **T2** | 7-9 | Strong Evidence | Literature-supported, likely real |
| **T3** | 4-6 | Moderate Evidence | Some support, needs confirmation |
| **T4** | 1-3 | Weak Evidence | Limited or correlational only |
| **T0** | 0 | Unverified | No literature support found |

### New matrix columns

| Column | Type | Description |
|--------|------|-------------|
| `consensus_pmids` | text | Top PMIDs from Consensus |
| `consensus_meter` | int | % agreement (0-100) |
| `llm_mechanistic_role` | text | EXECUTOR/REGULATOR/MARKER/SUBSTRATE/INTERACTOR/UNRELATED |
| `llm_evidence_level` | text | DIRECT_EXPERIMENTAL/INDIRECT/CORRELATION_ONLY/NO_EVIDENCE |
| `llm_direction` | text | PROMOTES/INHIBITS/CONTEXT_DEPENDENT/UNKNOWN |
| `llm_confidence` | text | HIGH/MEDIUM/LOW |
| `llm_key_pmid` | text | Single best PMID |
| `llm_key_sentence` | text | Verbatim sentence from paper |
| `pubmed_cooccurrence_count` | int | Number of PubMed articles |
| `pubmed_top_pmids` | text | Top 5 PMIDs from PubMed |
| `evidence_tier` | text | T1/T2/T3/T4/T0 |
| `evidence_score` | int | 0-15 raw score |
| `curator_flag` | text | AUTO_VERIFIED / NEEDS_REVIEW / DISPUTED |
| `curator_notes` | text | Free-text for manual review |

---

## 7. EXECUTION PLAN

### Phase 2a: Infrastructure (Week 1)
- [ ] Set up Consensus API access or browser automation
- [ ] Set up DeepSeek/GPT API key and prompt engineering
- [ ] Implement PubMed E-utilities batch harvester
- [ ] Create scoring engine module

### Phase 2b: Bulk Extraction (Weeks 2-3)
- [ ] Consensus queries for all gene-RCD pairs (~30,000)
- [ ] PubMed PMID harvesting for pairs without RCDdb coverage
- [ ] LLM classification for high-priority pairs (T2 confidence tier first: 8,453 rows)
- [ ] LLM classification for T3 pairs (8,415 rows)
- [ ] T4 pairs (1,459 rows) — lower priority, do last

### Phase 2c: Scoring and Flagging (Week 4)
- [ ] Compute evidence scores and tiers
- [ ] Flag top PMIDs per gene-RCD pair
- [ ] Flag rows needing manual review (curator_flag = NEEDS_REVIEW)
- [ ] Generate audit report

### Phase 2d: Manual Curation (with Emanuell, Weeks 4-5)
- [ ] Review NEEDS_REVIEW flagged rows
- [ ] Confirm DISPUTED associations
- [ ] Add curator_notes
- [ ] Finalize evidence tiers

---

## 8. COST ESTIMATES

| Component | Volume | Unit Cost | Total |
|-----------|--------|-----------|-------|
| Consensus queries | ~30,000 | Free tier limited | Need API or distributed |
| PubMed E-utilities | ~25,000 pairs | Free (with API key) | $0 |
| LLM classification | ~18,000 pairs | ~1K tokens/query | ~$15-30 (DeepSeek) |
| Manual curation | ~500 rows | 2 min/row | ~17 hours |

---

## 9. DISCUSSION POINTS

1. **Consensus API availability**: Does Consensus have a programmatic API, or do we need browser automation (Selenium)?
2. **Priority ordering**: Start with T2 rows (8,453, highest confidence), then T3, then T4?
3. **LLM choice**: DeepSeek (cheaper, good for structured extraction) vs GPT-4o (better reasoning)?
4. **Co-occurrence vs causation**: How do we handle genes that appear in cell death papers but aren't mechanistically involved? The LLM classification should catch these.
5. **Batch size**: What batch size for LLM prompts? 5 papers per gene-RCD pair → 5 abstracts × 250 words ≈ 1,250 words ≈ 1,700 tokens per query.

---

*This plan is for discussion. Once agreed, we implement the extraction scripts as `channel_c_consensus.py`, `channel_c_llm_rag.py`, `channel_c_pubmed_harvest.py`, and `phase2_scoring_engine.py`.*
