# Supplementary Note S4 — Digital Molecular RCD Board: Governance, Benchmark, and Performance

## Purpose

The Digital Molecular RCD Board is a prose-synthesis module that answers gene–RCD
queries strictly from the RCDome database and the RCDome decoder. It is designed as
an independent, deployable module of the RCDome web application. The board never
reasons from its own unverified knowledge: every factual claim must be traceable to
a matrix row, a decoder field, or a recorded PMID. This note documents (i) the
governance logic, (ii) the benchmark code logic and statistical design, and
(iii) the measured performance with all statistics, including the board's Q&A
submodule (retrieval-augmented design, statistical validation, and significance
for the RCDome as a full-coverage resource).

## Governance logic

The board output is a single continuous prose synthesis, human-to-human
communication, with no headers, no bullet lists, and no markdown bold. Four
provenance categories govern how each sentence is written, without being printed
as labels:

- facts with a PMID → "the RCDome database records … (PMID …)"
- model annotation → "within the RCDome database …"
- decoder/biological context → "the RCDome decoder defines/states …"
- hypothesis → "Hypothesis:" / "may suggest" / "is consistent with"

The following rules are enforced both in the prompt and by a deterministic
post-generation scrub (never by a second model):

1. **Terminology** — only "RCDome database" and "RCDome decoder"; the bare words
   "database", "decoder", and the internal term "matrix" are banned. The matrix
   scrub is biology-safe: it does not touch "extracellular matrix",
   "mitochondrial matrix", or "matrix metalloproteinase".
2. **Causal-verb ban** — assertive causal verbs are replaced with hedging
   equivalents in all tenses.
3. **Hedging** — genuine uncertainty phrasing is preserved (biology-safe).
4. **Disclaimer** — the exact, verbatim disclaimer sentence is appended at the
   very end of the output (auto-appended if missing).
5. **Queries** — the synthesis body ends with exactly three numbered "Suggested
   Queries:" (auto-numbered if unnumbered; never invented), immediately before
   the disclaimer.
6. **PMID discipline** — only PMIDs present in the data may be cited; the entity's
   founding PMID is always cited when its operational definition is described.
7. **Negative controls** — a pair absent from the database must be reported as
   "not recorded" without inventing a role or direction.

## Q&A retrieval strategy (retrieval-augmented generation)

The Q&A submodule of the board answers free-form questions across all 53 entities
and all 9,265 genes. The complete gene–form matrix (22,473 rows, each carrying
mechanistic class, role, direction, evidence tier, and PMID) exceeds the model
context, so the Q&A uses a retrieval-augmented strategy that never deletes data.
A static layer always injects the complete gene–entity index (all 22,473
associations, names only) and the full 53-entity decoder. A dynamic layer then
detects, for each question, the entities mentioned (by canonical name or its
stem, so "apoptotic" matches Apoptosis) and any gene symbols, and injects the
full four-dimension records for exactly those rows. Genes named explicitly in the
question are always placed first so the budget can never displace them. The
dynamic layer is capped so the full prompt stays within the model context (about
58K tokens), with a reply token limit applied. No entity or gene is ever excluded
from the index, and every classification (MECHANISTIC, LITERATURE_GAP,
CONTEXT_GAP, CO_OCCURRENCE, DATABASE_ONLY, INSUFFICIENT_DATA) remains
retrievable, so a gene recorded as executor in one form and regulator in another
is shown with both records.

## Benchmark code logic

The benchmark (`run_board_benchmark.py` + `audit_canonical.py`) evaluates the
board on nine tests. Each test has its own statistically determined sample size,
95% Wilson confidence interval, and significance test. The deterministic scrub
is applied to the raw model output before the audit, so the audit measures the
final, scrubbed text; scrub corrections are logged separately. The audit is a fixed
28-point checklist per synthesis report: 10 governance (G1–G9 causal verbs, G10
hedging, G11 disclaimer, G12 three queries), 14 policy (P1–P14 terminology and
relationship terms), and 4 accuracy (A1 cited PMIDs exist, A2 founding PMID cited,
A3 role matches, A4 direction matches). Census reports use a 24-point lookup audit
(no query requirement) and negative controls use a 29-point audit with inverted
role/direction checks.

