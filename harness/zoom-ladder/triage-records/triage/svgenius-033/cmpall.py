import numpy as np, os, sys
from PIL import Image
H=os.path.expanduser('~/src/femtovg-wt/runs/zoom')
zz,bd,gd=sys.argv[1:4]
def load(p): return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
def n8(a,b):
    h,w=min(a.shape[0],b.shape[0]),min(a.shape[1],b.shape[1])
    return int((np.abs(a[:h,:w]-b[:h,:w]).max(-1)>8).sum())
moved=[];same=0
for line in open('all.txt'):
    k,p=line.rstrip('\n').split('\t')
    bp,gp=f'{bd}/{k}.png',f'{gd}/{k}.png'
    if not (os.path.exists(bp) and os.path.exists(gp)): continue
    b,g=load(bp),load(gp)
    if b.shape==g.shape and (b==g).all(): same+=1; continue
    r={}
    for br in ['chr','ff','wk']:
        for d in [f'{H}/refs',f'{H}/fresh/refs']:
            rp=f'{d}/{br}_{k}_z{zz}.png'
            if os.path.exists(rp): R=load(rp); r[br]=(n8(b,R),n8(g,R)); break
    bb=min((v[0] for v in r.values()),default=-1); gb=min((v[1] for v in r.values()),default=-1)
    moved.append((k,int((np.abs(b-g).max(-1)>0).sum()),bb,gb,r))
print('same',same,'moved',len(moved))
print('best-browser n8 better',sum(m[3]<m[2] for m in moved),'worse',sum(m[3]>m[2] for m in moved),'equal',sum(m[3]==m[2] for m in moved))
print('sum best n8 base',sum(m[2] for m in moved),'gate',sum(m[3] for m in moved))
for m in sorted(moved,key=lambda m:m[3]-m[2]):
    print(f'{m[2]:6d} -> {m[3]:6d}  moved {m[1]:5d}  {m[0][:80]}', m[4])
