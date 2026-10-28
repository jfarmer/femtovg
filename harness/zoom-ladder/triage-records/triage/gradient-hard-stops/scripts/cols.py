import sys, numpy as np
from PIL import Image
R='/Users/matt/src/femtovg-wt/runs/zoom/'
steps={'z1':0,'z125':1,'z15':2,'z175':3,'z2':4,'z3':5,'z4':6,'z075':13,'z05':14,'z033':15,'z025':16}
zoom={'z1':1,'z125':1.25,'z15':1.5,'z175':1.75,'z2':2,'z3':3,'z4':4,'z075':.75,'z05':.5,'z033':.33,'z025':.25}
def load(p):
    try: return np.asarray(Image.open(p).convert('RGB')).astype(int)
    except Exception: return None
key=sys.argv[1]; fr=sys.argv[2:] or list(steps)
for f in fr:
    fv=load(f'{R}png/zl_zm_svg/{key}/{steps[f]:02d}.png')
    out=[f'{f}:']
    for b in ['chr','ff','wk']:
        r=load(f'{R}fresh/refs/{b}_{key}_{f}.png')
        if r is None: out.append(f'{b}=None'); continue
        d=np.abs(fv-r).max(axis=2)
        bad=d>8
        ys,xs=np.nonzero(bad)
        cols=sorted(set(xs.tolist()))
        out.append(f'{b}={bad.sum()} cols={cols[:12]}')
    print(' '.join(out))
