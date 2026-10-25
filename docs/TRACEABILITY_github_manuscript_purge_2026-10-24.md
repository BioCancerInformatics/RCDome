# TRACEABILITY — GitHub purge: manuscript files removed from public repo (2026-10-24)

## Context
The unsubmitted manuscript (`RCDome_manuscript_governance_V027.docx`) and its supplementary files (information, tables, canonical entities) were publicly visible in the GitHub repository (`BioCancerInformatics/RCDome`), before submission. This posed a pre-submission embargo / scooping risk.

## Decision
Remove the manuscript + supplementary files from the **public** repo, keeping the public repo limited to code + data + the app. The manuscript files will be **re-added only after submission, upon authorization**.

## Action
1. **HEAD removal** — `git rm` of 6 tracked files (governance V027, supplementary information, supplementary tables, canonical entities ×2, docs copies). Commit `90dc223`.
2. **History purge** — `git filter-repo --invert-paths` with 4 globs:
   - `*manuscript_governance*.docx`
   - `*supplementary_information*.docx`
   - `*supplementary_tables*.xlsx`
   - `*canonical_entities*.docx`
3. **Force-push** — re-added `origin` and `git push --force origin main`.

## Result
- Manuscript + supplementary files are gone from **HEAD and full history**.
- History rewritten; commits that touched *only* the purged files were dropped. Public history now ends at `1a858cb` (README anonymize curators).
- Repo size: 247 MB → 225 MB.
- Public repo retains: `README.md`, `app/` (Shiny), `data/` (decoder + matrix RDS), code, docs.
- Safety backup: `/d/RCDome_github_backup_before_purge_20261024.git` (pre-purge .git).

## Future sync plan (logged)
- The manuscript files **stay out** of the public GitHub until submission.
- **After submission authorization**, they will be re-added (or replaced by links to the published version).
- **Planned first:** submit to **bioRxiv** (preprint) — possibly Monday — to resolve the public-visibility/embargo issue before final journal submission.

## Status update (2026-10-24)
- ✅ **Submitted to bioRxiv** — processing takes 3–5 days.
- Once processed → preprint **URL + DOI** available.
- Then: add the preprint URL/DOI to (1) GitHub **README**, and (2) the **RCDome app** (citation/footer).
- **Target:** submit to **Frontiers in AI** by **Tuesday** (once the bioRxiv preprint is live).
