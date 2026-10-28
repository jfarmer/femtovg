import sys, numpy as np
from PIL import Image
def load(p): return 255-np.asarray(Image.open(p).convert('L')).astype(float)
def runs(on):
    r=[];s=None
    for i,v in enumerate(on):
        if v and s is None: s=i
        if not v and s is not None: r.append((s,i)); s=None
    if s is not None: r.append((s,len(on)))
    return r
ref=load(sys.argv[1])
# find line bands from ref row sums
rows=ref.sum(1)>0
bands=[(a,b) for a,b in runs(rows) if b-a>3]
print("bands",bands)
for p in sys.argv[2:]:
    a=load(p); out=[]; outy=[]
    for (y0,y1) in bands:
        y0-=2;y1+=2
        colsum=ref[y0:y1].sum(0)+a[y0:y1].sum(0)
        for (x0,x1) in runs(colsum>0):
            r=ref[y0:y1,x0:x1]; q=a[y0:y1,x0:x1]
            if r.sum()<50 or q.sum()<50: continue
            X=np.arange(x0,x1); Y=np.arange(y0,y1)
            out.append((q.sum(0)*X).sum()/q.sum()-(r.sum(0)*X).sum()/r.sum())
            outy.append((q.sum(1)*Y).sum()/q.sum()-(r.sum(1)*Y).sum()/r.sum())
    out=np.array(out); outy=np.array(outy)
    print(f"{p}: n={len(out)} dx mean {out.mean():+.3f} meanabs {np.abs(out).mean():.3f} maxabs {np.abs(out).max():.3f} | dy mean {outy.mean():+.3f}")
