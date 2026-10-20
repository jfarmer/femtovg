import sys, numpy as np
from PIL import Image
import os
H=os.path.expanduser('~/src/femtovg-wt/runs/zoom')
def load(p):
    im=Image.open(p).convert('RGBA'); a=np.asarray(im).astype(np.int32)
    return a
def comp(a):
    # composite on white
    rgb=a[...,:3]; al=a[...,3:4]
    return (rgb*al+255*(255-al))//255
def diff(a,b,t=8):
    d=np.abs(comp(a)-comp(b)).max(-1)
    return d
key=sys.argv[1]; step=sys.argv[2]; fr=sys.argv[3]
fv=load(f'{H}/png/zl_zm_svg/{key}/{step}.png')
out={}
for br in ['chr','ff','wk']:
    p=f'{H}/fresh/refs/{br}_{key}_{fr}.png'
    if not os.path.exists(p): continue
    b=load(p)
    d=diff(fv,b)
    ys,xs=np.nonzero(d>8)
    print(br, (d>8).sum(), 'max',d.max(), 'bbox', (xs.min(),ys.min(),xs.max(),ys.max()) if len(xs) else None, 'mean signed lum fv-br', (comp(fv).mean(-1)-comp(b).mean(-1))[d>8].mean() if len(xs) else 0)
    out[br]=b
bs=list(out)
for i in range(len(bs)):
    for j in range(i+1,len(bs)):
        d=diff(out[bs[i]],out[bs[j]]); print(bs[i],bs[j],(d>8).sum(),d.max())
