#!/usr/bin/env python3
"""Evidence sheet: rows of (before | after | Chromium | diff before | diff after) crops for chosen (key, framing, box)
with the red/orange diff panels (>20/255 red, 8-20 orange), plus a markdown table of the numbers.
  sheet.py OUT.png before_build after_build key:framing[:x,y,w,h[:scale]] ...
A scale of n shows the crop at 1/n: images box-filtered, the diff panels by the block maximum, so a
single deviating pixel still shows."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.abspath(__file__))
out, before, after = sys.argv[1], sys.argv[2], sys.argv[3]
rows = [json.loads(l) for l in open(f'{R}/accuracy.jsonl')]
acc = {(r['key'], r['framing'], r['build']): r for r in rows if 'vs_chr' in r}
files = {f['key']: f for f in json.load(open(f'{R}/files.json'))}
def load(p): return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
def heat(a, c, scale=1):
    dm = np.abs(a - c).max(axis=2)
    if scale > 1:
        hh, ww = dm.shape[0] // scale * scale, dm.shape[1] // scale * scale
        dm = dm[:hh, :ww].reshape(hh // scale, scale, ww // scale, scale).max(axis=(1, 3))
    h = np.full(dm.shape + (3,), 255, np.uint8); h[dm > 8] = [255, 160, 0]; h[dm > 20] = [255, 0, 0]
    return h
def shrink(im, scale):
    if scale == 1: return im
    w, h = im.shape[1] // scale, im.shape[0] // scale
    return np.asarray(Image.fromarray(im).resize((w, h), Image.BOX))
def font(size):
    try: return ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', size)
    except Exception: return ImageFont.load_default()
panels = []
table = ['| file | framing | before px>20 / structural | after | Chromium vs Firefox |', '|---|---|---:|---:|---:|']
for spec in sys.argv[4:]:
    parts = spec.split(':'); key, fr = parts[0], parts[1]
    box = tuple(int(v) for v in parts[2].split(',')) if len(parts) > 2 else None
    scale = int(parts[3]) if len(parts) > 3 else 1
    k = [f['key'] for f in files.values() if f['key'].endswith('__' + key) or f['key'] == key][0]
    a = load(f'{R}/png/{before}_{k}_{fr}.png'); b = load(f'{R}/png/{after}_{k}_{fr}.png'); c = load(f'{R}/refs/chr_{k}_{fr}.png')
    h, w = min(a.shape[0], b.shape[0], c.shape[0]), min(a.shape[1], b.shape[1], c.shape[1]); a, b, c = a[:h, :w], b[:h, :w], c[:h, :w]
    if box:
        x, y, bw, bh = box; a, b, c = (im[y:y + bh, x:x + bw] for im in (a, b, c))
    imgs = [shrink(im.astype(np.uint8), scale) for im in (a, b, c)] + [heat(a, c, scale), heat(b, c, scale)]
    panels.append((key, fr, [Image.fromarray(im) for im in imgs]))
    rb, ra = acc[(k, fr, before)], acc[(k, fr, after)]
    env = ra.get('chr_vs_ff', {}).get('px20', float('nan'))
    table.append(f"| {key} | {fr} | {rb['vs_chr']['px20']:.2f} % / {rb['vs_chr']['struct']:.3f} % | {ra['vs_chr']['px20']:.2f} % / {ra['vs_chr']['struct']:.3f} % | {env:.2f} % |")
labels = ['before', 'after', 'Chromium 131', 'before vs Chromium', 'after vs Chromium']
pw = max(p.width for _, _, ps in panels for p in ps); ph = sum(max(p.height for p in ps) + 30 for _, _, ps in panels) + 24
W = 5 * (pw + 8) + 8; im = Image.new('RGB', (W, ph), 'white'); d = ImageDraw.Draw(im); f12, f13 = font(12), font(13)
for i, l in enumerate(labels): d.text((8 + i * (pw + 8), 4), l, fill='#555', font=f12)
y = 24
for key, fr, ps in panels:
    d.text((8, y), f'{key} at {fr}', fill='black', font=f13); y += 18
    for i, p in enumerate(ps): im.paste(p, (8 + i * (pw + 8), y))
    y += max(p.height for p in ps) + 12
im.save(out); print('\n'.join(table)); print('wrote', out, im.size)
