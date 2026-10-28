#!/usr/bin/env python3
"""Zoom ladder for one corpus file: per framing a row femtovg | Chromium | diff, cropped to the artwork (the union of both
frames' ink plus a margin) and scaled up with nearest-neighbour so each row is the same height; prints signed weight.
  nyt_sheet.py OUT.png <build> <key-suffix> framing[,framing...] [crop=x,y,w,h in z1 box units]"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.abspath(__file__))
files = {f['key']: f for f in json.load(open(f'{R}/files.json'))}
out, build, name, frs = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(',')
crop = None
for a in sys.argv[5:]:
    if a.startswith('crop='): crop = [float(v) for v in a[5:].split(',')]
k = [k for k in files if k.endswith('__' + name)][0]
font = lambda s: ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', s)
Z = {'z01': 0.1, 'z025': 0.25, 'z05': 0.5, 'z1': 1, 'z2': 2, 'z4': 4}
rows = []
for fr in frs:
    a = Image.open(f'{R}/png_nyt/{build}_{k}_{fr}.png').convert('RGB') if os.path.exists(f'{R}/png_nyt/{build}_{k}_{fr}.png') else Image.open(f'{R}/png/{build}_{k}_{fr}.png').convert('RGB'); c = Image.open(f'{R}/refs/chr_{k}_{fr}.png').convert('RGB')
    A = np.asarray(a, dtype=np.int16); C = np.asarray(c, dtype=np.int16)
    d = np.abs(A - C).max(axis=2)
    if crop and fr == 'hd':
        box = [int(420 + 5.4 * crop[0]), int(5.4 * crop[1]), int(np.ceil(420 + 5.4 * (crop[0] + crop[2]))), int(np.ceil(5.4 * (crop[1] + crop[3])))]
    elif crop and fr in Z:
        z = Z[fr]; x0 = 230 + z * (130 + crop[0] - 230); y0 = 130 + z * (30 + crop[1] - 130)
        box = [int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x0 + z * crop[2])), int(np.ceil(y0 + z * crop[3]))]
    else:
        ink = (A.sum(axis=2) < 765) | (C.sum(axis=2) < 765) if fr != 'hd' else d > 0
        ys, xs = np.nonzero(ink); m = 2
        box = [xs.min() - m, ys.min() - m, xs.max() + 1 + m, ys.max() + 1 + m]
    W, H = a.size
    box = [max(0, box[0]), max(0, box[1]), min(W, box[2]), min(H, box[3])]
    heat = np.full(d.shape + (3,), 255, np.uint8); heat[(d > 0) & (d <= 20)] = [255, 190, 110]; heat[d > 20] = [220, 30, 30]
    lum = lambda X: (0.299 * X[:, :, 0] + 0.587 * X[:, :, 1] + 0.114 * X[:, :, 2])
    sl = (slice(box[1], box[3]), slice(box[0], box[2]))
    weight_f = (255 - lum(A)[sl]).sum(); weight_c = (255 - lum(C)[sl]).sum()
    rows.append((fr, [im.crop(box) for im in (a, c, Image.fromarray(heat))], 100 * (d[sl] > 20).mean(), int(d[sl].max()), 100 * (weight_f - weight_c) / max(weight_c, 1)))
target_h = 150
out_rows = []
for fr, panels, pct, mx, dw in rows:
    w, h = panels[0].size; s = max(1, int(target_h // h)) if h <= target_h else None
    if s: panels = [p.resize((w * s, h * s), Image.NEAREST) for p in panels]
    else: panels = [p.resize((int(w * target_h / h), target_h), Image.LANCZOS) for p in panels]
    out_rows.append((f'{fr}: {w}x{h} px crop, {pct:.1f} % beyond 20/255, max {mx}, ink weight {dw:+.1f} % vs Chromium', panels))
    print(name, fr, f'crop {w}x{h} px>20 {pct:.2f}% max {mx} ink weight {dw:+.2f}%')
gap, cap = 8, 18
width = max(sum(p.size[0] for p in ps) + 4 * gap for _, ps in out_rows); width = max(width, 760)
height = sum(ps[0].size[1] + cap + gap for _, ps in out_rows) + gap + 16
sheet = Image.new('RGB', (width, height), 'white'); dr = ImageDraw.Draw(sheet)
dr.text((gap, 2), f'{name}: femtovg (master 9d574e0) | Chromium 131 | diff (red > 20/255, orange 1-20)', fill=(0, 0, 0), font=font(12))
y = 18
for label, ps in out_rows:
    dr.text((gap, y), label, fill=(60, 60, 60), font=font(11)); x = gap
    for p in ps:
        sheet.paste(p, (x, y + cap)); dr.rectangle([x - 1, y + cap - 1, x + p.size[0], y + cap + p.size[1]], outline=(200, 200, 200)); x += p.size[0] + gap
    y += ps[0].size[1] + cap + gap
sheet.save(out)
