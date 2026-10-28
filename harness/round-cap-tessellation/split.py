#!/usr/bin/env python3
"""split.py: where in measure.py's windows the pixels more than 20/255 off the exact coverage lie, for master (mstc),
the prototype (caps), Chromium, Firefox and WebKit. Caps (caps.svg): pixel centres past the stroke's end (on the arc)
against the rest of the window (the sides). Joins (joins.svg): pixel centres past the first leg's end and before the
second leg's start (the join's arc) against the rest."""
import sys
import numpy as np
sys.argv = sys.argv[:1]
import measure as M

TAGS = ('mstc', 'caps', 'chr', 'ff', 'wk')
print('caps.svg, px off exact: total (past the end / sides)')
for fr in ('z1', 'z2', 'hd'):
    wins, s = M.caps_windows('round', fr), M.MAP[fr][0]
    ends = []
    for ln in M.shapes['caps']:
        a, b = M.dev(ln['a'], fr), M.dev(ln['b'], fr); d = (b - a) / np.linalg.norm(b - a)
        ends += [(a, -d), (b, d)]
    cells = []
    for t in TAGS:
        im = M.frame(t, 'red__caps', fr); past = side = 0
        for (w, x0, y0, x1, y1, ex, m), (end, d) in zip(wins, ends):
            Yc, Xc = np.mgrid[y0:y1, x0:x1] + 0.5
            beyond = (Xc - end[0]) * d[0] + (Yc - end[1]) * d[1] > 0
            off = (np.abs(im[y0:y1, x0:x1] - ex) > 20 / 255) & m
            past += int((off & beyond).sum()); side += int((off & ~beyond).sum())
        cells.append(f'{t} {past + side} ({past} / {side})')
    print(f'  {fr}: ' + ', '.join(cells))
print('joins.svg, px off exact: total (the arc / the rest)')
for fr in ('z1', 'z2', 'hd'):
    wins = M.joins_windows(fr); cells = []
    for t in TAGS:
        im = M.frame(t, 'red__joins', fr); arc = rest = 0
        for p, (k, x0, y0, x1, y1, ex, m) in zip(M.shapes['joins'], wins):
            P = [M.dev(q, fr) for q in p['pts']]; c = P[1]
            d1 = (P[1] - P[0]) / np.linalg.norm(P[1] - P[0]); d2 = (P[2] - P[1]) / np.linalg.norm(P[2] - P[1])
            Yc, Xc = np.mgrid[y0:y1, x0:x1] + 0.5
            region = ((Xc - c[0]) * d1[0] + (Yc - c[1]) * d1[1] > 0) & ((Xc - c[0]) * d2[0] + (Yc - c[1]) * d2[1] < 0)
            off = (np.abs(im[y0:y1, x0:x1] - ex) > 20 / 255) & m
            arc += int((off & region).sum()); rest += int((off & ~region).sum())
        cells.append(f'{t} {arc + rest} ({arc} / {rest})')
    print(f'  {fr}: ' + ', '.join(cells))
