"""
Sync the RCDome Decoder + amended manuscript into the GitHub mirror, update the
sha256 manifest, and commit. (No secrets, no intermediates — truth snapshot only.)
"""
import os, shutil, hashlib, subprocess, sys

DEC = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome Decoder"
MAN = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_manuscript_governance.docx"
MIR = r"D:/RCDome_github"

# --- mapping: source file -> mirror relative path ---
DATA = [
    "RCDome_Decoder_53.csv", "RCDome_Decoder_53.csv",
    "RCDome_Decoder_53.xlsx", "RCDome_Decoder_53.xlsx",
    "definition_review_worksheet.csv", "definition_review_worksheet.xlsx",
    "merge_log.csv", "galluzzi2018_nccd_definitions.json",
    "entity_evidence_V026.csv", "founding_pmids_pending_FINAL.csv",
    "gap_inventory_V026.csv", "definitions_SOLID_draft.csv", "definitions_CANDIDATE_draft.csv",
    "od_validation_deepseek_fulltext.csv", "od_crossref_consensus.csv",
    "consensus_crossvalidation_report.csv", "consensus_deep_search_report.csv",
    "governance_audit_report.json", "recovered_fulltexts.json",
    "Rodrigues 2025_Dataset S1.xlsx",
]
DOCS = [
    ("RCDome_Definition_Governance.md", "docs/governance/RCDome_Definition_Governance.md"),
    ("MandM_operational_definitions.md", "docs/manuscript/MandM_operational_definitions.md"),
    ("Results_OD_census.md", "docs/manuscript/Results_OD_census.md"),
    ("gap_inventory_V026.md", "docs/decoder/gap_inventory_V026.md"),
    ("definitions_SOLID_draft.md", "docs/decoder/definitions_SOLID_draft.md"),
    ("definitions_CANDIDATE_draft.md", "docs/decoder/definitions_CANDIDATE_draft.md"),
    ("review_guide.md", "docs/decoder/review_guide.md"),
    ("github_sync_tracking.md", "docs/decoder/github_sync_tracking.md"),
]
SCRIPTS = [
    "build_decoder_53.py", "scoring_formulas.py", "governance_checker.py",
    "final_readiness_audit.py", "deep_audit.py", "verbatim_audit.py", "pmid_topic_audit.py",
    "consensus_crossvalidate.py", "consensus_deep_search.py",
    "validate_od_deepseek.py", "validate_od_fulltext.py", "validate_od_consensus.py",
    "merge_approved.py", "make_review_worksheet.py", "founding_pmid_lookup.py",
    "recover_fulltexts.py", "add_provenance.py", "apply_galluzzi_format.py",
    "add_rodrigues_complement.py", "standardize_citations.py", "fix_nccd_complements.py",
    "inject_od_subsections.py",
]

copied = []
for f in DATA:
    src, dst = os.path.join(DEC, f), os.path.join(MIR, "data", f)
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst); copied.append(dst)
for f, rel in DOCS:
    src, dst = os.path.join(DEC, f), os.path.join(MIR, rel)
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst); copied.append(dst)
for f in SCRIPTS:
    src, dst = os.path.join(DEC, f), os.path.join(MIR, "code", "decoder", f)
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst); copied.append(dst)
# amended manuscript -> docs/manuscript/
if os.path.exists(MAN):
    dst = os.path.join(MIR, "docs", "manuscript", "RCDome_manuscript_governance.docx")
    shutil.copy2(MAN, dst); copied.append(dst)

# update manifest (sha256)
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(65536), b""):
            h.update(c)
    return h.hexdigest()
lines = []
for p in copied:
    rel = os.path.relpath(p, MIR).replace("\\", "/")
    lines.append(f"{sha256(p)}  {rel}")
with open(os.path.join(MIR, "mirror_manifest.txt"), "a", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"copied {len(copied)} files; manifest updated")
