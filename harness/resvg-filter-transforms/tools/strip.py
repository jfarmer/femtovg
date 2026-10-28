#!/usr/bin/env python3
"""strip.py OUT.png NAME[:zoom]... : r48 | r49 | Chrome | Firefox | WebKit 27.2 | STP | r49 vs Chrome | r49 vs Firefox | r49 vs STP"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
COLS = [('r48', 'resvg 0.48.1'), ('r49', 'resvg 0.49.0'), ('chrome', 'Chrome Canary 158'), ('firefox', 'Firefox 159b5'),
        ('webkit', 'Safari 27.2 WebKit'), ('stp', 'Safari TP WebKit')]
DIFFS = [('r49', 'chrome'), ('r49', 'firefox'), ('r49', 'stp')]
def diffimg(a, b):
    d = np.abs(np.asarray(a, np.int16) - np.asarray(b, np.int16)).max(2)
    out = np.full(d.shape + (3,), 255, np.uint8)
    out[(d > 8) & (d <= 20)] = (255, 165, 0); out[d > 20] = (255, 0, 0)
    return Image.fromarray(out)
rows = []
for arg in sys.argv[2:]:
    name, _, z = arg.partition(':'); z = float(z or 1)
    ims = {r: Image.open(f'{HERE}/out/{r}/{name}.png').convert('RGB') for r, _ in COLS}
    panels = [(ims[r], l) for r, l in COLS] + [(diffimg(ims[a], ims[b]), f'{a} vs {b}') for a, b in DIFFS]
    w, h = panels[0][0].size; W, H = int(w * z), int(h * z)
    row = Image.new('RGB', (len(panels) * (W + 8), H + 34), 'white'); d = ImageDraw.Draw(row)
    d.text((2, 2), name, fill='black')
    for i, (im, l) in enumerate(panels):
        row.paste(im.resize((W, H), Image.NEAREST if z >= 1 else Image.LANCZOS), (i * (W + 8), 30)); d.text((i * (W + 8) + 2, 17), l, fill='black')
        d.rectangle([i * (W + 8), 30, i * (W + 8) + W - 1, 30 + H - 1], outline=(200, 200, 200))
    rows.append(row)
out = Image.new('RGB', (max(r.size[0] for r in rows), sum(r.size[1] for r in rows)), 'white'); y = 0
for r in rows: out.paste(r, (0, y)); y += r.size[1]
out.save(sys.argv[1]); print(sys.argv[1], out.size)
