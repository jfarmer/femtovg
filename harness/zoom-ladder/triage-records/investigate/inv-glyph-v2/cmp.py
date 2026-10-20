import sys, numpy as np
from PIL import Image
a=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
b=np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(int)
d=np.abs(a-b).max(axis=2)
th=int(sys.argv[3]) if len(sys.argv)>3 else 8
m=d>th
ys,xs=np.nonzero(m)
print(f"px>{th}: {m.sum()} max {d.max()} any>0: {(d>0).sum()}", end='')
if m.sum(): print(f" bbox x{xs.min()}-{xs.max()} y{ys.min()}-{ys.max()}")
else: print()
