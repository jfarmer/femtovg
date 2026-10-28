import json, numpy as np, math
from PIL import Image
from geom import *
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2-verify'
geo = json.load(open(f'{D}/svg/geo.json'))['v_corners']
L = lambda p: np.asarray(Image.open(p).convert('L'), float) / 255
ims = {'fv': L(f'{D}/png/mst4_t__v_corners_hd.png'), 'fm': L(f'{D}/png/fm_t__v_corners_hd.png')}
ims.update({b: L(f'{D}/refs/{b}_t__v_corners_hd.png') for b in ('chr', 'ff', 'wk', 'id')})
acc = {}
for sh in geo['shapes']:
    pts = np.array(sh['pts'])
    kind = sh['kind'] if not sh['kind'].startswith('spike') else ('spike<=30' if int(sh['kind'][5:]) <= 30 else 'spike45-90')
    for (vx, vy), cv in zip(pts, sh['convex']):
        px, py = int(math.floor(vx)), int(math.floor(vy))
        c = coverage(px - 1, py - 1, px + 2, py + 2, lambda X, Y: inside_polys(X, Y, [pts]), ss=32)
        k = (kind, 'convex' if cv else 'reflex'); r = acc.setdefault(k, {b: [] for b in ims})
        for b in ims: r[b].append(ims[b][py - 1:py + 2, px - 1:px + 2] - c)
for k, r in acc.items():
    s = []
    for b, v in r.items():
        v = np.array(v); s.append(f'{b}: maxabs {np.abs(v).max():.3f} n>20 {(np.abs(v) > 20 / 255).sum():3d}')
    print(f'{str(k):26s} n={len(r["fv"])} (3x3 windows) ' + ' | '.join(s))
