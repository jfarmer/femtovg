import sys, numpy as np
sys.path.insert(0,'.')
from cmp import *
from disc import disc_cov
key='corpus__clip-probes__evenodd-clip-thin-ring'
yy,xx=np.mgrid[0:260,0:460]+0.5
for z in [0.5,0.75,1,1.5,1.75,2,3,4]:
    cx=230; cy=130-20*z; ro=40*5/3*z; ri=39.5*5/3*z
    a=disc_cov(460,260,cx,cy,ro,n=256)-disc_cov(460,260,cx,cy,ri,n=256)
    ex=255*(1-a)
    out=[]
    for n,im in [('mst',fem(key,z)),('r16',load(f'png/r16/ring16/{z}.png'))]+[(b,ref(b,key,z)) for b in ('chr','ff','wk')]:
        if im is None: continue
        d=np.abs(im[...,0]-ex); out.append(f'{n}:{int((d>8).sum())}({d.max():.0f})')
    print(z,' '.join(out))
