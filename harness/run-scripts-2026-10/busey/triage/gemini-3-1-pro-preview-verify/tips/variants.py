import sys, numpy as np
sys.path.insert(0,'/Users/matt/src/femtovg-wt/runs/busey/triage/gemini-3-1-pro-preview-verify/tips')
import sim
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
S=sim.S
D={}
import re
for n in sys.argv[1:]:
    D[n]=re.search(r'<path d="([^"]*)"',open(f'{S}/svg/{n}.svg').read()).group(1).replace(',',' ')
def dev(u,v): return 30+0.390625*u, -70+0.390625*v
def fringe_layers(V,dr,st):
    """per strip triangle: (k, box, alpha) of the pixels it draws (stencil 0, front facing)"""
    out=[]
    for f0,fn,s0,sn in dr:
        for k in range(sn-2):
            a,b,c=V[s0+k],V[s0+k+1],V[s0+k+2]
            r=sim.raster_tri(a,b,c)
            if r is None: continue
            (y0,y1,x0,x1),m,area,(w0,w1,w2)=r
            if area*(1 if k%2==0 else -1)*-1<0: continue
            u=w0*a[2]+w1*b[2]+w2*c[2]; v=w0*a[3]+w1*b[3]+w2*c[3]
            al=np.clip(np.minimum(1,(1-np.abs(u*2-1)))*np.minimum(1,v),0,1)
            ok=m&(st[y0:y1,x0:x1]==0)
            out.append((k,(y0,y1,x0,x1),np.where(ok,al,0)))
    return out
for name in D:
    V,kind,dr,tv=sim.capture(D[name])
    full=sim.render(V,kind,dr,tv)
    fv=(255-L(f'{S}/png/mst2_t__{name}_z2.png').mean(2))/255
    assert np.abs(full['cov']-fv).max()<2/255, 'model off'
    # stencil as the library leaves it before the fringe
    st=np.zeros((sim.H,sim.W),int)
    for f0,fn,s0,sn in dr:
        for i in range(f0+1,f0+fn-1):
            r=sim.raster_tri(V[f0],V[i],V[i+1])
            if r is None: continue
            (y0,y1,x0,x1),m,area,_=r; st[y0:y1,x0:x1]+=np.where(m,1 if area>0 else -1,0)
    layers=fringe_layers(V,dr,st)
    union=np.zeros((sim.H,sim.W)); mx=np.zeros((sim.H,sim.W)); first=np.zeros((sim.H,sim.W)); taken=np.zeros((sim.H,sim.W),bool)
    ks=[[] for _ in range(sim.H*sim.W)]
    for k,(y0,y1,x0,x1),al in layers:
        union[y0:y1,x0:x1]=1-(1-union[y0:y1,x0:x1])*(1-al)
        mx[y0:y1,x0:x1]=np.maximum(mx[y0:y1,x0:x1],al)
        t=taken[y0:y1,x0:x1]; first[y0:y1,x0:x1]=np.where(~t&(al>0),al,first[y0:y1,x0:x1]); taken[y0:y1,x0:x1]|=al>0
        for (yy,xx) in zip(*np.nonzero(al>0)): ks[(y0+yy)*sim.W+x0+xx].append(k)
    cov=full['cov']; coverpart=cov-union*(st==0)   # cover pass pixels (stencil != 0)
    covmax=np.where(st!=0,cov,mx); covfirst=np.where(st!=0,cov,first)
    refs={b:L(f'{S}/refs/{b}_t__{name}_z2.png') for b in ('chr','ff','wk','id')}
    def agreed(c):
        o=np.repeat((255*(1-c))[...,None],3,2)
        return (np.abs(o-refs['chr']).max(2)>20)&(np.abs(o-refs['ff']).max(2)>20)&(np.abs(o-refs['wk']).max(2)>20)
    area=(255-refs['id'].mean(2))/255
    sn=dr[0][3]
    print(f'== {name}: agreed px  library {agreed(cov).sum()}  | fringe blended once per pixel (max) {agreed(covmax).sum()}  | first fringe triangle only {agreed(covfirst).sum()}')
    for (u,v) in {'inner':((290,720),(734,720)),'top':((300,250),(724,250))}.get(name,((280,725),(744,725))):
        x,y=dev(u,v); r=14; b=(slice(int(y-r),int(y+r)),slice(int(x-r),int(x+r)))
        multi=np.zeros((sim.H,sim.W),bool); opp=np.zeros((sim.H,sim.W),bool)
        for yy in range(b[0].start,b[0].stop):
            for xx in range(b[1].start,b[1].stop):
                kk=ks[yy*sim.W+xx]
                if len(kk)>=2:
                    multi[yy,xx]=True
                    d=max(kk)-min(kk); opp[yy,xx]= min(d, sn-d) > 6   # far apart in the strip = the other side of the sliver
        print(f'  tip ({u},{v}): ink library {cov[b].sum():5.1f}  max {covmax[b].sum():5.1f}  first {covfirst[b].sum():5.1f}  area {area[b].sum():5.1f};'
              f' multi-hit px {multi[b].sum()} (from both sides of the sliver {opp[b].sum()}), their ink {cov[b][multi[b]].sum():.1f} vs area {area[b][multi[b]].sum():.1f}')
