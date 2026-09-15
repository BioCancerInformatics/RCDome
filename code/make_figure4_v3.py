# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont

ASSETS = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures/Figure4_assets'
OUT = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures/Figure_4_app'

W, H = 7014, 4962
MX, GAP, TOP = 147, 60, 110
PW, PH = 3347, 2230
CAP_H = 120
ROW_GAP = 60

captions = {
    'A': 'Home dome — 53 entities, 9,265 genes, 21,569 associations',
    'B': 'Explore RCDome — modules, benchmarks and governance',
    'C': 'Gene Catalog — DeepSeek/Elicit source selector and Death-core filter (469 executors)',
    'D': 'Gene detail page — entity jump, chain-of-thought columns and verified PMIDs',
}

try:
    f_letter = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 92)
    f_cap = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 52)
except Exception:
    f_letter = ImageFont.load_default(); f_cap = ImageFont.load_default()

def load_cell(src, pw, ph, focus=None):
    img = Image.open(src).convert('RGB')
    if focus:
        x0, y0, x1, y1 = focus
        img = img.crop((x0, y0, x1, y1))
    w, h = img.size
    target = pw / ph
    cur = w / h
    if cur > target:   # too wide -> crop width
        nw = int(h * target)
        x0 = (w - nw) // 2
        img = img.crop((x0, 0, x0 + nw, h))
    else:              # too tall -> crop height (keep top)
        nh = int(w / target)
        img = img.crop((0, 0, w, nh))
    return img.resize((pw, ph), Image.LANCZOS)

sources = {
    'A': (f'{ASSETS}/panel_A_big.png', (430, 0, 1570, 760)),   # dome focus from big render
    'B': (f'{ASSETS}/panel_B_explore.png', None),
    'C': (f'{ASSETS}/panel_C_catalog.png', None),
    'D': (f'{ASSETS}/panel_D_detail.png', None),
}

canvas = Image.new('RGB', (W, H), 'white')
draw = ImageDraw.Draw(canvas)
pos = {
    'A': (MX, TOP),
    'B': (MX + PW + GAP, TOP),
    'C': (MX, TOP + PH + CAP_H + ROW_GAP),
    'D': (MX + PW + GAP, TOP + PH + CAP_H + ROW_GAP),
}
for k, (x, y) in pos.items():
    src, focus = sources[k]
    img = load_cell(src, PW, PH, focus)
    draw.rectangle([x, y, x + PW, y + PH], outline=(30, 41, 59), width=4)
    canvas.paste(img, (x, y))
    draw.rectangle([x, y, x + 110, y + 110], fill=(11, 16, 32))
    tw = draw.textlength(k, font=f_letter)
    draw.text((x + (110 - tw) / 2, y + 8), k, font=f_letter, fill=(255, 215, 0))
    draw.text((x, y + PH + 42), captions[k], font=f_cap, fill=(31, 41, 55))

canvas.save(f'{OUT}.png', dpi=(600, 600))
canvas.save(f'{OUT}.tiff', dpi=(600, 600), compression='tiff_lzw')
print('Figure 4 composite:', canvas.size, '@600dpi')
