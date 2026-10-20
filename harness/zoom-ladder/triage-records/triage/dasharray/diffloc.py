import sys, numpy as np
from PIL import Image
R='/Users/matt/src/femtovg-wt/runs/zoom'
LAD=[1,1.25,1.5,1.75,2,3,4,3,2,1.75,1.5,1.25,1,0.75,0.5,0.33,0.25,0.33,0.5,0.75,1]
FR={1:'z1',1.25:'z125',1.5:'z15',1.75:'z175',2:'z2',3:'z3',4:'z4',0.75:'z075',0.5:'z05',0.33:'z033',0.25:'z025'}
key=sys.argv[1]; zoom=float(sys.argv[2])
step=LAD.index(zoom)
def L(p):
    try: return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
    except FileNotFoundError: return None
f=L(f'{R}/png/zl_zm_svg/{key}/{step:02}.png')
for b in ['chr','ff','wk']:
    o=L(f'{R}/fresh/refs/{b}_{key}_{FR[zoom]}.png')
    if o is None: print(b,'none'); continue
    d=np.abs(f-o).max(2); m=d>8
    ys,xs=np.nonzero(m)
    print(b, m.sum())
    from collections import Counter
    print('  rows', sorted(Counter(ys).items())[:40])
    print('  cols', sorted(Counter(xs).items())[:40])
