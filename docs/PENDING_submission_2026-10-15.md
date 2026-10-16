# Pending — RCDome submission (2026-10-15, sweep-consolidated)

Complete pending inventory after sweeping the master project folder.

## A. Human adjudication (critical path — blocks final matrix)

1. **Higor's 47 empty rows** — emailed 2026-10-15; awaiting return (17 role + 30 mechanistic block).
2. **Victor's Track A + Track B verdicts** — not yet received (the 6,953 main disagreements).
3. **Delta (942 rows)** — to be sent AFTER Higor + Victor return (244 Track A + 698 Track B, incl. TOLLIP).
4. **Three-way vote** — populate `argumentative` (GPT-4o + Higor + Victor) per `REGRA_argumentative_voto_triplo.md`.
5. **Kappa** — Higor ↔ Victor agreement measure.
6. **Apply final labels** — majority vote → final columns. Gate: destructive verdicts (OUT_OF_CONTEXT / UNCLEAR) require ≥2-way agreement before flattening.

## B. Second-order curation (after A)

7. **Human adjudication layer** — new synthesis columns `adjudicated_role` / `adjudicated_direction` / `adjudicated_mechanistic` (never replacing `cot_*` / `consensus_*` / `rcd_gene_type`). Coverage rule: DeepSeek=Consensus → inherit; disagree → human verdict; NEITHER → note's corrected value.
8. **G5/BG5 independent replication** — per-entity `replication_summary` + `curator_verdict` (N=0→none, 1–2→limited, ≥3→multiple), for all 53 entities.
9. **Discrepancy Radar — Phase 2** — blocked on #1–#6.

## C. Regeneration (after A/B)

10. **Figure 3C** — regenerate with final counts; remove the "10 pairs pending" footnote.
11. **Matrix CSV + RDS** — re-sync the final matrix everywhere (distribution + Phase 2C + GitHub).

## D. App + distribution

12. **Human smoke test** of the app — scheduled just before publication (`code/test_app_smoke_v027.py`).
13. **App artifact spread + GitHub sync** — end-to-end horizontal/vertical propagation audit before ZIP + push.

## E. Content (parallel, non-blocking)

14. **Emanuell videos** — Zima AI (external). Cartoons + logos + legends already done.
15. **H46 freeze date** — write the real date + SHA-256 hash at the actual submission freeze.

## F. Manuscript formatting (EndNote)

16. **C01 — Format Bibliography** — run EndNote at submission to resolve `{Author, Year #id}` markers.
17. **C01b — 4 missing references** — Cai 2014 · Sborgi 2016 · Tsvetkov 2022 · Yang 2014 (generated at format time).

## G. Submission logistics (last)

18. **Rebuild the distribution ZIP** — after final matrix + Figure 3C + app artifacts.
19. **GitHub → public** — on submission day; verify no secrets, clean tree.

## Deferred but settled (KEEP — no action unless reviewers request)

- C02 word count (15,739 vs 12,000) · C03 abstract (367 words).
- Definition-status flags (CRITERION-PENDING / UMBRELLA-SCOPE / ABSTRACT-LIMITED / PRE_PUBMED) — documented annotations, not deferrals.

## Dependency order

```
Higor(47) + Victor(6,953) → delta(942) → 3-way vote → kappa
  → adjudicated_* layer → G5/BG5 → matrix → Figure 3C → app smoke test
  → ZIP → EndNote format → GitHub public
```

Longest pole: **Victor's verdicts**.

## Key files

- Main/delta sheets + vote rule: `manuscript_V027/Higor_Arbitragem de rótulos do RCDome — veredito humano necessário/`
- Originals/audit: `analysis/benchmark_label_error_n800/results/`
- Deferrals: `docs/DEFERRALS_for_publication.md` · `docs/APPENDIX_2026-10-04_pending_work_log.md`
- Traceability: `docs/TRACEABILITY_Victor_V027_audit_2026-10-14.md`
