import numpy as np, glob
from PIL import Image
tag = 'custom_0_5,180,30;0_625,167_5,5'
def ink(p): return 255 - np.asarray(Image.open(p).convert('L')).astype(float)
bands = [(16, 36), (41, 61), (66, 86)]
def cx(im, b):
    w = im[b[0]:b[1]]; s = w.sum()
    if s < 1: return None
    return (w.sum(0) * np.arange(w.shape[1])).sum() / s + 0.5
rows = {}
for g in range(14):
    ref = ink(f'sweep/master/{g}/PathRef_{tag}_fresh.ppm')
    for cfg, kind in [('master','fresh'),('master','ladder'),('subpx','fresh'),('grid','fresh'),('gridsubpx','fresh'),('gridsubpx','ladder')]:
        im = ink(f'sweep/{cfg}/{g}/GlyphRun_{tag}_{kind}.ppm')
        for li, b in enumerate(bands):
            r = cx(ref, b); c = cx(im, b)
            if r is None or c is None: continue
            rows.setdefault((cfg, kind), []).append(c - r)
print("centroid x error vs outline (path regime) render, px; 14 glyphs x 3 lines, scale 0.625, tx 167.5")
for k, v in rows.items():
    v = np.array(v)
    print(f"{k[0]:10s} {k[1]:6s} n={len(v)} mean={v.mean():+.3f} mean|e|={np.abs(v).mean():.3f} max|e|={np.abs(v).max():.3f}")
