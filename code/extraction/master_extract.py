"""
RCDome Gene Extraction Pipeline — Master Orchestrator
=======================================================
Executes all 16 extraction scripts in sequence, producing
traceability-compliant CSV outputs for every database.

Usage: python master_extract.py [--channel A|B|C|D|all]

Repository: RCDome/extraction/
"""

import os, sys, subprocess, time
from datetime import datetime

EXTRACTION_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(os.path.dirname(EXTRACTION_DIR), "output databases")
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOG = []

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    LOG.append(line)

def run_script(name, description=""):
    """Run an extraction script and log results."""
    log(f"\n{'='*50}")
    log(f"EXTRACTING: {description or name}")
    log(f"{'='*50}")
    script = os.path.join(EXTRACTION_DIR, name)
    if not os.path.exists(script):
        log(f"  SKIP: {script} not found")
        return
    start = time.time()
    result = subprocess.run([sys.executable, script], capture_output=True, text=True, cwd=EXTRACTION_DIR)
    elapsed = time.time() - start
    log(result.stdout)
    if result.stderr:
        log(f"  STDERR: {result.stderr[:500]}")
    log(f"  Completed in {elapsed:.1f}s (exit code {result.returncode})")

# ================================================================
# EXTRACTION SEQUENCE
# ================================================================

def extract_all():
    log("=" * 60)
    log("RCDome GENE EXTRACTION PIPELINE — MASTER ORCHESTRATOR")
    log(f"Started: {datetime.now().isoformat()}")
    log("=" * 60)

    # Channel A: PubMed Boolean
    run_script("channel_a_rodrigues2025.py", "Rodrigues et al. 2025 (PubMed Boolean + FerrDB/RCDdb)")

    # Channel B: Tier 1 — RCD-Specific Databases
    run_script("channel_b_ferrdb_v3.py", "FerrDB v3 (22 modalities, 5,299 rows)")
    run_script("channel_b_lncrcd.py", "LncRCD (12 RCD forms, 1,951 rows)")
    run_script("channel_b_rcddb.py", "RCDdb (15 RCD forms, 3,085 rows)")
    run_script("channel_b_ipcd.py", "iPCD (15 RCD forms, filtered Homo sapiens)")
    run_script("channel_b_ilir.py", "iLIR (LC3-interacting proteins, 6,087 entries)")
    run_script("channel_b_amtdb.py", "AMT-DB (autophagy modulators, 860 genes)")
    run_script("channel_b_atd.py", "ATD (autophagy-disease, 87 genes)")
    run_script("channel_b_hadb.py", "HADb (Human Autophagy DB, 371 genes)")
    run_script("channel_b_hamdb.py", "HAMdb (Human Autophagy Modulators, 551 genes)")

    # Channel B: Tier 2 — Pathway/Molecular
    run_script("channel_b_kegg.py", "KEGG (5 pathways via KGML)")
    run_script("channel_b_reactome.py", "Reactome (Programmed Cell Death hierarchy)")
    run_script("channel_b_go.py", "GO (QuickGO, RCD-specific terms)")
    run_script("channel_b_msigdb.py", "MSigDB/GSEA (RCD gene sets)")

    # Channel B: Tier 3 — Gene-Centric
    run_script("channel_b_ncbi_gene.py", "NCBI Gene (E-utilities, 32 RCD form queries)")

    # Final report
    log("\n" + "=" * 60)
    log("EXTRACTION COMPLETE")
    log("=" * 60)

    # Count outputs
    for fname in sorted(os.listdir(OUTPUT_DIR)):
        if fname.endswith('.csv'):
            path = os.path.join(OUTPUT_DIR, fname)
            with open(path) as f:
                lines = sum(1 for _ in f)
            log(f"  {fname}: {lines-1} entries")

    # Save log
    logpath = os.path.join(OUTPUT_DIR, f"master_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    with open(logpath, 'w') as f:
        f.write('\n'.join(LOG))
    log(f"\nLog saved to {logpath}")


if __name__ == '__main__':
    extract_all()
