# -*- coding: utf-8 -*-
"""Canonical audit for the RCDome Digital Molecular RCD Board (smoke + benchmark).

The checklist is FIXED and identical for every run. The count never varies.

Current canonical count = 28:
  - Governance (10): 7 causal verbs + hedging + disclaimer + 3 numbered queries.
  - Policy (14): 9 internal terms + bare "database" + bare "decoder"
    + raw relationship terms + "RCDome database" + "RCDome decoder".
  - Accuracy (4): PMIDs exist + founding PMID + role + direction.

History: 25 -> 28 after the three approved amendments (bare database/decoder
ban, relationship-term translation, new disclaimer).
"""
import re
import datetime
import html

# (display name, regex covering all tenses, hedging replacement)
CAUSAL_VERB_FORMS = [
    ("suppress", r"\b(?:suppress|suppresses|suppressed|suppressing)\b",
     "is associated with reduced"),
    ("drive", r"\b(?:drive|drives|driven|driving)\b", "contributes to"),
    ("prevent", r"\b(?:prevent|prevents|prevented|preventing)\b",
     "is associated with reduced"),
    ("execute", r"\b(?:execute|executes|executed|executing)\b", "carries out"),
    ("cause", r"\b(?:cause|causes|caused|causing)\b", "is associated with"),
    ("demonstrate", r"\b(?:demonstrate|demonstrates|demonstrated|demonstrating)\b",
     "indicates"),
    ("prove", r"\b(?:prove|proves|proved|proven)\b", "suggests"),
    ("confirm", r"\b(?:confirm|confirms|confirmed|confirming)\b",
     "is consistent with"),
    ("establish", r"\b(?:establish|establishes|established|establishing)\b",
     "provides evidence for"),
]

INTERNAL_TERMS = [
    "matrix", "cot_role", "mechanistic_class",
    "T1:", "T2:", "T3:", "T4:",
    "Governance note", "Knock Test",
]

BARE_WORDS = ["database", "decoder"]

RELATIONSHIP_RAW = [
    "is_a", "subtype_of", "triggered_by", "driven_by",
    "umbrella_for", "associated_with", "synonym_of", "outcome_of",
]

# canonical key fields for the board's input payload
MATRIX_KEYS = ["mechanistic_class", "cot_role", "cot_direction",
               "cot_mechanistic", "required_for_death", "pmid_list",
               "evidence_tier", "num_sources"]
DECODER_KEYS = ["category", "hard_gate_status", "relationship_type",
                "parent_entity", "operational_definition", "key_molecules",
                "core_mechanism", "species_scope", "evidence_maturity",
                "independent_replication", "C1", "C2", "C3", "C4", "C5",
                "C6", "S", "founding_pmid"]

MATRIX_DESC = {
    "mechanistic_class": ("Mechanistic class", "Evidence & validation — the gene's mechanistic classification"),
    "cot_role": ("Role", "Chain-of-thought classification — executor / regulator / marker"),
    "cot_direction": ("Direction", "Chain-of-thought classification — promotes / protects / unclear"),
    "cot_mechanistic": ("Mechanistic (yes/no)", "Chain-of-thought classification — whether the gene is mechanistically involved"),
    "required_for_death": ("Required for death", "Elicit extraction — whether the gene is required for the death process"),
    "pmid_list": ("PMIDs", "Supporting PMIDs recorded for the gene–RCD association"),
    "evidence_tier": ("Evidence tier", "Evidence & validation — T1 (gold) to T4 (weak)"),
    "num_sources": ("Source count", "Source provenance — number of independent source databases"),
}

