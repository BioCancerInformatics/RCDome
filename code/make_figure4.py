# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont

ASSETS = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures/Figure4_assets'
OUT = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures/Figure_4_app'

# A4 landscape @ 600 DPI
W, H = 7014, 4962
MARGIN_X = 147
GAP = 60
TOP = 110
PW = 3347            # panel width
PH = 2230            # panel height (3:2 crop)
CAP_H = 120          # caption strip
ROW_GAP = 60

panels = {
    'A': f'{ASSETS}/panel_A_dome.png',
    'B': f'{ASSETS}/panel_B_explore.png',
    'C': f'{ASSETS}/panel_C_catalog.png',
    'D': f'{ASSETS}/panel_D_detail.png',
}
captions = {
    'A': 'Home dome — 53 entities, 9,265 genes, 21,568 unique gene–RCD pairs',
    'B': 'Explore RCDome — modules, benchmarks and governance',
    'C': 'Gene Catalog — DeepSeek/Compiled gene role source selector and Death-core filter (469 executor pairs)',
    'D': 'Gene detail page — entity jump, chain-of-thought columns and verified PMIDs',
}

# font
try:
    f_letter = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 92)
    f_cap    = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 52)
except Exception:
    f_letter = ImageFont.load_default()
    f_cap = ImageFont.load_default()

canvas = Image.new('RGB', (W, H), 'white')
draw = ImageDraw.Draw(canvas)

positions = {
    'A': (MARGIN_X, TOP),
    'B': (MARGIN_X + PW + GAP, TOP),
    'C': (MARGIN_X, TOP + PH + CAP_H + ROW_GAP),
    'D': (MARGIN_X + PW + GAP, TOP + PH + CAP_H + ROW_GAP),
}

def crop_to(src, pw, ph):
    img = Image.open(src).convert('RGB')
    w, h = img.size
    # resize to target width
    nh = int(h * pw / w)
    img = img.resize((pw, nh), Image.LANCZOS)
    # crop height (keep top)
    if nh > ph:
        top_cut = 0
        img = img.crop((0, top_cut, pw, top_cut + ph))
    else:
        # pad vertically on white
        padded = Image.new('RGB', (pw, ph), 'white')
        padded.paste(img, (0, 0))
        img = padded
    return img

for k, (x, y) in positions.items():
    img = crop_to(panels[k], PW, PH)
    # thin border
    draw.rectangle([x, y, x + PW, y + PH], outline=(30, 41, 59), width=4)
    canvas.paste(img, (x, y))
    # panel letter badge
    bbox_w = 110
    draw.rectangle([x, y, x + bbox_w, y + 110], fill=(11, 16, 32))
    tw = draw.textlength(k, font=f_letter)
    draw.text((x + (bbox_w - tw) / 2, y + 8), k, font=f_letter, fill=(255, 215, 0))
    # caption
    draw.text((x, y + PH + 42), captions[k], font=f_cap, fill=(31, 41, 55))

canvas.save(f'{OUT}.png', dpi=(600, 600))
canvas.save(f'{OUT}.tiff', dpi=(600, 600), compression='tiff_lzw')
print('Figure 4 composite saved:', canvas.size, '@600dpi =', W/600, 'x', H/600, 'in')
