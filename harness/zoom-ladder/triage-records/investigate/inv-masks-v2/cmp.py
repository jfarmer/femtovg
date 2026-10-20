import sys, numpy as np
from PIL import Image
def load(p): return np.asarray(Image.open(p).convert('RGBA') if not p.endswith('.ppm') else Image.open(p).convert('RGB')).astype(int)
a=load(sys.argv[1]); b=load(sys.argv[2])
if a.shape[2]!=b.shape[2]:
    a=a[...,:3]; b=b[...,:3]
d=np.abs(a-b).max(axis=2)
print(f"{sys.argv[1]} vs {sys.argv[2]}: diff px {int((d>0).sum())} n8 {int((d>8).sum())} max {int(d.max())}")