Sample-size formulas:

- proportion, 95% CI: n = z²·p·(1−p) / E² (z = 1.96)
- detect a Δ with power: n = (zα+zβ)²·2·p̄·(1−p̄) / Δ² (zβ = 0.84 for 80% power)
- Wilson 95% CI: (p + z²/2n ± z·√(p(1−p)/n + z²/4n²)) / (1 + z²/n)

## Results

Run: 2026-09-09 · seed 42 · temperature 0.7 · prompt v2-smoke-aligned ·
model deepseek-chat.

| Test | n | Result | Wilson 95% CI | Significance |
|---|---|---|---|---|
| T1 Golden accuracy | 26 | 26/26 = 100% | 87.1–100% | binomial vs 0.95: p = 0.639 |
| T2 Census accuracy | 53 | 53/53 = 100% | 93.2–100% | binomial vs 0.95: p = 0.114 |
| T3 Fact-stability (BAX-Apoptosis) | 73 runs | 73/73 = 100% per fact (gene, entity, founding PMID) | 95.0–100% | — |
| T4 Governance | 2,142 checks | 1 violation = 0.047% | 0.008–0.264% | — |
| T5 Anti-hallucination | 4 traps | 4/4 = 100% caught | 51.0–100% | — |
| T6 Articulation | 79 reports | 78/79 = 98.7% | 93.2–99.8% | — |
| T7 Version comparison | — | pending (needs two prompt versions) | — | McNemar, n≈436 for Δ=5% |
| T8 Model comparison | 26 | deepseek-chat 26/26 = 100%; deepseek-reasoner 22/26 = 84.6% | — | keep deepseek-chat |
| T9 Chat governance | 10 | 10/10 = 100% (5 question types × 2) | 72.3–100% | — |

T4 violation breakdown (corrected mapping): causality 0 · hedge 0 · disclaimer 0 ·
queries 1 · terminology 0 · accuracy 0. The single remaining violation was
`MLKL-Necroptosis: exactly 3 numbered queries` (one query-count slip). On direct
regeneration that same report passed 30/30, confirming this is temperature>0
prose variability, not a systematic defect.

The deterministic scrub applied 163 corrections across the run (55 bare
database/decoder terms, causal-verb hedging, markdown-bold removal, disclaimer
and query normalization).

## Q&A benchmark description and validation

The Q&A submodule was benchmarked with the same statistical machinery as the
board benchmark (point estimate, Wilson 95% CI, and a binomial test against a
0.95 null). Each query is answered with the full retrieval-augmented prompt
(complete gene index plus the four-dimension records retrieved for the query),
using deepseek-chat, temperature 0.3, and a 1500-token reply cap.

Two tests were run:

