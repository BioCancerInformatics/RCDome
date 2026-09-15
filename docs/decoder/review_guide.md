# RCDome Definition — Call B (Human Two-Call Review) Guide

**Call A (AI draft):** complete · fully audited (40 PASS / 0 FAIL) · every field carries its source.
**Call B (human review):** your sign-off below.
**Output:** fill `reviewer_decision` in `definition_review_worksheet.csv`, then run `merge_approved.py`.

---

## How to review (3 decision options per field)

| Decision | Meaning |
|---|---|
| **APPROVE** | keep the draft value |
| **EDIT** | replace with `reviewer_value` + a justification |
| **REJECT** | flag for re-draft (stays PENDING) |

> **Invariance guard:** any EDIT/REJECT on a **NCCD-verbatim** `operational_definition` is automatically refused (20 entities). The 12 Rodrigues-verbatim ODs are likewise invariant — only their `complement` is editable.

---

## Review checklist — 28 entities, by focus

### 🔍 1. VERIFY PMID (11) — confirm the founding PMID actually coins the entity
| Entity | PMID | Check |
|---|---|---|
| Apoptosis (extrinsic) | 15451440 | "extrinsic apoptosis" in title |
| Apoptosis (intrinsic) | 12186923 | "intrinsic apoptosis" in title |
| Autophagy-dependent cell death | 18942750 | autophagy-dependent death |
| Eryptosis | 16910766 | eryptosis (term coined 2001) |
| Lysosomal cell death | 15289336 | lysosomal cell death pathway |
| Lysozincrosis | 37550363 | review only — find the primary coining paper |
| Metalloptosis | 41094656 | review that coins the umbrella |
| MPT-driven necrosis | 27161573 | describes "(MPT)-driven necrosis" (FLAG resolved) |
| NECSO | 39915626 | sodium-overload necrosis |
| Regulated Necrosis | 21894190 | RIP3-driven regulated necrosis |
| Vacuolar cell death | 15358773 | non-vacuolar pathway |

### 📖 2. PRIMARY SOURCE (1)
| Entity | Action |
|---|---|
| Hypersensitive response | supply the pre-PubMed citation (Stakman 1915 / Klement 1963–1967) |

### 🧩 3. COMPOSITE (1)
| Entity | Action |
|---|---|
| Senescence and Autophagy in Cancer | confirm the WikiPathways-composite note + parent PMIDs (29362479;36864290) |

### 🧪 4. KEY-MOL (6) — molecules exceeding the founding abstract (general-knowledge enrichments)
| Entity | Molecule | Action |
|---|---|---|
| Apoptosis (intrinsic) | Bax | cite secondary source or annotate |
| Phagoptosis | CD47 | cite secondary source or annotate |
| Oncosis | Na⁺/K⁺-ATPase | cite secondary source or annotate |
| Metalloptosis | Fe/Cu/Zn/Mn elements | annotate (implied by forms) |
| Lysozincrosis | "zinc" | annotate |
| Triaptosis | "endosomal machinery" | annotate (paraphrase) |

### ✅ 5. BULK-APPROVE (rest) — prose/molecules verified; judge the C1–C6 rubric drafts
Remaining entities: Ammonia-induced cell death · Aponecrosis · Cornification · Floatptosis ·
Linker cell-type death · Lysoptosis · Mitotic death · Mitoxyperilysis · PANoptosis ·
Programmed cell death · Pyronecrosis · Spectosis.

---

## The C1–C6 judgment (the core of Call B)

For **every** entity, judge the six draft scores (rubric-informed, not computable):

| Criterion | Meaning |
|---|---|
| C1 Extent of Research | literature volume |
| C2 Direct Involvement | causal role in death |
| C3 Impact on homeostasis | tissue/homeostasis impact |
| C4 Emerging Potential | novelty/future promise |
| C5 Biological Significance | importance |
| C6 Pathophysiological relevance | translational relevance |

S is computed automatically: `S = 0.25·C1 + 0.25·C2 + 0.20·C3 + 0.15·C4 + 0.10·C5 + 0.05·C6`.

Calibration anchors: 25 Rodrigues locked (S 4.15–9.70) · 28 drafts (S 3.25–7.20).

---

## After your sign-off

1. Fill `reviewer_decision` (+ `reviewer_value`, `justification`) in `definition_review_worksheet.csv`.
2. Run `merge_approved.py` → produces `RCDome_Decoder_53.csv` + `merge_log.csv` (traceability).
3. Re-run `final_ocean_audit.py` to confirm the locked decoder.
