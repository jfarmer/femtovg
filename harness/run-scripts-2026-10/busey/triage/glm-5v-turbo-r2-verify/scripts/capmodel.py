# femtovg round-cap AA model (expand_stroke + shader stroke mask) vs exact area, horizontal stroke ending at x=cx going +x
import numpy as np, math
def tess_n(r, tol=0.125):
    da=math.acos(r/(r+tol))*2; return max(2, math.ceil(math.pi/da))
def fem_cov(px, py, cx, cy, w0, ncap, fringe=1.0):
    w=w0+fringe*0.5; mult=w/fringe
    # body (x<=cx): coverage by perpendicular distance
    d=np.abs(py-cy)
    body=np.clip((1-d/w)*mult,0,1)*(px<=cx)
    # cap fan: rim angles from -90..+90 deg around +x direction
    ang=np.linspace(-math.pi/2, math.pi/2, ncap)
    cap=np.zeros_like(px)
    for a0,a1 in zip(ang[:-1],ang[1:]):
        am=(a0+a1)/2; h=w*math.cos((a1-a0)/2)
        nx,ny=math.cos(am),math.sin(am)
        dx,dy=px-cx,py-cy
        # inside the wedge between a0 and a1?
        th=np.arctan2(dy,dx); inw=(th>=a0)&(th<=a1)&(dx>=0)
        xp=dx*nx+dy*ny
        c=np.clip((1-xp/h)*mult,0,1)
        cap=np.where(inw&(xp<=h),c,cap)
    return np.maximum(body,cap)
def exact_cov(X, Y, cx, cy, w0, ss=16):
    o=(np.arange(ss)+0.5)/ss-0.5; acc=np.zeros_like(X)
    for ox in o:
        for oy in o:
            x=X+ox; y=Y+oy
            inside=((x<=cx)&(np.abs(y-cy)<=w0))|(((x-cx)**2+(y-cy)**2)<=w0*w0)
            acc+=inside
    return acc/ss/ss
w0=2.5*1080/1024/2; print('hd half-width',w0,'ncap',tess_n(w0))
yy,xx=np.mgrid[0:8,0:10]; X=xx+0.5; Y=yy+0.5
worst={}
for n in [tess_n(w0), 6, 8, 16, 64]:
    errs=[]; inks=[]
    for fx in np.linspace(0,1,8,endpoint=False):
        for fy in np.linspace(0,1,8,endpoint=False):
            cx,cy=4+fx,4+fy
            f=fem_cov(X,Y,cx,cy,w0,n); e=exact_cov(X,Y,cx,cy,w0)
            m=X>cx-0.5   # cap region only
            errs.append(((f-e)*m).min()); inks.append(((f-e)*m).sum())
    print(f'ncap {n:3d}: worst cap pixel {min(errs)*188:6.1f} levels (188 = full lash/skin contrast), mean cap ink error {np.mean(inks):+.3f} px, worst {min(inks):+.3f}')
