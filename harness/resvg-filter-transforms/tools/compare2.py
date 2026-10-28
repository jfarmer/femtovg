#!/usr/bin/env python3
"""Per file and scale: each resvg build's distance to the browsers (share beyond 20/255), and a summary:
the distance to the nearest browser and to the browsers' median, per build, summed over scales."""
import json, os, statistics, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
SCALES = ['1', '1.5', '1.77', '2']
BUILDS = ['r49', 'rT', 'rE', 'rB', 'rB2']
BROWSERS = ['chrome', 'firefox', 'webkit', 'stp']
def load(s, r, n):
    p = f'{HERE}/out_{s}/{r}/{n}.png'
    return np.asarray(Image.open(p).convert('RGB'), np.int16) if os.path.exists(p) else None
def d(a, b):
    return None if a is None or b is None or a.shape != b.shape else float((np.abs(a - b).max(2) > 20).mean() * 100)
names = sorted(f[:-4] for f in os.listdir(f'{HERE}/svg') if f.endswith('.svg') and not f.startswith('i949'))
rows = {}
for n in names:
    for s in SCALES:
        im = {r: load(s, r, n) for r in BUILDS + BROWSERS}
        br = {b: {c: d(im[b], im[c]) for c in BROWSERS} for b in BUILDS}
        spread = d(im['chrome'], im['firefox'])
        rows[(n, s)] = (br, spread, d(im['chrome'], im['stp']), d(im['firefox'], im['stp']))
json.dump({f'{n}@{s}': v for (n, s), v in rows.items()}, open(f'{HERE}/compare2.json', 'w'))
f = lambda v: '  -  ' if v is None else f'{v:5.2f}'
print(f'{"file":46} {"s":>4} | ch~ff ch~tp ff~tp | ' + ' | '.join(f'{b}: ch    ff    tp ' for b in BUILDS))
for (n, s), (br, sp, ct, ft) in rows.items():
    cells = ' | '.join(f'{b}: ' + ' '.join(f(br[b][c]) for c in ('chrome', 'firefox', 'stp')) for b in BUILDS)
    print(f'{n[-46:]:46} {s:>4} | {f(sp)} {f(ct)} {f(ft)} | {cells}')
print()
for b in BUILDS:
    tot = {c: sum(rows[k][0][b][c] or 0 for k in rows) for c in BROWSERS}
    worse = sum(1 for k in rows if (rows[k][0][b]['chrome'] or 0) > (rows[k][0]['r49']['chrome'] or 0) + 0.05)
    better = sum(1 for k in rows if (rows[k][0][b]['chrome'] or 0) < (rows[k][0]['r49']['chrome'] or 0) - 0.05)
    print(f'{b}: summed % vs ' + ', '.join(f'{c} {tot[c]:7.2f}' for c in BROWSERS) + f'   vs r49 on Chrome: {better} closer, {worse} further')
