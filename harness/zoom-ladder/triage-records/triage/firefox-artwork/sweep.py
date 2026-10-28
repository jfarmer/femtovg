import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
files=json.load(open('sweep_files.json'))
R='/Users/matt/src/femtovg-wt/runs/zoom/fresh/refs'
E='bin/_logos_full_exp'
ENV={**os.environ,'FRAME_W':'460','FRAME_H':'260','BOX':'200','BOX_X':'130','BOX_Y':'30','SKIP_UNSUPPORTED_FILTERS':'1','VIEWPORT_CLIP':'1','TRANSIENT_BUDGET_MB':'1024'}
Z={'z1':'1','z175':'1.75'}
def job(a):
    e,fr,v=a
    out=f"sweep/{e['key']}_{fr}_{v}.ppm"
    if not os.path.exists(out):
        env=dict(ENV)
        if v=='fold': env['FV_INNER']='fold'
        subprocess.run([E,Z[fr],out,e['path']],env=env,capture_output=True,timeout=120)
    return out
jobs=[(e,fr,v) for e in files for fr in Z for v in ('master','fold')]
with ThreadPoolExecutor(4) as ex: list(ex.map(job,jobs))
def L(p): return np.asarray(Image.open(p).convert('RGB'),dtype=np.int32)
tot={'moved':0,'toward_wk':0,'away_wk':0,'toward_chr':0,'away_chr':0}
rows=[]
for e in files:
    for fr in Z:
        a,b=f"sweep/{e['key']}_{fr}_master.ppm",f"sweep/{e['key']}_{fr}_fold.ppm"
        if not (os.path.exists(a) and os.path.exists(b)): continue
        A,B=L(a),L(b)
        ch=np.abs(A-B).max(axis=2)>0
        if not ch.any(): continue
        tot['moved']+=1
        r=[e['key'],fr,int(ch.sum())]
        for br in ('wk','chr'):
            p=f"{R}/{br}_{e['key']}_{fr}.png"
            if not os.path.exists(p): r+=['-','-']; continue
            Rf=L(p)
            na=int((np.abs(A-Rf).max(axis=2)>8).sum()); nb=int((np.abs(B-Rf).max(axis=2)>8).sum())
            r+=[na,nb]
            if nb<na: tot['toward_'+br]+=1
            elif nb>na: tot['away_'+br]+=1
        rows.append(r)
for r in sorted(rows,key=lambda r:-r[2]): print(*r)
print(tot)
