# Traceability — RCDome Scout candidate-term adjudication

Date: 2026-10-25
Source: RCDome Scout Run_001 (2025-01-01 → 2026-10-22)
Evidence file: `/mnt/sharefiles/medina/students/aluno0549-6/RCDome/RCDome_scout/scout_output/Run_001_2025-01__2026-10/evidence.csv`
Notification: same run — `notification.md` and `monthly_report.md`

## Candidate terms flagged (notification.md / monthly_report.md)
- mechanoptosis (n=6), pan-apoptosis (n=9), calcicoptosis (n=4), photopyroptosis (n=4), and spelling variants disulfidoptosis (n=22) / disulfideptosis (n=5) of the existing Disulfidptosis entity.

## Adjudication (scout-not-judge → human verdict)

| Term | Evidence (verbatim) | Verdict |
|---|---|---|
| mechanoptosis | mechanical-force-triggered cell death (title-level) | contextual variant (a trigger), not a new mechanism |
| pan-apoptosis | "TAK1-mediated pan-apoptosis (PANoptosis)"; "pan-apoptosis prognostic genes/gene set/biomarker" (6 evidence rows) | loose synonym of PANoptosis / gene-set label → PANoptosis or Apoptosis; NOT a new entity |
| calcicoptosis | "artesunate induces Ca²⁺ overload driving calcicoptosis-ferroptosis" (EGFR row, mapped Ferroptosis) | contextual variant under the Metalloptosis umbrella (entity #53) |
| photopyroptosis | photo/photodynamic-triggered pyroptosis (title-level, n=4) | contextual variant of Pyroptosis |
| disulfidoptosis / disulfideptosis | spelling variants of Disulfidptosis | synonyms → Disulfidptosis |

## Decision
- **No new canonical entity added.** Decoder stays at 53 entities.
- Scout's own mapping validated: pan-apoptosis rows → PANoptosis / Apoptosis; calcicoptosis row → Ferroptosis (acceptable; umbrella = Metalloptosis).

## Verification notes
- evidence.csv rows: pan-apoptosis = 6, calcicoptosis = 1, photopyroptosis = 0 (title-level only; not in evidence rows).
- The n= counts in monthly_report.md are title-mention counts (from work/*.jsonl), not evidence rows.
