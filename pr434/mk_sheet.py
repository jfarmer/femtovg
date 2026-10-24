#!/usr/bin/env python3
"""pr434-pads.png: Chromium, main, #434 and #434 + the suggested shader fix on pad.svg, each as render | shadows x16 | |diff vs Chromium| x20."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
L = lambda p: np.asarray(Image.open(p).convert('RGB').crop((0, 0, 400, 150))).astype(int)
ref = L('pad.chr.png')
builds = [('main (1bca261c)', 'main'), ('#434 (6c806522)', 'pr'), ('#434 + suggested shader fix', 'fix')]
F = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 15)
FS = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 12)
def stretch(a):
    return Image.fromarray(np.clip(a * 16, 0, 255).astype(np.uint8))
def diff(a):
    d = np.abs(a - ref).max(axis=2)
    v = np.clip(d * 20, 0, 255).astype(np.uint8)
    img = np.zeros(a.shape, np.uint8); img[..., 0] = v; img[..., 1] = (v * 0.25).astype(np.uint8)
    img[d <= 1] = (255, 255, 255)
    return Image.fromarray(img)
def regions(a):
    dd = np.abs(a - ref).max(axis=2); out = []
    for name, (y0, y1) in (('linear b→w', (55, 95)), ('linear r→b', (105, 145))):
        out.append(f"{name}: start pad {dd[y0:y1, 0:118].max()}, ramp {dd[y0:y1, 122:278].max()}, end pad {dd[y0:y1, 282:400].max()}")
    return '   '.join(out)
PW, PH, GAP, LH, TOP = 400, 150, 10, 40, 58
cols = ['render', 'render, shadows ×16 (0–16 → 0–255)', '|render − Chromium| ×20 (≤ 1 level, dither, white)']
W = 3 * PW + 4 * GAP; H = TOP + (len(builds) + 1) * (PH + LH) + 10
sheet = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(sheet)
d.text((GAP, 8), 'Each panel, top to bottom: sRGB black→white, linearRGB black→white, linearRGB red→blue; gradient line x = 120…280, pads either side', fill='black', font=F)
for i, c in enumerate(cols):
    d.text((GAP + i * (PW + GAP), 34), c, fill='black', font=F)
rowsets = [('Chromium 131 (Firefox within 2 levels, WebKit within 7; all three paint both pads with the exact stop colour)', ref, None)] + [(n, L(f'{k}.ppm'), k) for n, k in builds]
for r, (name, img, k) in enumerate(rowsets):
    y = TOP + r * (PH + LH)
    d.text((GAP, y + 2), name if k is None else f'{name}. Max levels off Chromium: {regions(img)}', fill='black', font=FS)
    y += 20
    sheet.paste(Image.fromarray(img.astype(np.uint8)), (GAP, y))
    sheet.paste(stretch(img), (GAP + PW + GAP, y))
    if k is None:
        d.text((GAP + 2 * (PW + GAP) + 10, y + 60), '(reference)', fill='gray', font=F)
    else:
        sheet.paste(diff(img), (GAP + 2 * (PW + GAP), y))
sheet.save('pr434-pads.png'); print(sheet.size)
