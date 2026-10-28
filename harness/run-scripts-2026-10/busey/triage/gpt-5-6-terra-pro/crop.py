import sys, numpy as np
from PIL import Image
sys.path.insert(0, '.')
from off3 import L, off3
R='/Users/matt/src/femtovg-wt/runs/busey'; K='corpus__buseybench__gpt-5-6-terra-pro'
fr = sys.argv[1] if len(sys.argv)>1 else 'z2'
o = L(f'{R}/png/mst2_{K}_{fr}.png'); refs=[L(f'{R}/refs/{b}_{K}_{fr}.png') for b in ('chr','ff','wk')]
a, s = off3(o, refs)
ys, xs = np.nonzero(a)
print('bbox', xs.min(), ys.min(), xs.max(), ys.max())
# histogram by row band
for y0 in range(0, a.shape[0], 20):
    print(y0, a[y0:y0+20].sum(), end='; ')
print()
for x0 in range(0, a.shape[1], 40):
    print(x0, a[:, x0:x0+40].sum(), end='; ')
print()
