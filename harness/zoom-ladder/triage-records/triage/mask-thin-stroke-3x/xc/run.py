import json, os, subprocess, sys
from PIL import Image
import numpy as np
d=json.load(open('../clusters_compact.json'))
R=os.path.expanduser('~/src/femtovg-wt/runs/zoom/fresh/refs/')
bins={'master':os.path.expanduser('~/src/femtovg-wt/bin/_logos_full_zm2'),'cull':'bin/_logos_cull'}
fr={1:'z1',1.25:'z125',1.5:'z15',1.75:'z175',2:'z2',3:'z3',4:'z4',0.75:'z075',0.5:'z05',0.33:'z033',0.25:'z025'}
env=dict(os.environ,FRAME_W='460',FRAME_H='260',BOX='200',BOX_X='130',BOX_Y='30',SKIP_UNSUPPORTED_FILTERS='1',VIEWPORT_CLIP='1',TRANSIENT_BUDGET_MB='1024')
res=[]
for cname,c in d.items():
    if cname=='mask-thin-stroke-3x': continue
    for e in c:
        k=e['key']; svg=os.path.expanduser('~/'+e['path'])
        for b in e['bad']:
            z=b[0]; f=fr[z]
            imgs={}
            for bn,bp in bins.items():
                out=f'xc/{bn}.ppm'
                subprocess.run([bp,str(z),out,svg],capture_output=True,env=env)
                imgs[bn]=np.asarray(Image.open(out).convert('RGB')).astype(int)
            same=np.array_equal(imgs['master'],imgs['cull'])
            if same:
                res.append((cname,k,z,'identical')); continue
            row={}
            for bn,a in imgs.items():
                vals=[]
                for br in ['chr','ff','wk']:
                    p=f'{R}{br}_{k}_{f}.png'
                    if os.path.exists(p):
                        vals.append((np.abs(a-np.asarray(Image.open(p).convert('RGB')).astype(int)).max(-1)>8).sum())
                row[bn]=min(vals)
            res.append((cname,k,z,row))
            print(cname,k,z,row,flush=True)
json.dump([(a,b,c,(d if isinstance(d,str) else {k:int(v) for k,v in d.items()})) for a,b,c,d in res],open('xc/results.json','w'),indent=0)
print('pairs',len(res),'changed',sum(1 for r in res if r[3]!='identical'))
