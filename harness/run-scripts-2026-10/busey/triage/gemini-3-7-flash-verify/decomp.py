import numpy as np, re
from PIL import Image
from model import *
from hair import parse, cov, L
def contribs(E, pts):
    st=E['strip']; P=E['P']; n=len(P)
    # map strip triangles to source point index
    owner=[]
    for i in range(n):
        f=E['flags'][i]; cnt=8 if ('B' in f and 'IB' in f) else 2
        owner+=[i]*cnt
    owner+=[0,0]
    res=[]
    for (x,y) in pts:
        c=[]
        for k in range(len(st)-2):
            a,b,cc=st[k],st[k+1],st[k+2]; A,B,Cc=a[0],b[0],cc[0]
            den=(B[1]-Cc[1])*(A[0]-Cc[0])+(Cc[0]-B[0])*(A[1]-Cc[1])
            if abs(den)<1e-12: continue
            l1=((B[1]-Cc[1])*(x-Cc[0])+(Cc[0]-B[0])*(y-Cc[1]))/den
            l2=((Cc[1]-A[1])*(x-Cc[0])+(A[0]-Cc[0])*(y-Cc[1]))/den
            l3=1-l1-l2
            if min(l1,l2,l3)>=0:
                u=l1*a[1]+l2*b[1]+l3*cc[1]; cv=max(0,1-abs(2*u-1))
                if cv>0: c.append((owner[k+2] if k+2<len(owner) else 0, cv, u))
        res.append(c)
    return res
def inside(P, x, y):
    # nonzero winding of the true flattened polygon
    w=0; n=len(P)
    for i in range(n):
        x0,y0=P[i-1]; x1,y1=P[i]
        if y0<=y<y1 or y1<=y<y0:
            t=(y-y0)/(y1-y0); xi=x0+t*(x1-x0)
            if xi>x: w+= 1 if y1>y0 else -1
    return w!=0
for k in ['v00_crescent','v10_hairL','v12_cap']:
    d=re.search(r'<path d="([^"]+)"',open(f'svg/{k}.svg').read()).group(1)
    P,C=build(parse(d)); E=expand(P,C); R=raster(E,460,260)
    o=cov(L(f'png/mst2_t__{k}_z2.png')); i=cov(L(f'refs/id_t__{k}_z2.png'))
    oi=L(f'png/mst2_t__{k}_z2.png'); refs=[L(f'refs/{b}_t__{k}_z2.png') for b in ('chr','ff','wk')]
    all3=np.logical_and.reduce([np.abs(oi-r).max(2)>20 for r in refs]); all3[:,:31]=False; all3[:,429:]=False
    ys,xs=np.nonzero(all3)
    pts=[(x+0.5,y+0.5) for x,y in zip(xs,ys)]
    cs=contribs(E,pts)
    tot=ex=ex_single=0; multi=0; outside=0; ex_out=0; ex_multi=0
    for (x,y),c,yy,xx in zip(pts,cs,ys,xs):
        comb=1-np.prod([1-v for _,v,_ in c]) if c else 0
        sing=max([v for _,v,_ in c],default=0)
        e=comb-i[yy,xx]; ex+=e; ex_single+=max(0,sing-i[yy,xx])
        owners={ow for ow,_,_ in c}
        if len(c)>1: multi+=1; ex_multi+=e
        if not inside(E['P'],x,y): outside+=1; ex_out+=e
    print(f'{k:13s} all3 px {len(pts)}: >1 band triangle {multi} (excess {ex_multi:.1f} of {ex:.1f}); pixel centre outside the shape {outside} (excess {ex_out:.1f}); excess if only the strongest band counted {ex_single:.1f}')
