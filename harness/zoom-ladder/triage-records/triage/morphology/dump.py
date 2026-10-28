import sys
from PIL import Image
import numpy as np
R='/Users/matt/src/femtovg-wt/runs/zoom'
key=sys.argv[1]; fr=sys.argv[2]; step=sys.argv[3]
ims={}
ims['fv']=np.asarray(Image.open(f'{R}/png/zl_zm_svg/{key}/{step}.png').convert('RGBA')).astype(int)
for b in ['chr','ff','wk']:
    try: ims[b]=np.asarray(Image.open(f'{R}/fresh/refs/{b}_{key}_{fr}.png').convert('RGBA')).astype(int)
    except Exception as e: pass
for b,a in ims.items(): print(b,a.shape)
fv=ims['fv']
for b in ['chr','ff','wk']:
    if b not in ims: continue
    d=np.abs(fv[...,:3]-ims[b][...,:3]).max(-1)
    ys,xs=np.nonzero(d>8)
    print(b,'n>8',len(ys), 'x',xs.min() if len(xs) else None, xs.max() if len(xs) else None,'y',ys.min() if len(ys) else None,ys.max() if len(ys) else None)
# print profile through the rect
y0=int(sys.argv[4]); x0=int(sys.argv[5])
print('row',y0, 'cols',x0-3,'..',x0+3)
for b,a in ims.items(): print(b,[tuple(a[y0,x,:3]) for x in range(x0-3,x0+4)])
print('col',x0,'rows',y0-3,'..',y0+3)
