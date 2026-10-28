# Re-implements femtovg master's convex fill (PathCache::calculate_joins + expand_fill,
# src/path/cache.rs) for the sliver triangle and rasterizes it the way the GPU does
# (pixel-centre sampling, fill fan then fringe strip, source-over), to compare with
# the harness frame.  Options: clamp (the 600 cap on 1/dmr2), woff.
import sys, math, numpy as np
def V(x,y): return np.array([x,y],dtype=np.float64)
def orth(v): return V(v[1],-v[0])
def cross(a,b): return a[1]*b[0]-a[0]*b[1]  # femtovg: orthogonal(a).dot(b)
def xstd(a,b): return a[0]*b[1]-a[1]*b[0]
def build(pts, fringe=1.0, miter_limit=2.4, clamp=600.0, f32=True, rule='any'):
    n=len(pts)
    P=[dict(pos=V(*p)) for p in pts]
    # polygon_area as femtovg: sum (x1-x0)(y1+y0) over (prev,cur)
    area=0
    for i in range(n):
        p0=P[i-1]['pos']; p1=P[i]['pos']; area+=(p1[0]-p0[0])*(p1[1]+p0[1])
    if area*0.5<0: P=P[::-1]
    for i in range(n):
        d=P[(i+1)%n]['pos']-P[i]['pos']; L=math.hypot(*d); P[i]['dpos']=d/L; P[i]['len']=L
    inv=1/fringe
    for i in range(n):
        p0=P[i-1]; p1=P[i]
        dl0=orth(p0['dpos']); dl1=orth(p1['dpos'])
        dm=(dl0+dl1)*0.5; dmr2=dm@dm
        if dmr2>1e-6: dm=dm*min(1/dmr2,clamp)
        p1['dm']=dm; p1['dmr2']=dmr2
        fl=set(['CORNER'])
        if cross(p0['dpos'],p1['dpos'])>0: fl.add('LEFT')
        limit=max(min(p0['len'],p1['len'])*inv,1.01)
        if dmr2*limit*limit<1: fl.add('INNERBEVEL')
        if dmr2*miter_limit**2<1: fl.add('BEVEL')
        p1['fl']=fl
    woff=0.5*fringe
    fill=[]
    for i in range(n):
        p0=P[i-1]; p1=P[i]
        if 'BEVEL' in p1['fl']:
            if 'LEFT' in p1['fl']: fill.append((p1['pos']+p1['dm']*woff,0.5))
            else:
                fill.append((p1['pos']+orth(p0['dpos'])*woff,0.5)); fill.append((p1['pos']+orth(p1['dpos'])*woff,0.5))
        else: fill.append((p1['pos']+p1['dm']*woff,0.5))
    lw,lu,rw,ru=woff,0.5,fringe-woff,1.0
    strip=[]
    for i in range(n):
        p0=P[i-1]; p1=P[i]
        if (p1['fl'] & {'BEVEL','INNERBEVEL'}) if rule=='any' else ({'BEVEL','INNERBEVEL'} <= p1['fl']):
            dl0=orth(p0['dpos']); dl1=orth(p1['dpos'])
            assert 'LEFT' in p1['fl']
            if 'INNERBEVEL' in p1['fl']: l0=p1['pos']+dl0*lw; l1=p1['pos']+dl1*lw
            else: l0=l1=p1['pos']+p1['dm']*lw
            strip += [(l0,lu),(p1['pos']-dl0*rw,ru)]
            if 'BEVEL' in p1['fl']:
                strip += [(l0,lu),(p1['pos']-dl0*rw,ru),(l1,lu),(p1['pos']-dl1*rw,ru)]
            else:
                r0=p1['pos']-p1['dm']*rw
                strip += [(p1['pos'],0.5),(p1['pos']-dl0*rw,ru),(r0,ru),(r0,ru),(p1['pos'],0.5),(p1['pos']-dl1*rw,ru)]
            strip += [(l1,lu),(p1['pos']-dl1*rw,ru)]
        else:
            strip += [(p1['pos']+p1['dm']*lw,lu),(p1['pos']-p1['dm']*rw,ru)]
    strip += [strip[0],strip[1]]
    return P,fill,strip
def raster(img, tris):
    H,W=img.shape
    for (a,ua),(b,ub),(c,uc) in tris:
        den=xstd(b-a,c-a)
        if abs(den)<1e-12: continue
        x0=max(0,int(math.floor(min(a[0],b[0],c[0])))); x1=min(W-1,int(math.ceil(max(a[0],b[0],c[0]))))
        y0=max(0,int(math.floor(min(a[1],b[1],c[1])))); y1=min(H-1,int(math.ceil(max(a[1],b[1],c[1]))))
        if x1<x0 or y1<y0: continue
        xs=np.arange(x0,x1+1)+0.5+1e-7; ys=np.arange(y0,y1+1)+0.5+1e-13  # top-left fill rule tie-break
        X,Y=np.meshgrid(xs,ys)
        w0=((b[0]-X)*(c[1]-Y)-(b[1]-Y)*(c[0]-X))/den
        w1=((c[0]-X)*(a[1]-Y)-(c[1]-Y)*(a[0]-X))/den
        w2=1-w0-w1
        inside=(w0>=0)&(w1>=0)&(w2>=0)
        u=w0*ua+w1*ub+w2*uc
        m=np.clip(1-np.abs(u*2-1),0,1)
        sub=img[y0:y1+1,x0:x1+1]
        sub[inside]=sub[inside]+m[inside]*(1-sub[inside])
def render(z, W=460, H=260, dx=0.0, dy=0.0, tri=None, **kw):
    tri=tri or [(150,130),(310,130),(230,131)]
    tri=[(230+z*(x-230)+dx,130+z*(y-130)+dy) for x,y in tri]
    P,fill,strip=build(tri,**kw)
    img=np.zeros((H,W))
    raster(img,[(fill[0],fill[i],fill[i+1]) for i in range(1,len(fill)-1)])
    raster(img,[(strip[i],strip[i+1],strip[i+2]) for i in range(len(strip)-2)])
    return img,P,fill,strip
if __name__=="__main__":
    from PIL import Image
    import os
    K=sys.argv[1]; base=os.path.expanduser("~/src/femtovg-wt/runs/zoom")
    sys.path.insert(0,os.path.dirname(__file__)); from exact import exact
    for z,step in [(3,"05"),(4,"06")]:
        img,P,fill,strip=render(z)
        f=255-np.asarray(Image.open(f"{base}/png/zl_zm_svg/{K}/{step}.png").convert("RGB")).astype(float)[:,:,0]
        s=np.round(img*255)
        print(f"z{z}: points", [(tuple(np.round(p['pos'],3)), sorted(p['fl']), np.round(p['dm'],3).tolist(), f"{p['dmr2']:.3g}") for p in P])
        print("  fill verts", [tuple(np.round(v,3)) for v,_ in fill])
        print(f"  sim vs harness: maxd={np.abs(s-f).max():.0f} n>2={(np.abs(s-f)>2).sum()} ; sim vs exact n>8={(np.abs(s-exact(z)*255)>8).sum()}")
