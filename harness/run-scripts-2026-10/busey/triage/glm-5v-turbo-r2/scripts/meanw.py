import re, sys, numpy as np
# mean width (2*area/perimeter) of every filled path in a PATH_DUMP log, in device px at z2 and hd
log=sys.argv[1]
P=lambda s: [float(v) for v in re.findall(r'x: ([-\d.e]+), y: ([-\d.e]+)', s)[0]] if False else [(float(a),float(b)) for a,b in re.findall(r'x: ([-\d.e]+), y: ([-\d.e]+)', s)]
paths=[]; cur=None
for line in open(log):
    if line.startswith('--- path'):
        cur={'hdr':line.strip()[9:70],'segs':[]}; paths.append(cur)
    elif cur is not None and line.startswith('  ') and ('To(' in line or 'Close' in line):
        cur['segs'].append(line.strip())
def flatten(segs,n=32):
    contours=[]; pts=[]
    for s in segs:
        if s.startswith('MoveTo'):
            if pts: contours.append(pts)
            pts=[P(s)[0]]
        elif s.startswith('LineTo'): pts.append(P(s)[0])
        elif s.startswith('QuadTo'):
            a,p=P(s); f=pts[-1]
            for i in range(1,n+1):
                t=i/n; pts.append(((1-t)**2*f[0]+2*(1-t)*t*a[0]+t*t*p[0],(1-t)**2*f[1]+2*(1-t)*t*a[1]+t*t*p[1]))
        elif s.startswith('CubicTo'):
            a,b,p=P(s); f=pts[-1]
            for i in range(1,n+1):
                t=i/n; u=1-t
                pts.append((u**3*f[0]+3*u*u*t*a[0]+3*u*t*t*b[0]+t**3*p[0],u**3*f[1]+3*u*u*t*a[1]+3*u*t*t*b[1]+t**3*p[1]))
        elif s.startswith('Close'):
            if pts: contours.append(pts); pts=[]
    if pts: contours.append(pts)
    return contours
def meanw(contours):
    A=0; Pm=0; convex=True
    for c in contours:
        c=np.array(c); d=np.roll(c,-1,0)
        A+=0.5*np.sum(c[:,0]*d[:,1]-d[:,0]*c[:,1]); Pm+=np.sum(np.hypot(*(d-c).T))
        e=d-c; e=e[np.hypot(*e.T)>1e-6]; cr=e[:,0]*np.roll(e[:,1],-1)-e[:,1]*np.roll(e[:,0],-1)
        if (cr>1e-9).any() and (cr<-1e-9).any(): convex=False
    return abs(A), Pm, 2*abs(A)/Pm if Pm else 0, convex
if __name__=='__main__':
    for i,p in enumerate(paths):
        if 'fill=None' in p['hdr'] or not p['segs']: continue
        c=flatten(p['segs']); A,Pm,w,cv=meanw(c)
        first=P(p['segs'][0])[0]
        z2=w*0.390625; hd=w*1080/1024; gate=1 if cv else 2
        print(f'{i:3d} start({first[0]:.0f},{first[1]:.0f}) w={w:6.2f}u z2={z2:5.2f}px{"*" if z2<gate else " "} hd={hd:5.2f}px{"*" if hd<gate else " "} convex={cv} {p["hdr"][:40]}')
