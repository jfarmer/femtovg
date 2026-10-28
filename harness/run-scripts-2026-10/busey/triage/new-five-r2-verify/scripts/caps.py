import json, sys, numpy as np, math
from PIL import Image
from geom import *
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2-verify'
geo = json.load(open(f'{D}/svg/geo.json'))['v_caps']
b = sys.argv[1] if len(sys.argv) > 1 else 'mst4'
im = np.asarray(Image.open(f'{D}/png/{b}_t__v_caps_hd.png').convert('L'), float) / 255
def ncap(w, tol):
    r = max(w, 1.0) * 0.5; da = math.acos(r / (r + tol)) * 2; return max(2, math.ceil(math.pi / da))
rows = {}
for ln in geo['lines']:
    a = np.array(ln['a']); bb = np.array(ln['b']); w = ln['w']; d = (bb - a) / np.linalg.norm(bb - a); n = np.array([-d[1], d[0]])
    def shape(X, Y):
        if ln['cap'] == 'round': return seg_dist(X, Y, a, bb) <= w / 2
        t = (X - a[0]) * d[0] + (Y - a[1]) * d[1]; u = (X - a[0]) * n[0] + (Y - a[1]) * n[1]
        return (t >= 0) & (t <= np.linalg.norm(bb - a)) & (np.abs(u) <= w / 2)
    for end, sgn in ((a, -1), (bb, 1)):
        # window: pixels whose centre lies within [end - 1.5px along line inward, end + w/2 + 1.5 outward], |u| < w/2+1.5
        x0, y0 = np.floor(end - (w / 2 + 3)).astype(int); x1, y1 = np.ceil(end + (w / 2 + 3)).astype(int)
        cov = coverage(x0, y0, x1, y1, shape, ss=32)
        f = im[y0:y1, x0:x1]
        Yc, Xc = np.mgrid[y0:y1, x0:x1] + 0.5
        t = ((Xc - end[0]) * d[0] + (Yc - end[1]) * d[1]) * sgn; u = (Xc - end[0]) * n[0] + (Yc - end[1]) * n[1]
        m = (t > -1.0) & (t < w / 2 + 2.0) & (np.abs(u) < w / 2 + 2.0)
        lw = max(w, 1.0); alpha = min(w, 1.0)
        k = (w, ln['cap'], ln['ang'])
        rows.setdefault(k, []).append((f[m].sum() / max(cov[m].sum(), 1e-9), (np.abs(f - cov)[m] > 20 / 255).sum(), (f - cov)[m].min(), (f - cov)[m].max()))
print(f"{'w(px)':>6} {'ncap@.125':>9} {'ncap@.25':>8} | {'cap':5} ang  ink/area  px>20  minerr  maxerr")
for k, v in sorted(rows.items()):
    v = np.array(v)
    print(f'{k[0]:6.2f} {ncap(k[0], .125):9d} {ncap(k[0], .25):8d} | {k[1]:5} {k[2]:3d}  {v[:, 0].mean():.3f}  {int(v[:, 1].sum()):5d}  {v[:, 2].min():+.3f}  {v[:, 3].max():+.3f}')
