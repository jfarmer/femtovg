"""Emulate femtovg's round-cap stroke (PathCache::expand_stroke + round_cap_start/end + strokeMask) for a
horizontal segment, sampling the interpolated u at pixel centres, and compare with the harness frame and the
area reference. ncap override shows what finer caps would give."""
import numpy as np, math, sys
sys.path.insert(0,'scripts')
from red import L
TOL=0.125; FR=1.0
def curve_div(r,arc,tol): return max(2, math.ceil(arc/(2*math.acos(r/(r+tol)))))
def strip(p0,p1,lw,ncap=None):
    r=lw/2; nc=ncap or curve_div(r,math.pi,TOL); w=r+FR*0.5
    d=np.subtract(p1,p0); d=d/np.hypot(*d); dl=np.array([d[1],-d[0]])
    V=[]
    for i in range(nc):
        a=i/(nc-1)*math.pi; off=(math.cos(a)*(-dl)+math.sin(a)*(-d))*w
        V.append((*(np.add(p0,off)),0.0)); V.append((*p0,0.5))
    V.append((*(p0+dl*w),0.0)); V.append((*(p0-dl*w),1.0))
    V.append((*(np.add(p1,dl*w)),0.0)); V.append((*(np.subtract(p1,dl*w)),1.0))
    for i in range(nc):
        a=i/(nc-1)*math.pi; off=(math.cos(a)*(-dl)+math.sin(a)*(d))*w
        V.append((*p1,0.5)); V.append((*(np.add(p1,off)),0.0))
    return np.array(V,float),nc
def raster(V,lw,H,W):
    mult=(lw*0.5+FR*0.5)/FR
    out=np.zeros((H,W)); done=np.zeros((H,W),bool)
    yy,xx=np.mgrid[0:H,0:W]; px=xx+.5; py=yy+.5
    for k in range(len(V)-2):
        A,B,C=V[k],V[k+1],V[k+2]
        den=(B[1]-C[1])*(A[0]-C[0])+(C[0]-B[0])*(A[1]-C[1])
        if abs(den)<1e-9: continue
        l1=((B[1]-C[1])*(px-C[0])+(C[0]-B[0])*(py-C[1]))/den
        l2=((C[1]-A[1])*(px-C[0])+(A[0]-C[0])*(py-C[1]))/den
        l3=1-l1-l2
        inside=(l1>=-1e-7)&(l2>=-1e-7)&(l3>=-1e-7)&~done
        u=l1*A[2]+l2*B[2]+l3*C[2]
        cov=np.minimum(1,(1-np.abs(u*2-1))*mult)
        out[inside]=cov[inside]; done|=inside
    return out
def main():
  pass
widths=[0.8,1.2,1.5,2.0,2.5,3.0,4.0,6.0]
for fr in (['z1','z2'] if __name__=='__main__' else []):
    z=int(fr[1:])
    fv=L(f'png/mst4_v__r1_round_{fr}.png')[...,0].astype(float)
    idr=L(f'refs/id_v__r1_round_{fr}.png')[...,0].astype(float)
    H,W=fv.shape
    for i,w in enumerate(widths):
        y=12.37+i*23.1; x0=14.29; x1=x0+55
        P0=np.array([230+z*(130+x0-230),130+z*(30+y-130)]); P1=np.array([230+z*(130+x1-230),P0[1]])
        if P0[1]<4 or P0[1]>H-4: continue
        lw=w*z
        if lw<1: continue  # sub-fringe strokes get alpha scaling; skip
        V,nc=strip(P0,P1,lw); e=raster(V,lw,H,W)*255
        V2,_=strip(P0,P1,lw,64); e2=raster(V2,lw,H,W)*255
        R=int(lw/2+3)
        ys=slice(int(P0[1])-R,int(P0[1])+R+1)
        for name,xs in (('start',slice(int(P0[0])-R,int(P0[0])+1)),('end',slice(int(P1[0]),int(P1[0])+R+1))):
            a=fv[ys,xs]; b=e[ys,xs]; c=e2[ys,xs]; d=idr[ys,xs]
            print(f'{fr} w={lw:4.1f}px ncap={nc} {name:5s}: max|femtovg-emu(ncap)|={np.abs(a-np.rint(b)).max():4.0f}  ink femtovg/id={a.sum()/d.sum():.3f} emu(ncap)/id={b.sum()/d.sum():.3f} emu(64)/id={c.sum()/d.sum():.3f}  px>20 off id: femtovg {(np.abs(a-d)>20).sum()} emu64 {(np.abs(c-d)>20).sum()}')
