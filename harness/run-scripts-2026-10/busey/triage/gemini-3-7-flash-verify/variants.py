import numpy as np, re, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from hair import parse, cov, L, img_of
import model
from model import *
def expand_half(P,C):
    """as expand, but the concave fringe is the convex half band: 0.5 px in (u=0.5) to 0.5 px out (u=1)"""
    E=expand(P,C); P2=E['P']; n=len(P2); d=np.roll(P2,-1,0)-P2; d=d/np.hypot(d[:,0],d[:,1])[:,None]; dm=E['dm']
    st=[]; lw=0.5; lu=0.5; rw=0.5; ru=1.0
    for i in range(n):
        p1=P2[i]; dl0=orth(d[i-1]); dl1=orth(d[i]); f=E['flags'][i]
        if 'B' in f and 'IB' in f:
            l0=p1+dl0*lw; l1=p1+dl1*lw
            st+=[(l0,lu),(p1-dl0*rw,ru),(l0,lu),(p1-dl0*rw,ru),(l1,lu),(p1-dl1*rw,ru),(l1,lu),(p1-dl1*rw,ru)]
        else: st+=[(p1+dm[i]*lw,lu),(p1-dm[i]*rw,ru)]
    st+=[st[0],st[1]]; E['strip']=st; return E
def raster_max(E,W,H):
    """fringes combined by max instead of source-over: no adding"""
    R=raster(E,W,H)
    ys,xs=np.mgrid[0:H,0:W]; px=xs+0.5; py=ys+0.5
    st=E['strip']; mx=np.zeros((H,W))
    st0=R['wind']==0
    for k in range(len(st)-2):
        a,b,c=st[k],st[k+1],st[k+2]; A,B,Cc=a[0],b[0],c[0]
        den=(B[1]-Cc[1])*(A[0]-Cc[0])+(Cc[0]-B[0])*(A[1]-Cc[1])
        if abs(den)<1e-12: continue
        l1=((B[1]-Cc[1])*(px-Cc[0])+(Cc[0]-B[0])*(py-Cc[1]))/den
        l2=((Cc[1]-A[1])*(px-Cc[0])+(A[0]-Cc[0])*(py-Cc[1]))/den
        l3=1-l1-l2; ins=(l1>=0)&(l2>=0)&(l3>=0)&st0
        u=l1*a[1]+l2*b[1]+l3*c[1]; cv=np.clip(1-np.abs(2*u-1),0,1)
        mx[ins]=np.maximum(mx[ins],cv[ins])
    return np.where(st0,mx,1.0)
box=np.s_[0:260,31:429]
for k in ['v00_crescent','v10_hairL','v12_cap','v03_dart','v05_dart_split']:
    s=open(f'svg/{k}.svg').read(); d=re.search(r'<path d="([^"]+)"',s).group(1)
    if 'C' in d: P,C=build(parse(d))
    else:
        t=[float(v) for v in re.findall(r'-?\d+\.?\d*',d)]; pts=list(zip(t[0::2],t[1::2]))
        P,C=build((pts[0],[(p,) for p in pts[1:]]+[(pts[0],)]))
    i=cov(L(f'refs/id_t__{k}_z2.png')); I=img_of(i)
    def score(c):
        off=np.abs(img_of(c)-I).max(2)>20; ex=np.clip(c-i,0,None)
        return f'{int(off[box].sum()):3d} px>20 vs area, over-ink {ex[box].sum():5.1f}'
    print(f'{k:15s} master: {score(raster(expand(P,C),460,260)["total"])} | no adding (max): {score(raster_max(expand(P,C),460,260))} | half band (no inner ramp): {score(raster(expand_half(P,C),460,260)["total"])}')
