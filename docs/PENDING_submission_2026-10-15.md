# Pending — RCDome submission (2026-10-15, sweep-consolidated)

## STATE UPDATE 2026-10-16 — evidence-first adjudication + matrix merge DONE

Completed since the 10-15 sweep (full trail in `TRACEABILITY_optionB_execution_and_agreement_policy_2026-10-16.md`):

- **Disagreement pool (6,953)** — evidence-first verdict on full-text verbatim (UNIFORM_PIPELINE). DONE.
- **Agreement pool (13,737)** — audited: DeepSeek-label (85.6%) + Consensus-abstract (99.8%), NOT full-text. Verdict = AGREED_LABEL_ABSTRACT (agreement stands); abstract re-check = INSUFFICIENT/CONFIRMED/DIFFERENT_VIEW (comparable view, non-cancelling). DONE.
- **Recovered rows (15)** — 9 direction-only + 6 MARKER-role (were dropped by the worksheet builder). DONE.
- **Matrix merged** — 22,473 × 94 (83 original byte-identical + 11 additive columns). RDS + copies synced, ZIP rebuilt (583.6 MB), GitHub `f855318`. DONE.

**Changed statuses below** (A.2 done; A.6 superseded by evidence-first; matrix + ZIP no longer pending).

---

Complete pending inventory after sweeping the master project folder.

## A. Human adjudication (critical path — blocks final matrix)

1. **Higor's empty rows** — **47 DONE 2026-10-17** (verdicts merged, 0 mismatches; `argumentative` re-classified: 19 CORROBORATED · 17 GPT_PLUS_ONE · 6 TOTAL_DISAGREEMENT · 5 HUMANS_AGREE). The remaining 10 recovered rows (9 direction + 1 KRT18) still need Higor + Victor votes.
2. ~~Victor's Track A + Track B verdicts~~ **RECEIVED 2026-10-16** — merged into the Track tables (`Victor_arbitragem_de_rotulos_do_RCDome_veredito_human/`). 10 recovered rows still need Victor's vote (added post-return).
3. **Delta (942 rows)** — to be sent AFTER the 10 recovered are voted (244 Track A + 698 Track B, incl. TOLLIP).
4. **Three-way vote** — `gpt4o_verdict`/`higor_verdict`/`victor_verdict` already populated in the Track tables; the vote is logged but is NOT the final verdict.
5. **Kappa** — Higor ↔ Victor agreement measure (still to compute on the final sheets).
6. **Final labels** — NOT majority vote. Per `REGRA_agreement_policy_fulltext_vs_abstract.md`: evidence-first (full-text verbatim) is the verdict; a vote is overturned only by equal-or-stronger evidence, never by a weaker abstract.

## B. Second-order curation (after A)

7. ~~Human adjudication layer~~ **DONE as `final_mechanistic`/`final_role`/`final_direction`** (11 additive columns, never replacing `cot_*`/`consensus_*`). Coverage rule: disagreement → evidence-first (full-text verbatim); agreement → AGREED_LABEL_ABSTRACT (agreement stands + abstract flag); delta → PENDING_DELTA.
8. **G5/BG5 independent replication** — per-entity `replication_summary` + `curator_verdict` (N=0→none, 1–2→limited, ≥3→multiple), for all 53 entities.
9. **Discrepancy Radar — Phase 2** — now unblocked on the adjudication layer; still gated on the delta round (#3) for full coverage.

## C. Regeneration (after delta round only)

10. **Figure 3C** — regenerate with final counts; remove the "10 pairs pending" footnote.
11. **Matrix CSV + RDS** — re-sync the FINAL matrix after the delta round (the 94-column merge is already in place).

## C-bis. Full-text retrieval (future work, NOT blocking submission)

- **13,019 agreement rows are abstract-INSUFFICIENT** (full text not retrieved). Honest status: AGREED_LABEL_ABSTRACT, not "validated."
- **250 DIFFERENT_VIEW rows** — recorded, not cancelled; future full-text re-verification list.
- **Full-text retrieval campaign** for these rows is declared future work, explicitly NOT claimed as done.

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

## Dependency order (updated 2026-10-16)

```
Higor(57) → delta(942) → 3-way vote → kappa
  → matrix re-sync (delta + recovered rows) → Figure 3C → app smoke test
  → ZIP (rebuilt, re-run after delta) → EndNote format → GitHub public
```

Longest pole: **the 952 pending rows** (942 delta + 10 recovered). (Higor's 47 + Victor + evidence-first + agreement pool + matrix merge already done.)

## Key files

- Main/delta sheets + vote rule: `manuscript_V027/Higor_Arbitragem de rótulos do RCDome — veredito humano necessário/`
- Agreement policy: `REGRA_agreement_policy_fulltext_vs_abstract.md` (same folder)
- Option B traceability: `docs/TRACEABILITY_optionB_execution_and_agreement_policy_2026-10-16.md`
- Retrieval artifacts: `manuscript_V027/verbatim_agreement_progress.json` · `agreement_pool_final_verdicts.json` · `OptionB_execution_audit_2026-10-16.csv`
- Originals/audit: `analysis/benchmark_label_error_n800/results/`
- Deferrals: `docs/DEFERRALS_for_publication.md` · `docs/APPENDIX_2026-10-04_pending_work_log.md`
