import sys, re, os, numpy as np
sys.path.insert(0,'.')
import sim
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
S=sim.S
def dev(u,v): return 30+0.390625*u, -70+0.390625*v
for name in sys.argv[1:]:
    d=re.search(r'<path d="([^"]*)"',open(f'{S}/svg/{name}.svg').read()).group(1).replace(',',' ')
    refs={b:L(f'{S}/refs/{b}_t__{name}_z2.png') for b in ('chr','ff','wk','id')}
    area=(255-refs['id'].mean(2))/255
    for tag,env in (('library',None),('no inner bevel',{**os.environ,'FV_NO_INNERBEVEL':'1'})):
        V,kind,dr,tv=sim.capture(d,env=env); c=sim.render(V,kind,dr,tv)['cov']
        o=np.repeat((255*(1-c))[...,None],3,2)
        ag=(np.abs(o-refs['chr']).max(2)>20)&(np.abs(o-refs['ff']).max(2)>20)&(np.abs(o-refs['wk']).max(2)>20)
        tips=((290,720),(734,720)) if 'inner' in name else ((280,725),(744,725))
        s=[]
        for (u,v) in tips:
            x,y=dev(u,v); r=14; b=(slice(int(y-r),int(y+r)),slice(int(x-r),int(x+r)))
            s.append(f'tip ink {c[b].sum():5.1f} (area {area[b].sum():5.1f}) agreed {ag[b].sum()}')
        print(f'{name:12s} {tag:15s} agreed {ag.sum():3d}  '+' | '.join(s))
