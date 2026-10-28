import sys,os
from PIL import Image
import numpy as np
os.chdir(sys.argv[1]); z=sys.argv[2]; vs=sys.argv[3].split(',')
def ld(p):
    im=Image.open(p).convert('RGB')
    if im.size[0]>460 and 'area8' not in p: im=im.crop((0,0,460,260))
    return np.asarray(im).astype(float)
def cnt(a,b):
    d=np.abs(a-b).max(-1); return int((d>8).sum())
ref=None
for v in vs:
    A=ld(f'area8_{v}_{z}.png'); A=A[:2080,:3680].reshape(260,8,460,8,3).mean((1,3))
    ims={'fem':ld(f'fem_{v}_{z}.ppm')}
    for b in ['chr','ff','wk']:
        ims[b]=ld(f'{b}_{v}_{z}.png')
    row=[v]+[f'{k}~area {cnt(im,A)}' for k,im in ims.items()]
    row+=[f'fem~{b} {cnt(ims["fem"],ims[b])}' for b in ['chr','ff','wk']]+[f'chr~ff {cnt(ims["chr"],ims["ff"])}', f'chr~wk {cnt(ims["chr"],ims["wk"])}']
    print(' | '.join(row))
    # left-edge profile of the first grey rect at its middle row
    y=120
    print('   row',y,'x=128..132:', {k: im[y,128:133,1].astype(int).tolist() for k,im in list(ims.items())+[('area',A)]})
