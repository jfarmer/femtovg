#!/usr/bin/env python3
"""Comparison sheet for an issue: one row per reftest, panels femtovg | Chromium | Firefox | diff (femtovg vs Chromium),
cropped to the 200-unit box of the framing, with a caption row.
  issue_sheet.py OUT.png <build> name:framing[:label] ...   (frames from png_wpt/ or png/, refs from refs/)"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.abspath(__file__))
files = {f['key']: f for f in json.load(open(f'{R}/files.json'))}
def key(name):
    hits = [k for k in files if k.endswith('__' + name)]
    assert len(hits) == 1, (name, hits)
    return hits[0]
def font(size):
    for p in ('/System/Library/Fonts/Helvetica.ttc', '/System/Library/Fonts/SFNS.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()
def frame(build, k, fr):
    for d in ('png_wpt', 'png'):
        p = f'{R}/{d}/{build}_{k}_{fr}.png'
        if os.path.exists(p):
            return Image.open(p).convert('RGB')
    raise SystemExit(f'no frame for {build} {k} {fr}')
out, build = sys.argv[1], sys.argv[2]
rows = []
for spec in sys.argv[3:]:
    parts = spec.split(':', 2)
    name, fr = parts[0], parts[1]
    label = parts[2] if len(parts) > 2 else name
    k = key(name)
    a = frame(build, k, fr); c = Image.open(f'{R}/refs/chr_{k}_{fr}.png').convert('RGB')
    ffp = f'{R}/refs/ff_{k}_{fr}.png'; f = Image.open(ffp).convert('RGB') if os.path.exists(ffp) else None
    d = np.abs(np.asarray(a, dtype=np.int16) - np.asarray(c, dtype=np.int16)).max(axis=2)
    heat = np.full(d.shape + (3,), 255, np.uint8); heat[(d > 0) & (d <= 20)] = [255, 170, 60]; heat[d > 20] = [220, 30, 30]
    pct = 100 * (d > 20).mean()
    box = (0, 0, 1920, 1080) if fr == 'hd' else (120, 20, 340, 240)
    panels = [im.crop(box) for im in ([a, c] + ([f] if f is not None else []) + [Image.fromarray(heat)])]
    rows.append((f'{label}  ({fr}: {pct:.1f} % of the frame beyond 20/255)', panels, f is not None))
pw, ph = rows[0][1][0].size
cols = max(len(r[1]) for r in rows)
gap, cap = 8, 22
sheet = Image.new('RGB', (cols * pw + (cols + 1) * gap, len(rows) * (ph + cap + 18) + gap), 'white')
dr = ImageDraw.Draw(sheet); f13 = font(13); f11 = font(11)
for i, (label, panels, has_ff) in enumerate(rows):
    y = gap + i * (ph + cap + 18)
    dr.text((gap, y), label, fill=(0, 0, 0), font=f13)
    names = ['femtovg', 'Chromium 131'] + (['Firefox'] if has_ff else []) + ['diff: red > 20/255, orange 1-20']
    for j, (p, n) in enumerate(zip(panels, names)):
        x = gap + j * (pw + gap)
        dr.text((x, y + cap - 4), n, fill=(90, 90, 90), font=f11)
        sheet.paste(p, (x, y + cap + 10)); dr.rectangle([x - 1, y + cap + 9, x + pw, y + cap + 10 + ph], outline=(200, 200, 200))
sheet.save(out); print(out, sheet.size)