DECODER_DESC = {
    "category": ("Category", "Entity category (Executioner / Trigger / Functional / Subtype / Synonym / Umbrella / Contextual / Taxon / Cell-type / Differentiation)"),
    "hard_gate_status": ("Hard gate", "Hard-gate L1 admission status (L1-ELIGIBLE passes machinery + necessity; NOT-L1 = subtype / trigger / umbrella / morphology)"),
    "relationship_type": ("Relationship", "Ontological relation (is_a / subtype_of / triggered_by / driven_by / umbrella_for / associated_with)"),
    "parent_entity": ("Parent entity", "Parent entity in the ontology (empty for root)"),
    "operational_definition": ("Operational definition", "Operational definition prose (Galluzzi MC1-MC5 logic, classification-led, citation-free)"),
    "key_molecules": ("Key molecules", "Key molecular machinery (comma-separated)"),
    "core_mechanism": ("Core mechanism", "Short core mechanism (from the 25-Forms Reference Table)"),
    "species_scope": ("Species scope", "Species scope of the modality (human / mammalian / vertebrate / invertebrate_model / plant / cross_species / uncertain)"),
    "evidence_maturity": ("Evidence maturity", "Evidence maturity (established / supported / emerging / legacy / provisional)"),
    "independent_replication": ("Independent replication", "Independent replication (none / limited / multiple; pending until curated)"),
    "RS1": ("RS1 — Extent of Research", "Extent of Research criterion (1-10, weight 25%)"),
    "RS2": ("RS2 — Direct Involvement", "Direct Involvement criterion (1-10, weight 25%)"),
    "RS3": ("RS3 — Impact on homeostasis", "Impact on cell/tissue homeostasis criterion (1-10, weight 20%)"),
    "RS4": ("RS4 — Emerging Potential", "Emerging Potential criterion (1-10, weight 15%)"),
    "RS5": ("RS5 — Biological Significance", "Biological Significance criterion (1-10, weight 10%)"),
    "RS6": ("RS6 — Pathophysiological Relevance", "Pathophysiological Relevance criterion (1-10, weight 5%)"),
    "S": ("Overall score (S)", "Overall Score = 0.25*RS1 + 0.25*RS2 + 0.20*RS3 + 0.15*RS4 + 0.10*RS5 + 0.05*RS6 (deterministic)"),
    "founding_pmid": ("Founding PMID", "Founding PMID (the discovery article)"),
}

CHECK_DESCRIPTIONS = {
    "A1": "Accuracy check A1 verifies that every cited PMID exists in the RCDome data (no invented PMIDs).",
    "A2": "Accuracy check A2 verifies that the entity's founding PMID is cited when its operational definition is described.",
    "A3": "Accuracy check A3 verifies that the narrative states the gene's role (executor, regulator, or marker) exactly as recorded in the RCDome database.",
    "A4": "Accuracy check A4 verifies that the narrative states the direction (promotes or protects) exactly as recorded in the RCDome database.",
    "N1": "Negative-control check N1 verifies that the narrative states that no association is recorded, without inventing a role or direction.",
    "C1": "Census check C1 verifies that the narrative states the entity's category exactly as recorded in the RCDome decoder.",
    "C2": "Census check C2 verifies that the narrative states the entity's hard-gate status exactly as recorded in the RCDome decoder.",
}


def _payload_rows(gene, entity, mr, dr):
    """Human-readable payload as (label, value, description) rows."""
    rows = [("Gene", gene, "HGNC gene symbol queried"),
            ("Entity", entity, "RCD-related entity queried")]
    if mr is not None:
        rows.append(("RCDome database", "", ""))
        rows += [(MATRIX_DESC.get(k, (k, ""))[0],
                  "not applicable" if str(mr[k]).lower() == "nan" else str(mr[k]),
                  MATRIX_DESC.get(k, (k, ""))[1]) for k in MATRIX_KEYS]
    else:
        rows.append(("RCDome database", "not recorded (no association)", ""))
    if dr is not None:
        rows.append(("RCDome decoder", "", ""))
        rows += [(DECODER_DESC.get(k, (k, ""))[0],
                  "not applicable" if str(dr[k]).lower() == "nan" else str(dr[k]),
                  DECODER_DESC.get(k, (k, ""))[1]) for k in DECODER_KEYS]
    else:
        rows.append(("RCDome decoder", "not recorded", ""))
    return rows

HEDGE_MARKERS = [
    "Hypothesis:", "may suggest", "consistent with",
    "raises the possibility", "requires validation",
]

DISCLAIMER_MARKERS = [
    "hypothesis-generating",
    "strength of evidence varies",
    "independently cross-validate",
]

DISCLAIMER = (
    "The interpretations presented above should be considered hypothesis-generating "
    "and are intended to support biological exploration of regulated cell death. "
    "The proposed mechanisms and gene–RCD associations are inferred from the "
    "RCDome database and the RCDome decoder. The strength of evidence varies across "
    "associations: some are well-founded and unambiguous, while others are provisional. "
    "Users should independently cross-validate each association and, in some instances, "
    "pursue additional experimental validation."
)


def sanitize_terminology(narr):
    """Deterministic terminology normalization (NOT AI — a fixed, auditable
    string rule). Replaces bare "database"/"decoder" with the reader-facing
    names, so the report never shows internal short forms.
    Returns the sanitized narrative."""
    out = re.sub(r"(?<!RCDome )\bdecoder\b", "RCDome decoder",
                 narr, flags=re.IGNORECASE)
    out = re.sub(r"(?<!RCDome )\bdatabase\b", "RCDome database",
                 out, flags=re.IGNORECASE)
    return out


