import sys, numpy as np
sys.path.insert(0,'.')
from cmp import *
from disc import disc_cov
key=sys.argv[1]; X=float(sys.argv[2]); Y=float(sys.argv[3]); RR=float(sys.argv[4])
for z in [0.33,0.5,0.75,1,1.25,1.5,1.75,2,3,4]:
    cx=230+z*(X-100); cy=130+z*(Y-100); r=RR*z
    a=disc_cov(460,260,cx,cy,r)
    exR=np.round(255*(1-a)).astype(int)
    out=[]
    imgs={'fem':fem(key,z)}
    for b in ('chr','ff','wk'): imgs[b]=ref(b,key,z)
    for n,im in imgs.items():
        if im is None: out.append(f'{n}:-'); continue
        d=np.abs(im[...,0]-exR)
        out.append(f'{n}:{int((d>8).sum())}({d.max()})')
    print(z,' '.join(out))