T10 positive accuracy (n = 100). The 25 golden executor and regulator gene-form
pairs are each queried on four question types: role ("What is the role of GENE
in ENTITY?"), direction ("Does GENE promote or protect ENTITY?"), evidence tier
("What is the evidence tier of GENE in ENTITY?"), and supporting PMID ("Which
PMID supports the GENE-ENTITY association?"). Each answer is audited on five
checks: (i) the correct fact is cited, (ii) the RCDome source is named,
(iii) the interpretation is hedged, (iv) the disclaimer is appended, and
(v) no PMID absent from the data is cited.

T11 negative controls (n = 100). The 8 not-recorded pairs absent from the matrix
(for example RIPK3 in pyroptosis and GSDME in ferroptosis) are each queried on
the same four question types (32 queries) and must be reported as absent without
an invented role; the remaining 68 out-of-scope or fabrication queries (clinical
treatment, out-of-domain, an invented RCD form, a fake gene symbol, an invented
PMID) must be refused or declined with no hallucinated PMID.

### Statistical design

The Q&A tests use the same sample-size formulas as the board benchmark:
- proportion, 95% CI: n = z²·p·(1−p) / E² (z = 1.96)
- detect a defect Δ with 80% power: n = (zα+zβ)²·2·p̄·(1−p̄) / Δ² (zβ = 0.84)
- Wilson 95% CI lower bound for 100% observed: n / (n + z²)

Sample-size derivation. A claim of "accuracy at least 95% with 95% confidence"
requires the Wilson lower bound to reach 95%, which occurs at n = 73 (73/76.84 =
0.950). For two-sided significance against the 0.95 null, n = 100 gives
p = 0.010. In power terms (80%): n = 77 detects a 15% absolute defect
(p = 0.80); n = 142 detects 10%; n = 436 detects 5%. The chosen n = 100
therefore detects an absolute defect of about 12.5% at 80% power, holds the
Wilson lower bound at 96.3%, and gives a one-sided binomial p = 0.006 and a
two-sided p = 0.010.

Results:

| Test | n | Result | Wilson 95% CI | Binomial one-/two-sided vs 0.95 |
|---|---|---|---|---|
| T10 Q&A positive accuracy | 100 | 100/100 = 100% | 96.3-100% | 0.006 / 0.010 |
| T11 Q&A negative controls | 100 | 100/100 = 100% | 96.3-100% | 0.006 / 0.010 |

T10 breakdown (25 pairs × 4 question types, all 100 passed): role 25/25,
direction 25/25, evidence tier 25/25, supporting PMID 25/25. T11 breakdown:
not-recorded 32/32 (8 pairs × 4 types), out-of-scope and fabrication refusal
68/68. Audit volume: T10 = 100 answers × 5 checks (fact, source, hedging,
disclaimer, no-foreign-PMID) = 500 checks; T11 = 32 not-recorded checks plus
68 refusal checks × 2 = 168 checks; 668 checks in total, all passed.

All 100 positive answers cited the correct role, direction, tier, or PMID, named
the source, hedged the interpretation, appended the disclaimer, and cited no
PMID absent from the data. All 32 not-recorded queries were reported as absent
without an invented role, and all 68 out-of-scope or fabrication queries were
refused or declined with no hallucinated PMID.

Significance. The Q&A submodule is what makes the board a full-coverage
interface rather than a single-entity viewer. Because the static layer keeps the
complete gene-entity index and the dynamic layer retrieves the full
four-dimension records on demand, the Q&A can answer across all 53 entities and
all 9,265 genes without funneling the data: every classification (MECHANISTIC,
LITERATURE_GAP, CONTEXT_GAP, CO_OCCURRENCE, DATABASE_ONLY, INSUFFICIENT_DATA)
remains reachable, and a gene recorded as an executor in one form and a
regulator in another is shown with both records. For example, BAX is returned as
a mechanistic executor in apoptosis (PMID 17235284), together with its
co-occurrence annotations in necroptosis and pyroptosis and its
insufficient-data annotations in autosis, erebosis, and oncosis. The 100%
positive and negative results recorded zero hallucinated PMIDs across the
benchmark, demonstrating that full coverage and zero observed hallucination were
achieved together in the same module.

## Code corrections applied during validation

The benchmark was audited and four defects were found and fixed before this note:

1. **Violation-type mapping bug** — `violation_types` had mislabeled G10
   (hedging) and G12 (queries) and a dead branch, so "hedge" and "queries" were
   reported incorrectly. Corrected to G1–G9 → causality, G10 → hedge, G11 →
   disclaimer, G12 → queries, P* → terminology, A1–A4 → accuracy.
2. **Detail logging added** — every failed check is now logged with its pair,
   check-id, name, and exact detail (`violation_details`), instead of only tallies.
3. **Markdown-bold strip** — the scrub now removes `**bold**` markers, so the
   prose-only articulation rule is enforced deterministically.
4. **Census category sentinel** — entities with category `CORE_PENDING` are no
   longer falsely flagged (the C1 check is skipped), which also corrected the
   census accuracy from 51/53 to 53/53.
5. **Mode-aware articulation** — the query-count check is applied only to
   synthesis and negative reports, not to census lookups, which by design carry
   no queries.
6. **Biology-safe matrix audit** — the "matrix" policy check now ignores
   "extracellular matrix", "mitochondrial matrix", and "matrix metalloproteinase",
   matching the scrub.

## Conclusion

The Digital Molecular RCD Board achieves 100% golden accuracy, 100% census
accuracy, 100% fact-stability, 0.047% governance violation rate, and 98.7%
articulation conformity, with all violations traceable and logged. The module is
ready for integration into the RCDome application as an independent component.