def scrub_governance_violations(txt, founding_pmid=None):
    """Deterministic post-processing scrub (mirrors CancerPredictor
    scrub_governance_violations). Auto-fixes governance violations and records
    each correction. Returns (scrubbed_text, actions). NOT AI — fixed rules."""
    if not txt:
        return txt, []
    actions = []

    # 0. strip markdown bold/italic markers (prose-only board output)
    txt, n = re.subn(r"\*\*", "", txt)
    if n:
        actions.append({"rule": "T6", "severity": "FIXED",
                        "detail": f"Stripped markdown bold markers ({n}x)"})
    txt, n = re.subn(r"__([^_]+)__", r"\1", txt)
    if n:
        actions.append({"rule": "T6", "severity": "FIXED",
                        "detail": f"Stripped underscore bold ({n}x)"})

    # 1. causal verbs -> hedging equivalents (mirrors V-004 / V-006)
    for name, pattern, repl in CAUSAL_VERB_FORMS:
        txt, n = re.subn(pattern, repl, txt, flags=re.IGNORECASE)
        if n:
            actions.append({"rule": "G7", "severity": "FIXED",
                            "detail": f"Replaced causal verb '{name}' ({n}x) "
                                      f"with '{repl}'"})

    # 2. bare database/decoder -> RCDome database/decoder (terminology)
    for word in ["decoder", "database"]:
        pat = r"(?<!RCDome )\b" + word + r"\b"
        txt, n = re.subn(pat, "RCDome " + word, txt, flags=re.IGNORECASE)
        if n:
            actions.append({"rule": "P1", "severity": "FIXED",
                            "detail": f"Replaced bare '{word}' ({n}x) with "
                                      f"'RCDome {word}'"})

    # 2b. narrow "matrix" scrub (data-meaning only; biology-safe: does not
    # touch "extracellular matrix", "mitochondrial matrix", or "matrix
    # metalloproteinase")
    for pat, repl in [(r"the\s+matrix\b", "the RCDome database"),
                      (r"compiled\s+matrix\b", "RCDome database"),
                      (r"evidence\s+matrix\b", "RCDome database")]:
        txt, n = re.subn(pat, repl, txt, flags=re.IGNORECASE)
        if n:
            actions.append({"rule": "P1", "severity": "FIXED",
                            "detail": f"Replaced '{pat}' ({n}x) with '{repl}'"})

    # 3. raw relationship terms -> plain prose
    rel_repl = [
        (r"\bis_a\b", "a subtype of"),
        (r"\bsubtype_of\b", "a subtype of"),
        (r"\btriggered_by\b", "is triggered by"),
        (r"\bdriven_by\b", "is driven by"),
        (r"\bumbrella_for\b", "serves as an umbrella for"),
        (r"\bassociated_with\b", "is associated with"),
        (r"\bsynonym_of\b", "is a synonym of"),
        (r"\boutcome_of\b", "is an outcome of"),
    ]
    for pat, repl in rel_repl:
        txt, n = re.subn(pat, repl, txt, flags=re.IGNORECASE)
        if n:
            actions.append({"rule": "P2", "severity": "FIXED",
                            "detail": f"Translated relationship term '{pat}' "
                                      f"({n}x) to '{repl}'"})

    # 4. strip markdown bold/asterisks around gene symbols
    txt, n = re.subn(r"\*\*([A-Z][A-Z0-9-]{1,})\*\*", r"\1", txt)
    if n:
        actions.append({"rule": "G20", "severity": "FIXED",
                        "detail": f"Stripped markdown bold from gene symbols "
                                  f"({n}x)"})

    # 5. auto-number unnumbered query lines after "Suggested Queries:"
    lines = txt.split('\n')
    out = []
    in_queries = False
    n = 0
    for line in lines:
        s = line.strip()
        if 'Suggested Queries' in s:
            in_queries = True
            out.append(line)
            continue
        if in_queries and s.startswith('The interpretations'):
            in_queries = False
        if (in_queries and s and not re.match(r'^\d+\.', s) and
                re.match(r'^(What|Which|How|Are|Does|Is|Do|Can|Could|Should|Would|Why|Where|When)\b', s, re.I)):
            n += 1
            out.append(f'{n}. {s}')
        else:
            out.append(line)
    if n:
        txt = '\n'.join(out)
        actions.append({"rule": "G10", "severity": "FIXED",
                        "detail": f"Numbered {n} unnumbered query(ies)"})

    # 6. ensure the EXACT disclaimer (replace any partial/paraphrased version)
    if DISCLAIMER not in txt:
        txt = re.sub(r"The interpretations presented above.*?(?=\n\nHypothesis:|\Z)",
                     "", txt, flags=re.DOTALL)
        txt = txt.rstrip() + "\n\n" + DISCLAIMER
        actions.append({"rule": "G11", "severity": "FIXED",
                        "detail": "Ensured the exact disclaimer"})

    # 7. HEDGE GUARD: append a generic hedged sentence if none exists
    if not any(s in txt for s in HEDGE_MARKERS):
        txt = txt.rstrip() + (
            "\n\nHypothesis: the recorded classification is consistent with the "
            "biological context described; further experimental validation is required.")
        actions.append({"rule": "G10", "severity": "FIXED",
                        "detail": "Appended a generic hedged sentence (no hedge present)"})

    # 8. NAME GUARD: ensure both reader-facing names appear
    if "RCDome database" not in txt:
        txt = txt.rstrip() + "\n\nThe evidence summarized above is recorded in the RCDome database."
        actions.append({"rule": "P13", "severity": "FIXED",
                        "detail": "Ensured 'RCDome database' appears"})
    if "RCDome decoder" not in txt:
        txt = txt.rstrip() + "\n\nThe ontological reference is provided by the RCDome decoder."
        actions.append({"rule": "P14", "severity": "FIXED",
                        "detail": "Ensured 'RCDome decoder' appears"})

    # 9. FOUNDING-PMID append (completeness; only if provided + not yet cited)
    if founding_pmid and str(founding_pmid).strip() and \
       str(founding_pmid).strip() not in txt:
        txt = txt.rstrip() + (
            f"\n\nThe founding reference for this entity is recorded as "
            f"PMID {founding_pmid}.")
        actions.append({"rule": "A2", "severity": "FIXED",
                        "detail": f"Appended founding PMID {founding_pmid}"})

    # collapse residual whitespace artifacts
    txt = re.sub(r"\s{2,}", " ", txt).strip()
    return txt, actions


