# -*- coding: utf-8 -*-
"""Universal renumbering of supplementary figures (infographic->S1, database S1->S2, source S2->S3)
across code, docs, and the GitHub mirror. Specific strings only (no blanket S1/S2 replacement)."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

MAIN = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
GH   = r"D:/RCDome_github"

# (relative path, [(old, new), ...])
EDITS = {
 "code/add_supplementary_legends.py": [
   ("Supplementary Figure S1. Database contribution", "Supplementary Figure S2. Database contribution"),
   ("Supplementary Figure S2. Fraction of associations", "Supplementary Figure S3. Fraction of associations"),
   ("(Supplementary Figure S1)", "(Supplementary Figure S2)"),
   ("(Supplementary Figure S2)", "(Supplementary Figure S3)"),
 ],
 "code/merge_supplementary_notes.py": [
   ("Supplementary Figure S1. Database contribution", "Supplementary Figure S2. Database contribution"),
   ("Supplementary Figure S2. Fraction of associations", "Supplementary Figure S3. Fraction of associations"),
 ],
 "code/make_figure_db_contribution.R": [
   ("RCDome Supplementary Figure S1: database contribution", "RCDome Supplementary Figure S2: database contribution"),
   ("Figure_S1_database_contribution", "Figure_S2_database_contribution"),
 ],
 "code/make_figure_s2_stacked_by_level.py": [
   ("Figure S2 (improved)", "Figure S3 (improved)"),
   ("Figure_S2_source_classification", "Figure_S3_source_classification"),
 ],
 "code/make_figure_source_classification.R": [
   ("RCDome Supplementary Figure S2 (V026)", "RCDome Supplementary Figure S3 (V026)"),
   ("Figure_S2_source_classification", "Figure_S3_source_classification"),
 ],
 "code/final_review_77.py": [
   ("Figure S1/S2 present", "Figure S2/S3 present"),
   ("Figure_S1_database_contribution", "Figure_S2_database_contribution"),
   ("Figure_S2_source_classification", "Figure_S3_source_classification"),
 ],
 "code/manuscript_v026_deep_audit.py": [
   ("Supplementary Fig S1 vs matrix", "Supplementary Fig S2 vs matrix"),
   ("Supplementary Figure S1", "Supplementary Figure S2"),
 ],
 "code/build_github_mirror.py": [
   ("Figure_S1_database_contribution.tiff", "Figure_S2_database_contribution.tiff"),
   ("Figure_S1_database_contribution.png", "Figure_S2_database_contribution.png"),
   ("Figure_S2_source_classification.tiff", "Figure_S3_source_classification.tiff"),
   ("Figure_S2_source_classification.png", "Figure_S3_source_classification.png"),
 ],
 "code/full_manuscript_conformity_audit.py": [
   ("Figure_S1_database_contribution", "Figure_S2_database_contribution"),
   ("Figure_S2_source_classification", "Figure_S3_source_classification"),
 ],
 "RCDome_distribution/CHANGELOG_V026_6.md": [
   ("Figure S2 (level counts)", "Figure S3 (level counts)"),
 ],
 "docs/TRACEABILITY_V026_auditoria_2026-09-19.md": [
   ("Figure S2 (stacked by level)", "Figure S3 (stacked by level)"),
 ],
 "Expert Nomenclature and Ontological Adjudication Audit/HIGOR_CORRECTIONS_APPLIED.md": [
   ("Figure S2 (legend entity counts 12->11, 18->19)", "Figure S3 (legend entity counts 12->11, 18->19)"),
   ("supplementary Figure S2 legend", "supplementary Figure S3 legend"),
 ],
 "comms/emails_coautores/HACN_validation_package/HACN_validation_package/audit/HIGOR_CORRECTIONS_APPLIED.md": [
   ("Figure S2 (legend entity counts 12->11, 18->19)", "Figure S3 (legend entity counts 12->11, 18->19)"),
   ("supplementary Figure S2 legend", "supplementary Figure S3 legend"),
 ],
}

# GitHub path mapping: code/* -> code/*; RCDome_distribution/CHANGELOG -> app/CHANGELOG
GH_MAP = {
 "RCDome_distribution/CHANGELOG_V026_6.md": "app/CHANGELOG_V026_6.md",
}

def apply(root, rel, pairs):
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        print("  MISSING:", p); return 0
    s = open(p, encoding='utf-8').read()
    n = 0
    for old, new in pairs:
        if old in s:
            s = s.replace(old, new); n += 1
    open(p, 'w', encoding='utf-8').write(s)
    print(f"  {p}: {n} edits")
    return n

total = 0
print("=== MAIN ===")
for rel, pairs in EDITS.items():
    total += apply(MAIN, rel, pairs)
print("=== GITHUB MIRROR ===")
for rel, pairs in EDITS.items():
    ghp = GH_MAP.get(rel, rel)
    total += apply(GH, ghp, pairs)

# rename make_figure_s2_stacked_by_level.py -> make_figure_s3_stacked_by_level.py
for root in (MAIN, GH):
    src = os.path.join(root, 'code', 'make_figure_s2_stacked_by_level.py')
    dst = os.path.join(root, 'code', 'make_figure_s3_stacked_by_level.py')
    if os.path.exists(src):
        os.rename(src, dst)
        print("  renamed:", dst)
print("TOTAL edits:", total)
