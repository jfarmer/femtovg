import os
import numpy as np
from PIL import Image
S = os.path.dirname(os.path.abspath(__file__))
K = 0.390625
def L(p): return np.asarray(Image.open(p).convert('RGB'), dtype=np.float64)
def fr(x, y): return 230 + (x - 512) * K, 130 + (y - 512) * K
boxes = []
for cx in (408, 616):
    x, y = fr(cx, 458)
    boxes.append((int(y - 10), int(y + 11), int(x - 10), int(x + 11)))
pre = {'fv': 'png/mst2_t__{}_z2.png', 'chr': 'refs/chr_t__{}_z2.png', 'ff': 'refs/ff_t__{}_z2.png', 'wk': 'refs/wk_t__{}_z2.png', 'id': 'refs/id_t__{}_z2.png'}
img = {n: {k: L(f'{S}/' + v.format(n)) for k, v in pre.items()} for n in ('p00_orig', 'p01_nodash', 'p02_dash_arcs', 'p03_solid_rings')}
def red(n):
    a = img[n]; tot = 0; tot_all = 0
    off = [np.abs(a['fv'] - a[b]).max(axis=2) > 20 for b in ('chr', 'ff', 'wk')]
    all3 = off[0] & off[1] & off[2]
    agreed_ref = None
    return sum(all3[y0:y1, x0:x1].sum() for y0, y1, x0, x1 in boxes), all3.sum()
def ring_ink(n, k):
    # signed luminance change the rings make over the no-dash frame, summed over both iris boxes
    d = (img[n][k] - img['p01_nodash'][k]).mean(axis=2) / 255
    return sum(np.abs(d[y0:y1, x0:x1]).sum() for y0, y1, x0, x1 in boxes), sum(d[y0:y1, x0:x1].sum() for y0, y1, x0, x1 in boxes)
for n in ('p00_orig', 'p02_dash_arcs', 'p03_solid_rings', 'p01_nodash'):
    r = red(n)
    s = f'{n:16s} iris px>20 off all3: {r[0]:4d}  frame: {r[1]:5d}'
    if n != 'p01_nodash':
        ink = {k: ring_ink(n, k) for k in pre}
        s += '   ring |dlum| ' + ' '.join(f'{k}={ink[k][0]:6.1f}' for k in pre) + '   fv/id=%.2f fv/chr=%.2f fv/ff=%.2f fv/wk=%.2f' % tuple(ink['fv'][0] / ink[b][0] for b in ('id', 'chr', 'ff', 'wk'))
    print(s)
