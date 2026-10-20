import sys, numpy as np
from PIL import Image
from collections import Counter
R='/Users/matt/src/femtovg-wt/runs/zoom/'
steps={'z1':0,'z125':1,'z15':2,'z175':3,'z2':4,'z3':5,'z4':6,'z075':13,'z05':14,'z033':15,'z025':16}
def load(p):
    try: return np.asarray(Image.open(p).convert('RGB')).astype(int)
    except Exception: return None
key=sys.argv[1]; f=sys.argv[2]; b=sys.argv[3]; x0=int(sys.argv[4]); x1=int(sys.argv[5]); y=int(sys.argv[6]) if len(sys.argv)>6 else 130
fv=load(f'{R}png/zl_zm_svg/{key}/{steps[f]:02d}.png')
r=load(f'{R}fresh/refs/{b}_{key}_{f}.png')
d=np.abs(fv-r).max(axis=2)
ys,xs=np.nonzero(d>8)
print('per-col fails', sorted(Counter(xs.tolist()).items()))
for x in range(x0,x1):
    print(x, 'fv',fv[y,x].tolist(), b, r[y,x].tolist(), 'd',d[y,x])
