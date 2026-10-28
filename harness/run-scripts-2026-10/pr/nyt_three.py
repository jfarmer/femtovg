#!/usr/bin/env python3
"""Fringe fills vs exact-coverage fills vs Chromium: one row per name:framing[:crop x,y,w,h in z1 box units], panels
master | #358 | Chromium 131, each crop scaled up with nearest-neighbour; the caption carries each build's ink weight and
pixels beyond 20/255 against Chromium within the crop.
  nyt_three.py OUT.png name:framing[:x,y,w,h] ..."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.abspath(__file__))
files = {f['key']: f for f in json.load(open(f'{R}/files.json'))}
font = lambda s: ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', s)
Z = {'z01': 0.1, 'z025': 0.25, 'z05': 0.5, 'z1': 1, 'z2': 2, 'z4': 4}
lum = lambda X: 0.299 * X[:, :, 0] + 0.587 * X[:, :, 1] + 0.114 * X[:, :, 2]
rows = []
for spec in sys.argv[2:]:
    parts = spec.split(':'); name, fr = parts[0], parts[1]; crop = [float(v) for v in parts[2].split(',')] if len(parts) > 2 else None
    k = [k for k in files if k.endswith('__' + name)][0]
    ims = {b: Image.open(f'{R}/png_nyt/{b}_{k}_{fr}.png').convert('RGB') for b in ('master', 'tf')}
    ims['chr'] = Image.open(f'{R}/refs/chr_{k}_{fr}.png').convert('RGB')
    A = {b: np.asarray(im, dtype=np.int16) for b, im in ims.items()}
    if crop and fr == 'hd':
        box = [int(420 + 5.4 * crop[0]), int(5.4 * crop[1]), int(np.ceil(420 + 5.4 * (crop[0] + crop[2]))), int(np.ceil(5.4 * (crop[1] + crop[3])))]
    elif crop:
        z = Z[fr]; x0 = 230 + z * (130 + crop[0] - 230); y0 = 130 + z * (30 + crop[1] - 130)
        box = [int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x0 + z * crop[2])), int(np.ceil(y0 + z * crop[3]))]
    else:
        ink = np.zeros(A['chr'].shape[:2], bool)
        for X in A.values(): ink |= X.sum(axis=2) < 765
        ys, xs = np.nonzero(ink); box = [xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3]
    W, H = ims['chr'].size; box = [max(0, box[0]), max(0, box[1]), min(W, box[2]), min(H, box[3])]
    sl = (slice(box[1], box[3]), slice(box[0], box[2]))
    wc = (255 - lum(A['chr'])[sl]).sum()
    stat = {}
    for b in ('master', 'tf'):
        d = np.abs(A[b] - A['chr']).max(axis=2)[sl]
        stat[b] = (100 * ((255 - lum(A[b])[sl]).sum() - wc) / max(wc, 1), 100 * (d > 20).mean(), int(d.max()))
    panels = [ims[b].crop(box) for b in ('master', 'tf', 'chr')]
    w, h = panels[0].size; s = max(1, 140 // h)
    panels = [p.resize((w * s, h * s), Image.NEAREST) for p in panels]
    label = f"{name} {fr} ({w}x{h} px): fringe ink {stat['master'][0]:+.0f} %, {stat['master'][1]:.1f} % beyond 20/255 (max {stat['master'][2]})  |  exact coverage ink {stat['tf'][0]:+.0f} %, {stat['tf'][1]:.1f} % (max {stat['tf'][2]})"
    rows.append((label, panels)); print(label)
gap, cap = 8, 30
width = max(max(sum(p.size[0] for p in ps) + 4 * gap for _, ps in rows), 900)
height = sum(ps[0].size[1] + cap + gap for _, ps in rows) + gap + 4
sheet = Image.new('RGB', (width, height), 'white'); dr = ImageDraw.Draw(sheet); y = gap
for label, ps in rows:
    dr.text((gap, y), label, fill=(0, 0, 0), font=font(12)); x = gap
    for p, n in zip(ps, ['master (fringe fills)', '#358 (exact coverage)', 'Chromium 131']):
        dr.text((x, y + 15), n, fill=(90, 90, 90), font=font(10)); sheet.paste(p, (x, y + cap)); dr.rectangle([x - 1, y + cap - 1, x + p.size[0], y + cap + p.size[1]], outline=(200, 200, 200)); x += p.size[0] + gap
    y += ps[0].size[1] + cap + gap
sheet.save(sys.argv[1]); print(sys.argv[1], sheet.size)
