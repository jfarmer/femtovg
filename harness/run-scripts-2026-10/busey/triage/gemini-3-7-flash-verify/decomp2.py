import numpy as np, re, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from decomp import contribs, inside
    from hair import parse, cov, L
from model import *
for k in ['v00_crescent','v10_hairL','v12_cap']:
    d=re.search(r'<path d="([^"]+)"',open(f'svg/{k}.svg').read()).group(1)
    P,C=build(parse(d)); E=expand(P,C)
    o=cov(L(f'png/mst2_t__{k}_z2.png')); i=cov(L(f'refs/id_t__{k}_z2.png'))
    oi=L(f'png/mst2_t__{k}_z2.png'); refs=[L(f'refs/{b}_t__{k}_z2.png') for b in ('chr','ff','wk')]
    all3=np.logical_and.reduce([np.abs(oi-r).max(2)>20 for r in refs]); all3[:,:31]=False; all3[:,429:]=False
    ys,xs=np.nonzero(all3); pts=[(x+0.5,y+0.5) for x,y in zip(xs,ys)]
    cs=contribs(E,pts)
    far=0; far_ex=0; near_ex=0; inn=0
    for (x,y),c,yy,xx in zip(pts,cs,ys,xs):
        if not c: continue
        ow,v,u=max(c,key=lambda t:t[1])
        e=max(0,v-i[yy,xx])
        if not inside(E['P'],x,y):
            if u<0.75: far+=1; far_ex+=e
            else: near_ex+=e
        else: inn+=1
    print(f'{k:13s} outside px whose strongest band is the inner ramp of the far edge (u<0.75): {far}, its excess {far_ex:.1f}; outside px by own outer ramp: excess {near_ex:.1f}; inside px {inn}')
