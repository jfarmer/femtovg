from PIL import Image
import numpy as np
K="wpt22__19-filter-subregions-and-offcanvas__wpt-2d-layer-ctm-drop-shadow-filter"
O="triage/layer-ctm-drop-shadow"
def ld(p): return np.asarray(Image.open(p).convert('RGB')).astype(float)
zs={'1.25':'z125','1.75':'z175','0.75':'z075','0.33':'z033','0.25':'z025'}
print('zoom browser | fem-vs-br>8 | of which: br off area & fem on area | fem off area & br on | both off | fem-vs-area>8 br-vs-area>8')
for z,t in zs.items():
    A=ld(f'{O}/area8_{z}.png').reshape(260,8,460,8,3).mean((1,3))
    f=ld(f'png/zl_zm_svg/{K}/fresh_{t}.png')
    fa=np.abs(f-A).max(-1)>8
    for b in ['chr','ff','wk']:
        try: r=ld(f'fresh/refs/{b}_{K}_{t}.png')
        except: continue
        fb=np.abs(f-r).max(-1)>8
        ra=np.abs(r-A).max(-1)>8
        print(z,b,'|',int(fb.sum()),'|',int((fb&ra&~fa).sum()),int((fb&fa&~ra).sum()),int((fb&fa&ra).sum()),'|',int(fa.sum()),int(ra.sum()))
