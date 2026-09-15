# -*- coding: utf-8 -*-
import os, re, sys, io

BASE = "D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript"
os.chdir(BASE)

out = io.StringIO()
def log(*a): print(*a, file=out)

# acceptable (keep) substrings — biological/schema/third-party/deferred
ACCEPT = [
    "canonicalized", "rcd_form_canonical", "canonical_pathways", "canonical_set",
    "is_canonical", "canonical_symbol", "canonical_transcript",
    "canonical executor", "canonical gene set", "canonical gene sets",
    "canonical apoptosis", "canonical autophagy", "canonical inflammasome",
    "canonical ferroptosis", "canonical notch", "canonical bmp", "canonical nlrp",
    "canonical signaling", "canonical pathway diagram", "canonical mechanism",
    "canonical concept name", "canonical label", "canonicaltile", "canonicalize",
    "canonical audit", "audit_canonical", "canonical count", "canonical name accuracy",
    "non-canonical", "noncanonical",
]

def is_acc(frag):
    f = frag.lower()
    return any(a in f for a in ACCEPT)

files = []
for root, dirs, fs in os.walk("."):
    dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "_archive", "papers")]
    for f in fs:
        p = os.path.join(root, f).replace("\\", "/").lstrip("./")
        if f.endswith((".md", ".R", ".html", ".txt", ".py", ".json", ".csv")):
            files.append(p)

pat = re.compile(r"[^\n]{0,90}canonical[^\n]{0,90}", re.IGNORECASE)
uniq = {}
for p in files:
    try:
        txt = io.open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    for m in pat.finditer(txt):
        frag = " ".join(m.group(0).split())
        if not is_acc(frag):
            uniq.setdefault(p, []).append(frag)

total = 0
for p in uniq:
    uniq[p] = list(dict.fromkeys(uniq[p]))
    total += len(uniq[p])

log("REMAINING ambiguous 'canonical' (text artifacts)")
log("files:", len(uniq), "| occurrences:", total)
log("=" * 70)
for p in sorted(uniq):
    log("### " + p)
    for f in uniq[p]:
        log("    …" + f + "…")
    log("")

io.open("D:/pa0_rescan.txt", "w", encoding="utf-8").write(out.getvalue())
print("WROTE D:/pa0_rescan.txt | files:", len(uniq), "| occurrences:", total)
