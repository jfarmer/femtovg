import sys, json, numpy as np
sys.path.insert(0,'.')
from cmp import *
C=json.load(open('/Users/matt/src/femtovg-wt/runs/zoom/triage/clusters_compact.json'))['clip-edges']
ident=0; tot=0
fails={'mst':0,'area':0}; per={}
for f in C:
    k=f['key']
    for z in TAG:
        m=load(f'png/mst/{k}/{z}.png'); l=fem(k,z)
        tot+=1; ident+= (m is not None and l is not None and np.array_equal(m[...,:3],l[...,:3]))
    row=[]
    for b in f['bad']:
        z=b[0]
        res={}
        for tag in ('mst','area'):
            im=load(f'png/{tag}/{k}/{z}.png')
            best=min(v for v in (beyond(im,ref(br,k,z)) for br in ('chr','ff','wk')) if v is not None)
            res[tag]=best
            fails[tag]+= best>24
        row.append(f"{z}:{res['mst']}->{res['area']}")
    per[k]=row
    print(k.split('__')[-1][:40], ' '.join(row))
print('master bit-identical to ladder:',ident,'/',tot)
print('failing pairs master',fails['mst'],'patched',fails['area'])
