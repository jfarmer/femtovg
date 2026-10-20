# Integer-device-shift variant of each group-A (file, zoom): every engine renders the SAME rewritten file.
# If femtovg's failure is only fractional-shift resampling, it should vanish here against the best browser.
import json, re, math, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
V='/Users/matt/src/femtovg-wt/runs/zoom/triage/feoffset-v/'
D='/Users/matt/src/femtovg-wt/da/corpus/wpt-feoffset-reftests/'
SHOOT='/Users/matt/src/femtovg-wt/runs/zoom/triage/feoffset/shoot.py'
scale={'offset-with-element-transform-scale':2,'offset-with-parent-transform-scale':1.5}
obb={'offset-primitive-units-non-square':(120,60),'offset-primitive-units-objectboundingbox-25':(100,100),
     'offset-primitive-units-objectboundingbox-50':(80,80),'offset-primitive-units-objectboundingbox-negative':(100,100)}
skip=('offset-triple-chain-rgb-shadow','offset-sourcealpha-flood','offset-circle-shape')
FR={0.25:'z025',0.33:'z033',0.5:'z05',0.75:'z075',1.25:'z125',1.5:'z15',1.75:'z175',2:'z2',3:'z3',4:'z4',1:'z1'}
cl=json.load(open('/Users/matt/src/femtovg-wt/runs/zoom/triage/clusters_compact.json'))['feoffset']
def snap(v, k):  # v user units, k user->device factor
    d=v*k
    if abs(d)<1e-9: return v
    n=round(d)
    if n==0: return 0.0
    return (n+math.copysign(1e-3,n))/k
jobs=[]
for e in cl:
    if not e['key'].startswith('corpus__'): continue
    name=e['key'].split('__')[-1]
    if name in skip: continue
    t=open(D+name+'.svg').read()
    s=scale.get(name,1.0); bw,bh=obb.get(name,(1,1))
    for b in e['bad']:
        z=b[0]
        def rep(m):
            a=m.group(0)
            def f(attr,bb):
                nonlocal a
                mm=re.search(attr+r'="([-\d.]+)"',a)
                if mm:
                    v=float(mm.group(1)); a=a.replace(mm.group(0), f'{attr}="{snap(v,bb*s*z)!r}"')
            f('dx',bw); f('dy',bh); return a
        t2=re.sub(r'<feOffset[^>]*/>',rep,t)
        p=f'{V}intshift/{name}_{FR[z]}.svg'; open(p,'w').write(t2)
        jobs.append((name,z,p))
def run(j):
    name,z,p=j
    subprocess.run(['python3',SHOOT,p,str(z),p[:-4]],check=True)
    return j
with ThreadPoolExecutor(6) as ex:
    for j in ex.map(run,jobs): print('done',j[0],j[1],flush=True)
json.dump(jobs,open(V+'intshift/jobs.json','w'))
