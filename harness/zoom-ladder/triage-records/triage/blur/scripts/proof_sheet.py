# Proof sheet: femtovg and Chromium at zoom 0.5 beside the analytic Gaussian and Skia's
# three-box model, with >8/255 maps. Rows: blur-variation-4-4-15 (device sigma 2,2),
# blur-variation-6-4-11 (3,2), 2d.layer.anisotropic-blur.isotropic (2,2, wider region).
import sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from exact_rect import exact_profile, threebox_profile, compose
R = '/Users/matt/src/femtovg-wt/runs/zoom/'
W, H = 460, 260
rows = [('blur-variation-4-4-15  device sigma 2,2', 'corpus__wpt-fegaussianblur-reftests__blur-variation-4-4-15', (205,105,235,135), (205,105,235,135), (2,2), (0,128,0), (200,100,40,40)),
        ('blur-variation-6-4-11  device sigma 3,2', 'corpus__wpt-fegaussianblur-reftests__blur-variation-6-4-11', (205,105,235,135), (205,105,235,135), (3,2), (0,128,0), (200,100,40,40)),
        ('2d.layer.anisotropic-blur.isotropic  device sigma 2,2', 'corpus__wpt-layer-blur-reftests__2d.layer.anisotropic-blur.isotropic', (205,105,255,155), (180,80,280,180), (2,2), (0,128,128), (198,98,30,30))]
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 13)
S = 6
def L(p): return np.asarray(Image.open(p).convert('RGB')).astype(float)
def diff(a, b):
    d = np.abs(a-b).max(axis=2); img = np.stack([np.clip(d*4, 0, 255)]*3, -1); img[d > 8] = [230, 30, 30]
    return img, int((d > 8).sum()), int(round(d.max()))
tiles_all = []
for title, key, r, g, (sx, sy), col, crop in rows:
    ex = compose(exact_profile(W, r[0], r[2], sx, g[0], g[2]), exact_profile(H, r[1], r[3], sy, g[1], g[3]), col)
    tb = compose(threebox_profile(W, r[0], r[2], sx, g[0], g[2])[0], threebox_profile(H, r[1], r[3], sy, g[1], g[3])[0], col)
    f = L(R+f'png/zl_zm_svg/{key}/14.png'); c = L(R+f'fresh/refs/chr_{key}_z05.png')
    ts = [('femtovg master', f), ('Chromium 131', c), ('exact Gaussian', ex), ('Skia three-box model', tb)]
    for n, a, b in [('femtovg vs Chromium', f, c), ('femtovg vs exact', f, ex), ('Chromium vs exact', c, ex), ('Chromium vs 3-box model', c, tb)]:
        img, k, m = diff(a, b); ts.append((f'{n}: {k} px, max {m}', img))
    tiles_all.append((title, ts, crop))
x, y, w, h = tiles_all[0][2]
tw, th = 40*S, 40*S
pad, top, rowh = 8, 22, 40*S + 22 + 22
sheet = Image.new('RGB', (8*(tw+pad)+pad, len(tiles_all)*rowh + 30), (40, 40, 40))
d = ImageDraw.Draw(sheet)
d.text((pad, 6), 'zoom 0.5: femtovg is the Gaussian; Chromium (and Firefox, identical to 1/255) is the SVG-spec three-box approximation (Skia legacy raster blur)', fill=(255,255,255), font=font)
for ri, (title, ts, (cx, cy, cw, ch)) in enumerate(tiles_all):
    oy = 30 + ri*rowh
    d.text((pad, oy), title, fill=(255, 220, 120), font=font)
    for i, (n, a) in enumerate(ts):
        im = Image.fromarray(np.clip(a[cy:cy+ch, cx:cx+cw], 0, 255).astype(np.uint8)).resize((tw, th), Image.NEAREST)
        ox = pad + i*(tw+pad)
        d.text((ox, oy+18), n, fill=(255, 255, 255), font=font)
        sheet.paste(im, (ox, oy+18+top-4))
out = sys.argv[1]
sheet.save(out); print(out, sheet.size)
