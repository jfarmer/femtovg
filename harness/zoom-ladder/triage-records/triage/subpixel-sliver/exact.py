# Exact area coverage of the sliver triangle per pixel, compared with femtovg and the browsers.
import sys, numpy as np
from PIL import Image
def clip(poly, a, b, c):  # keep a*x+b*y <= c
    out=[]
    n=len(poly)
    for i in range(n):
        p=poly[i]; q=poly[(i+1)%n]
        fp=a*p[0]+b*p[1]-c; fq=a*q[0]+b*q[1]-c
        if fp<=0: out.append(p)
        if (fp<0)!=(fq<0) and fp!=fq:
            t=fp/(fp-fq); out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
    return out
def area(poly):
    s=0
    for i in range(len(poly)):
        x0,y0=poly[i]; x1,y1=poly[(i+1)%len(poly)]
        s+=x0*y1-x1*y0
    return abs(s)/2
def exact(z, W=460, H=260, dx=0.0, dy=0.0, tri=None):
    tri=tri or [(150,130),(310,130),(230,131)]
    tri=[(230+z*(x-230)+dx,130+z*(y-130)+dy) for x,y in tri]
    img=np.zeros((H,W))
    ys=range(int(np.floor(min(p[1] for p in tri))), int(np.ceil(max(p[1] for p in tri))))
    for y in ys:
        for x in range(W):
            p=clip(tri,1,0,x+1); p=clip(p,-1,0,-x); p=clip(p,0,1,y+1); p=clip(p,0,-1,-y)
            if len(p)>=3: img[y,x]=area(p)
    return img
if __name__=="__main__":
    import os
    K=sys.argv[1]; base=os.path.expanduser("~/src/femtovg-wt/runs/zoom")
    steps={"z1":"00","z125":"01","z15":"02","z175":"03","z2":"04","z3":"05","z4":"06","z075":"13","z05":"14","z033":"15","z025":"16"}
    for z,zs in [(1,"z1"),(2,"z2"),(3,"z3"),(4,"z4")]:
        e=exact(z)*255
        f=255-np.asarray(Image.open(f"{base}/png/zl_zm_svg/{K}/{steps[zs]}.png").convert("RGB")).astype(float)[:,:,0]
        row=[f"z{z}"]
        for b in ["chr","ff","wk"]:
            try: r=255-np.asarray(Image.open(f"{base}/fresh/refs/{b}_{K}_{zs}.png").convert("RGB")).astype(float)[:,:,0]
            except: continue
            row.append(f"{b}-exact: n>8={int((np.abs(r-e)>8).sum())} maxd={np.abs(r-e).max():.0f}; fv-{b} n>8={int((np.abs(f-r)>8).sum())}")
        row.append(f"fv-exact n>8={int((np.abs(f-e)>8).sum())} maxd={np.abs(f-e).max():.0f} sum fv={f.sum()/255:.1f} exact={e.sum()/255:.1f}")
        print(" | ".join(row))
