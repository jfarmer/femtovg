# exact_disk_cmp.py KEY cx cy r [extra.png per zoom pattern with {fr}]: renderers vs the exact disk (green on white)
import sys, numpy as np, os
from PIL import Image
from exact_circle import coverage_circle, framing, compose
from cmp import fem, ref, load
k = sys.argv[1]; cx, cy, r = map(float, sys.argv[2:5]); extras = sys.argv[5:]
FR = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05', 0.33: 'z033', 0.25: 'z025'}
L = lambda p: np.asarray(Image.open(p).convert('RGB')).astype(int) if os.path.exists(p) else None
names = ['fem', 'chr', 'ff', 'wk', 'id'] + [os.path.basename(e).split('_')[0] for e in extras]
print('zoom ' + ''.join(f'{n:>10}' for n in names) + '    px beyond 8/255 of the exact disk (max err)')
for z, fr in FR.items():
    X, Y, R = framing(cx, cy, r, z)
    ex = compose(coverage_circle(X, Y, R, ss=48))
    imgs = [fem(k, z)] + [ref(b, k, z) for b in ('chr', 'ff', 'wk')] + [load(f'../area/id_{k}_{fr}.png')] + [L(e.format(fr=fr)) for e in extras]
    row = ''
    for img in imgs:
        if img is None: row += '         -'; continue
        d = np.abs(img[..., :3] - ex).max(-1); row += f'{int((d > 8).sum()):5d}({d.max():3.0f})'
    print(f'{z:<5}' + row)
