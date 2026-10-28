import sys; sys.path.insert(0,'.')
from shoecls import *
def hexc(h): return np.array([int(h[i:i+2],16) for i in (1,3,5)],float)
X,Y=np.meshgrid(np.arange(460)+0.5,np.arange(260)+0.5)
def contour_alpha(x0,y0,x1,y1):
    a=np.zeros_like(X)
    for s,t,lo,hi in [(Y-y0,X,x0,x1),(y1-Y,X,x0,x1),(X-x0,Y,y0,y1),(x1-X,Y,y0,y1)]:
        m=(s>=-0.5)&(s<=1.5)&(t>=lo+s)&(t<=hi-s)
        a=np.where(m,1-np.abs(s-0.5),a)
    return a
def sim(z,mode='fringe'):
    R=dev(z); img=np.full((260,460,3),255.0)
    for pi,(d,col) in enumerate(paths):
        C=hexc(col)
        rs=[r for r in R if r[0]==pi]
        if mode=='fringe':
            st=np.zeros_like(X,bool); keep=np.ones_like(X)
            for _,x0,y0,x1,y1 in rs:
                st|=(X>x0+0.5)&(X<x1-0.5)&(Y>y0+0.5)&(Y<y1-0.5)
                keep*=1-contour_alpha(x0,y0,x1,y1)
            a=np.where(st,1.0,1-keep)
        else: # exact area of union (squares don't overlap)
            a=np.zeros_like(X)
            for _,x0,y0,x1,y1 in rs:
                ox=np.clip(np.minimum(X+0.5,x1)-np.maximum(X-0.5,x0),0,None); oy=np.clip(np.minimum(Y+0.5,y1)-np.maximum(Y-0.5,y0),0,None)
                a+=ox*oy
            a=np.clip(a,0,1)
        img=C*a[...,None]+img*(1-a[...,None])
    return img
