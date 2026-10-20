import json, numpy as np
from PIL import Image
V='/Users/matt/src/femtovg-wt/runs/zoom/triage/feoffset-v/'
FR={0.25:'z025',0.33:'z033',0.5:'z05',0.75:'z075',1.25:'z125',1.5:'z15',1.75:'z175'}
def L(p):
    try: return np.asarray(Image.open(p).convert('RGB')).astype(int)
    except Exception: return None
def n(a,b):
    if a is None or b is None: return None
    return int((np.abs(a-b).max(-1)>8).sum())
cl={e['key'].split('__')[-1]:e for e in json.load(open('/Users/matt/src/femtovg-wt/runs/zoom/triage/clusters_compact.json'))['feoffset'] if e['key'].startswith('corpus__')}
jobs=json.load(open(V+'intshift/jobs.json'))
print(f"{'name':44s} {'z':>5s} | orig best | int: fv_chr fv_ff fv_wk best | chr_ff chr_wk ff_wk")
over=0
for name,z,p in jobs:
    F={k:L(p[:-4]+f'_{k}.png') for k in ('fv','chr','ff','wk')}
    ob=[b for b in cl[name]['bad'] if b[0]==z][0][1]
    c=[n(F['fv'],F[k]) for k in ('chr','ff','wk')]
    best=min(x for x in c if x is not None)
    if best>24: over+=1
    pr=[n(F['chr'],F['ff']),n(F['chr'],F['wk']),n(F['ff'],F['wk'])]
    print(f"{name[7:51]:44s} {z:5} | {ob:9d} | {c[0]:6} {c[1]:5} {c[2]:5} {best:4d}{'*' if best>24 else ' '} | {pr[0]:6} {pr[1]:6} {pr[2]:5}")
print('over 24:',over,'of',len(jobs))
