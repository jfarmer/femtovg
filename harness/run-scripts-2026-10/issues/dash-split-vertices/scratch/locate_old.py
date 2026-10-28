import sys, math, os
sys.path.insert(0, '/Users/matt/src/femtovg-wt/da/harness/dash-split-vertices')
os.environ.setdefault('CORPUS_RUN_OUT', '/Users/matt/src/femtovg-wt/runs/issues/dash-split-vertices')
_argv = sys.argv[:]
sys.argv = [sys.argv[0], 'mst4']
import measure as M
sys.argv = _argv
import numpy as np
fr = sys.argv[1] if len(sys.argv) > 1 else 'z2'
variant = sys.argv[2] if len(sys.argv) > 2 else 'p02_dash_arcs'
against = sys.argv[3] if len(sys.argv) > 3 else 'all3'
k = lambda n: f'portrait__{n}'
orig = {b: M.ref(b, k('p00_orig'), fr) for b in ('chr', 'ff', 'wk', 'id')}
fv = M.frame(k(variant), fr)
mask, half = M.iris_mask(fr, fv.shape)
if against == 'all3':
    sel = M.off(fv, orig['chr']) & M.off(fv, orig['ff']) & M.off(fv, orig['wk']) & mask
else:
    sel = M.off(fv, orig[against]) & mask
to, s = M.mapping(fr)
ys, xs = np.nonzero(sel)
print(variant, fr, against, len(ys))
rows = []
for y, x in zip(ys, xs):
    best = None
    for cx in (408, 616):
        px, py = to(cx, 458)
        # pixel centre -> user units
        u, v = (x + 0.5 - px) / s, (y + 0.5 - py) / s
        r = math.hypot(u, v); a = math.degrees(math.atan2(v, u)) % 360
        if best is None or r < best[1]:
            best = (cx, r, a)
    rows.append(best)
for cx, r, a in sorted(rows):
    print(f'  eye {cx} r={r:6.2f} angle={a:6.1f}')
