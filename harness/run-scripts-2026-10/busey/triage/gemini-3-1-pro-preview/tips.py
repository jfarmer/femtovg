import re, math, numpy as np
from cmp import get
S='/Users/matt/src/femtovg-wt/runs/busey/triage/gemini-3-1-pro-preview'
src=open(f'{S}/svg/orig.svg').read()
s=200/1024
def fr(u,v): return 230+2*(130+u*s-230), 130+2*(30+v*s-130)
tips=[]
for m in re.finditer(r'<path d="([^"]*)"([^>]*)>', src):
    d, rest = m.group(1), m.group(2)
    if 'fill="none"' in rest: continue
    toks=re.findall(r'[MLCQZ]|-?[\d.]+', d.replace(',',' '))
    segs=[]; i=0; cur=None; start=None; cmd=None
    while i<len(toks):
        t=toks[i]
        if t in 'MLCQZ': cmd=t; i+=1
        if cmd=='M': cur=start=(float(toks[i]),float(toks[i+1])); i+=2; cmd='L'; continue
        if cmd=='Z':
            if cur!=start: segs.append((cur,cur,start,start))
            break
        n={'L':1,'Q':2,'C':3}[cmd]
        pts=[(float(toks[i+2*k]),float(toks[i+2*k+1])) for k in range(n)]; i+=2*n
        if cmd=='L': segs.append((cur,cur,pts[0],pts[0]))
        elif cmd=='Q': segs.append((cur,pts[0],pts[0],pts[1]))
        else: segs.append((cur,pts[0],pts[1],pts[2]))
        cur=pts[-1]
    if len(segs)<2: continue
    for k in range(len(segs)):
        a=segs[k-1]; b=segs[k]
        # incoming tangent at end of a, outgoing tangent at start of b
        p=a[3]
        tin=next((np.subtract(p,q) for q in (a[2],a[1],a[0]) if tuple(q)!=tuple(p)),None)
        tout=next((np.subtract(q,p) for q in (b[1],b[2],b[3]) if tuple(q)!=tuple(p)),None)
        if tin is None or tout is None: continue
        c=np.dot(-tin,tout)/np.linalg.norm(tin)/np.linalg.norm(tout)
        ang=math.degrees(math.acos(max(-1,min(1,c))))
        if ang<35: tips.append((fr(*p),ang,d[:30]))
if __name__=='__main__':
    print(len(tips),'acute vertices')
    H,W=260,460
    yy,xx=np.mgrid[0:H,0:W]
    near=np.zeros((H,W),bool)
    for (x,y),ang,dd in tips:
        if -5<x<W+5 and -5<y<H+5: near|=(xx+0.5-x)**2+(yy+0.5-y)**2<=3.5**2
    for b in ('mst2','lsm'):
        o,r,a,sp=get('orig',b); ag=a&~sp
        print(b,'agreed',ag.sum(),'within 3.5px of an acute vertex',(ag&near).sum(),'area share of frame %.3f%%'%(100*near.mean()))
    np.save(f'{S}/near_tips.npy',near)
