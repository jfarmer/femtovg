import numpy as np, os, sys, json
from PIL import Image
H=os.path.expanduser('~/src/femtovg-wt/runs/zoom')
zz,step,tag=sys.argv[1:4]
def load(p): return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
def n8(a,b): return int((np.abs(a-b).max(-1)>8).sum())
moved=[];same=0;missing=0
for line in open('qual.txt'):
    k,p=line.rstrip('\n').split('\t')
    bp=f'{H}/png/zl_zm_svg/{k}/{step}.png'; gp=f'gate_{tag}/{k}.png'
    if not os.path.exists(bp) or not os.path.exists(gp): missing+=1; continue
    b=load(bp); g=load(gp)
    if (b==g).all(): same+=1; continue
    r={}
    for br in ['chr','ff','wk']:
        rp=f'{H}/fresh/refs/{br}_{k}_z{zz}.png'
        if os.path.exists(rp):
            R=load(rp); r[br]=(n8(b,R),n8(g,R))
    bb=min(v[0] for v in r.values()) if r else None; gb=min(v[1] for v in r.values()) if r else None
    moved.append((k,int((np.abs(b-g).max(-1)>0).sum()),bb,gb,r))
print('same',same,'moved',len(moved),'missing',missing)
better=sum(1 for m in moved if m[3]<m[2]); worse=sum(1 for m in moved if m[3]>m[2])
print('best-browser n8: better',better,'worse',worse,'equal',len(moved)-better-worse)
fail_b=sum(1 for m in moved if m[2]>24); fail_g=sum(1 for m in moved if m[3]>24)
print('of moved: failing(>24) base',fail_b,'gate',fail_g)
for m in sorted(moved,key=lambda m:m[3]-m[2]):
    print(f'{m[2]:5d} -> {m[3]:5d}  px moved {m[1]:5d}  {m[0][:90]}', {k:v for k,v in m[4].items()})