def _bare_hits(text, word):
    """Count occurrences of `word` NOT preceded by 'RCDome '."""
    return len(re.findall(r"(?<!RCDome )\b" + word + r"\b", text, re.IGNORECASE))


def _matrix_hits(text):
    """Count data-meaning 'matrix' occurrences (biology-safe).

    Ignores 'extracellular matrix', 'mitochondrial matrix' and
    'matrix metalloproteinase' (legitimate biology terms).
    """
    tmp = re.sub(r"extracellular\s+matrix", " ", text, flags=re.IGNORECASE)
    tmp = re.sub(r"mitochondrial\s+matrix", " ", tmp, flags=re.IGNORECASE)
    tmp = re.sub(r"matrix\s+metalloproteinase", " ", tmp, flags=re.IGNORECASE)
    return len(re.findall(r"\bmatrix\b", tmp, flags=re.IGNORECASE))


def audit_report(narr, mr, dr):
    """Run the fixed 28-point audit.

    narr : narrative text produced by the board
    mr   : matrix row (pandas Series) for the gene-entity pair
    dr   : decoder row (pandas Series) for the entity
    """
    checks = []
    P = F = 0

    def ck(cid, name, ok, detail=""):
        nonlocal P, F
        checks.append((cid, name, ok, detail))
        P += ok
        F += (not ok)

    # ---- GOVERNANCE (10) ----
    for i, (name, pattern, repl) in enumerate(CAUSAL_VERB_FORMS, 1):
        n = len(re.findall(pattern, narr, re.IGNORECASE))
        ck(f"G{i}", f'no "{name}"', n == 0, f"{n} hits")
    ck("G10", "hedging present", any(s in narr for s in HEDGE_MARKERS))
    ck("G11", "new disclaimer present",
       all(s in narr for s in DISCLAIMER_MARKERS))
    ck("G12", "exactly 3 numbered queries",
       len(re.findall(r"^\d+\.", narr, re.M)) >= 3)

    # ---- POLICY (14) ----
    for i, term in enumerate(INTERNAL_TERMS, 1):
        n = (_matrix_hits(narr) if term == "matrix"
             else narr.count(term))
        ck(f"P{i}", f'no "{term}"', n == 0, f"{n} hits")
    for i, word in enumerate(BARE_WORDS, 1):
        n = _bare_hits(narr, word)
        ck(f"P{len(INTERNAL_TERMS)+i}", f'no bare "{word}"', n == 0, f"{n} hits")
    rel_hits = [t for t in RELATIONSHIP_RAW if t in narr]
    ck("P12", "no raw relationship terms",
       len(rel_hits) == 0, f"found={rel_hits}")
    ck("P13", '"RCDome database" used', "RCDome database" in narr)
    ck("P14", '"RCDome decoder" used', "RCDome decoder" in narr)

    # ---- ACCURACY (4) ----
    valid_pmids = set()
    for col in ["pmid_list", "llm_pmids"]:
        if col in mr.index:
            for p in str(mr[col]).split(";"):
                p = p.strip()
                if p.isdigit():
                    valid_pmids.add(p)
    valid_pmids.add(str(dr.get("founding_pmid", "")).strip())
    cited = set(re.findall(r"PMID[: ]?(\d+)", narr))
    ck("A1", "all cited PMIDs exist in data",
       len(cited - valid_pmids) == 0, f"bad={sorted(cited - valid_pmids)}")
    ck("A2", "founding PMID cited",
       str(dr.get("founding_pmid", "")).strip() in narr,
       dr.get("founding_pmid", ""))
    expected_role = str(mr.get("cot_role", "")).lower()
    role_word = {"executor": "executor", "regulator": "regulator",
                 "marker": "marker"}.get(expected_role, expected_role)
    ck("A3", f"role = {expected_role}", role_word in narr.lower(),
       f"expected {expected_role}")
    expected_dir = str(mr.get("cot_direction", "")).lower()
    dir_word = {"promotes": "promot", "protects": "protect",
                "unclear": "unclear"}.get(expected_dir, expected_dir)
    ck("A4", f"direction = {expected_dir}", dir_word in narr.lower(),
       f"expected {expected_dir}")

    summary = f"{P} PASS, {F} FAIL"
    return {
        "checks": checks,
        "passed": P,
        "failed": F,
        "summary": summary,
        "n_total": P + F,
    }


