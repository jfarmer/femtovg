import numpy as np, sys, os
from PIL import Image
H=os.path.expanduser('~/src/femtovg-wt/runs/zoom')
def c(p):
    a=np.asarray(Image.open(p).convert('RGBA')).astype(float); return (a[...,:3]*a[...,3:4]+255*(255-a[...,3:4]))/255
def n(a,b,t=8): return int((np.abs(a-b).max(-1)>t).sum())
def ink(a): return (255-a.mean(-1)).sum()
key,name,zz,step=sys.argv[1:5]
extra=sys.argv[5:]
ims={'fv':c(f'{H}/png/zl_zm_svg/{key}/{step}.png'),'area':c(f'area_{name}_{zz}.png'),'chr_mine':c(f'chr_{name}_{zz}.png')}
for br in ['chr','ff','wk']:
    p=f'{H}/fresh/refs/{br}_{key}_z{zz}.png'
    if os.path.exists(p): ims[br]=c(p)
for e in extra: ims[os.path.basename(e)]=c(e)
A=ims['area']
for k,v in ims.items():
    print(f'{k:24s} vs area {n(v,A):5d}  ink/area {ink(v)/ink(A):.4f}  vs chr {n(v,ims["chr"]):5d}')
