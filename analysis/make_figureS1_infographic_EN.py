# -*- coding: utf-8 -*-
"""English infographic from Nomeclatura_4K.png — excluding internal title/subtitle + harmonization section.
MATHEMATICAL size hierarchy + card-width fitting (systematic, proportional)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from rapidocr_onnxruntime import RapidOCR
from PIL import Image, ImageDraw, ImageFont
from statistics import median

BASE = r'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/analysis/Victor_analysis/Auditoria_V26-20260912T123815Z-1-001/Auditoria_V26/Versões do infográfico nomeclatura/Nomeclatura_4K_PT_source.png'
OUT_PNG = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Submission FAI/Figures_A4/Figure_2_evaluation_architecture_A4.png"
OUT_PDF = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Submission FAI/Figures_A4/Figure_2_evaluation_architecture_A4.pdf"
OUT_TIFF = r"D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Submission FAI/Figures_A4/Figure_2_evaluation_architecture_A4.tiff"
CROP_TOP = 340
CROP_Y = 3980

# Portuguese -> (English, category)
T = {
 "Entidade RCD": ("RCD entity", "COL"),
 "Associacao gene-RCD": ("Gene\u2013RCD association", "COL"),
 "Qualidade do pipeline": ("Pipeline quality", "COL"),
 "(classificacao biologica/ontologica)": ("(biological / ontological classification)", "PAREN"),
 "Fontes e validacao": ("Sources & validation", "CARD"),
 "Crit\u00e9rios de modalidade": ("Modality criteria", "CARD"),
 "(maquinaria, trigger, morfologia,": ("(machinery, trigger, morphology,", "PAREN"),
 "(curadoria, literatura, bases de dados)": ("(curation, literature, databases)", "PAREN"),
 "Elicit Governance Gates": ("Elicit Governance Gates", "CARD"),
 "nomenclatura, distinguibilidade)": ("nomenclature, distinguishability)", "PAREN"),
 "Checklist de evid\u00e9ncia": ("Evidence checklist", "CARD"),
 "Evidence Tier": ("Evidence Tier", "CARD"),
 "validacao da entrada": ("Input validation", "CARD"),
 "allow-list compliance": ("Allow-list compliance", "FIELD"),
 "vocabulary compliance": ("Vocabulary compliance", "FIELD"),
 "Biological Gates": ("Biological Gates", "CARD"),
 "confidence_score": ("CT1\u2013CT4", "GATE"),
 "precisao de EXECUTOR": ("Unsupported EXECUTOR rate", "FIELD"),
 "ou CT1-CT4": ("or confidence_score", "FIELD"),
 "rastreabilidade": ("Traceability", "FIELD"),
 "Nivel ontologico final": ("Final ontological level", "CARD"),
 "Papel mecanistico e direcao": ("Mechanistic role & direction", "CARD"),
 "Descritores complementares:": ("Complementary descriptors:", "FIELDB"),
 "(EXECUTOR, REGULATOR, MARKER;": ("(EXECUTOR, REGULATOR, MARKER;", "PAREN"),
 "evidence_maturity": ("evidence_maturity", "FIELD"),
 "positive/negative/mixed)": ("PROMOTES / PROTECTS / UNCLEAR)", "PAREN"),
 "species_scope": ("species_scope", "FIELD"),
 "relationship_type": ("relationship_type", "FIELD"),
 "parent_entity": ("parent_entity", "FIELD"),
 "Objetivo:": ("Goal:", "GOAL"),
 "decidir o que a entidade \u00e9": ("Determine what the entity is", "GOALTXT"),
 "qualificar a forca e o tipo da": ("Rate strength and type of", "GOALTXT"),
 "avaliar a confiabilidade da": ("Assess the reliability of", "GOALTXT"),
 "biologicamente.": ("biologically.", "GOALTXT"),
 "associacao gene-RCD.": ("gene\u2013RCD association.", "GOALTXT"),
 "extracao automatizada.": ("automated extraction.", "GOALTXT"),
 "Mensagem central": ("Key message", "KEY"),
 "Tr\u00e9s objetos diferentes estao sendo avaliados:": ("Three distinct objects are being evaluated:", "KEYTXT"),
 "1) a entidade RCD; 2) a associacao gene-RCD; 3) a qualidade do pipeline.": ("(1) the RCD entity; (2) the gene\u2013RCD association; (3) pipeline quality.", "KEYTXT"),
}

# MATHEMATICAL size hierarchy (px). Multipliers are fixed ratios off the base 70.
BASE_SIZE = 70
CAT = {
 "COL":    dict(size=84,  bold=True),   # column headers
 "GATE":   dict(size=96,  bold=True),   # gate labels
 "CARD":   dict(size=80,  bold=True),   # card titles (bigger than FIELD)
 "FIELD":  dict(size=70,  bold=False),  # body / field names
 "FIELDB": dict(size=70,  bold=True),   # bold field labels (Complementary descriptors:)
 "PAREN":  dict(size=60,  bold=False),  # long parentheticals
 "GOAL":   dict(size=128, bold=True),   # Goal: headers
 "GOALTXT":dict(size=70,  bold=False),  # goal text (same as FIELD)
 "KEY":    dict(size=152, bold=True),   # Key message header
 "KEYTXT": dict(size=70,  bold=False),  # key message text (same as FIELD)
}

# column card boundaries (x) for card-width fitting
COLUMNS = [(250, 1350), (1350, 2650), (2650, 3950)]

im = Image.open(BASE).convert("RGB")
im = im.crop((0, CROP_TOP, im.width, min(CROP_Y, im.height)))
draw = ImageDraw.Draw(im)
ocr = RapidOCR()
result, _ = ocr(BASE)

try:
    F_BOLD = "C:/Windows/Fonts/arialbd.ttf"; F_REG = "C:/Windows/Fonts/arial.ttf"
except Exception:
    F_BOLD = F_REG = "arial.ttf"

def card_width(x0):
    for l, r in COLUMNS:
        if l <= x0 < r:
            return (r - l) - 60
    return 900

def card_center(x0):
    for l, r in COLUMNS:
        if l <= x0 < r:
            return (l + r) / 2
    return x0

blocks = []
for box, text, conf in result:
    if text not in T: continue
    y0 = int(min(p[1] for p in box))
    if y0 >= CROP_Y or y0 < CROP_TOP: continue
    box = [[p[0], p[1]-CROP_TOP] for p in box]
    x0 = int(min(p[0] for p in box)); y0 = int(min(p[1] for p in box))
    x1 = int(max(p[0] for p in box)); y1 = int(max(p[1] for p in box))
    blocks.append(dict(text=text, en=T[text][0], cat=T[text][1],
                       x0=x0, y0=y0, x1=x1, y1=y1, h=y1-y0, w=x1-x0))

def bg_color(bx):
    x0=max(0,bx['x0']); y0=max(0,bx['y0']); x1=min(im.width-1,bx['x1']); y1=min(im.height-1,bx['y1'])
    pts=[]
    for x in range(max(0,x0-8), min(im.width,x1+8), max(1,(x1-x0+16)//10)):
        pts += [(x,max(0,y0-8)),(x,min(im.height-1,y1+8))]
    for y in range(max(0,y0-8), min(im.height,y1+8), max(1,(y1-y0+16)//10)):
        pts += [(max(0,x0-8),y),(min(im.width-1,x1+8),y)]
    if not pts: return (255,255,255)
    return (int(median(im.getpixel(p)[0] for p in pts)),
            int(median(im.getpixel(p)[1] for p in pts)),
            int(median(im.getpixel(p)[2] for p in pts)))

def text_color(bx):
    x0=max(0,bx['x0']); y0=max(0,bx['y0']); x1=min(im.width-1,bx['x1']); y1=min(im.height-1,bx['y1'])
    best=None; best_lum=999
    for x in range(x0, min(im.width,x1), max(1,(x1-x0)//40)):
        for y in range(y0, min(im.height,y1), max(1,(y1-y0)//4)):
            r,g,b = im.getpixel((x,y)); lum = 0.299*r+0.587*g+0.114*b
            if lum < best_lum: best_lum=lum; best=(r,g,b)
    return best if best else (11,16,32)

# per-category fit using the CARD width (systematic, not the tight OCR box)
sizes = {c: s['size'] for c, s in CAT.items()}
for c in CAT:
    bs = [b for b in blocks if b['cat'] == c]
    if not bs: continue
    size = sizes[c]
    while size > 12:
        ok = True
        f = ImageFont.truetype(F_BOLD if CAT[c]['bold'] else F_REG, size)
        for b in bs:
            allowed = card_width(b['x0']) if c == 'COL' else b['w'] + 8
            if draw.textlength(b['en'], font=f) > allowed:
                ok = False; break
        if ok: break
        size -= 2
    sizes[c] = size

LEFT_TXT = {"Allow-list compliance", "Vocabulary compliance", "Unsupported EXECUTOR rate", "Traceability", "evidence_maturity", "species_scope", "relationship_type", "parent_entity"}
# horizontal alignment: column headers share one TOP line (glyph tops ~450 in the original)
COL_TOP = 110
for b in blocks:
    bg = bg_color(b); fg = text_color(b)
    pad = 4
    draw.rectangle([b['x0']-pad, b['y0']-pad, b['x1']+pad, b['y1']+pad], fill=bg)
    c = b['cat']; size = sizes[c]
    font = ImageFont.truetype(F_BOLD if CAT[c]['bold'] else F_REG, size)
    if c == 'COL':
        anchor = 'mt'
        tx = (b['x0']+b['x1'])/2
        ty = COL_TOP
    else:
        if c in ("GOAL", "GOALTXT", "KEYTXT") or b['en'] in LEFT_TXT:
            anchor = "lm"; tx = b['x0']
        else:
            anchor = "mm"; tx = (b['x0']+b['x1'])/2
        ty = (b['y0']+b['y1'])/2
    draw.text((tx, ty), b['en'], font=font, fill=fg, anchor=anchor)

# remove the gold bullet/icon before the "Input validation" header (items keep their bullets)
draw.rectangle([2625, 1110, 2830, 1210], fill=(254, 241, 229))

# --- V027 parallel-arrow fix: replace the sequential Sources->ET->CT->Role cascade ---
# ET (evidence tier) and CT (confidence tier) are distinct, parallel metrics (Methods);
# so three arrows emerge from the Sources card bottom line: solid center -> ET,
# dashed left -> CT, dashed right -> Mechanistic role (crossing the intermediate boxes).
ARROW_RGB = (0, 90, 225); PAGE = (237, 248, 254)
# erase ALL THREE original sequential arrows (shaft + arrowhead only, NOT the card borders)
# shaft 13px (x 1978-1990); arrowhead 52px (x 1958-2010); erase x 1955-2015, y below each card border
draw.rectangle([1955, 782, 2015, 925],  fill=PAGE)   # Sources -> ET (redrawn from y=778)
draw.rectangle([1955, 1274, 2015, 1415], fill=PAGE)  # ET -> CT
draw.rectangle([1955, 1752, 2015, 1895], fill=PAGE)  # CT -> Role
# draw three parallel arrows from the Sources card bottom line (y=778)
_SHAFT, _HEAD_W, _HEAD_H, _Y0 = 13, 52, 60, 778
def _arrow(x, y_end, dashed=False):
    if dashed:
        y = _Y0
        while y < y_end - _HEAD_H:
            draw.line([x, y, x, min(y + 24, y_end - _HEAD_H)], fill=ARROW_RGB, width=_SHAFT)
            y += 24 + 16
    else:
        draw.line([x, _Y0, x, y_end - _HEAD_H], fill=ARROW_RGB, width=_SHAFT)
    draw.polygon([(x - _HEAD_W // 2, y_end - _HEAD_H), (x + _HEAD_W // 2, y_end - _HEAD_H), (x, y_end)], fill=ARROW_RGB)
_arrow(1650, 1420, dashed=True)   # left  -> CT
_arrow(1984, 932,  dashed=False)  # center-> ET
_arrow(2320, 1900, dashed=True)   # right -> Role

# --- A4 adaptation: fit + center on A4 landscape canvas @ 600 DPI ---
A4_W, A4_H = 7016, 4962
_canvas = Image.new("RGB", (A4_W, A4_H), (255, 255, 255))
_scale = min(A4_W / im.width, A4_H / im.height)
_im2 = im.resize((int(im.width * _scale), int(im.height * _scale)), Image.LANCZOS)
_canvas.paste(_im2, ((A4_W - _im2.width) // 2, (A4_H - _im2.height) // 2))
im = _canvas

im.save(OUT_PNG, "PNG", dpi=(600, 600))
im.save(OUT_PDF, "PDF", resolution=600.0)
im.save(OUT_TIFF, "TIFF", dpi=(600, 600), compression="tiff_lzw")
print("saved:", OUT_PNG, OUT_PDF, OUT_TIFF)
print("image:", im.size, "| blocks:", len(blocks))
print("category sizes:", sizes)
