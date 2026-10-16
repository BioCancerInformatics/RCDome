# Pending — RCDome submission (2026-10-15)

Status snapshot of everything still open for the final submission.

## A. Human adjudication (critical path — blocks final matrix)

1. **Higor's 47 empty rows** — emailed 2026-10-15; awaiting return (17 role + 30 mechanistic block).
2. **Victor's Track A + Track B verdicts** — not yet received (the 6,953 main disagreements).
3. **Delta (942 rows)** — to be sent AFTER Higor + Victor return the main sheets (244 Track A + 698 Track B, incl. TOLLIP).
4. **Three-way vote** — populate `argumentative` (GPT-4o + Higor + Victor) per `REGRA_argumentative_voto_triplo.md`.
5. **Kappa** — Higor ↔ Victor agreement measure.
6. **Apply final labels to the matrix** — majority vote → final columns. Gate: destructive verdicts (OUT_OF_CONTEXT / UNCLEAR) require ≥2-way agreement before flattening.

## B. Regeneration (after A)

7. **Figure 3C** — regenerate with final counts; remove the "10 pairs pending" footnote.
8. **Matrix CSV + RDS** — re-sync the final matrix everywhere (distribution + Phase 2C + GitHub).

## C. Content still pending (parallel, non-blocking)

9. **Emanuell videos** — Zima AI (external).
10. **H46 freeze date** — write the real date + SHA-256 hash at the actual submission freeze.

## D. Submission logistics (last)

11. **Rebuild the distribution ZIP** — after final matrix + Figure 3C.
12. **GitHub → public** — on submission day; verify no secrets, clean tree.

## Dependency order

```
Higor(47) + Victor(6,953) → delta(942) → 3-way vote → kappa → matrix → Figure 3C → ZIP → GitHub public
```

Longest pole: **Victor's verdicts**.

## Key files

- Main sheets: `manuscript_V027/Higor_Arbitragem de rótulos do RCDome — veredito humano necessário/human_resolution_worksheet_trackA/B_Higor_Victor.xlsx`
- Delta sheets: `…/human_resolution_worksheet_delta_trackA/B_Higor_Victor.xlsx`
- Vote rule: `…/REGRA_argumentative_voto_triplo.md`
- Originals/audit: `analysis/benchmark_label_error_n800/results/`
- Traceability: `docs/TRACEABILITY_Victor_V027_audit_2026-10-14.md`
