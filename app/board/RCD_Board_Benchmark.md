# RCDome — Digital Molecular RCD Board Benchmark

**Version:** v1 (2026-09-06) · **Approved:** Enrique (human).
**Principle:** every test has its own statistically determined sample size (n), 95% CI, and
significance test. The benchmark measures **content and context** (accuracy, fidelity,
governance, reproducibility-of-facts), never identity of text.

---

## Sample-size formulas

```
Proportion, 95% CI:      n = z²·p·(1−p) / E²          (z = 1.96)
Detect a Δ with power:   n = (zα+zβ)²·2·p̄·(1−p̄) / Δ²   (zβ = 0.84 for 80% power)
Wilson 95% CI:           (p + z²/2n ± z·√(p(1−p)/n + z²/4n²)) / (1 + z²/n)
```

---

## Test 1 — Golden-pair accuracy (gene level)

| | |
|---|---|
| n | 26 (fixed ground-truth: 10 EXEC · 8 REG · 8 negative) |
| Metric | accuracy = correct / 26 |
| CI | Wilson 95% → 86.8% – 100.0% |
| Test | binomial (H0: p = 0.95) |
| To tighten CI to ±5% | expand golden set to ≥ 73 curated pairs |

## Test 2 — Census accuracy (entity level)

| | |
|---|---|
| n | 53 (all entities) |
| Metric | level + category == decoder |
| CI | Wilson 95% → 93.2% – 100.0% |

## Test 3 — Reproducibility of CONTENT (facts stable, prose free)

| | |
|---|---|
| n (runs per case) | 73 (detect 95% fact-stability, ±5%) |
| Cases | the 26 golden pairs (or a random sample) |
| Metric | per FACT (PMID, role, level, category, C1–C6, S): correct in X/73 runs |
| CI | Wilson per fact |
| temperature | > 0 (e.g., 0.7) — prose varies, facts must not |

## Test 4 — Governance compliance (violations)

| | |
|---|---|
| n (violation tests) | 73 (detect 5% violation, ±5%) · 471 (2%) · 381 (1%) |
| Test | binomial per violation type (causality, hedge, domain drift, terminology) |

## Test 5 — Anti-hallucination (traps)

| | |
|---|---|
| n (trap tests) | 73 (5% hallucination, ±5%) · 381 (1%, ±1%) |
| Traps | fake PMID, fake gene, fake entity, empty-field fill-in |
| Metric | never cited / correctly "not recorded" |

## Test 6 — Articulation (output structure)

| | |
|---|---|
| n | 53 reports (1 per entity) or a sample |
| Check | prose (no bullets/bold) · exactly 3 queries · exact disclaimer · numeric values |

## Test 7 — Governance-version comparison (v1 → v2)

| | |
|---|---|
| Detect | 5% improvement (90% → 95%) at 80% power |
| n | ~290 paired runs |
| Test | **McNemar** (paired proportions) |


## Test 8 — Model comparison (deepseek-chat vs deepseek-reasoner)

| Dimension | Metric |
|---|---|
| Accuracy | 26 golden + 53 census in BOTH models |
| Reliability | fact-stability n=73 per model (IC 95%) |
| Cost | tokens × price → R$/run + R$/full benchmark |
| Latency | seconds/run (median) |

Decision rule: choose the model whose accuracy gain justifies its cost; log the choice
(model, price, accuracy, CI) in the traceability.

### RESULT (registered 2026-09-07 — do not re-test the reasoner)

| Model | Golden accuracy | Median latency | Tokens/pair |
|---|---|---|---|
| **deepseek-chat** | **26/26 = 100%** | ~6 s | ~650 |
| deepseek-reasoner | 22/26 = 84.6% | 53 s | ~9,600 |

**Decision: keep deepseek-chat.** The reasoner is less accurate (it over-reasons and
misclassifies role/direction on BAX, CASP9, CYCS, TP53), 9× slower, and 15× costlier.
This conforms to earlier DeepSeek tests (the model-selection benchmark): the
non-reasoning model with governance + scrub outperforms the reasoning model.
Do not insist on deepseek-reasoner for the RCDome board.

## Test 9 — Chat governance (interactive Q&A)

| | |
|---|---|
| n | 73 test questions (genes associated · lethal genes · relationships · maturity · key molecules) |
| Check | answers sourced from RCDome database + RCDome decoder · hedged · no hallucination · domain boundary respected |
| Test | binomial per question type · CI 95% |

---

## Report format (every run)

```
RCD BOARD BENCHMARK — run #NNN · seed=… · temperature=… · prompt-version=…
1. Golden accuracy:  X/26 = …%  (Wilson 95% CI: …–…%)
2. Census accuracy:  X/53 = …%  (Wilson 95% CI: …–…%)
3. Fact-stability:   per-fact X/73 (CI) …
4. Governance:       0/73 violations (CI) …
5. Anti-hallucination: 0/73 traps cited (CI) …
6. Articulation:     X/53 conform (CI) …
7. Version delta:    McNemar p=… (significant y/n)
All formulas, parameters, seed, and logs are auditable.
```

## Auditability

- Every statistic: formula + p + E + n + seed + timestamp.
- Every run logged (input, output, extracted facts, flags).
- Re-runnable: same seed + parameters → same extracted facts (prose may vary).