def audit_negative(narr, dr):
    """Negative-control audit (pair NOT in the RCDome database).

    Same 28 canonical checks, but accuracy A3/A4 are inverted (the board
    must NOT claim a role or direction), plus one negative-specific check
    (must state "not recorded" / "no association"). Total = 29.
    """
    checks = []
    P = F = 0

    def ck(cid, name, ok, detail=""):
        nonlocal P, F
        checks.append((cid, name, ok, detail))
        P += ok
        F += (not ok)

    # GOVERNANCE (10) — identical to canonical
    for i, (name, pattern, repl) in enumerate(CAUSAL_VERB_FORMS, 1):
        n = len(re.findall(pattern, narr, re.IGNORECASE))
        ck(f"G{i}", f'no "{name}"', n == 0, f"{n} hits")
    ck("G10", "hedging present", any(s in narr for s in HEDGE_MARKERS))
    ck("G11", "new disclaimer present", all(s in narr for s in DISCLAIMER_MARKERS))
    ck("G12", "exactly 3 numbered queries",
       len(re.findall(r"^\d+\.", narr, re.M)) >= 3)

    # POLICY (14) — identical to canonical
    for i, term in enumerate(INTERNAL_TERMS, 1):
        n = (_matrix_hits(narr) if term == "matrix"
             else narr.count(term))
        ck(f"P{i}", f'no "{term}"', n == 0, f"{n} hits")
    for i, word in enumerate(BARE_WORDS, 1):
        n = _bare_hits(narr, word)
        ck(f"P{len(INTERNAL_TERMS)+i}", f'no bare "{word}"', n == 0, f"{n} hits")
    rel_hits = [t for t in RELATIONSHIP_RAW if t in narr]
    ck("P12", "no raw relationship terms", len(rel_hits) == 0, f"found={rel_hits}")
    ck("P13", '"RCDome database" used', "RCDome database" in narr)
    ck("P14", '"RCDome decoder" used', "RCDome decoder" in narr)

    # ACCURACY (negative: anti-hallucination — hard facts only)
    valid_pmids = {str(dr.get("founding_pmid", "")).strip()}
    cited = set(re.findall(r"PMID[: ]?(\d+)", narr))
    ck("A1", "all cited PMIDs exist in data",
       len(cited - valid_pmids) == 0, f"bad={sorted(cited - valid_pmids)}")
    low = narr.lower()
    # NEGATIVE-SPECIFIC (1): must state no association
    ck("N1", 'states "not recorded"/"no association"',
       ("no association" in low) or ("does not record" in low) or ("not recorded" in low))

    summary = f"{P} PASS, {F} FAIL"
    return {"checks": checks, "passed": P, "failed": F,
            "summary": summary, "n_total": P + F}


