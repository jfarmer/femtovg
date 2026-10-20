"""Software model of femtovg's ConcaveFill on WGPU (stencil fan -> fringe strip where stencil==0, front faces only
-> cover quad where stencil!=0), from the vertices the library itself emits (cap tool, Void renderer patched to dump).
Returns per-pixel coverage layers so the over-ink can be split by pass."""
import re, subprocess, sys, numpy as np
S='/Users/matt/src/femtovg-wt/runs/busey/triage/gemini-3-1-pro-preview-verify/tips'
W,H=460,260
def capture(d, zoom=2, env=None):
    out=subprocess.run([f'{S}/cap/target/release/cap',str(zoom),d],capture_output=True,text=True,env=env).stdout
    lines=out.splitlines(); n=int(lines[0].split()[1])
    V=np.array([[float(t) for t in l.split()] for l in lines[1:1+n]])
    cmds=[l for l in lines[1+n:] if l.startswith('CMD')]
    fill=[c for c in cmds if 'ConcaveFill' in c or 'ConvexFill' in c]
    assert len(fill)==1, [c[:60] for c in cmds]
    c=fill[0]
    dr=re.findall(r'fill_verts: (?:Some\(\((\d+), (\d+)\)\)|None), stroke_verts: (?:Some\(\((\d+), (\d+)\)\)|None)',c)
    tv=re.search(r'triangles_verts: Some\(\((\d+), (\d+)\)\)',c)
    kind='concave' if 'ConcaveFill' in c else 'convex'
    return V, kind, [tuple(int(x) if x else None for x in t) for t in dr], (tuple(map(int,tv.groups())) if tv else None)
yy,xx=np.mgrid[0:H,0:W]; PX=xx+0.5; PY=yy+0.5
def raster_tri(a,b,c):
    """mask of pixel centres inside triangle abc, signed area, and barycentrics"""
    area=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    if area==0: return None
    x0=int(max(0,np.floor(min(a[0],b[0],c[0])))); x1=int(min(W,np.ceil(max(a[0],b[0],c[0]))+1))
    y0=int(max(0,np.floor(min(a[1],b[1],c[1])))); y1=int(min(H,np.ceil(max(a[1],b[1],c[1]))+1))
    if x0>=x1 or y0>=y1: return None
    px=PX[y0:y1,x0:x1]; py=PY[y0:y1,x0:x1]
    w0=((b[0]-px)*(c[1]-py)-(b[1]-py)*(c[0]-px))/area
    w1=((c[0]-px)*(a[1]-py)-(c[1]-py)*(a[0]-px))/area
    w2=1-w0-w1
    m=(w0>=0)&(w1>=0)&(w2>=0)
    return (y0,y1,x0,x1), m, area, (w0,w1,w2)
def render(V, kind, drawables, tv, fringe=True, cover=True, stencil_override=None, front=-1, cull=True):
    st=np.zeros((H,W),int)
    if kind=='concave':
        for f0,fn,s0,sn in drawables:
            if f0 is None: continue
            hub=V[f0]
            for i in range(f0+1,f0+fn-1):
                r=raster_tri(hub,V[i],V[i+1])
                if r is None: continue
                (y0,y1,x0,x1),m,area,_=r
                st[y0:y1,x0:x1]+=np.where(m,1 if area>0 else -1,0)
    if stencil_override is not None: st=stencil_override
    cov=np.zeros((H,W))           # composited coverage of black
    fr=np.zeros((H,W)); fr_hits=np.zeros((H,W),int); cv=np.zeros((H,W))
    if fringe:
        for f0,fn,s0,sn in drawables:
            if s0 is None: continue
            for k in range(sn-2):
                a,b,c=V[s0+k],V[s0+k+1],V[s0+k+2]
                r=raster_tri(a,b,c)
                if r is None: continue
                (y0,y1,x0,x1),m,area,(w0,w1,w2)=r
                # strip: odd triangles have their winding flipped for facing
                facing=area*(1 if k%2==0 else -1)
                if cull and facing*front<0: continue
                u=w0*a[2]+w1*b[2]+w2*c[2]; v=w0*a[3]+w1*b[3]+w2*c[3]
                al=np.minimum(1,(1-np.abs(u*2-1))*1.0)*np.minimum(1,v)
                ok=m&((st[y0:y1,x0:x1]==0) if kind=='concave' else True)
                al=np.where(ok,np.clip(al,0,1),0)
                sub=cov[y0:y1,x0:x1]; cov[y0:y1,x0:x1]=1-(1-sub)*(1-al)
                fr[y0:y1,x0:x1]=1-(1-fr[y0:y1,x0:x1])*(1-al); fr_hits[y0:y1,x0:x1]+=ok&(al>0)
    if kind=='convex':
        for f0,fn,s0,sn in drawables:
            hub=V[f0]
            for i in range(f0+1,f0+fn-1):
                r=raster_tri(hub,V[i],V[i+1])
                if r is None: continue
                (y0,y1,x0,x1),m,area,(w0,w1,w2)=r
                a,b,c=hub,V[i],V[i+1]
                u=w0*a[2]+w1*b[2]+w2*c[2]; v=w0*a[3]+w1*b[3]+w2*c[3]
                al=np.where(m,np.minimum(1,(1-np.abs(u*2-1)))*np.minimum(1,v),0)
                sub=cov[y0:y1,x0:x1]; cov[y0:y1,x0:x1]=1-(1-sub)*(1-al)
    elif cover and tv:
        t0,tn=tv
        for k in range(tn-2):
            a,b,c=V[t0+k],V[t0+k+1],V[t0+k+2]
            r=raster_tri(a,b,c)
            if r is None: continue
            (y0,y1,x0,x1),m,area,(w0,w1,w2)=r
            ok=m&(st[y0:y1,x0:x1]!=0)
            u=w0*a[2]+w1*b[2]+w2*c[2]; v=w0*a[3]+w1*b[3]+w2*c[3]
            al=np.where(ok,np.minimum(1,(1-np.abs(u*2-1)))*np.minimum(1,v),0)
            sub=cov[y0:y1,x0:x1]; cov[y0:y1,x0:x1]=1-(1-sub)*(1-al)
            cv[y0:y1,x0:x1]=np.maximum(cv[y0:y1,x0:x1],al)
            st[y0:y1,x0:x1]=np.where(m,0,st[y0:y1,x0:x1])
    return dict(cov=cov, fringe=fr, hits=fr_hits, cover=cv)
