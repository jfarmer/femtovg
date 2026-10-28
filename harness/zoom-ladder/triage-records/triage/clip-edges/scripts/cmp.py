import sys, numpy as np
from PIL import Image
import os
H=os.path.expanduser('~/src/femtovg-wt/runs/zoom')
ZOOMS=[1,1.25,1.5,1.75,2,3,4,3,2,1.75,1.5,1.25,1,0.75,0.5,0.33,0.25,0.33,0.5,0.75,1]
FR={1:'z1',1.25:'z125',1.5:'z15',1.75:'z175',2:'z2',3:'z3',4:'z4',0.75:'z075',0.5:'z05',0.33:'z033',0.25:'z025'}
def load(p):
    if not os.path.exists(p): return None
    return np.asarray(Image.open(p).convert('RGBA')).astype(np.int32)
def fem(key,z):
    if z==1: return load(f'{H}/png/zl_zm_svg/{key}/00.png')
    return load(f'{H}/png/zl_zm_svg/{key}/fresh_{FR[z]}.png')
def ref(b,key,z): return load(f'{H}/fresh/refs/{b}_{key}_{FR[z]}.png')
def diff(a,b): return np.abs(a[...,:3]-b[...,:3]).max(-1)
if __name__=='__main__':
    key=sys.argv[1]; z=float(sys.argv[2])
    z = int(z) if z==int(z) else z
    f=fem(key,z)
    for b in ['chr','ff','wk']:
        r=ref(b,key,z)
        if r is None: print(b,'none'); continue
        d=diff(f,r); ys,xs=np.nonzero(d>8)
        print(b, 'n>8', len(ys), 'max', d.max(), 'bbox', (xs.min(),ys.min(),xs.max(),ys.max()) if len(ys) else None)
        # signed: femtovg green-channel ink minus ref
        sd=(f[...,:3]-r[...,:3])
        m=d>8
        if m.any(): print('   mean signed diff per channel over bad px', sd[m].mean(0).round(1))
