#!/usr/bin/env python3
"""strip.py OUT.png ROWS... : five-column comparison strip. Each ROW is label=REF,BEFORE,AFTER (PNG paths, same
size) or label=REF,BEFORE,AFTER@x0,y0,x1,y1 to crop all three to that box first. Columns: before, after, the
reference, before vs the reference and after vs the reference (the reference in grey, red where a channel differs
by more than 20, orange by more than 8, and - at a SCALE of 8 or more - the pixels before and after differ at by
more than 2 outlined in magenta). Panels are scaled by SCALE (env, default 2) with nearest neighbour. Prints per row the pixels more than
20 off the reference, before and after."""
import os, sys
from PIL import Image, ImageDraw
import numpy as np

SCALE = int(os.environ.get('SCALE', 2))
out, rows = sys.argv[1], sys.argv[2:]
HEADS = ['before (master)', 'after (this PR)', 'Chromium', 'before vs Chromium', 'after vs Chromium']


def load(path, box):
    im = Image.open(path).convert('RGB')
    if box:
        im = im.crop(box)
    return np.asarray(im).astype(int)


def diff_panel(ref, img):
    d = np.abs(ref - img).max(axis=2)
    g = (ref.mean(axis=2) * 0.35 + 120).clip(0, 255).astype('uint8')
    panel = np.stack([g, g, g], 2)
    panel[(d > 8) & (d <= 20)] = [255, 170, 0]
    panel[d > 20] = [230, 0, 0]
    return panel, int((d > 20).sum())


panels, labels = [], []
for row in rows:
    label, spec = row.split('=', 1)
    files, _, box = spec.partition('@')
    box = tuple(int(v) for v in box.split(',')) if box else None
    ref, before, after = (load(p, box) for p in files.split(','))
    db, nb = diff_panel(ref, before)
    da, na = diff_panel(ref, after)
    moved = np.abs(before - after).max(axis=2) > 2
    panels.append([before.astype('uint8'), after.astype('uint8'), ref.astype('uint8'), db, da, moved])
    labels.append(label)
    print(f'{label}: pixels more than 20 off Chromium: before {nb}, after {na}')

pad, head, side = 8, 22, 0
pw = max(p[0].shape[1] for p in panels) * SCALE
ph = [p[0].shape[0] * SCALE for p in panels]
width = 5 * pw + 6 * pad
height = head + sum(h + 20 + pad for h in ph) + pad
sheet = Image.new('RGB', (width, height), 'white')
draw = ImageDraw.Draw(sheet)
for c, title in enumerate(HEADS):
    draw.text((pad + c * (pw + pad), 6), title, fill='black')
y = head
for label, row, h in zip(labels, panels, ph):
    draw.text((pad, y), label, fill='black')
    y += 16
    moved = row[5]
    for c, arr in enumerate(row[:5]):
        im = Image.fromarray(arr).resize((arr.shape[1] * SCALE, arr.shape[0] * SCALE), Image.NEAREST)
        x0 = pad + c * (pw + pad)
        sheet.paste(im, (x0, y))
        if c >= 3 and SCALE >= 8:
            for py, px in zip(*np.nonzero(moved)):
                draw.rectangle([x0 + px * SCALE, y + py * SCALE, x0 + (px + 1) * SCALE - 1, y + (py + 1) * SCALE - 1],
                               outline=(255, 0, 255), width=max(1, SCALE // 8))
    y += h + pad + 4
sheet.save(out)
print('wrote', out, sheet.size)
