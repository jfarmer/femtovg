#!/usr/bin/env python3
"""sheet337.py OUT.png name:framing:label ... : reftest rows for issue #337 - femtovg (mst2 = master 09f5174c) |
Chromium 131 | Firefox 159 | WebKit (macOS 27.2) | femtovg vs Chromium (red > 20/255, orange 1-20), cropped to the
200-unit box of the z1 framing."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
R = os.path.expanduser('~/src/femtovg-wt/runs/wpt22')
files = [f['key'] for f in json.load(open(f'{R}/files.json'))]
key = lambda name: next(k for k in files if k.endswith('__' + name))
font = lambda s: ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', s)
out, rows = sys.argv[1], []
for spec in sys.argv[2:]:
    name, fr, label = spec.split(':', 2)
    k = key(name)
    ims = [Image.open(p).convert('RGB') for p in (f'{R}/png/mst2_{k}_{fr}.png', f'{R}/refs/chr_{k}_{fr}.png',
                                                    f'{R}/refs/ff_{k}_{fr}.png', f'{R}/refs/wk_{k}_{fr}.png')]
    d = np.abs(np.asarray(ims[0], dtype=np.int16) - np.asarray(ims[1], dtype=np.int16)).max(axis=2)
    heat = np.full(d.shape + (3,), 255, np.uint8); heat[(d > 0) & (d <= 20)] = [255, 170, 60]; heat[d > 20] = [220, 30, 30]
    box = (120, 20, 340, 240)
    rows.append((label, [im.crop(box) for im in ims + [Image.fromarray(heat)]]))
pw, ph = rows[0][1][0].size
gap, cap = 8, 22
heads = ['femtovg (master 09f5174c)', 'Chromium 131', 'Firefox 159', 'WebKit (macOS 27.2)', 'femtovg vs Chromium']
sheet = Image.new('RGB', (5 * pw + 6 * gap, len(rows) * (ph + cap + 18) + gap), 'white')
dr = ImageDraw.Draw(sheet)
for i, (label, panels) in enumerate(rows):
    y = gap + i * (ph + cap + 18)
    dr.text((gap, y), label, fill=(0, 0, 0), font=font(13))
    for j, (p, n) in enumerate(zip(panels, heads)):
        x = gap + j * (pw + gap)
        dr.text((x, y + cap - 4), n, fill=(90, 90, 90), font=font(11))
        sheet.paste(p, (x, y + cap + 10)); dr.rectangle([x - 1, y + cap + 9, x + pw, y + cap + 10 + ph], outline=(200, 200, 200))
sheet.save(out); print(out, sheet.size)
