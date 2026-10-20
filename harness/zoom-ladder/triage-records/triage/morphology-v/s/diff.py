import sys
from PIL import Image
import numpy as np
def L(p): return np.asarray(Image.open(p).convert('RGB')).astype(int)
a=L(sys.argv[1]); b=L(sys.argv[2])
m=np.abs(a-b).max(-1)>8
ys,xs=np.nonzero(m)
print(sys.argv[1].split('/')[-1], 'vs', sys.argv[2].split('/')[-1], 'n=',int(m.sum()), end=' ')
if m.sum():
    print('rows',sorted(set(ys.tolist()))[:6],'cols',min(xs),max(xs), 'sample a',a[ys[0],xs[0]].tolist(),'b',b[ys[0],xs[0]].tolist())
else: print()
