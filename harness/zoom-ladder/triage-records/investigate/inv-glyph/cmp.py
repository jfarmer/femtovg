import sys, numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
b = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(int)
d = np.abs(a-b).max(axis=2)
n = int((d>0).sum()); m = int(d.max())
ys, xs = np.nonzero(d)
bbox = (xs.min(), ys.min(), xs.max(), ys.max()) if n else None
print(f"diff px={n} max={m} bbox={bbox} >8: {(d>8).sum()}")
if len(sys.argv) > 3 and n:
    # cluster by rows
    for y0 in sorted(set(ys//10)):
        sel = (ys//10)==y0
        print("  rows", y0*10, "x", xs[sel].min(), xs[sel].max(), "n", sel.sum(), "max", d[ys[sel], xs[sel]].max())
