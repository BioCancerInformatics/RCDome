# RCDome — build the distribution ZIP ONLY if the pre-flight validation passes.
# Proactive packaging: a broken asset is caught here, before the ZIP ships.
import subprocess, os, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # RCDome_manuscript
APP = os.path.join(BASE, 'RCDome_distribution')
RSCRIPT = 'C:/Program Files/R/R-4.2.3/bin/Rscript.exe'

# 1. pre-flight validation (same function the app runs at startup)
r_code = ('source("R/validate_data_files.R"); '
          'v <- validate_data_files(); '
          'cat("ok:", v$ok, "\\n"); '
          'if (!v$ok) cat(paste(v$issues, collapse = "\\n"))')
r = subprocess.run([RSCRIPT, '-e', r_code], cwd=APP, capture_output=True, text=True)
print(r.stdout.strip())
if 'ok: TRUE' not in r.stdout:
    print('\nVALIDATION FAILED — ZIP not built. Fix the issues above, then re-run.')
    sys.exit(1)

# 2. build the ZIP (exclude _archive provenance backups — they contain stale
#    placeholder checks and duplicate secret backups; not needed to run the app)
out = os.path.join(BASE, 'RCDome_V027_distribution.zip')
if os.path.exists(out):
    os.remove(out)
import zipfile
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(APP):
        # exclude ALL archive/backup folders (any name starting with _archive),
        # not just the exact '_archive' — so stale V026 copies, _archive_backups,
        # and _archive_V027_partial provenance backups never ship in the ZIP.
        dirs[:] = [d for d in dirs if not d.startswith('_archive')]
        for f in files:
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, APP)
            parts = rel.split(os.sep)
            if any(p.startswith('_archive') for p in parts[:-1]):
                continue
            # Ship the REAL secret files (.Renviron API key + email creds) so the
            # coauthor distribution is fully functional; never ship the .example placeholders.
            if f in ('.Renviron.example', 'email_creds.txt.example'):
                continue
            z.write(fp, rel)
print(f'\nZIP built: {os.path.getsize(out) / 1048576:.1f} MB')
