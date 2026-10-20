# femtovg frames of each variant against the browsers' frames of the ORIGINAL (the dashed circles are the target).
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
def box_sum(a): return sum(a[y0:y1, x0:x1].sum() for y0, y1, x0, x1 in boxes)
refs = {b: L(f'{S}/refs/{b}_t__p00_orig_z2.png') for b in ('chr', 'ff', 'wk', 'id')}
base = {b: L(f'{S}/refs/{b}_t__p01_nodash_z2.png') for b in ('chr', 'ff', 'wk', 'id')}
fv0 = L(f'{S}/png/mst2_t__p01_nodash_z2.png')
ink = {b: box_sum(np.abs(refs[b] - base[b]).mean(axis=2) / 255) for b in refs}
print('browser ring ink (|dlum| over the no-dash frame, both iris boxes):', ' '.join(f'{b}={v:.1f}' for b, v in ink.items()))
for n in ('p00_orig', 'p04_emul_split', 'p05_emul_joined', 'p02_dash_arcs', 'p01_nodash'):
    fv = L(f'{S}/png/mst2_t__{n}_z2.png')
    off = [np.abs(fv - refs[b]).max(axis=2) > 20 for b in ('chr', 'ff', 'wk')]
    all3 = off[0] & off[1] & off[2]
    i = box_sum(np.abs(fv - fv0).mean(axis=2) / 255)
    print(f'{n:16s} iris all3 red {box_sum(all3):3d}  frame all3 red {all3.sum():4d}  ring ink {i:5.1f}  ' +
          ' '.join(f'/{b} {i / ink[b]:.2f}' for b in ink))
