import json, os, sys, subprocess, numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
H=os.path.expanduser('~'); R=f'{H}/src/femtovg-wt/runs/zoom'
d=json.load(open(f'{R}/triage/clusters_compact.json'))['thin-frame-stroke-fractional']
fr={'z1':1,'z125':1.25,'z15':1.5,'z175':1.75,'z2':2,'z3':3,'z4':4,'z075':0.75,'z05':0.5,'z033':0.33,'z025':0.25}
B='bin/_logos_full_v'
env={**os.environ,'FRAME_W':'460','FRAME_H':'260','BOX':'200','BOX_X':'130','BOX_Y':'30','SKIP_UNSUPPORTED_FILTERS':'1','VIEWPORT_CLIP':'1','TRANSIENT_BUDGET_MB':'1024'}
mode=sys.argv[1]  # on/off
if mode=='on': env['V_THIN']='1'
def job(a):
    e,f=a; k=e['key']; out=f'cl/{mode}_{k}_{f}.png'
    if not os.path.exists(out):
        ppm=out[:-4]+'.ppm'; subprocess.run([B,f'{fr[f]:g}',ppm,f'{H}/'+e['path']],env=env,capture_output=True,timeout=300)
        Image.open(ppm).convert('RGB').save(out); os.remove(ppm)
    a=np.asarray(Image.open(out).convert('RGB'),dtype=int); res={}
    for t in ['chr','ff','wk']:
        p=f'{R}/fresh/refs/{t}_{k}_{f}.png'
        if os.path.exists(p):
            b=np.asarray(Image.open(p).convert('RGB'),dtype=int); res[t]=int((np.abs(a-b).max(axis=2)>8).sum())
    return k,f,res
jobs=[(e,f) for e in d for f in fr]
with ThreadPoolExecutor(6) as ex: rs=list(ex.map(job,jobs))
json.dump(rs,open(f'cl_{mode}.json','w'))
from collections import defaultdict
bad=defaultdict(list)
for k,f,res in rs:
    best=min(res.values()) if res else None
    if best is not None and best>24: bad[k].append((f,best,min(res,key=res.get),res))
print('files failing somewhere:',len(bad),'of',len(d))
for k,v in bad.items(): print(k[-55:], v)
