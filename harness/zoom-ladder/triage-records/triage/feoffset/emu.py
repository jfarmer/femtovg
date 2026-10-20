# Emulate each browser's offset rule in femtovg by rewriting dx/dy so the device shift is the integer the browser uses:
# Gecko int32_t() truncation, Skia nearest-neighbour ceil(d - 0.5). Compare with that browser's frame of the original.
import json, re, math, subprocess, numpy as np
from cmp import *
D='/Users/matt/src/femtovg-wt/da/corpus/wpt-feoffset-reftests/'
FR={0.25:'z025',0.33:'z033',0.5:'z05',0.75:'z075',1.25:'z125',1.5:'z15',1.75:'z175',2:'z2',3:'z3',4:'z4',1:'z1'}
# element-to-root scale and obb factor (bbox w,h) per file
scale={'offset-with-element-transform-scale':2,'offset-with-parent-transform-scale':1.5}
obb={'offset-primitive-units-non-square':(120,60),'offset-primitive-units-objectboundingbox-25':(100,100),
     'offset-primitive-units-objectboundingbox-50':(80,80),'offset-primitive-units-objectboundingbox-negative':(100,100)}
single=[n for n in sorted(set(v['key'].split('__')[-1] for v in json.load(open('../clusters_compact.json'))['feoffset']))
        if n not in ('offset-chained-cancelling','offset-chained-sequential','offset-triple-chain-rgb-shadow','offset-sourcealpha-flood','offset-circle-shape')]
d=json.load(open('../clusters_compact.json'))['feoffset']
rules={'ff':lambda v: math.trunc(v),'chr':lambda v: math.ceil(v-0.5)}
res=[]
for v in d:
    if not v['key'].startswith('corpus__'): continue
    name=v['key'].split('__')[-1]
    if name not in single: continue
    t=open(D+name+'.svg').read()
    m=re.search(r'<feOffset([^>]*)/>',t); a=m.group(1)
    dx=float(re.search(r'dx="([-\d.]+)"',a).group(1)) if 'dx=' in a else 0.0
    dy=float(re.search(r'dy="([-\d.]+)"',a).group(1)) if 'dy=' in a else 0.0
    s=scale.get(name,1.0); bw,bh=obb.get(name,(1,1))
    for b in v['bad']:
        z=b[0]; fr=FR[z]; F=frames(v['key'],fr)
        row={'name':name,'z':z,'orig':{k:int(bad(F['fv'],F[k])[0].sum()) for k in ('chr','ff','wk') if F[k] is not None}}
        for br,rule in rules.items():
            if F[br] is None: continue
            ddx=rule(dx*bw*s*z)/(s*z); ddy=rule(dy*bh*s*z)/(s*z)
            t2=t.replace(m.group(0), re.sub(r'dy="[-\d.]+"', f'dy="{ddy!r}"', re.sub(r'dx="[-\d.]+"', f'dx="{ddx!r}"', m.group(0))))
            t2=t2.replace(' primitiveUnits="objectBoundingBox"','')
            p=f'emu/{name}_{fr}_{br}.svg'; open(p,'w').write(t2)
            subprocess.run(['python3','shoot.py',p,str(z),p[:-4],'fv'],check=True)
            E=load(p[:-4]+'_fv.png')
            mk,dd=bad(E,F[br]); row['emu_'+br]=int(mk.sum()); row['emu_'+br+'_max']=int(dd.max())
        res.append(row); print(row, flush=True)
json.dump(res,open('emu.json','w'))
