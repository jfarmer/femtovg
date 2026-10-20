"""Model of femtovg master's ConcaveFill (expand_fill + stencil/fringe/cover) at pixel centres."""
import numpy as np, math, sys
from flat import tess, T
def build(segs, shift=True, line_only=False):
    start=T(*segs[0]); pts=[(start,True)]
    for seg in segs[1]:
        a=pts[-1][0]
        if len(seg)==1:
            pts.append((T(*seg[0]),True)); continue
        c1,c2,p=seg
        f=tess([*a,*T(*c1),*T(*c2),*T(*p)], shift=shift)
        pts+=[(q,False) for q in f[:-1]]+[(f[-1],True)]
    if math.hypot(pts[-1][0][0]-pts[0][0][0],pts[-1][0][1]-pts[0][0][1])<0.01: pts.pop()
    P=np.array([p for p,_ in pts]); C=np.array([c for _,c in pts])
    return P,C
def orth(v): return np.array([v[1],-v[0]])
def expand(P,C,fringe=1.0,miter=2.4):
    n=len(P)
    area=0.5*sum((P[i][0]-P[i-1][0])*(P[i][1]+P[i-1][1]) for i in range(n))
    rev = area<0
    if rev: P=P[::-1].copy(); C=C[::-1].copy()
    d=np.roll(P,-1,0)-P; ln=np.hypot(d[:,0],d[:,1]); d=d/ln[:,None]
    dm=np.zeros_like(P); fl=[]
    for i in range(n):
        p0=i-1
        dl0=orth(d[p0]); dl1=orth(d[i]); m=(dl0+dl1)*0.5; r2=m@m
        if r2>1e-6: m=m*min(1/r2,600)
        dm[i]=m
        f=set()
        cross=d[p0][1]*d[i][0]-d[p0][0]*d[i][1]  # orth(a).b = a.y*b.x - a.x*b.y
        if cross>0: f.add('L')
        lim=max(min(ln[p0],ln[i])/fringe,1.01)
        if r2*lim*lim<1: f.add('IB')
        if C[i] and r2*miter*miter<1: f.add('B')
        fl.append(f)
    woff=0.5*fringe
    fill=[]
    for i in range(n):
        p0=i-1
        if 'B' in fl[i]:
            if 'L' in fl[i]: fill.append(P[i]+dm[i]*woff)
            else:
                fill.append(P[i]+orth(d[p0])*woff); fill.append(P[i]+orth(d[i])*woff)
        else: fill.append(P[i]+dm[i]*woff)
    fill=np.array(fill)
    if rev: fill=np.concatenate([fill[:1],fill[1:][::-1]])
    rw=fringe-woff; ru=1.0; lw=fringe+woff; lu=0.0
    st=[]
    for i in range(n):
        p0=i-1; p1=P[i]; dl0=orth(d[p0]); dl1=orth(d[i])
        if 'B' in fl[i] and 'IB' in fl[i]:
            if 'L' in fl[i]:
                l0=p1+dl0*lw; l1=p1+dl1*lw
                st+=[(l0,lu),(p1-dl0*rw,ru),(l0,lu),(p1-dl0*rw,ru),(l1,lu),(p1-dl1*rw,ru),(l1,lu),(p1-dl1*rw,ru)]
            else:
                r0=p1-dl0*rw; r1=p1-dl1*rw
                st+=[(p1+dl0*lw,lu),(r0,ru),(p1+dl0*lw,lu),(r0,ru),(p1+dl1*lw,lu),(r1,ru),(p1+dl1*lw,lu),(r1,ru)]
        else:
            st+=[(p1+dm[i]*lw,lu),(p1-dm[i]*rw,ru)]
    st+=[st[0],st[1]]
    return dict(P=P,fill=fill,strip=st,flags=fl,rev=rev,dm=dm)
def raster(E,W,H):
    ys,xs=np.mgrid[0:H,0:W]; px=xs+0.5; py=ys+0.5
    def bary(a,b,c):
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-12: return None,None
        l1=((b[1]-c[1])*(px-c[0])+(c[0]-b[0])*(py-c[1]))/den
        l2=((c[1]-a[1])*(px-c[0])+(a[0]-c[0])*(py-c[1]))/den
        l3=1-l1-l2
        inside=(l1>=0)&(l2>=0)&(l3>=0)
        return inside,(l1,l2,l3,den)
    wind=np.zeros((H,W),int)
    f=E['fill']; hub=f[0]
    for k in range(1,len(f)-1):
        ins,info=bary(hub,f[k],f[k+1])
        if ins is None: continue
        wind[ins]+= 1 if info[3]>0 else -1
    stencil0=(wind==0)
    trans=np.ones((H,W))  # product of (1-a) from fringes
    fr_only=np.ones((H,W))
    st=E['strip']
    for k in range(len(st)-2):
        a,b,c=st[k],st[k+1],st[k+2]
        ins,info=bary(a[0],b[0],c[0])
        if ins is None: continue
        l1,l2,l3,_=info
        u=l1*a[1]+l2*b[1]+l3*c[1]
        cov=np.clip(1-np.abs(2*u-1),0,1)
        m=ins&stencil0
        trans[m]*= (1-cov[m])
        fr_only[ins]*=(1-cov[ins])
    cover=(~stencil0).astype(float)
    total=1-(1-cover)*trans
    return dict(total=total,wind=wind,fringe=1-trans,cover=cover,fringe_nostencil=1-fr_only)
CRES=((345,645),[((380,710),(430,762),(512,762)),((594,762),(644,710),(679,645)),((654,715),(594,772),(512,772)),((430,772),(370,715),(345,645))])
if __name__=='__main__':
    from PIL import Image
    P,C=build(CRES); E=expand(P,C); R=raster(E,460,260)
    np.save('model_total.npy',R['total']); np.save('model_wind.npy',R['wind']); np.save('model_cover.npy',R['cover']); np.save('model_fringe.npy',R['fringe'])
    print('rev',E['rev'],'tip flags',E['flags'][0], 'n',len(P))
