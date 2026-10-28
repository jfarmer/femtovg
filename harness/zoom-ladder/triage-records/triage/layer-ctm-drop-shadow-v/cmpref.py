import numpy as np
from PIL import Image
import os
R=os.path.expanduser('~/src/femtovg-wt/runs/zoom')
K="wpt22__19-filter-subregions-and-offcanvas__wpt-2d-layer-ctm-drop-shadow-filter"
def ld(p): return np.asarray(Image.open(p).convert('RGB')).astype(int)
def cnt(a,b):
    d=np.abs(a-b).max(-1); return int((d>8).sum()), int(d.max())
zs=[('1','z1'),('1.25','z125'),('1.5','z15'),('1.75','z175'),('2','z2'),('3','z3'),('4','z4'),('0.75','z075'),('0.5','z05'),('0.33','z033'),('0.25','z025')]
print('zoom | fem vs chrRef | fem vs wkRef | chrRef vs wkRef | chr vs chrRef | ff vs chrRef | wk vs wkRef | fem vs chr | fem vs wk')
for z,t in zs:
    f=ld(f'{R}/png/zl_zm_svg/{K}/fresh_{t}.png') if t!='z1' else ld(f'{R}/png/zl_zm_svg/{K}/00.png')
    cr=ld(f'{R}/fresh/refs/chr_{K}-ref_{t}.png'); wr=ld(f'{R}/fresh/refs/wk_{K}-ref_{t}.png')
    c=ld(f'{R}/fresh/refs/chr_{K}_{t}.png'); w=ld(f'{R}/fresh/refs/wk_{K}_{t}.png')
    try: ff=ld(f'{R}/fresh/refs/ff_{K}_{t}.png'); ffr=cnt(ff,cr)
    except Exception: ffr=None
    print(z, cnt(f,cr), cnt(f,wr), cnt(cr,wr), cnt(c,cr), ffr, cnt(w,wr), cnt(f,c), cnt(f,w))
