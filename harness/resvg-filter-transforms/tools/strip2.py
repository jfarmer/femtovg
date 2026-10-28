#!/usr/bin/env python3
"""strip2.py OUT.png BEFORE AFTER NAME@SCALE[:zoom]... : before | after | Chrome | Firefox | Safari TP | before vs Chrome | after vs Chrome
(difference panels: white within 8/255, orange to 20, red beyond; the caption has the share beyond 20/255)."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
LABEL = {'r49': 'resvg 0.49.0', 'rB2': 'this PR', 'rU': 'this PR', 'chrome': 'Chrome Canary 158', 'firefox': 'Firefox 159b5', 'stp': 'Safari TP (WebKit 22627)'}
def diffimg(a, b):
    d = np.abs(np.asarray(a, np.int16) - np.asarray(b, np.int16)).max(2)
    out = np.full(d.shape + (3,), 255, np.uint8); out[(d > 8) & (d <= 20)] = (255, 165, 0); out[d > 20] = (220, 0, 0)
    return Image.fromarray(out), (d > 20).mean() * 100
out_path, before, after = sys.argv[1:4]
rows = []
for arg in sys.argv[4:]:
    spec, _, z = arg.partition(':'); name, _, scale = spec.partition('@'); z = float(z or 1)
    d = f'{HERE}/out_{scale}' if os.path.isdir(f'{HERE}/out_{scale}/{after}') else f'{HERE}/out'
    ims = {r: Image.open(f'{d}/{r}/{name}.png').convert('RGB') for r in (before, after, 'chrome', 'firefox', 'stp')}
    db, pb = diffimg(ims[before], ims['chrome']); da, pa = diffimg(ims[after], ims['chrome'])
    panels = [(ims[r], LABEL.get(r, r)) for r in (before, after, 'chrome', 'firefox', 'stp')] + [(db, f'{LABEL[before]} vs Chrome'), (da, f'{LABEL[after]} vs Chrome')]
    w, h = panels[0][0].size; W, H = int(w * z), int(h * z)
    row = Image.new('RGB', (len(panels) * (W + 8), H + 36), 'white'); dr = ImageDraw.Draw(row)
    dr.text((2, 2), f'{name} at {scale}x: beyond 20/255 vs Chrome {pb:.2f} % -> {pa:.2f} %', fill='black')
    for i, (im, l) in enumerate(panels):
        row.paste(im.resize((W, H), Image.NEAREST if z >= 1 else Image.LANCZOS), (i * (W + 8), 32)); dr.text((i * (W + 8) + 2, 19), l, fill='black')
        dr.rectangle([i * (W + 8), 32, i * (W + 8) + W - 1, 32 + H - 1], outline=(200, 200, 200))
    rows.append(row)
img = Image.new('RGB', (max(r.size[0] for r in rows), sum(r.size[1] for r in rows)), 'white'); y = 0
for r in rows: img.paste(r, (0, y)); y += r.size[1]
img.save(out_path); print(out_path, img.size)
