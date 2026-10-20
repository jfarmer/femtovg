import json, sys, numpy as np, math
from PIL import Image
from geom import *
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2-verify'
geo = json.load(open(f'{D}/svg/geo.json'))['v_corners']
b = sys.argv[1] if len(sys.argv) > 1 else 'mst4'
im = np.asarray(Image.open(f'{D}/png/{b}_t__v_corners_hd.png').convert('L'), float) / 255
res = {}
for sh in geo['shapes']:
    pts = np.array(sh['pts']); x0, y0 = np.floor(pts.min(0)).astype(int) - 2; x1, y1 = np.ceil(pts.max(0)).astype(int) + 2
    cov = coverage(x0, y0, x1, y1, lambda X, Y: inside_polys(X, Y, [pts]), ss=32)
    f = im[y0:y1, x0:x1]; err = f - cov
    for (vx, vy), cv in zip(pts, sh['convex']):
        px, py = int(math.floor(vx)), int(math.floor(vy))
        e = err[py - y0, px - x0]
        key = (sh['kind'], 'convex' if cv else 'reflex')
        res.setdefault(key, []).append((e, f[py - y0, px - x0], cov[py - y0, px - x0], vx - px - 0.5, vy - py - 0.5))
    res.setdefault((sh['kind'], 'all>20'), []).append(int((np.abs(err) > 20 / 255).sum()))
for k, v in res.items():
    if k[1] == 'all>20': print(k, 'px>20/255 per shape', v); continue
    e = np.array([x[0] for x in v])
    print(k, f'n={len(v)} vertex-pixel err mean {e.mean():+.3f} max {e.max():+.3f} min {e.min():+.3f}  >20/255: {(np.abs(e) > 20 / 255).sum()}')
# detail for axis-aligned squares: top-left corner pixel by offset
print('square TL corner: offset(dx,dy) femtovg area')
for sh in geo['shapes']:
    if sh['kind'] != 'square': continue
    vx, vy = sh['pts'][0]; px, py = int(math.floor(vx)), int(math.floor(vy))
    pts = np.array(sh['pts']); c = coverage(px, py, px + 1, py + 1, lambda X, Y: inside_polys(X, Y, [pts]), ss=64)[0, 0]
    print(f'  ({vx - px - 0.5:+.2f},{vy - py - 0.5:+.2f}) {im[py, px]:.3f} {c:.3f}', end='')
print()
