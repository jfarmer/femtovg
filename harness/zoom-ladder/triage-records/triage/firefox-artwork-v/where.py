import sys, numpy as np
from PIL import Image
def L(p): return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
a=L(sys.argv[1]); b=L(sys.argv[2])
d=(b-a); m=np.abs(d).max(axis=2)>8
s=d.sum(axis=2)
# simple flood fill labelling with 8-connectivity, merge within radius 3
pts=list(zip(*np.nonzero(m)))
seen=set(); rows=[]
P=set(pts)
for p in pts:
    if p in seen: continue
    stack=[p]; seen.add(p); comp=[]
    while stack:
        y,x=stack.pop(); comp.append((y,x))
        for dy in range(-3,4):
            for dx in range(-3,4):
                q=(y+dy,x+dx)
                if q in P and q not in seen: seen.add(q); stack.append(q)
    ys=np.array([c[0] for c in comp]); xs=np.array([c[1] for c in comp])
    sign='DARK(more ink)' if s[ys,xs].sum()<0 else 'light(less ink)'
    rows.append((len(ys),int(xs.mean()),int(ys.mean()),sign,int(np.abs(d[ys,xs]).max())))
rows.sort(key=lambda r:(r[2],r[1]))
for r in rows: print(r)
print('total',m.sum(),'dark px',int(((s<0)&m).sum()),'light px',int(((s>0)&m).sum()))
