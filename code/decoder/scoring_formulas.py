"""
RCDome Definition Governance — deterministic scoring reference (V026).

Objective inputs are pure functions of the V026 matrix.
Overall Score S is the reverse-engineered Rodrigues weighted formula,
verified 25/25 exact against Dataset S1A anchors.

C1-C6 are EXPERT JUDGMENTS (two-call). This module provides:
  1. objective_inputs(entity_evidence)  -> deterministic
  2. overall_score_s(c1..c6)            -> deterministic, verified
  3. verify_s_formula()                 -> re-checks 25/25 against Dataset S1A
"""

WEIGHTS = {"C1": 0.25, "C2": 0.25, "C3": 0.20, "C4": 0.15, "C5": 0.10, "C6": 0.05}
W_ORDER = ["C1", "C2", "C3", "C4", "C5", "C6"]


def objective_inputs(row: dict) -> dict:
    """Deterministic inputs computed from one entity's V026 aggregates."""
    n_m = row["n_mechanistic"]
    n_c = row["n_context_gap"]
    denom = n_m + n_c
    return {
        "n_pairs": row["n_pairs"],
        "n_genes": row["n_genes"],
        "n_sources_sum": row["n_sources_sum"],
        "n_mechanistic": n_m,
        "n_context_gap": n_c,
        "mechanistic_ratio": (n_m / denom) if denom else None,
        "n_unique_pmids": row["n_unique_pmids"],
        "min_year": row["min_year"],
        "tier_T1": row["tier_T1"],
        "tier_T2": row["tier_T2"],
        "tier_T3": row["tier_T3"],
        "tier_T4": row["tier_T4"],
    }


def overall_score_s(c1: float, c2: float, c3: float, c4: float, c5: float, c6: float) -> float:
    """S = 0.25*C1 + 0.25*C2 + 0.20*C3 + 0.15*C4 + 0.10*C5 + 0.05*C6 (verified)."""
    vals = [c1, c2, c3, c4, c5, c6]
    return round(sum(w * v for w, v in zip(WEIGHTS.values(), vals)), 2)


def verify_s_formula(path: str = None) -> bool:
    """Re-check S against all 25 Rodrigues Dataset S1A anchors. Returns True if 25/25."""
    import openpyxl
    if path is None:
        path = (r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/"
                r"RCDome_manuscript/output databases/Dataset S1_Rodrigues et al 2025.xlsx")
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb["Dataset S1A"]
    ok = 0
    total = 0
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[1] is None:
            continue
        c = list(r[4:10])
        given = r[10]
        calc = overall_score_s(*c)
        total += 1
        ok += abs(calc - given) < 0.005
    print(f"S formula verification: {ok}/{total} exact match")
    return ok == total == 25


if __name__ == "__main__":
    verify_s_formula()
