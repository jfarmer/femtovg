import sys, numpy as np
from PIL import Image
def load(p): return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
T = 24
for p in sys.argv[1:]:
    a = load(p); m = (255 - a).max(axis=2) > T
    cols = m.any(axis=0)
    # split on gaps of >=1 empty column
    segs=[]; x=0; W=len(cols)
    while x<W:
        if cols[x]:
            s=x
            while x<W and cols[x]: x+=1
            segs.append((s,x))
        x+=1
    out=[]
    for s,e in segs:
        ys=np.nonzero(m[:,s:e].any(axis=1))[0]
        if e-s<3: continue
        out.append(f'[x{s}..{e} y{ys.min()}..{ys.max()+1} {e-s}x{ys.max()+1-ys.min()}]')
    print(f'{p.split("/")[-1][:58]:58s}', ' '.join(out))
