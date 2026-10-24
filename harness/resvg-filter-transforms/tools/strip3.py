#!/usr/bin/env python3
"""strip3.py OUT.png DIR:NAME... : resvg's reference before | after | Chrome | Firefox | Safari TP | before vs Chrome | after vs Chrome,
at the suite's 300 px (t15.py's directories). White within 8/255, orange to 20, red beyond."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
def load(p):
    im = Image.open(p).convert('RGBA'); bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im); return bg.convert('RGB')
def diffimg(a, b):
    d = np.abs(np.asarray(a, np.int16) - np.asarray(b, np.int16)).max(2)
    out = np.full(d.shape + (3,), 255, np.uint8); out[(d > 8) & (d <= 20)] = (255, 165, 0); out[d > 20] = (220, 0, 0)
    return Image.fromarray(out), (d > 20).mean() * 100
rows = []
for arg in sys.argv[2:]:
    d, name = arg.split(':', 1); z = 0.6
    ims = {k: load(f'{HERE}/{d}/{name}__{k}.png') for k in ('old', 'new', 'chrome', 'firefox', 'stp')}
    db, pb = diffimg(ims['old'], ims['chrome']); da, pa = diffimg(ims['new'], ims['chrome'])
    labels = ['reference, main', 'reference, this PR', 'Chrome Canary 158', 'Firefox 159b5', 'Safari Technology Preview', 'main vs Chrome', 'this PR vs Chrome']
    panels = list(zip([ims['old'], ims['new'], ims['chrome'], ims['firefox'], ims['stp'], db, da], labels))
    w, h = ims['old'].size; W, H = int(w * z), int(h * z)
    row = Image.new('RGB', (len(panels) * (W + 8), H + 36), 'white'); dr = ImageDraw.Draw(row)
    dr.text((2, 2), f'{name.replace("_", "/", 2)}: beyond 20/255 vs Chrome {pb:.2f} % -> {pa:.2f} %', fill='black')
    for i, (im, l) in enumerate(panels):
        row.paste(im.resize((W, H), Image.LANCZOS if i < 5 else Image.BOX), (i * (W + 8), 32)); dr.text((i * (W + 8) + 2, 19), l, fill='black')
        dr.rectangle([i * (W + 8), 32, i * (W + 8) + W - 1, 32 + H - 1], outline=(200, 200, 200))
    rows.append(row)
img = Image.new('RGB', (max(r.size[0] for r in rows), sum(r.size[1] for r in rows)), 'white'); y = 0
for r in rows: img.paste(r, (0, y)); y += r.size[1]
img.save(sys.argv[1]); print(sys.argv[1], img.size)