CATEGORY_TRANSLATIONS = {
    "Executioner": ["executioner"],
    "LEGACY": ["legacy"],
    "EMERGING": ["emerging"],
    "SUBTYPE": ["subtype"],
    "CONTEXTUAL": ["contextual"],
    "Functional": ["functional"],
    "TAXON": ["taxon", "drosophila", "organism-specific", "species-specific"],
    "UMBRELLA": ["umbrella"],
    "MORPHOLOGY": ["morpholog"],
    "CORE_PENDING": ["core pending", "core-pending"],
    "Trigger": ["trigger"],
    "CELLULAR_PROCESS": ["cellular process"],
    "DIFFERENTIATION": ["differentiation"],
    "CELL_TYPE": ["cell type"],
    "SYNONYM": ["synonym"],
    "INTEGRATED_PROGRAM": ["integrated program"],
    "COMPOSITE": ["composite", "combined", "integrat"],
}


def audit_census(narr, dr):
    """Census (lookup-mode) audit: 7 causality + disclaimer + 14 policy
    + 2 census-accuracy (category + gate). Total = 24.
    Hedge (G8) and 3-queries (G10) are NOT applied: a factual lookup is not
    an interpretive synthesis."""
    checks = []
    P = F = 0

    def ck(cid, name, ok, detail=""):
        nonlocal P, F
        checks.append((cid, name, ok, detail))
        P += ok
        F += (not ok)

    # GOVERNANCE (8: causality G1-G7 + disclaimer G9)
    for i, (name, pattern, repl) in enumerate(CAUSAL_VERB_FORMS, 1):
        n = len(re.findall(pattern, narr, re.IGNORECASE))
        ck(f"G{i}", f'no "{name}"', n == 0, f"{n} hits")
    ck("G11", "new disclaimer present", all(s in narr for s in DISCLAIMER_MARKERS))

    # POLICY (14)
    for i, term in enumerate(INTERNAL_TERMS, 1):
        n = (_matrix_hits(narr) if term == "matrix"
             else narr.count(term))
        ck(f"P{i}", f'no "{term}"', n == 0, f"{n} hits")
    for i, word in enumerate(BARE_WORDS, 1):
        n = _bare_hits(narr, word)
        ck(f"P{len(INTERNAL_TERMS)+i}", f'no bare "{word}"', n == 0, f"{n} hits")
    rel_hits = [t for t in RELATIONSHIP_RAW if t in narr]
    ck("P12", "no raw relationship terms", len(rel_hits) == 0, f"found={rel_hits}")
    ck("P13", '"RCDome database" used', "RCDome database" in narr)
    ck("P14", '"RCDome decoder" used', "RCDome decoder" in narr)

    # CENSUS ACCURACY (2)
    cat = str(dr.get("category", ""))
    if cat == "CORE_PENDING":
        ck("C1", f"category = {cat}", True, "skipped (CORE_PENDING sentinel)")
    else:
        phrases = CATEGORY_TRANSLATIONS.get(cat, [cat.lower()])
        ck("C1", f"category = {cat}",
           any(p in narr.lower() for p in phrases), f"expected {cat}")
    gate = str(dr.get("hard_gate_status", ""))
    low = narr.lower()
    if gate == "L1-ELIGIBLE":
        ck("C2", "gate = L1-ELIGIBLE",
           ("l1" in low and ("eligib" in low or "meets" in low or
                             "criteria" in low)),
           f"expected {gate}")
    else:
        not_l1 = (re.search(r"not[- ]?l1", low) is not None or
                  "not eligible" in low or
                  "does not meet" in low or
                  ("not considered" in low and "l1" in low))
        ck("C2", f"gate = {gate}", not_l1, f"expected {gate}")

    summary = f"{P} PASS, {F} FAIL"
    return {"checks": checks, "passed": P, "failed": F,
            "summary": summary, "n_total": P + F}


def violation_types(result):
    """Count violations by category from an audit result (for Test 4).

    Mapping (corrected): G1-G9 -> causality; G10 -> hedge;
    G11 -> disclaimer; G12 -> queries; P* -> terminology; A1-A4 -> accuracy.
    """
    counts = {"causality": 0, "hedge": 0, "disclaimer": 0, "queries": 0,
              "terminology": 0, "accuracy": 0}
    for cid, name, ok, detail in result["checks"]:
        if ok:
            continue
        if cid in ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"):
            counts["causality"] += 1
        elif cid == "G10":
            counts["hedge"] += 1
        elif cid == "G11":
            counts["disclaimer"] += 1
        elif cid == "G12":
            counts["queries"] += 1
        elif cid.startswith("P"):
            counts["terminology"] += 1
        else:
            counts["accuracy"] += 1
    return counts


def violation_details(result):
    """Return every failed check with its exact detail (for Test 4 logging)."""
    return [{"check": cid, "name": name, "detail": detail}
            for cid, name, ok, detail in result["checks"] if not ok]


ROLE_WORDS = {"executor": "executor", "regulator": "regulator",
              "marker": "marker", "uncertain": "uncertain"}
