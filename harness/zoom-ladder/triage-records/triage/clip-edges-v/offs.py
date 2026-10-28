import sys, numpy as np
sys.path.insert(0,'.')
from cmp import *
from disc import disc_cov
k='corpus__wpt-feoffset-reftests__offset-under-clip-path-ref'
for z in [0.75,1,1.75,3,4]:
    cx=230; cy=130; r=50*z
    a=disc_cov(460,260,cx,cy,r,n=256)
    x0=230+z*(80-100); y0=130+z*(80-100); x1=230+z*60; y1=130+z*60
    # rect coverage per pixel
    xs=np.arange(460); ys=np.arange(260)
    cx_=np.clip(np.minimum(xs+1,x1)-np.maximum(xs,x0),0,1); cy_=np.clip(np.minimum(ys+1,y1)-np.maximum(ys,y0),0,1)
    a=a*np.outer(cy_,cx_)
    ex=np.stack([255*(1-a),255*(1-a)+128*a,255*(1-a)],-1)
    out=[]
    for n,im in [('mst',fem(k,z)),('area',load(f'png/area/{k}/{z}.png'))]+[(b,ref(b,k,z)) for b in ('chr','ff','wk')]:
        if im is None: continue
        d=np.abs(im[...,:3]-ex).max(-1); out.append(f'{n}:{int((d>8).sum())}({d.max():.0f})')
    im=load(f'png/area/{k}/{z}.png'); wk=ref('wk',k,z)
    d=np.abs(im[...,:3]-wk[...,:3]).max(-1)>8
    ys_,xs_=np.nonzero(d)
    print(z,x0,y0,' '.join(out), 'patched-vs-wk bad px x range',xs_.min() if len(xs_) else None, xs_.max() if len(xs_) else None,'y',ys_.min() if len(ys_) else None,ys_.max() if len(ys_) else None)
