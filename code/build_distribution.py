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

# 2. build the ZIP
out = os.path.join(BASE, 'RCDome_V026_distribution.zip')
if os.path.exists(out):
    os.remove(out)
shutil.make_archive(os.path.join(BASE, 'RCDome_V026_distribution'), 'zip', APP)
print(f'\nZIP built: {os.path.getsize(out) / 1048576:.1f} MB')
