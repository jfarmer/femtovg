import sys
from PIL import Image
import numpy as np
K="wpt22__19-filter-subregions-and-offcanvas__wpt-2d-layer-ctm-drop-shadow-filter"
O="triage/layer-ctm-drop-shadow"
def ld(p): return np.asarray(Image.open(p).convert('RGB')).astype(float)
def area(z):
    a=ld(f'{O}/area8_{z}.png')
    print(z, a.shape) if a.shape[0]!=2080 else None
    return a.reshape(260,8,460,8,3).mean((1,3))
zs={'1.25':'z125','1.75':'z175','0.75':'z075','0.33':'z033','0.25':'z025'}
for z,t in zs.items():
    A=area(z)
    f=ld(f'png/zl_zm_svg/{K}/fresh_{t}.png')
    row=[z]
    def cnt(x,y):
        d=np.abs(x-y).max(-1); return int((d>8).sum()), round(float(d.max()),1)
    row.append(('fem',cnt(f,A)))
    for b in ['chr','ff','wk']:
        try: r=ld(f'fresh/refs/{b}_{K}_{t}.png')
        except: row.append((b,None)); continue
        row.append((b,cnt(r,A)))
    c1=ld(f'{O}/chr1_{z}.png')
    row.append(('chr1_vs_ref',cnt(c1,ld(f'fresh/refs/chr_{K}_{t}.png'))))
    print(row)
