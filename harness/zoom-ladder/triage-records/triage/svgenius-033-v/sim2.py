import sys; sys.path.insert(0,'.')
from sim import *
def tri_raster(acc, a,b,c, ua,ub,uc):
    # sample pixel centres inside triangle; composite alpha src-over into acc (keep = prod(1-alpha))
    xs=[a[0],b[0],c[0]]; ys=[a[1],b[1],c[1]]
    x0=max(int(np.floor(min(xs)-0.5)),0); x1=min(int(np.ceil(max(xs)+0.5)),459)
    y0=max(int(np.floor(min(ys)-0.5)),0); y1=min(int(np.ceil(max(ys)+0.5)),259)
    if x1<x0 or y1<y0: return
    Xs=X[y0:y1+1,x0:x1+1]; Ys=Y[y0:y1+1,x0:x1+1]
    det=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(det)<1e-12: return
    l1=((b[1]-c[1])*(Xs-c[0])+(c[0]-b[0])*(Ys-c[1]))/det
    l2=((c[1]-a[1])*(Xs-c[0])+(a[0]-c[0])*(Ys-c[1]))/det
    l3=1-l1-l2
    m=(l1>=0)&(l2>=0)&(l3>=0)
    u=l1*ua+l2*ub+l3*uc
    al=np.clip(1-np.abs(2*u-1),0,1)
    acc[y0:y1+1,x0:x1+1]*=np.where(m,1-al,1)
def square_strip(acc,x0,y0,x1,y1,fold=True):
    # reversed contour order BL,BR,TR,TL with inward miter dm
    pts=[((x0,y1),(1,-1)),((x1,y1),(-1,-1)),((x1,y0),(-1,1)),((x0,y0),(1,1))]
    V=[]
    for (px,py),(dx,dy) in pts:
        V.append(((px+dx*1.5,py+dy*1.5),0.0)); V.append(((px-dx*0.5,py-dy*0.5),1.0))
    V+=V[:2]
    for i in range(len(V)-2):
        (a,ua),(b,ub),(c,uc)=V[i],V[i+1],V[i+2]
        tri_raster(acc,a,b,c,ua,ub,uc)
def sim2(z):
    R=dev(z); img=np.full((260,460,3),255.0)
    for pi,(d,col) in enumerate(paths):
        C=hexc(col); rs=[r for r in R if r[0]==pi]
        if len(rs)==1:
            _,x0,y0,x1,y1=rs[0]
            # convex fill: exact clamp(0.5+s) per axis (half fringe + fan)
            ax=np.clip(np.minimum(X-x0,x1-X)+0.5,0,1); ay=np.clip(np.minimum(Y-y0,y1-Y)+0.5,0,1)
            a=np.minimum(ax,ay)
        else:
            st=np.zeros_like(X,bool); keep=np.ones_like(X)
            for _,x0,y0,x1,y1 in rs:
                st|=(X>=x0+0.5)&(X<x1-0.5)&(Y>=y0+0.5)&(Y<y1-0.5)
                square_strip(keep,x0,y0,x1,y1)
            a=np.where(st,1.0,1-keep)
        img=C*a[...,None]+img*(1-a[...,None])
    return img
