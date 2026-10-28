import re, sys
sys.path.insert(0,'.')
from m import *
s=open(SVG[SHOE]).read()
paths=re.findall(r'<path d="([^"]+)"\s*fill="([^"]+)"',s)
rects=[]  # (path, x0,y0) in svg units, size 40.96
for i,(d,f) in enumerate(paths):
    for x,y in re.findall(r'M([\d.]+) ([\d.]+)',d):
        rects.append((i,float(x),float(y)))
def dev(z):
    sc=200/1024
    out=[]
    for i,x,y in rects:
        X0=230+(130+x*sc-230)*z; Y0=130+(30+y*sc-130)*z; S=40.96*sc*z
        out.append((i,X0,Y0,X0+S,Y0+S))
    return out
def classify(z):
    R=dev(z); out={}
    for py in range(260):
        for px in range(460):
            hits=[]; area=0
            for i,x0,y0,x1,y1 in R:
                ox=min(px+1,x1)-max(px,x0); oy=min(py+1,y1)-max(py,y0)
                if ox>1e-6 and oy>1e-6: hits.append(i); area+=ox*oy
            if not hits: continue
            same=len(hits)!=len(set(hits)); multi=len(set(hits))>1; empty=area<1-1e-6
            out[(px,py)]=(same,multi,empty)
    return out
