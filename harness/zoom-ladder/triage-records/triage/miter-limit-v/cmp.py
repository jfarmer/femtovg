import sys, os, numpy as np
from PIL import Image
key=sys.argv[1]; prefix=sys.argv[2]
R=os.path.expanduser('~/src/femtovg-wt/runs/zoom/fresh/refs')
fr={'0.25':'z025','0.33':'z033','0.5':'z05','0.75':'z075','1':'z1','1.25':'z125','1.5':'z15','1.75':'z175','2':'z2','3':'z3','4':'z4'}
for z,f in fr.items():
    p=f'{prefix}_{z}.ppm'
    if not os.path.exists(p): continue
    a=np.asarray(Image.open(p).convert('RGB')).astype(int)
    out=[z]
    for b in ('chr','ff','wk'):
        rp=f'{R}/{b}_{key}_{f}.png'
        if not os.path.exists(rp): out.append(f'{b}=NA'); continue
        r=np.asarray(Image.open(rp).convert('RGB')).astype(int)
        out.append(f'{b}={int((np.abs(a-r).max(axis=2)>8).sum())}')
    print(*out)
