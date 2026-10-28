#!/usr/bin/env python3
"""usage: ink.py x/name [band=18] -> for each browser, bands (y ranges) where resvg's ink and the browser's differ by more than 1 px
(ink = dark pixels; a pixel counts when no ink of the other image lies within 1 px)."""
import sys
import numpy as np
from PIL import Image
def binary_dilation(a, st):
    out = a.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            out |= np.roll(np.roll(a, dy, 0), dx, 1)
    return out
base = sys.argv[1]; band = int(sys.argv[2]) if len(sys.argv) > 2 else 18
def ink(p):
    im = Image.open(p).convert('RGBA'); bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im)
    a = np.asarray(bg.convert('RGB')).astype(int)
    return (a.sum(axis=2) < 600)
rs = ink(f'{base}.rs.png')
for k in ('chr', 'ff', 'wk'):
    try: o = ink(f'{base}.{k}.png')
    except FileNotFoundError: continue
    st = np.ones((3, 3), bool)
    m = (rs & ~binary_dilation(o, st)) | (o & ~binary_dilation(rs, st))
    bands = [(y, int(m[y:y + band].sum())) for y in range(0, m.shape[0], band) if m[y:y + band].sum() > 25]
    print(f'{k}: total {int(m.sum())} px; bands >25: {bands}')
