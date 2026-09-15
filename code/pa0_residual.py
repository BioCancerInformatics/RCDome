# -*- coding: utf-8 -*-
import os, re, sys, io
sys.stdout.reconfigure(encoding='utf-8')

BASE = "D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
os.chdir(BASE)

KEY = [
    "Shiny app/RCDome_Atlas/APP/modules/",
    "Shiny app/RCDome_Atlas/APP/R/",
    "Shiny app/RCDome_Atlas/APP/global.R",
    "Shiny app/RCDome_Atlas/APP/server.R",
    "Shiny app/RCDome_Atlas/APP/ui.R",
    "Shiny app/RCDome_Atlas/APP/www/landing_page.html",
    "Shiny app/RCDome_Atlas/APP/www/dome_prototype.html",
    "Shiny app/RCDome_Atlas/APP/www/detail_page_wireframe.html",
    "Shiny app/RCDome_Atlas/APP/board/",
    "RCDome Decoder/",
    "docs/",
]
files = []
for root, dirs, fs in os.walk("."):
    dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "_archive")]
    for f in fs:
        if not f.endswith((".md", ".R", ".html", ".txt", ".py")):
            continue
        p = os.path.join(root, f).replace("\\", "/").lstrip("./")
        if any(p == k.rstrip("/") or p.startswith(k) for k in KEY):
            files.append(p)
files = sorted(set(files))

ACC = ["canonicalized", "rcd_form_canonical", "canonical_pathways", "canonical_set",
       "is_canonical", "canonical_symbol", "canonical_transcript", "canonical executor",
       "canonical gene set", "canonical apoptosis", "canonical autophagy",
       "canonical inflammasome", "canonical ferroptosis", "canonical notch", "canonical bmp",
       "canonical nlrp", "canonical signaling", "canonical mechanism", "canonical concept name",
       "canonical label", "canonicaltile", "canonicalize", "canonical audit", "audit_canonical",
       "canonical count", "non-canonical", "noncanonical", "canonical wnt",
       "canonical mitochondrial", "canonical mapk", "canonical pathway", "group g",
       "canonical name accuracy", "canonical values", "canonical forms are listed"]

pat = re.compile(r"[^\n]{0,70}canonical[^\n]{0,70}", re.IGNORECASE)
out = []
for p in files:
    try:
        txt = io.open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    for m in pat.finditer(txt):
        frag = " ".join(m.group(0).split())
        f = frag.lower()
        if not any(a in f for a in ACC):
            out.append((p, frag))

seen = set(); uniq = []
for p, frag in out:
    k = (p, frag.lower())
    if k not in seen:
        seen.add(k); uniq.append((p, frag))

print("RESIDUAL ambiguous 'canonical' in CURRENT user-facing artifacts:", len(uniq))
print("=" * 70)
for p, frag in uniq:
    print("### " + p)
    print("    …" + frag + "…")
