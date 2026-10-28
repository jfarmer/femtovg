"""Emulate femtovg's miter-joined open polyline (expand_stroke: butt caps, join pair p1 +- dmpos*w, strokeMask) and
compare the inner-corner pixels with the harness frame and the 8x area reference."""
import numpy as np, math, json, sys
sys.path.insert(0,'scripts')
from emu import raster
from red import L
FR=1.0
def orth(d): return np.array([d[1],-d[0]])
def strip(P,lw):
    hw=lw/2; w=hw+FR*0.5
    d=[(P[i+1]-P[i])/np.hypot(*(P[i+1]-P[i])) for i in range(len(P)-1)]
    V=[]
    # butt_cap_start(p0,p0,w,d=-0.5,aa=1)
    pp=P[0]+d[0]*0.5; dl=orth(d[0])
    V+= [(*(pp+dl*w-d[0]*FR),0.0),(*(pp-dl*w-d[0]*FR),1.0),(*(pp+dl*w),0.0),(*(pp-dl*w),1.0)]
    for i in range(1,len(P)-1):
        dm=(orth(d[i-1])+orth(d[i]))*0.5; s=min(600,1/np.dot(dm,dm)); dm=dm*s
        V+=[(*(P[i]+dm*w),0.0),(*(P[i]-dm*w),1.0)]
    pp=P[-1]-d[-1]*0.5; dl=orth(d[-1])
    V+=[(*(pp+dl*w),0.0),(*(pp-dl*w),1.0),(*(pp+dl*w+d[-1]*FR),0.0),(*(pp-dl*w+d[-1]*FR),1.0)]
    return np.array(V)
fv=L('png/mst4_v__r2_innerjoin_z1.png')[...,0].astype(float); idr=L('refs/id_v__r2_innerjoin_z1.png')[...,0].astype(float)
H,W=fv.shape; meta=json.load(open('r2_meta.json'))
E=np.zeros((H,W))
for ang,bx,by in meta:
    a=math.radians(ang)
    P=[np.array([130+bx+16,30+by]),np.array([130+bx,30+by]),np.array([130+bx+16*math.cos(a),30+by+16*math.sin(a)])]
    V=strip(P,1.27); e=raster(V,1.27,H,W); E=np.maximum(E,e)
E=np.rint(E*255)
m=np.zeros_like(fv,bool); m[30:230,130:330]=True; m&=(fv>8)|(E>8)
print('max |femtovg - emulation| over the strokes:',np.abs(fv-E)[m].max(),' px differing >2:',(np.abs(fv-E)[m]>2).sum(),'of',m.sum())
for ang in (45,61,90):
    rows=[]
    for an,bx,by in meta:
        if an!=ang: continue
        a=math.radians(ang); hw=0.635; d=hw/math.sin(a/2)
        x,y=int(130+bx+d*math.cos(a/2)),int(30+by+d*math.sin(a/2))
        rows.append((int(fv[y,x]),int(E[y,x]),int(idr[y,x])))
    print(ang,'inner corner (femtovg, emulated, area):',rows)
bad=np.argwhere(m&(np.abs(fv-E)>2))
import collections
c=collections.Counter()
for y,x in bad:
    best=None
    for ang,bx,by in meta:
        a=math.radians(ang)
        pts={'vertex':(130+bx,30+by),'end1':(130+bx+16,30+by),'end2':(130+bx+16*math.cos(a),30+by+16*math.sin(a))}
        for k,(px,py) in pts.items():
            dd=math.hypot(x+.5-px,y+.5-py)
            if best is None or dd<best[0]: best=(dd,k)
    c[(best[1], 'near' if best[0]<3 else 'far')]+=1
print(c)
