# RCDome — AI-output benchmark results (2026-09-18)

**Purpose:** statistically validate the two fixes that make the Digital Molecular RCD Board / Q&A correct-by-construction:
1. **Reference discipline** — the synthesis cites the gene-specific PMID for associations and the entity founding PMID for definitions (never interchanges them).
2. **T06 context fidelity** — the synthesis does not contradict the structured payload (role/direction/mechanistic/tier/required_for_death) now fed into its context.

## Method

- Real DeepSeek (`deepseek-chat`) calls, temperature 0.7, timeout 120 s.
- System prompt: `board/RCD_Board_DeepSeek_Prompt.md` (governance rules + REFERENCE DISCIPLINE).
- Context built exactly as the app does (truncated PMIDs, role/direction/mechanistic/tier/required_for_death/PMID).
- Population: gene–RCD pairs with a real PMID (benchmark 1) / with a real role+direction+PMID (benchmark 2).
- Reproducible: `set.seed(2026)` (benchmark 1), `set.seed(7)` (benchmark 2), random sample of size **n = 100**.

## Results (n = 100)

| Benchmark | n | Pass | Rate | Exact binomial 95% CI |
|---|---|---|---|---|
| Reference discipline (gene vs entity PMID) | 100 | 100/100 | 100% | **96.4–100%** |
| T06 context fidelity (no payload contradiction) | 100 | 100/100 | 100% | **96.4–100%** |

**Claim standard:** “100% (100/100), 95% CI [96.4%, 100%]” → “≥96% with 95% confidence.”

## Statistical justification for n = 100

The outcome is 100% pass, so hypothesis-test *power* is degenerate; the meaningful statistic is **precision** (CI width):

| n | 95% CI lower bound (if 100% pass) |
|---|---|
| 30 | 88.4% |
| 50 | 92.9% |
| **100** | **96.4%** |
| 200 | 98.2% |

n = 100 gives a reviewer-proof lower bound of 96.4%. This is now codified in the governance contract (Benchmark Statistical Standard).

## Artifacts excluded

- HK2–Mitoxyperilysis: its `pmid_list` is the literal text *"Not reported (the DOI is not mentioned…)"* — no gene PMID exists, so there is nothing to cite (correctly handled as “no gene-specific PMID recorded”). Benchmark 1 filters to real-PMID pairs (`grepl("^[0-9]", pmid_list)`).

## Reproducibility

Scripts: `code/benchmark_reference_discipline.R`, `code/benchmark_t06_context_fidelity.R` (n = 100).

Re-run with the DeepSeek API key in `RCDome_distribution/.Renviron`:

```
Rscript code/benchmark_reference_discipline.R
Rscript code/benchmark_t06_context_fidelity.R
```

## Held-out validation (2026-09-19) — Victor §23

Fresh held-out sample (seed 20260919, n = 100 each, **excluding** the dev cases: reference seed 2026, T06 seed 7). Same DeepSeek calls + same scoring.

| Benchmark | n | Pass | Rate | Exact binomial 95% CI |
|---|---|---|---|---|
| Reference discipline (held-out) | 100 | 100/100 | 100% | **96.4–100%** |
| T06 context fidelity (held-out) | 100 | 100/100 | 100% | **96.4–100%** |

**Conclusion:** dev and held-out agree at 100% → the "≥96% with 95% confidence" claim is **generalization-validated**, not a dev-only artifact.

Script: `code/benchmark_heldout_20260919.R`.
