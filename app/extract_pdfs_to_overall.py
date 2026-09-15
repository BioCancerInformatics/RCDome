"""
extract_pdfs_to_overall.py
===========================
Extracts text from PDFs in RUN/PAPERS/PDFs/ and writes .txt files to
data/papers/overall/ so RCDchat can read them alongside R-generated papers.

Usage:
    python extract_pdfs_to_overall.py
    python extract_pdfs_to_overall.py --pdf-dir E:/RCDome_Atlas/RUN/PAPERS/PDFs

Never re-processes PDFs that already have a .txt counterpart.
"""

import os, sys, re, argparse, subprocess, glob
from pathlib import Path

SCRIPT_DIR  = Path(__file__).resolve().parent
OVERALL_DIR = SCRIPT_DIR / "data" / "papers" / "Overall"
DEFAULT_PDF_DIR = SCRIPT_DIR.parent / "RUN" / "PAPERS" / "PDFs"


def log(msg):
    print(f"[extract] {msg}")


def pdf_to_text(pdf_path):
    """Extract text from PDF using pdftotext (poppler) or pdftools (R fallback)."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0 and len(result.stdout.strip()) > 200:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    except Exception as e:
        log(f"  pdftotext error: {e}")

    # Fallback: PyPDF2 (pure Python, no external deps)
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if len(text.strip()) > 200:
            return text.strip()
    except ImportError:
        pass
    except Exception as e:
        log(f"  PyPDF2 error: {e}")

    return None


def is_pdf(path):
    """Check magic bytes."""
    try:
        with open(path, "rb") as f:
            return f.read(4) == b"%PDF"
    except Exception:
        return False


def extract_all(pdf_dir, overall_dir, force=False):
    pdf_dir = Path(pdf_dir)
    overall_dir = Path(overall_dir)
    overall_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = list(pdf_dir.glob("*.pdf"))
    log(f"Found {len(pdf_files)} PDFs in {pdf_dir}")

    done = 0
    skipped = 0
    failed = 0

    for pdf_path in sorted(pdf_files):
        # Extract PMID from filename: PMC12345.pdf or PMID12345.pdf → PMID_12345.txt
        name = pdf_path.stem
        if name.upper().startswith("PMC"):
            pmid = name[3:]  # Strip PMC prefix, keep just the number
        elif name.upper().startswith("PMID"):
            pmid = name[4:]
        else:
            pmid = name
        txt_path = overall_dir / f"PMID_{pmid}.txt"

        if txt_path.exists() and not force:
            sz = txt_path.stat().st_size
            if sz > 200:
                skipped += 1
                continue

        if not is_pdf(pdf_path):
            log(f"  SKIP {name}: not a valid PDF")
            failed += 1
            continue

        log(f"  Processing {name}...")
        text = pdf_to_text(pdf_path)

        if text and len(text) > 200:
            # Clean: normalize whitespace
            text = re.sub(r"\s+", " ", text)
            text = f"TITLE: (from PDF)\n\n[FULL TEXT - Open Access]\n{text}"
            txt_path.write_text(text, encoding="utf-8")
            done += 1
            log(f"    → {txt_path.name} ({len(text):,} chars)")
        else:
            log(f"    ✗ Could not extract text")
            failed += 1

    log(f"\nDone. Extracted: {done} | Skipped: {skipped} | Failed: {failed}")


def main():
    parser = argparse.ArgumentParser(description="Extract PDFs to overall/ for RCDchat")
    parser.add_argument("--pdf-dir", default=str(DEFAULT_PDF_DIR),
                       help="Directory with PDF files")
    parser.add_argument("--out-dir", default=str(OVERALL_DIR),
                       help="Output directory for .txt files")
    parser.add_argument("--force", action="store_true",
                       help="Re-extract even if .txt exists")
    args = parser.parse_args()

    extract_all(args.pdf_dir, args.out_dir, args.force)


if __name__ == "__main__":
    main()
