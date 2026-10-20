import sys, numpy as np, os
from PIL import Image
R=os.path.expanduser('~/src/femtovg-wt/runs/zoom/')
def load(p): return np.asarray(Image.open(p).convert('RGB')).astype(int)
img=load(sys.argv[1]); key=sys.argv[2]; f=sys.argv[3]
for b in ['chr','ff','wk']:
    p=f'{R}fresh/refs/{b}_{key}_{f}.png'
    if not os.path.exists(p): print(b,'none'); continue
    r=load(p); bad=np.abs(img-r).max(axis=2)>8
    ys,xs=np.nonzero(bad)
    from collections import Counter
    print(b, bad.sum(), sorted(Counter(xs.tolist()).items())[:20])
