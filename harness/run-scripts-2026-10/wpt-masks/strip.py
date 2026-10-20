#!/usr/bin/env python3
"""Side by side: strip.py OUT.png KEY FRAMING WHO[,WHO...] [crop=x0,y0,x1,y1] [scale=N]
WHO is a build tag (png/) or a reference prefix (refs/); 'diff:A:B' shows |A-B| > 20 in red over A."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
out, key, framing, who = sys.argv[1:5]
opts = dict(a.split('=', 1) for a in sys.argv[5:])


def load(w):
    if w.startswith('diff:'):
        _, a, b = w.split(':')
        A, B = load(a), load(b)
        d = np.abs(A.astype(int) - B.astype(int)).max(axis=2) > 20
        o = (A * 0.35 + 165).astype(np.uint8)
        o[d] = (255, 0, 0)
        return o
    p = f'{HERE}/refs/{w}_{key}_{framing}.png' if w in ('id', 'chr', 'chg', 'ff', 'wk') else f'{HERE}/png/{w}_{key}_{framing}.png'
    return np.asarray(Image.open(p).convert('RGB'))


ims = [load(w) for w in who.split(',')]
if 'crop' in opts:
    x0, y0, x1, y1 = map(int, opts['crop'].split(','))
    ims = [im[y0:y1, x0:x1] for im in ims]
s = int(opts.get('scale', 1))
tiles = [Image.fromarray(im).resize((im.shape[1] * s, im.shape[0] * s), Image.NEAREST) for im in ims]
w, h = tiles[0].size
sheet = Image.new('RGB', (len(tiles) * (w + 6), h + 16), 'white')
d = ImageDraw.Draw(sheet)
for i, (t, label) in enumerate(zip(tiles, who.split(','))):
    sheet.paste(t, (i * (w + 6), 16))
    d.text((i * (w + 6) + 2, 2), label, fill='black')
sheet.save(out)
