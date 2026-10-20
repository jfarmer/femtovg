import re, sys, json, numpy as np, math
from PIL import Image
from geom import *
from lip import flatten
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2-verify'
geo = json.load(open(f'{D}/svg/geo.json'))
P = flatten(geo['v_hair']['d'])
cls = json.load(open('/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2/classes.json'))
for fr in ('z2', 'hd'):
    ox, oy, s = FS[fr]; Q = np.column_stack([ox + P[:, 0] * s, oy + P[:, 1] * s])
    f = np.asarray(Image.open(f'{D}/png/mst4_t__v_hair_{fr}.png').convert('L'), float) / 255
    fm = np.asarray(Image.open(f'{D}/png/fm_t__v_hair_{fr}.png').convert('L'), float) / 255
    H, W = f.shape; cov = pil_cov([Q], W, H, 8)
    e = f - cov
    print(fr, 'white-on-black L269: px >20/255 off analytic', (np.abs(e) > 20 / 255).sum(), ' FILL_MASKS', (np.abs(fm - cov) > 20 / 255).sum())
    for (x, y, c, ln) in cls[f'pareto_{fr}']['pixels']:
        if ln != 269: continue
        c1 = coverage(x, y, x + 1, y + 1, lambda X, Y: inside_polys(X, Y, [Q]), ss=32)[0, 0]
        print(f'   portrait red px ({x},{y}) [{c}]: reduction femtovg {f[y, x]:.2f} analytic {c1:.2f} err {f[y, x] - c1:+.2f}')
