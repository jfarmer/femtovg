# area_strip.py OUT KEY zooms=1.5,3,4 crop=x,y,w,h scale=N [exact=PATTERN with {fr}] [extra=TAG:PATTERN,...]
# Rows = zooms; panels: femtovg master, corner-area build, WebKit, Chromium, Firefox, then each one's difference
# from the exact area (grey = |d| x 8, red = beyond 8/255, count of such px in the whole frame on the label).
import sys, os, numpy as np
from PIL import Image, ImageDraw, ImageFont
from cmp import ref, load, fem
T = os.path.expanduser('~/src/femtovg-wt/runs/zoom/triage/clip-edges')
FR = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05', 0.33: 'z033', 0.25: 'z025'}
out, key = sys.argv[1], sys.argv[2]
o = dict(a.split('=', 1) for a in sys.argv[3:])
zooms = [float(v) for v in o['zooms'].split(',')]; zooms = [int(z) if z == int(z) else z for z in zooms]
crops = {float(k): list(map(int, v.split(','))) for k, v in (c.split(':') for c in o['crops'].split(';'))}
PW = int(o.get('pw', 300))
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 13)
cols = [('femtovg master', lambda z, fr: fem(key, z))] + ([] if o.get('nocorner') else [('master + exact corner area', lambda z, fr: load(f'{T}/png/area/{key}_{fr}.png'))])
for e in [v for v in o.get('extra', '').split(',') if v]:
    tag, pat = e.split(':', 1); cols.append((tag, lambda z, fr, pat=pat: load(pat.format(fr=fr))))
cols += [('WebKit', lambda z, fr: ref('wk', key, z)), ('Chromium (software)', lambda z, fr: ref('chr', key, z)), ('Firefox', lambda z, fr: ref('ff', key, z))]
rows = []
for z in zooms:
    fr = FR[z]
    x, y, w, h = crops[float(z)]
    ex = load(o['exact'].format(fr=fr)) if 'exact' in o else load(f'{T}/area/id_{key}_{fr}.png')
    tiles, diffs = [], []
    for name, get in cols:
        img = get(z, fr)
        if img is None: tiles.append((name + ': no frame', None)); diffs.append(('', None)); continue
        img = img[..., :3]
        d = np.abs(img - ex[..., :3]).max(-1)
        dd = np.stack([np.clip(255 - d * 8, 0, 255)] * 3, -1).astype(np.uint8); dd[d > 8] = [220, 30, 30]
        tiles.append((f'{name}', img[y:y + h, x:x + w])); diffs.append((f'vs exact area: {int((d > 8).sum())} px > 8/255, max {int(d.max())}', dd[y:y + h, x:x + w]))
    rows.append((z, (x, y, w, h), tiles, diffs))
pad, lab = 8, 18
sizes = [(PW, int(PW * c[3] / c[2])) for _, c, _, _ in rows]
W = len(cols) * (PW + pad) + pad; Hh = sum(2 * (ph + lab) + 24 for _, ph in sizes) + pad
cv = Image.new('RGB', (W, Hh), (40, 40, 40)); dr = ImageDraw.Draw(cv)
yy = pad
for (z, (x, y, w, h), tiles, diffs), (pw, ph) in zip(rows, sizes):
    dr.text((pad, yy), f'{o.get("label", key)}   zoom {z:g}   crop {x},{y} {w}x{h} at {pw / w:.1f}x', fill='white', font=font); yy += 20
    for r in (tiles, diffs):
        for i, (t, a) in enumerate(r):
            xx = pad + i * (pw + pad)
            dr.text((xx, yy), t, fill='white', font=font)
            if a is not None: cv.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((pw, ph), Image.NEAREST), (xx, yy + lab))
        yy += ph + lab
    yy += 4
cv.save(out)
print(out, cv.size)
