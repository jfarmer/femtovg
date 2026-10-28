import sys,numpy as np
from PIL import Image
R='/Users/matt/src/femtovg-wt/runs/zoom/fresh/refs/'
name='corpus__babylon__vertex-pulling-normals-uvs-colors-tangents__1'
z=sys.argv[1]
def L(p): return np.asarray(Image.open(p).convert('RGB')).astype(int)
refs={k:L(f'{R}{k}_{name}_z{z}.png') for k in ('chr','wk')}
out=[]
for f in sys.argv[2:]:
    a=L(f); row=[f]
    for k,r in refs.items():
        d=np.abs(a-r).max(axis=2); row.append(f"{k} n8={int((d>8).sum())} max={int(d.max())}")
    print(' | '.join(row))
d=np.abs(refs['chr']-refs['wk']).max(axis=2); print('chr vs wk n8',int((d>8).sum()),'max',int(d.max()))