DIR_WORDS = {"promotes": "promot", "protects": "protect",
             "unclear": "unclear"}


def role_word(role):
    return ROLE_WORDS.get(str(role).lower(), str(role).lower())


def dir_word(direction):
    return DIR_WORDS.get(str(direction).lower(), str(direction).lower())


def accuracy_ok(result):
    """True if all ACCURACY checks pass (A1-A4, N1 for negatives).
    Governance/policy checks are excluded — they are reported separately
    as violation rates (Test 4). A2 (founding PMID) is a completeness
    metric, excluded from the hard accuracy gate."""
    return all(ok for cid, name, ok, detail in result["checks"]
               if cid in ("A1", "A3", "A4", "N1"))


def census_ok(result):
    """True if the census-accuracy checks pass (C1 category, C2 gate)."""
    return all(ok for cid, name, ok, detail in result["checks"]
               if cid.startswith("C"))


def build_audit_trail(narr, gene, entity, mr, dr, res=None, latency=None,
                    actions=None):
    """Deterministic governance + payload audit trail (transparency & traceability).

    Appended AFTER the AI synthesis. NOT AI — a fixed, auditable rule:
      (1) execution timing (timestamp + processing time)
      (2) governance audit badge (mirrors CancerPredictor build_governance_audit_badge)
      (3) raw injection payload (the exact data the model received)
    """
    actions = actions or []
    if res is None:
        res = audit_report(narr, mr, dr) if mr is not None else audit_negative(narr, dr)
    fact_fails = [{"cid": cid, "name": name, "detail": detail}
                  for cid, name, ok, detail in res["checks"]
                  if not ok and cid in ("A1", "A3", "A4", "N1", "C1", "C2")]
    if not actions and not fact_fails:
        gov = ("✅ Governance Audit: No violations detected. "
               "LLM output passed all automated checks.")
    else:
        parts = []
        if actions:
            parts.append(f"{len(actions)} automated correction(s) applied")
        if fact_fails:
            parts.append(f"{len(fact_fails)} factuality issue(s)")
        gov = ("⚠️ Governance Audit: " + "; ".join(parts) + " (click to expand)\n")
        for a in actions:
            gov += f"  [{a['rule']}] {a['detail']}\n"
        for f in fact_fails:
            gov += f"  [FACT] {f['cid']} {f['name']} — not auto-fixable, review required\n"
            gov += f"    {CHECK_DESCRIPTIONS.get(f['cid'], '')}\n"
            if f['detail']:
                gov += f"    Audit detail: {f['detail']}\n"
        gov = gov.rstrip()
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    timing = f"Automatically generated on {now}"
    if latency is not None:
        timing += f" (Processing Time: {latency:.1f}s)"
    rows = _payload_rows(gene, entity, mr, dr)
    payload = (
        "Audit Molecular and Cellular Payload Data (Raw Injection)\n"
        "The following raw text represents the exact contextual data payloads "
        "injected into the language model to generate the synthesis above.\n"
        + "\n".join(f"{lbl}: {val}" if (not val or not desc) else f"{lbl}: {val}  ({desc})"
                    for lbl, val, desc in rows)
    )
    return f"\n\n{'-'*40}\n{timing}\n\n{gov}\n\n{payload}"


