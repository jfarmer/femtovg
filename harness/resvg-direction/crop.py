#!/usr/bin/env python3
"""usage: crop.py x/name x0 y0 x1 y1 [scale=3] -> x/name.crop.png: the box of resvg | Chromium | Firefox | WebKit stacked, scaled."""
import sys
from PIL import Image, ImageDraw
base = sys.argv[1]; x0, y0, x1, y1 = map(int, sys.argv[2:6]); sc = int(sys.argv[6]) if len(sys.argv) > 6 else 3
def load(p):
    im = Image.open(p).convert('RGBA'); bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im); return bg.convert('RGB')
rows = []
for k, n in (('rs', 'resvg'), ('chr', 'Chromium'), ('ff', 'Firefox'), ('wk', 'WebKit')):
    im = load(f'{base}.{k}.png').crop((x0, y0, x1, y1)).resize(((x1 - x0) * sc, (y1 - y0) * sc), Image.NEAREST)
    rows.append((n, im))
w, h = rows[0][1].size
out = Image.new('RGB', (w, (h + 12) * len(rows)), 'white'); d = ImageDraw.Draw(out)
for i, (n, im) in enumerate(rows):
    out.paste(im, (0, i * (h + 12) + 12)); d.text((2, i * (h + 12)), n, fill='black')
out.save(f'{base}.crop.png'); print(out.size)
