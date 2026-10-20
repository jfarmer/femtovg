import sys, numpy as np
from PIL import Image
def ink(p): return 255 - np.asarray(Image.open(p).convert('L')).astype(float)
case = sys.argv[1]  # e.g. s0_5_tx180_-__s0_625_tx167_5
ims = {
 'path ref (outline, exact T)': ink(f't3m/PathRef_{case}_fresh.ppm'),
 'master fresh': ink(f't3m/GlyphRun_{case}_fresh.ppm'),
 'master ladder': ink(f't3m/GlyphRun_{case}_ladder.ppm'),
 'device-grid fresh': ink(f't3g/GlyphRun_{case}_fresh.ppm'),
 'device-grid ladder': ink(f't3g/GlyphRun_{case}_ladder.ppm'),
}
ref = ims['path ref (outline, exact T)']
boxes = [tuple(map(int, b.split(','))) for b in sys.argv[2:]]
for name, im in ims.items():
    out = []
    for (x0,y0,x1,y1) in boxes:
        w = im[y0:y1, x0:x1]; xs = np.arange(x0,x1)
        cx = (w.sum(0)*xs).sum()/w.sum() + 0.5
        out.append(f"cx={cx:7.3f}")
    d = np.abs(im-ref)
    print(f"{name:28s} {' '.join(out)}  vs path: px>8={(d>8).sum():4d} max={d.max():3.0f} mean={d.mean():.3f}")