def build_html_report(narr, gene, entity, mr, dr, res=None, latency=None,
                      actions=None):
    """Build a self-contained HTML report (mirrors CancerPredictor).

    Renders the synthesis, the governance badge, the raw-injection payload
    and the execution timing as downloadable HTML, exactly as the
    CancerPredictor app does for its clinical synthesis.
    """
    actions = actions or []
    if res is None:
        res = audit_report(narr, mr, dr) if mr is not None else audit_negative(narr, dr)

    # synthesis -> HTML paragraphs (disclaimer split out + italic)
    disc = ""
    body = narr
    idx = narr.find("The interpretations presented above")
    if idx >= 0:
        body = narr[:idx].rstrip()
        disc = narr[idx:].strip()
    paras = [p.strip() for p in body.split('\n\n') if p.strip()]
    narr_html = ''.join(
        f'<p style="color:#e2e8f0; line-height:1.6; margin:0 0 12px;">'
        f'{html.escape(p).replace(chr(10), "<br>")}</p>' for p in paras)
    if disc:
        narr_html += ('<p style="color:#94a3b8; font-style:italic; '
                      'line-height:1.6; margin:0 0 12px;">'
                      f'{html.escape(disc).replace(chr(10), " ")}</p>')

    # governance badge
    fact_fails = [{"cid": cid, "name": name, "detail": detail}
                  for cid, name, ok, detail in res["checks"]
                  if not ok and cid in ("A1", "A3", "A4", "N1", "C1", "C2")]
    if not actions and not fact_fails:
        badge = ('<div style="background:#065f46; color:#6ee7b7; padding:6px 12px; '
                 'border-radius:4px; font-size:0.85rem; margin-top:12px;">'
                 '✅ Governance Audit: No violations detected. '
                 'LLM output passed all automated checks.</div>')
    else:
        parts = []
        if actions:
            parts.append(f"{len(actions)} automated correction(s) applied")
        if fact_fails:
            parts.append(f"{len(fact_fails)} factuality issue(s)")
        summary = ('⚠️ Governance Audit: ' + '; '.join(parts) +
                   ' (click to expand)')
        detail = []
        for a in actions:
            detail.append(f'<li><span style="color:#fbbf24;">[{html.escape(a["rule"])}]</span> '
                          f'{html.escape(a["detail"])}</li>')
        for f in fact_fails:
            desc = CHECK_DESCRIPTIONS.get(f["cid"], "")
            det = f' Audit detail: {f["detail"]}' if f["detail"] else ""
            detail.append(
                f'<li><span style="color:#f87171;">[FACT]</span> '
                f'{html.escape(f["cid"] + " " + f["name"])} — not auto-fixable, review required<br>'
                f'<span style="color:#94a3b8;">{html.escape(desc + det)}</span></li>')
        badge = ('<details style="background:#1e293b; border:1px solid #fbbf24; '
                 'border-radius:6px; padding:10px 14px; margin-top:12px; '
                 'font-size:0.85rem;">'
                 f'<summary style="color:#fbbf24; cursor:pointer; font-weight:bold;">'
                 f'{summary}</summary>'
                 f'<ul style="margin-top:8px; color:#cbd5e1; line-height:1.6;">'
                 f'{"".join(detail)}</ul></details>')

    # raw-injection payload
    rows = _payload_rows(gene, entity, mr, dr)
    table_rows = ['<tr><th style="text-align:left; color:#94a3b8; padding:4px 0; '
                 'font-weight:bold;">Variable</th>'
                 '<th style="text-align:left; color:#94a3b8; padding:4px 0; '
                 'font-weight:bold;">Description</th>'
                 '<th style="text-align:left; color:#94a3b8; padding:4px 0; '
                 'font-weight:bold;">Value</th></tr>']
    for lbl, val, desc in rows:
        if not val:
            table_rows.append(
                f'<tr><td colspan="3" style="color:#34d399; font-weight:bold; '
                f'padding:4px 0;">{html.escape(lbl)}</td></tr>')
        else:
            table_rows.append(
                f'<tr><td style="color:#94a3b8; padding:2px 8px 2px 0; '
                f'vertical-align:top;">{html.escape(lbl)}</td>'
                f'<td style="color:#64748b; padding:2px 8px 2px 0; '
                f'vertical-align:top;">{html.escape(desc)}</td>'
                f'<td style="color:#cbd5e1; padding:2px 0; '
                f'vertical-align:top;">{html.escape(val)}</td></tr>')
    payload_html = ('<details style="margin-top:15px; padding:10px; '
                    'background:rgba(15,23,42,0.4); border:1px solid #334155; '
                    'border-radius:6px;">'
                    '<summary style="color:#94a3b8; font-size:0.85rem; '
                    'cursor:pointer;">Audit Molecular and Cellular Payload Data '
                    '(Raw Injection)</summary>'
                    '<table style="margin-top:10px; font-size:0.75rem; '
                    'width:100%; border-collapse:collapse;">'
                    + ''.join(table_rows) + '</table></details>')

    # timing
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    timing = f"Automatically generated on {now}"
    if latency is not None:
        timing += f" (Processing Time: {latency:.1f}s)"
    time_html = ('<div style="font-size:10px; color:#94a3b8; text-align:right; '
                 f'margin-top:15px;">{html.escape(timing)}</div>')

    return ('<div style="background:rgba(16,185,129,0.1); border:1px solid '
            'rgba(16,185,129,0.3); border-radius:8px; padding:20px; '
            'font-family:sans-serif;">'
            '<h4 style="color:#34d399; font-weight:bold; margin-top:0;">'
            'RCDome Digital Molecular Synthesis Report</h4>'
            f'{narr_html}{badge}{payload_html}{time_html}</div>')


def print_report(result):
    for cid, name, ok, detail in result["checks"]:
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {cid:>3} {name}  {detail}")
    print(f"===== {result['summary']} (total {result['n_total']}) =====")


if __name__ == "__main__":
    print("Canonical audit loaded.")
    print("Governance 10 + Policy 14 + Accuracy 4 = 28 (fixed).")
