import sys, numpy as np
from PIL import Image
def ink(p): return 255 - np.asarray(Image.open(p).convert('L')).astype(float)
d = sys.argv[1]; tag = 'custom_0_5,180,30;0_625,167_5,5'
ims = {
 'outline ref (path regime)': ink(f'{d}/m/PathRef_{tag}_fresh.ppm'),
 'master fresh': ink(f'{d}/m/GlyphRun_{tag}_fresh.ppm'),
 'master ladder': ink(f'{d}/m/GlyphRun_{tag}_ladder.ppm'),
 'device-grid fresh': ink(f'{d}/g/GlyphRun_{tag}_fresh.ppm'),
 'device-grid ladder': ink(f'{d}/g/GlyphRun_{tag}_ladder.ppm'),
}
ref = ims['outline ref (path regime)']
# one box per text line
bands = [(15, 35), (55, 75), (95, 115)]
for name, im in ims.items():
    out = []
    for (y0, y1) in bands:
        w = im[y0:y1]; xs = np.arange(w.shape[1])
        cx = (w.sum(0)*xs).sum()/max(w.sum(),1e-9) + 0.5
        rcx = (ref[y0:y1].sum(0)*xs).sum()/ref[y0:y1].sum() + 0.5
        out.append(f"cx={cx:7.3f} ({cx-rcx:+.3f})")
    dd = np.abs(im-ref)
    print(f"{name:27s} {'  '.join(out)}  vs outline: px>8={(dd>8).sum():3d} sum|d|={dd.sum()/255:.1f}")
