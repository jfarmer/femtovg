import numpy as np, os
from PIL import Image
R=os.path.expanduser('~/src/femtovg-wt/runs/zoom')
K="wpt22__19-filter-subregions-and-offcanvas__wpt-2d-layer-ctm-drop-shadow-filter"
ld=lambda p: np.asarray(Image.open(p).convert('RGB')).astype(int)
for z,t in [('1.25','z125'),('1.75','z175'),('0.75','z075'),('0.33','z033'),('0.25','z025')]:
    f=ld(f'{R}/png/zl_zm_svg/{K}/fresh_{t}.png')
    E=ld(f'{R}/fresh/refs/chr_{K}-ref_{t}.png')
    off=lambda a,b: np.abs(a-b).max(-1)>8
    fe=off(f,E)
    out=[z]
    for b in ['chr','ff','wk']:
        im=ld(f'{R}/fresh/refs/{b}_{K}_{t}.png')
        fail=off(f,im); be=off(im,E)
        out.append(f'{b}: fail={fail.sum()} browserOff&femOn={(fail&be&~fe).sum()} femOff&browserOn={(fail&fe&~be).sum()} bothOff={(fail&fe&be).sum()}')
    # where is femtovg off exact: rows/cols extents
    ys,xs=np.nonzero(fe)
    rowsets=sorted(set(ys.tolist())); colsets=sorted(set(xs.tolist()))
    out.append(f'femOff={fe.sum()} rows(n={len(rowsets)})={rowsets[:12]} cols(n={len(colsets)})')
    print(' | '.join(out))
