#!/usr/bin/env python3
"""capink.py [TAG ...]: per cap, the ink a renderer puts down beyond the exact shape, in device px^2, from caps.svg
and caps-butt.svg. Each stroke's whole neighbourhood (pixels within r + 2.5 px of its segment) is summed and the
exact ink (16 x 16 samples a pixel) subtracted; halved, that is one cap's excess, the body being exact in ink for
every renderer (caps-butt shows it). Prints the excess per width and framing next to the exact half-disc's area
pi r^2 / 2 and to pi f^2 / 24 (f = 1 px), what a ramp a fringe wide adds around a half turn."""
import json, math, os, sys
import numpy as np
sys.argv = sys.argv[:1] + (sys.argv[1:] or ['mstc', 'caps'])
from measure import shapes, dev, seg_dist, in_rect, coverage, frame, MAP, REFS
TAGS = sys.argv[1:]
for name, cap in (('caps', 'round'), ('caps-butt', 'butt')):
    for fr in ('z1', 'z2', 'hd'):
        s = MAP[fr][0]
        imgs = {t: frame(t, f'red__{name}', fr) for t in TAGS + REFS}
        print(f'\n{name} {fr}: excess ink per cap, px^2 (device width)   half-disc  pi/24   ' + ' '.join(f'{t:>7}' for t in TAGS + REFS))
        acc = {}
        for ln in shapes['caps']:
            a, b = dev(ln['a'], fr), dev(ln['b'], fr); r = ln['w'] * s / 2
            inside = (lambda X, Y, a=a, b=b, r=r: seg_dist(X, Y, a, b) <= r) if cap == 'round' else (lambda X, Y, a=a, b=b, r=r: in_rect(X, Y, a, b, r))
            m = 2.5 + r
            x0, y0 = np.floor(np.minimum(a, b) - m).astype(int); x1, y1 = np.ceil(np.maximum(a, b) + m).astype(int)
            ex = coverage(x0, y0, x1, y1, inside)
            Yc, Xc = np.mgrid[y0:y1, x0:x1] + 0.5
            win = seg_dist(Xc, Yc, a, b) <= m
            row = acc.setdefault(ln['w'], {t: [] for t in TAGS + REFS})
            for t, im in imgs.items():
                if im is None: continue
                row[t].append((im[y0:y1, x0:x1][win].sum() - ex[win].sum()) / 2)
        for w, row in acc.items():
            dw = w * s; r = max(dw, 1.0) / 2
            print(f'  {w:5} ({dw:5.2f} px)   {math.pi * (dw / 2) ** 2 / 2:8.3f} {math.pi / 24:6.3f}   ' + ' '.join(f'{np.mean(row[t]):7.3f}' if row[t] else f'{"-":>7}' for t in TAGS + REFS))
