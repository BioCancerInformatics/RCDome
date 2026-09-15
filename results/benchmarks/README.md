# Benchmark results — Consensus query-formulation benchmark

These are the raw result tables of the Consensus evidence-channel benchmark
(26-pair ground-truth set: 18 positive executor/regulator pairs + 8 form-mismatch
negatives). The generator scripts live in `code/benchmarks/`.

| File | Iteration | Query | Headline result |
|---|---|---|---|
| `consensus_benchmark_reference_results.csv` | v1 | gene + form (reference) | paper-support counts |
| `consensus_benchmark_reference_v2_results.csv` | v2 | strict support | paper-support counts |
| `consensus_benchmark_reference_v3_results.csv` | v3 | support + contradiction | paper-support counts |
| `consensus_benchmark_reference_v4_results.csv` | v4 | support + dominant form | paper-support counts |
| `consensus_benchmark_v6_results.csv` | v6 | gene + form + "cell death" | mechanistic 25/26 (96%) · FP 1/8 (12%) |
| `consensus_pilot_results.csv` | pilot | early channel test | exploratory |

**Adopted rule (v7, neutral query "gene cell death"): 26/26 (100%) combined accuracy · 0/8 (0%) false positives** — the v7 result table is produced by `code/benchmarks/consensus_benchmark_v7_neutral_query.py` (run on Zima; its CSV lives with the Zima run logs).

The DeepSeek model-selection benchmark (81% / 73% / 100% · 0 FP) is documented in
Supplementary Note S2; its raw result JSON (`cot_benchmark_v11_results.json`) lives
with the Zima run logs.
