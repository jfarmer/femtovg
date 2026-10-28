import numpy as np
def cub(p0,p1,p2,p3,n=4000):
    t=np.linspace(0,1,n)[:,None]
    P=[np.array(p,float) for p in (p0,p1,p2,p3)]
    return (1-t)**3*P[0]+3*(1-t)**2*t*P[1]+3*(1-t)*t**2*P[2]+t**3*P[3]
segs=[((250,600),(240,450),(270,200),(512,125)),((512,125),(754,200),(784,450),(774,600)),
((774,600),(760,550),(750,350),(730,280)),((730,280),(700,200),(620,160),(512,155)),
((512,155),(404,160),(324,200),(294,280)),((294,280),(274,350),(264,550),(250,600))]
pts=np.concatenate([cub(*s)[:-1] for s in segs])
P=np.vstack([pts,pts[:1]])
x,y=P[:,0],P[:,1]
A=0.5*np.sum(x[:-1]*y[1:]-x[1:]*y[:-1])
per=np.sum(np.hypot(np.diff(x),np.diff(y)))
print('net signed area',A,'perimeter',per,'mean width 2|A|/per',2*abs(A)/per)
# intersections between segment polylines
def inter(a,b):
    out=[]
    for i in range(len(a)-1):
        p,r=a[i],a[i+1]-a[i]
        q=b[:-1]; s=b[1:]-b[:-1]
        den=r[0]*s[:,1]-r[1]*s[:,0]
        with np.errstate(all='ignore'):
            t=((q[:,0]-p[0])*s[:,1]-(q[:,1]-p[1])*s[:,0])/den
            u=((q[:,0]-p[0])*r[1]-(q[:,1]-p[1])*r[0])/den
        k=np.where((t>=0)&(t<1)&(u>=0)&(u<1))[0]
        for j in k: out.append(p+t[j]*r)
    return out
C=[cub(*s,n=3000) for s in segs]
for i in range(6):
    for j in range(i+2,6):
        if (i,j)==(0,5): continue
        for X in inter(C[i],C[j]): print('seg',i,'x seg',j,X)
# winding-number area via raster at 8x per unit
from matplotlib.path import Path
pp=Path(P)
xs=np.arange(230,800,0.25)+0.125; ys=np.arange(110,620,0.25)+0.125
X,Y=np.meshgrid(xs,ys); g=np.c_[X.ravel(),Y.ravel()]
# winding number via ray crossing
def winding(px,py,poly):
    w=np.zeros(len(px),int)
    for k in range(len(poly)-1):
        x0,y0=poly[k];x1,y1=poly[k+1]
        up=(y0<=py)&(y1>py); dn=(y1<=py)&(y0>py)
        isl=(x1-x0)*(py-y0)-(px-x0)*(y1-y0)
        w+=np.where(up&(isl>0),1,0); w-=np.where(dn&(isl<0),1,0)
    return w
