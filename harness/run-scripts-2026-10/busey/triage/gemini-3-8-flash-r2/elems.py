# elems.py FR x,y ... : the SVG elements (by line of svg/g00_orig.svg) whose outline/centreline passes nearest each frame pixel
import re, sys, numpy as np, math
from xy import s2f
src=open('svg/g00_orig.svg').read().split('\n')
def num(s): return [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?',s)]
def path_pts(d):
    toks=re.findall(r'[MLCQZ]|-?\d+(?:\.\d+)?',d); i=0; pts=[]; cur=None; start=None; cmd=None; subs=[]
    while i<len(toks):
        t=toks[i]
        if t in 'MLCQZ': cmd=t; i+=1
        if cmd=='Z':
            if cur is not None: pts.append(start); subs.append(pts); pts=[]; cur=start
            continue
        if cmd=='M':
            if pts: subs.append(pts)
            cur=(float(toks[i]),float(toks[i+1])); start=cur; pts=[cur]; i+=2; cmd='L'
        elif cmd=='L':
            cur=(float(toks[i]),float(toks[i+1])); pts.append(cur); i+=2
        elif cmd=='Q':
            c=(float(toks[i]),float(toks[i+1])); p=(float(toks[i+2]),float(toks[i+3])); i+=4
            for t_ in np.linspace(0,1,40)[1:]: pts.append(((1-t_)**2*cur[0]+2*(1-t_)*t_*c[0]+t_**2*p[0],(1-t_)**2*cur[1]+2*(1-t_)*t_*c[1]+t_**2*p[1]))
            cur=p
        elif cmd=='C':
            a=(float(toks[i]),float(toks[i+1])); b=(float(toks[i+2]),float(toks[i+3])); p=(float(toks[i+4]),float(toks[i+5])); i+=6
            for t_ in np.linspace(0,1,60)[1:]:
                s=1-t_; pts.append((s**3*cur[0]+3*s*s*t_*a[0]+3*s*t_*t_*b[0]+t_**3*p[0], s**3*cur[1]+3*s*s*t_*a[1]+3*s*t_*t_*b[1]+t_**3*p[1]))
            cur=p
        else: i+=1
    if pts: subs.append(pts)
    return subs
def ellipse(cx,cy,rx,ry): return [[(cx+rx*math.cos(a),cy+ry*math.sin(a)) for a in np.linspace(0,2*math.pi,200)]]
E=[]
for ln,l in enumerate(src,1):
    s=l.strip()
    m=re.match(r'<(path|circle|ellipse|line|polygon|rect)\b',s)
    if not m: continue
    tag=m.group(1); g=lambda a: (re.search(rf'\b{a}="([^"]*)"',s) or [None,None])[1]
    if tag=='path': subs=path_pts(g('d'))
    elif tag=='circle': subs=ellipse(float(g('cx')),float(g('cy')),float(g('r')),float(g('r')))
    elif tag=='ellipse': subs=ellipse(float(g('cx')),float(g('cy')),float(g('rx')),float(g('ry')))
    elif tag=='line': subs=[[(float(g('x1')),float(g('y1'))),(float(g('x2')),float(g('y2')))]]
    elif tag=='polygon': p=num(g('points')); subs=[list(zip(p[0::2],p[1::2]))+[(p[0],p[1])]]
    else: continue
    sw=g('stroke-width'); E.append((ln,tag,subs,float(sw) if sw else None,'filter' in s,s[:90]))
def segdist(p,a,b):
    a=np.asarray(a); b=np.asarray(b); d=b-a; L2=(d*d).sum(1); t=np.clip(((p-a)*d).sum(1)/np.maximum(L2,1e-12),0,1)
    q=a+t[:,None]*d; return np.hypot(*(q-p).T)
def near(fr,x,y,n=4):
    out=[]
    for ln,tag,subs,sw,flt,txt in E:
        best=1e9
        for sp in subs:
            P=np.array([s2f(px,py,fr) for px,py in sp])
            if len(P)<2: continue
            best=min(best,segdist(np.array([x+.5,y+.5]),P[:-1],P[1:]).min())
        out.append((best,ln,txt))
    out.sort(); return out[:n]
if __name__=='__main__':
    fr=sys.argv[1]
    for a in sys.argv[2:]:
        x,y=map(int,a.split(','))
        print(f'({x},{y}):', ' | '.join(f'L{ln} {d:.1f}px' for d,ln,_ in near(fr,x,y)))
