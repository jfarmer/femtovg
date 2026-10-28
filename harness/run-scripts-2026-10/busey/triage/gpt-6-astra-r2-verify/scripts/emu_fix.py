import numpy as np, math, sys
sys.path.insert(0,'scripts')
from emu import strip, raster, curve_div, TOL
from red import L
widths=[1.2,1.5,2.0,2.5,3.0,4.0,6.0]
fr='z1'; z=1
fv=L(f'png/mst4_v__r1_round_{fr}.png')[...,0].astype(float); idr=L(f'refs/id_v__r1_round_{fr}.png')[...,0].astype(float)
H,W=fv.shape
print('width ncap(master) sagitta_px | px>20 off id per 2 caps: master, ncap(R)+1, max(6,..), 64')
for i,w in enumerate(widths):
    i=[0.8,1.2,1.5,2.0,2.5,3.0,4.0,6.0].index(w); y=12.37+i*23.1; x0=14.29; x1=x0+55
    P0=np.array([130+x0,30+y]); P1=np.array([130+x1,30+y]); lw=w
    r=lw/2; R=r+0.5; nm=curve_div(r,math.pi,TOL)
    sag=R*(1-math.cos(math.pi/(2*(nm-1))))
    res=[]
    for nc in (None, curve_div(R,math.pi,TOL)+1, max(6,curve_div(R,math.pi,TOL)+1), 64):
        V,n=strip(P0,P1,lw,nc); e=np.rint(raster(V,lw,H,W)*255)
        Rr=int(lw/2+3); ys=slice(int(P0[1])-Rr,int(P0[1])+Rr+1)
        cnt=0
        for xs in (slice(int(P0[0])-Rr,int(P0[0])+1), slice(int(P1[0]),int(P1[0])+Rr+1)):
            cnt+=(np.abs(e[ys,xs]-idr[ys,xs])>20).sum()
        res.append(f'{cnt}(n={n})')
    print(f'{w:4.1f} {nm} {sag:.3f} | '+' '.join(res))
