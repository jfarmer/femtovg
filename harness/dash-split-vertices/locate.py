#!/usr/bin/env python3
"""Where a portrait variant's pixels off the browsers sit on the irises of gemini-3-7-flash: each pixel's centre as a
radius (user units) and an angle (degrees, clockwise from +x, as the circles are drawn) about the nearer iris centre.
At z2 one pixel is 2.56 units, so a pixel on the r=16 ring (stroke 15.25-16.75) measures about 14-18, one on the r=21
ring about 19-23. The circles start and end at 0 degrees; the r=21 ring's last dash runs 354.7-360 (130-131.95 units),
the r=16 ring's 358.1-360 (100-100.53 units).

  locate.py [FRAMING] [VARIANT] [all3|chr|ff|wk|id]     (default: z2 p02_dash_arcs all3)"""
import math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
fr, variant, against = (sys.argv[1:] + ['z2', 'p02_dash_arcs', 'all3'][len(sys.argv) - 1:])[:3]
sys.argv = [sys.argv[0], 'mst4']
import measure as M  # noqa: E402

k = lambda n: f'portrait__{n}'
orig = {b: M.ref(b, k('p00_orig'), fr) for b in ('chr', 'ff', 'wk', 'id')}
fv = M.frame(k(variant), fr)
mask, _ = M.iris_mask(fr, fv.shape)
if against == 'all3':
    sel = M.off(fv, orig['chr']) & M.off(fv, orig['ff']) & M.off(fv, orig['wk']) & mask
else:
    sel = M.off(fv, orig[against]) & mask
to, s = M.mapping(fr)
found = []
for y, x in zip(*np.nonzero(sel)):
    best = None
    for cx in (408, 616):
        px, py = to(cx, 458)
        u, v = (x + 0.5 - px) / s, (y + 0.5 - py) / s
        r, a = math.hypot(u, v), math.degrees(math.atan2(v, u)) % 360
        if best is None or r < best[1]:
            best = (cx, r, a)
    found.append(best)
print(f'{variant} at {fr}, off {against}: {len(found)} px')
for cx, r, a in sorted(found):
    ring = 'r=16' if r < 18.5 else 'r=21'
    print(f'  eye {cx}  r {r:5.2f} ({ring})  angle {a:5.1f}')
