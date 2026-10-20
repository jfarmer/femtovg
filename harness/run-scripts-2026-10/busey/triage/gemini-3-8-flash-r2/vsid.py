import numpy as np, sys
from PIL import Image
from measure import REG
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
K='corpus__buseybench__gemini-3-8-flash'; R='/Users/matt/src/femtovg-wt/runs/busey/refs'
for fr in ('z2','hd'):
    o=L(f'png/mst4_t__g00_orig_{fr}.png'); refs=[L(f'{R}/{x}_{K}_{fr}.png') for x in ('chr','ff','wk')]; idr=L(f'{R}/id_{K}_{fr}.png')
    off=[np.abs(o-r).max(2)>20 for r in refs]; all3=off[0]&off[1]&off[2]
    near=np.abs(o-idr).max(2)<=20
    bmin=np.min([np.abs(r-idr).max(2) for r in refs],axis=0)
    cov=np.zeros(all3.shape,bool)
    print(fr,'all3',all3.sum(),'of which femtovg within 20 of the area ref',(all3&near).sum())
    for n,boxes in REG[fr].items():
        m=np.zeros(all3.shape,bool)
        for b in boxes: m[b[1]:b[3],b[0]:b[2]]=True
        cov|=m
        print('  ',n,(all3&m).sum(),'near area',(all3&m&near).sum(),' (all3 px where femtovg is closer to area than every browser:',(all3&m&(np.abs(o-idr).max(2)<bmin)).sum(),')')
    m=~cov
    ys,xs=np.nonzero(all3&m)
    print('   rest',(all3&m).sum(),'near area',(all3&m&near).sum())
    for x,y in zip(xs,ys): print(f'     ({x},{y}) fv-id {int(np.abs(o[y,x]-idr[y,x]).max())} best browser-id {int(bmin[y,x])}')
