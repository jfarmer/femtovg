import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
H=os.path.expanduser('~')
Z=H+'/src/femtovg-wt/runs/zoom/'
OUT=Z+'triage/miter-limit/scan/'
FIX=Z+'triage/miter-limit/bin/_logos_full_fix'
MST=H+'/src/femtovg-wt/bin/_logos_full_zm2'
fr={1:'z1',1.25:'z125',1.5:'z15',1.75:'z175',2:'z2',3:'z3',4:'z4',0.75:'z075',0.5:'z05',0.33:'z033',0.25:'z025'}
env=dict(os.environ,FRAME_W='460',FRAME_H='260',BOX='200',BOX_X='130',BOX_Y='30',SKIP_UNSUPPORTED_FILTERS='1',VIEWPORT_CLIP='1',TRANSIENT_BUDGET_MB='1024')
d=json.load(open(Z+'triage/clusters_compact.json'))
jobs=[]
for c,fs in d.items():
  for f in fs:
    p=f['path'];  p=p if p.startswith('/') else H+'/'+p
    zs=sorted(set(b[0] for b in f['bad'])|{1})
    for z in zs: jobs.append((c,f['key'],p,z))
def load(p):
  try: return np.asarray(Image.open(p).convert('RGB')).astype(int)
  except Exception: return None
def run(j):
  c,k,p,z=j
  o=OUT+'%s_%s_fix.ppm'%(k,fr[z]); m=OUT+'%s_%s_mst.ppm'%(k,fr[z])
  subprocess.run([FIX,str(z),o,p],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=300)
  subprocess.run([MST,str(z),m,p],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=300)
  a=load(o); b=load(m)
  if a is None or b is None: return (c,k,z,'missing',None)
  moved=int((np.abs(a-b).max(axis=2)>0).sum())
  res={}
  for br in ['chr','ff','wk']:
    r=load(Z+'fresh/refs/%s_%s_%s.png'%(br,k,fr[z]))
    if r is None: continue
    res[br]=(int((np.abs(b-r).max(axis=2)>8).sum()),int((np.abs(a-r).max(axis=2)>8).sum()))
  os.remove(o); os.remove(m)
  return (c,k,z,moved,res)
with ThreadPoolExecutor(4) as ex:
  for r in ex.map(run,jobs):
    print(json.dumps(r),flush=True)
