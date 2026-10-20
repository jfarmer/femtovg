import sys, os, json
import numpy as np
from PIL import Image
S = os.path.dirname(os.path.abspath(__file__))
K = 0.390625
ROWS = [320 + 20 * i for i in range(20)]
def load(p):
    return np.asarray(Image.open(p).convert('L'), dtype=np.float64) / 255.0
def rows_ink(im):
    out = []
    x0, x1 = int(230 + (195 - 512) * K), int(230 + (805 - 512) * K) + 1
    for y in ROWS:
        yc = 130 + (y - 512) * K
        a, b = int(round(yc - 3.5)), int(round(yc + 3.5)) + 1
        out.append(im[a:b, x0:x1].sum())
    return np.array(out)
names = sorted(n[:-4] for n in os.listdir(f'{S}/svg'))
sel = sys.argv[1:] or names
src = {'fv': 'png/mst2_t__{}_z2.png', 'chr': 'refs/chr_t__{}_z2.png', 'ff': 'refs/ff_t__{}_z2.png', 'wk': 'refs/wk_t__{}_z2.png', 'id': 'refs/id_t__{}_z2.png'}
res = {}
print(f'{"file":20s} ' + ' '.join(f'{k:>8s}' for k in src) + '   fv/id  chr/id  ff/id  wk/id')
for n in sel:
    r = {k: rows_ink(load(f'{S}/' + v.format(n))) for k, v in src.items()}
    res[n] = {k: v.tolist() for k, v in r.items()}
    t = {k: v.sum() for k, v in r.items()}
    print(f'{n:20s} ' + ' '.join(f'{t[k]:8.1f}' for k in src) + '   ' + '  '.join(f'{t[k]/t["id"]:5.2f}' for k in ('fv', 'chr', 'ff', 'wk')))
json.dump(res, open(f'{S}/ink.json', 'w'))
