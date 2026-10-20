import sys, os, numpy as np
from PIL import Image
def L(p): return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
def n8(a,b): d=np.abs(a-b).max(axis=2); return int((d>8).sum()), int(d.max())
a=L(sys.argv[1])
for p in sys.argv[2:]:
    print(os.path.basename(p), n8(L(p),a))
