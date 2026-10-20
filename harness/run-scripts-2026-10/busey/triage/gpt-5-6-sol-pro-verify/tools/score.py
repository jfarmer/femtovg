import sys, numpy as np
from PIL import Image
S='/Users/matt/src/femtovg-wt/runs/busey/triage/gpt-5-6-sol-pro-verify'
def L(p): return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
def score(name, frame):
    f=L(frame); out={}
    ds=[]
    for b in ('chr','ff','wk'):
        r=L(f'{S}/refs/{b}_t__{name}_z2.png'); d=np.abs(f-r).max(2); ds.append(d); out[b]=int((d>20).sum())
    out['all3']=int(np.all([d>20 for d in ds],0).sum())
    return out
for a in sys.argv[1:]:
    name, frame = a.split(':',1)
    print(f'{name:28s} {frame.split("/")[-1]:40s}', score(name, frame))
