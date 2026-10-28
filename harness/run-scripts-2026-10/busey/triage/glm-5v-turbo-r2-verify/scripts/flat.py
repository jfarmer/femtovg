# Port of femtovg 06243b80 PathCache::new (tesselate_bezier with CHORD_SHIFT) + calculate_joins for one contour
import numpy as np, sys
CORNER,LEFT,BEVEL,INNER=1,2,4,8
def tess(curve, tol, dist_tol, pts):
    pending=[]; piece=list(curve); depth=0; held=None; last=[curve[0],curve[1]]
    while True:
        x1,y1,x2,y2,x3,y3,x4,y4=piece
        dx=x4-x1; dy=y4-y1
        d2=(x2-x4)*dy-(y2-y4)*dx; d3=(x3-x4)*dy-(y3-y4)*dx; chord=dx*dx+dy*dy
        if (abs(d2)+abs(d3))**2 < tol*chord:
            bend=-0.375*0.5*(d2+d3)/chord if chord>0 else 0
            shift=[-dy*bend, dx*bend]
            prev=held; held=([x4,y4],shift)
            if prev is not None:
                at,ps=prev; mean=[(ps[0]+shift[0])/2,(ps[1]+shift[1])/2]
                p=[at[0]+mean[0],at[1]+mean[1]]
                if (p[0]-last[0])**2+(p[1]-last[1])**2>=dist_tol**2:
                    pts.append([p[0],p[1],0]); last=p
        elif depth<10:
            x12=(x1+x2)/2;y12=(y1+y2)/2;x23=(x2+x3)/2;y23=(y2+y3)/2;x34=(x3+x4)/2;y34=(y3+y4)/2
            x123=(x12+x23)/2;y123=(y12+y23)/2;x234=(x23+x34)/2;y234=(y23+y34)/2;x1234=(x123+x234)/2;y1234=(y123+y234)/2
            depth+=1; pending.append(([x1234,y1234,x234,y234,x34,y34,x4,y4],depth))
            piece=[x1,y1,x12,y12,x123,y123,x1234,y1234]; continue
        if not pending: break
        piece,depth=pending.pop()
    if held is not None: add(pts, held[0][0], held[0][1], CORNER, dist_tol)
def add(pts,x,y,f,dist_tol):
    if pts and (pts[-1][0]-x)**2+(pts[-1][1]-y)**2 < dist_tol**2: pts[-1][2]|=f; return
    pts.append([x,y,f])
def flatten(segs, T, tol=0.125, dist_tol=0.01):
    pts=[]
    tr=lambda x,y: (T[0]+T[2]*x, T[1]+T[2]*y)
    for s in segs:
        if s[0]=='M': add(pts,*tr(*s[1]),CORNER,dist_tol)
        elif s[0]=='C':
            a=tr(*s[1]);b=tr(*s[2]);p=tr(*s[3]); l=pts[-1]
            tess([l[0],l[1],a[0],a[1],b[0],b[1],p[0],p[1]],tol,dist_tol,pts)
        elif s[0]=='L': add(pts,*tr(*s[1]),CORNER,dist_tol)
    if (pts[-1][0]-pts[0][0])**2+(pts[-1][1]-pts[0][1])**2<dist_tol**2: pts.pop()
    return pts
def joins(pts, sw=1.0, miter=2.4):
    P=np.array([[p[0],p[1]] for p in pts]); n=len(P)
    d=np.roll(P,-1,0)-P; Ln=np.hypot(d[:,0],d[:,1]); D=d/Ln[:,None]
    orth=lambda v: np.array([v[1],-v[0]])
    out=[]
    for i in range(n):
        j=i-1
        dm=(orth(D[j])+orth(D[i]))*0.5; r2=dm@dm
        if r2>1e-6: dm=dm*min(1/r2,600)
        f=CORNER if pts[i][2]&CORNER else 0
        cross=D[j][1]*D[i][0]-D[j][0]*D[i][1]  # geometry.rs: orthogonal(self).dot(other)
        if cross>0: f|=LEFT
        lim=max(min(Ln[j],Ln[i])/sw,1.01)
        if r2*lim*lim<1: f|=INNER
        if (f&CORNER) and r2*miter*miter<1: f|=BEVEL
        out.append((P[i],f,dm,np.sqrt(r2),Ln[j],Ln[i]))
    return out
def area(pts):
    P=np.array([[p[0],p[1]] for p in pts]); x,y=P[:,0],P[:,1]
    return 0.5*np.sum(x*np.roll(y,-1)-np.roll(x,-1)*y)
