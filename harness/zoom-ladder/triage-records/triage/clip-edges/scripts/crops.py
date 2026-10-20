# crops.py KEY ZOOM x y w h scale out.png : side-by-side fem | chr | ff | wk | exact? with diff maps vs each
import sys, numpy as np
from PIL import Image, ImageDraw
from cmp import fem, ref
key, z = sys.argv[1], float(sys.argv[2]); z = int(z) if z == int(z) else z
x, y, w, h, s = map(int, sys.argv[3:8]); out = sys.argv[8]
extra = sys.argv[9] if len(sys.argv) > 9 else None
panels = [('fem', fem(key, z))] + [(b, ref(b, key, z)) for b in ('chr', 'ff', 'wk')]
if extra: panels.append(('exact', np.asarray(Image.open(extra).convert('RGBA')).astype(np.int32)))
panels = [(n, p) for n, p in panels if p is not None]
tiles = []
for n, p in panels:
    tiles.append((n, p[y:y+h, x:x+w, :3].clip(0, 255).astype(np.uint8)))
base = panels[-1][1] if extra else None
rows = [tiles]
if extra:
    drow = []
    for n, p in panels[:-1]:
        d = (p[y:y+h, x:x+w, 0] - base[y:y+h, x:x+w, 0])  # R channel signed
        img = np.full((h, w, 3), 255, np.uint8)
        a = np.clip(np.abs(d) * 8, 0, 255).astype(np.uint8)
        neg = d < 0  # more ink than exact
        img[..., 1] = 255 - a; img[neg, 0] = 255; img[neg, 2] = 255 - a[neg]
        img[~neg, 2] = 255; img[~neg, 0] = 255 - a[~neg]
        drow.append((n + '-ex', img))
    rows.append(drow)
W = max(len(r) for r in rows) * (w * s + 6); Hh = len(rows) * (h * s + 18)
canvas = Image.new('RGB', (W, Hh), 'white'); dr = ImageDraw.Draw(canvas)
for ri, r in enumerate(rows):
    for ci, (n, t) in enumerate(r):
        im = Image.fromarray(t).resize((w * s, h * s), Image.NEAREST)
        canvas.paste(im, (ci * (w * s + 6), ri * (h * s + 18) + 14)); dr.text((ci * (w * s + 6) + 2, ri * (h * s + 18)), n, fill='black')
canvas.save(out)
