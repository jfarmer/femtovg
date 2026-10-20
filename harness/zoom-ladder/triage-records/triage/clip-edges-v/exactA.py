import sys, json, numpy as np
sys.path.insert(0,'.')
from cmp import *
from disc import disc_cov
C=json.load(open('/Users/matt/src/femtovg-wt/runs/zoom/triage/clusters_compact.json'))['clip-edges']
circ={12:(50,80),16:(110,65),20:(80,50),24:(50,110),28:(110,95),32:(80,80),36:(50,65),40:(110,50),44:(80,110),48:(50,95)}
tot_fail=0; ex_fail=0; rows=[]
for f in C:
    k=f['key']
    if 'variation-' not in k: continue
    n=int(k.split('-')[-1]); X,Y=circ[n]
    for b in f['bad']:
        z=b[0]
        cx=230+z*(X-100); cy=130+z*(Y-100); r=25*z
        a=disc_cov(460,260,cx,cy,r,n=256)
        # green on white: R=255(1-a), G=255-127a? use measured fem G mapping: G = 255*(1-a)+128*a
        ex=np.stack([255*(1-a),255*(1-a)+128*a,255*(1-a)],-1)
        fe=fem(k,z)[...,:3]
        res={}
        for br in ('chr','ff','wk'):
            im=ref(br,k,z)
            if im is None: continue
            res[br]=int((np.abs(im[...,:3]-ex).max(-1)>8).sum())
        best=min(res.values())
        fx=int((np.abs(fe-ex).max(-1)>8).sum())
        tot_fail+=1; ex_fail+= best>24
        rows.append((n,z,b[1],best,res.get('wk'),fx))
for r in rows: print('v%d z%s fem-vs-best %d | exact-vs-best %d (wk %s) | fem-vs-exact %d'%r)
print('failing pairs',tot_fail,'exact disc also fails',ex_fail)
