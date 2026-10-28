import sys
from PIL import Image
import numpy as np
def load(p): return np.asarray(Image.open(p).convert('RGBA')).astype(int)
a=load(sys.argv[1]); b=load(sys.argv[2])
d=np.abs(a-b).max(axis=2)
m=d>8
print('beyond8:',m.sum(),'max',d.max())
ys,xs=np.nonzero(m)
if len(ys): print('bbox x',xs.min(),xs.max(),'y',ys.min(),ys.max())
if len(sys.argv)>3:
  y=int(sys.argv[3]); x0,x1=int(sys.argv[4]),int(sys.argv[5])
  print('A',[tuple(a[y,x,:3]) for x in range(x0,x1)])
  print('B',[tuple(b[y,x,:3]) for x in range(x0,x1)])
