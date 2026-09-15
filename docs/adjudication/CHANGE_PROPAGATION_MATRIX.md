# RCDome — Change-Propagation Matrix (final governance gate)

Principle: **adjudicated → propagated → independently verified.** Correction of the primary source is *not* completion. Every accepted change must be traceably propagated through every dependent artifact, and each dependency independently verified.

Verification instrument: `code/compliance_audit.py` (62 automated checks + cross-artifact alignment). Re-run after any future change.

---

## Change 1 — Vacuolar cell death: L4 → L5 (TAXON)

- **Original:** L4 Functional/contextual · category MORPHOLOGY · "cross_species"
- **Adjudicated:** L5 Generic/umbrella/legacy/taxon/emerging · category TAXON · plant + protist (not human)
- **Authoritative source:** Decoder (category) + Matrix (`rcdome_level`)
- **Dependencies & consequences:**
  - Matrix V-26 (24 rows): `rcdome_level`, `rcdome_level_name`, `decoder_category`, `elic_onto_rcd_type`, `elic_onto_operational_note`
  - Decoder CSV + XLSX: `category`, `species_scope`, `evidence_maturity`, `relationship_type`, `operational_definition`, `provenance_note`, `secondary_refs_pmids`
  - Table S11: same fields
  - App data decoder + matrix RDS
  - Level distribution **12/18 → 11/19** everywhere: manuscript, `explore.html`, landing/dome `LEVEL_COUNTS`, Traceability Contract
  - App UI: node color L4 purple → L5 orange
- **Verification:** PASS (compliance 62/62 + alignment 0 real mismatches)
- **Corrections performed:** manuscript "L1→L5 / cross-species" sentence → "L4→L5 / taxon-specific (plant+protist)"; definition "yeast" → "Dictyostelium"; landing/dome LEVEL_COUNTS.
- **Unresolved:** none.

## Change 2 — 8 definition rewords (remove "modality" from non-L1)

- **Original:** "…cell death **modality**…" (Ammonia-induced cell death, Oncosis, PANoptosis, Lysoptosis, Lysozincrosis, Mitoxyperilysis, NECSO, Triaptosis)
- **Adjudicated:** "…cell-death **process / pattern**…" (+ level qualifier)
- **Source:** Decoder `operational_definition`
- **Dependencies:** Decoder CSV+XLSX · app decoder · Table S11
- **Verification:** PASS (0 non-L1 defs contain "modality")
- **Unresolved:** none.

## Change 3 — 8 evidence-maturity updates (+ case normalization)

- **Adjudicated:** Alkaliptosis/Methuosis/Paraptosis → supported · Ammonia-induced cell death/Metalloptosis → provisional · Mitoptosis → legacy · VCD → provisional · Erebosis → emerging · (Entosis/Eryptosis/Mitotic death/Oncosis/Linker cell-type death kept "established")
- **Source:** Decoder `evidence_maturity`
- **Dependencies:** Decoder CSV+XLSX · app decoder · Table S11
- **Verification:** PASS (all lowercase, distribution: established 29 · supported 7 · provisional 6 · emerging 6 · legacy 5)
- **Unresolved:** none.

## Change 4 — Erebosis species + maturity

- **Original:** species_scope human · maturity established
- **Adjudicated:** species_scope **Drosophila (invertebrate model)** · maturity **emerging**
- **Source:** Decoder
- **Dependencies:** Decoder CSV+XLSX · app decoder · Table S11
- **Verification:** PASS
- **Unresolved:** none.

## Change 5 — VCD species correction (plant + protist, not human)

- **Original:** cross_species → (interim) fungal (yeast) → **plant (Arabidopsis, Picea abies) + protist (Dictyostelium discoideum); not human**
- **Source:** Decoder `species_scope` + `provenance_note`; Matrix `elic_onto_operational_note`
- **Dependencies:** Decoder CSV+XLSX · app decoder · Table S11 · Matrix CSV+RDS (24 rows)
- **Verification:** PASS (explicit organisms present; "yeast" absent)
- **Unresolved:** none.

## Change 6 — VCD plant reference PMIDs

- **Original:** `secondary_refs_pmids` empty
- **Adjudicated:** `24344187;35390283` (Minina 2013 Picea abies + Feng 2022 Arabidopsis root cap)
- **Note:** Hatsugai 2004 VPE (hypersensitive response) correctly EXCLUDED — different entity.
- **Source:** Decoder
- **Dependencies:** Decoder CSV+XLSX · app decoder · Table S11
- **Verification:** PASS
- **Unresolved:** none.

## Change 7 — Wang et al. 2025 disambiguation

- **Original:** "Wang et al. 2025" (both entities)
- **Adjudicated:** "Wang et al. 2025 (Metalloptosis umbrella)" · "Wang et al. 2025 (Mitoxyperilysis)"
- **Source:** Decoder `reference_citation`
- **Dependencies:** Decoder CSV+XLSX · app decoder · **Table S11 (was missed — caught by alignment audit, corrected)**
- **Verification:** PASS (0 real mismatches)
- **Unresolved:** none.

## Change 8 — Rodrigues citation year + PMID

- **Original:** "Rodrigues et al. 2026 (Dataset S1A)" + wrong founding PMID
- **Adjudicated:** "Rodrigues et al. 2025 (Dataset S1A)" + PMID 41048343
- **Source:** Decoder `reference_citation` + `reference_pmid`
- **Dependencies:** Decoder CSV+XLSX · app decoder · Table S11 · build script · example reports · audit report
- **Verification:** PASS (12 rows uniform 41048343)
- **Unresolved:** none (separate 2026 publication #784804 preserved).

## Change 9 — "canonical" → "canonicalized / normalized / RCD-related" (Pre-Audit 0)

- **Source:** manuscript + app + decoder + docs (user-facing strings)
- **Dependencies:** manuscript · supplementary info · supplementary tables (INDEX, Variable Descriptor, S5, S9, Matrix Descriptor) · decoder docs + code · app modules + www + board
- **Verification:** PASS (compliance checks; no stale "53 canonical entities"/"canonical RCD form")
- **Unresolved:** matrix column `rcd_form_canonical` (schema, intentionally kept); `docs/RCDome_manuscript.md` archived V025 draft (preserved) (54→53 archived (preserved)).

## Change 10 — Level distribution 12/18 → 11/19

- **Source:** Matrix (16 L1 · 5 L2 · 2 L3 · 11 L4 · 19 L5)
- **Dependencies:** manuscript · explore.html (app + top-level) · landing/dome `LEVEL_COUNTS` · Traceability Contract
- **Verification:** PASS (compliance "Level counts" group)
- **Unresolved:** none.

## Resolved / archived (not deferred)

- **Modality count = 16 bona fide modalities (L1)** — adjudicated truth; "39 modalities" is a historical correspondence, not a truth artifact.
- **V025→V026 (54→53)** — V025 draft ARCHIVED (preserved); truth = V026.

## Global deferred (the ONLY remaining expert-review item)

- **G5 / `independent_replication`** — uniform "pending until curated" (all 53; allowed values none / limited / multiple).

---

**Closure:** all accepted changes are propagated + independently verified (62/62). Re-run `code/compliance_audit.py` as the repeatable gate before submission.
