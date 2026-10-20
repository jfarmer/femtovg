import sys, numpy as np
from PIL import Image
sys.path.insert(0,'/Users/matt/src/femtovg-wt/runs/busey/triage/gemini-3-1-pro-preview-verify/tips')
import sim
from validate import D, L
S=sim.S
def dev(u,v): return 30+0.390625*u, -70+0.390625*v
TIPS={'lip':((280,725),(744,725)),'inner':((290,720),(734,720)),'wedge':((280,725),(744,725))}
def stencil(V,dr):
    st=np.zeros((sim.H,sim.W),int)
    for f0,fn,s0,sn in dr:
        hub=V[f0]
        for i in range(f0+1,f0+fn-1):
            r=sim.raster_tri(hub,V[i],V[i+1])
            if r is None: continue
            (y0,y1,x0,x1),m,area,_=r
            st[y0:y1,x0:x1]+=np.where(m,1 if area>0 else -1,0)
    return st
for name in sys.argv[1:]:
    V,kind,dr,tv=sim.capture(D[name])
    full=sim.render(V,kind,dr,tv)
    st=stencil(V,dr)
    body=np.sign(np.median(st[st!=0]))  # sign of the shape's interior winding
    area=(255-L(f'{S}/refs/id_t__{name}_z2.png').mean(2))/255
    chr_=(255-L(f'{S}/refs/chr_t__{name}_z2.png').mean(2))/255
    print(f'== {name}: interior winding sign {body:+.0f}; pixels with inverted winding {(np.sign(st)==-body).sum()}')
    for (u,v) in TIPS[name]:
        x,y=dev(u,v); r=14
        b=(slice(int(y-r),int(y+r)),slice(int(x-r),int(x+r)))
        inv=(np.sign(st)==-body)[b]; pos=(np.sign(st)==body)[b]
        cov=full['cov'][b]; a=area[b]
        print(f' tip ({u},{v}) dev ({x:.1f},{y:.1f}): femtovg ink {cov.sum():5.1f}  area {a.sum():5.1f}  chromium {chr_[b].sum():5.1f}  excess {cov.sum()-a.sum():+5.1f}')
        print(f'   cover pass: {pos.sum()} px of interior winding (ink {cov[pos].sum():.1f}, area there {a[pos].sum():.1f}), {inv.sum()} px of INVERTED winding (ink {cov[inv].sum():.1f}, area there {a[inv].sum():.1f})')
        fr=~(pos|inv)
        hits=full['hits'][b]
        print(f'   fringe pass (stencil 0): ink {cov[fr].sum():.1f}, area there {a[fr].sum():.1f}; px hit by >=2 fringe tris {((hits>=2)&fr).sum()} (ink {cov[fr&(hits>=2)].sum():.1f}, area {a[fr&(hits>=2)].sum():.1f})')
