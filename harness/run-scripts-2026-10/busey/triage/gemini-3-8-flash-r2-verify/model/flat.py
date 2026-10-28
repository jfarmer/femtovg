import numpy as np, math
CHORD_SHIFT=0.375
def tess(curve, tol=0.125, dist=0.01, shift=True):
    pts=[]; pending=[]; piece=list(curve); depth=0; held=None; last=curve[:2]
    while True:
        x1,y1,x2,y2,x3,y3,x4,y4=piece
        dx=x4-x1; dy=y4-y1
        d2=(x2-x4)*dy-(y2-y4)*dx; d3=(x3-x4)*dy-(y3-y4)*dx; ch=dx*dx+dy*dy
        if (abs(d2)+abs(d3))**2 < tol*ch:
            bend=-CHORD_SHIFT*0.5*(d2+d3)/ch if ch>0 else 0.0
            if not shift: bend=0.0
            sh=(-dy*bend, dx*bend)
            if held is not None:
                at,prev=held
                mean=((prev[0]+sh[0])*.5,(prev[1]+sh[1])*.5)
                p=(at[0]+mean[0],at[1]+mean[1])
                if (p[0]-last[0])**2+(p[1]-last[1])**2>=dist*dist:
                    pts.append(p); last=p
            held=((x4,y4),sh)
        elif depth<10:
            x12=(x1+x2)*.5;y12=(y1+y2)*.5;x23=(x2+x3)*.5;y23=(y2+y3)*.5;x34=(x3+x4)*.5;y34=(y3+y4)*.5
            x123=(x12+x23)*.5;y123=(y12+y23)*.5;x234=(x23+x34)*.5;y234=(y23+y34)*.5
            x1234=(x123+x234)*.5;y1234=(y123+y234)*.5
            depth+=1; pending.append(([x1234,y1234,x234,y234,x34,y34,x4,y4],depth))
            piece=[x1,y1,x12,y12,x123,y123,x1234,y1234]; continue
        if not pending: break
        piece,depth=pending.pop()
    if held is not None: pts.append(held[0])
    return pts
def T(x,y,s=0.390625,ox=30,oy=-70): return (ox+s*x, oy+s*y)
def path_points(segs, shift=True, **kw):
    """segs: start point + list of cubic (c1,c2,p)"""
    start=T(*segs[0]); pts=[start]
    for c1,c2,p in segs[1]:
        a=pts[-1]; pts+=tess([*a,*T(*c1,**kw),*T(*c2,**kw),*T(*p,**kw)], shift=shift)
    if math.hypot(pts[-1][0]-pts[0][0],pts[-1][1]-pts[0][1])<0.01: pts.pop()
    return pts
CRES=((345,645),[((380,710),(430,762),(512,762)),((594,762),(644,710),(679,645)),((654,715),(594,772),(512,772)),((430,772),(370,715),(345,645))])
if __name__=='__main__':
    for sh in (True,False):
        P=path_points(CRES,shift=sh); print('shift',sh,'npoints',len(P))
        n=len(P)
        # points near left tip
        tip=P[0]
        print(' first points (C1 out of tip):', [(round(x,3),round(y,3)) for x,y in P[:4]])
        print(' last points (C2 into tip):', [(round(x,3),round(y,3)) for x,y in P[-3:]])
        # segment intersection test among all non-adjacent segments
        def inter(a,b,c,d):
            def cr(o,p,q): return (p[0]-o[0])*(q[1]-o[1])-(p[1]-o[1])*(q[0]-o[0])
            d1=cr(c,d,a); d2=cr(c,d,b); d3=cr(a,b,c); d4=cr(a,b,d)
            return (d1*d2<0) and (d3*d4<0)
        segs=[(P[i],P[(i+1)%n]) for i in range(n)]
        hits=[]
        for i in range(n):
            for j in range(i+2,n):
                if i==0 and j==n-1: continue
                if inter(*segs[i],*segs[j]): hits.append((i,j))
        print(' self-intersections:',hits[:10], len(hits))
        for i,j in hits[:6]: print('   ',segs[i],segs[j])
