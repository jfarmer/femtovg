import json, numpy as np, math
from PIL import Image
from geom import *
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2-verify'
geo = json.load(open(f'{D}/svg/geo.json'))['v_caps']
L = lambda p: np.asarray(Image.open(p).convert('L'), float) / 255
ims = {b: L(f'{D}/png/mst4_t__v_caps_hd.png') if b == 'fv' else L(f'{D}/refs/{b}_t__v_caps_hd.png') for b in ('fv', 'chr', 'ff', 'wk', 'id')}
rows = {}
for ln in geo['lines']:
    a = np.array(ln['a']); bb = np.array(ln['b']); w = ln['w']; d = (bb - a) / np.linalg.norm(bb - a); n = np.array([-d[1], d[0]])
    def shape(X, Y):
        if ln['cap'] == 'round': return seg_dist(X, Y, a, bb) <= w / 2
        t = (X - a[0]) * d[0] + (Y - a[1]) * d[1]; u = (X - a[0]) * n[0] + (Y - a[1]) * n[1]
        return (t >= 0) & (t <= np.linalg.norm(bb - a)) & (np.abs(u) <= w / 2)
    for end, sgn in ((a, -1), (bb, 1)):
        x0, y0 = np.floor(end - (w / 2 + 3)).astype(int); x1, y1 = np.ceil(end + (w / 2 + 3)).astype(int)
        cov = coverage(x0, y0, x1, y1, shape, ss=32)
        Yc, Xc = np.mgrid[y0:y1, x0:x1] + 0.5
        t = ((Xc - end[0]) * d[0] + (Yc - end[1]) * d[1]) * sgn; u = (Xc - end[0]) * n[0] + (Yc - end[1]) * n[1]
        m = (t > -1.0) & (t < w / 2 + 2.0) & (np.abs(u) < w / 2 + 2.0)
        k = (ln['cap'], 'thin' if w <= 1.6 else ('mid' if w <= 3.0 else 'wide'))
        r = rows.setdefault(k, {b: [0, 0, 0.0] for b in ims})
        offs = {b: np.abs(ims[b][y0:y1, x0:x1] - cov) > 20 / 255 for b in ims}
        for b in ims:
            r[b][0] += int(offs[b][m].sum()); r[b][2] += ims[b][y0:y1, x0:x1][m].sum() / cov[m].sum()
        a3 = (np.abs(ims['fv'] - ims['chr']) > 20/255) & (np.abs(ims['fv'] - ims['ff']) > 20/255) & (np.abs(ims['fv'] - ims['wk']) > 20/255)
        r['fv'][1] += int(a3[y0:y1, x0:x1][m].sum())
for k, r in sorted(rows.items()):
    n = 0
    print(k, ' '.join(f'{b}: >20 off analytic {v[0]:3d}' for b, v in r.items()), '| femtovg off-all-3', r['fv'][1])
