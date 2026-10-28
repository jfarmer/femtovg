#!/usr/bin/env python3
"""The issue's sheet: before (master 06243b80) | after (variants.patch at SV_V=4) | WebKit | before vs WebKit | after vs
WebKit, the five panels stacked, since the sliver is 160 times as long as it is tall. A difference panel is white within
8/255, orange from 9 to 20 and red beyond. Crops are magnified nearest-neighbour.

  make_sheet.py OUT.png"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
ZOOM = 6
W, H = 153, 6  # crop: 153 x 6 px, 918 x 36 on the sheet


def load(name):
    return np.asarray(Image.open(f'{HERE}/{name}').convert('RGB'), dtype=np.int16)


def crop(a, x0, y0):
    return a[y0:y0 + H, x0:x0 + W]


def picture(a):
    return Image.fromarray(a.astype(np.uint8)).resize((W * ZOOM, H * ZOOM), Image.NEAREST)


def heat(a, b):
    d = np.abs(a - b).max(axis=2)
    h = np.full(d.shape + (3,), 255, np.uint8)
    h[d > 8] = [255, 160, 0]
    h[d > 20] = [255, 0, 0]
    return Image.fromarray(h).resize((W * ZOOM, H * ZOOM), Image.NEAREST), int((d > 20).sum()), int((d > 8).sum())


FRAME = '460x260 frame, 200 px box'
ROWS = [
    (f'fill-path-subpixel-sliver-control.svg at zoom 3 ({FRAME} at 3x), the left end: x 0-152, y 129-134',
     'frames/master_z3.png', 'frames/prototype_z3.png', 'frames/wk_z3.png', 0, 129),
    (f'fill-path-subpixel-sliver-control.svg at zoom 4 ({FRAME} at 4x), the left end: x 0-152, y 129-134',
     'frames/master_z4.png', 'frames/prototype_z4.png', 'frames/wk_z4.png', 0, 129),
    (f'probes/s_flat_dy0.25.svg at zoom 3: a shorter sliver (380 x 3 px, 0.9 deg corners), 0.25 px lower, both tips on the canvas; the left tip: '
     f'x 30-182, y 129-134', 'probes/s_flat_dy0.25_master.png', 'probes/s_flat_dy0.25_prototype.png',
     'probes/s_flat_dy0.25_wk.png', 30, 129),
]
LABELS = ['before: master 06243b80', 'after: prototype', 'WebKit (macOS 27.2)', 'before vs WebKit', 'after vs WebKit']


def font(size):
    return ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', size)


F_HEAD, F_CAP, F_NOTE, F_LABEL = font(14), font(15), font(13), font(13)
gap, pw, ph = 8, W * ZOOM, H * ZOOM
width = pw + 2 * gap


def wrap(text, f, w=width - 2 * gap):
    lines, line = [], ''
    for word in text.split(' '):
        t = (line + ' ' + word).strip()
        if line and f.getlength(t) > w:
            lines.append(line)
            line = word
        else:
            line = t
    return lines + ([line] if line else [])


rows = []
for i, (cap, before, after, ref, x0, y0) in enumerate(ROWS):
    B, A, R = load(before), load(after), load(ref)
    b, a, r = crop(B, x0, y0), crop(A, x0, y0), crop(R, x0, y0)
    hb, nb, _ = heat(b, r)
    ha, na, _ = heat(a, r)
    # Whole-frame counts beyond 8/255, as the ladder counts.
    fb = int((np.abs(B - R).max(axis=2) > 8).sum())
    fa = int((np.abs(A - R).max(axis=2) > 8).sum())
    cap += f'. Red in the crop: {nb} -> {na} px; beyond 8/255 in the whole frame: {fb} -> {fa} px'
    assert na == 0 and fa == 0, f'row {i}: red left after; caption it'
    rows.append((wrap(cap, F_CAP), [picture(b), picture(a), picture(r), hb, ha]))
    print(f'row {i}: {cap}')

HEADER = ('before: femtovg master 06243b80 on WGPU. after: the prototype, variants.patch at SV_V=4 (a convex '
          'contour\'s beveled corner takes bevel_join, its inset at the uncapped miter). The reference is WebKit, '
          'which is within 8/255 of the 8x area reference on both ladder frames and within 8/255 of the exact area '
          'on the probe; Chromium 131 and Firefox 159 are 334 px off the area on the ladder frames. Difference maps '
          'against WebKit: red beyond 20/255, orange 9-20/255. Crops 6x, nearest neighbour; the five panels are '
          'stacked because the sliver is 160 times as long as it is tall. No red is left on any after panel.')
head = wrap(HEADER, F_HEAD)
CAP_LH, LABEL_H, HEAD_LH = 19, 18, 18
head_h = HEAD_LH * len(head) + 10


def row_h(caps):
    return CAP_LH * len(caps) + 4 + 5 * (LABEL_H + ph + 6) + gap


height = gap + head_h + sum(row_h(cp) for cp, _ in rows)
sheet = Image.new('RGB', (width, height), 'white')
draw = ImageDraw.Draw(sheet)
for k, line in enumerate(head):
    draw.text((gap, gap + HEAD_LH * k), line, fill=(0, 0, 0), font=F_HEAD)
y = gap + head_h
for caps, panels in rows:
    yy = y
    for line in caps:
        draw.text((gap, yy), line, fill=(0, 0, 0), font=F_CAP)
        yy += CAP_LH
    yy += 4
    for j, p in enumerate(panels):
        draw.text((gap, yy + 1), LABELS[j], fill=(90, 90, 90), font=F_LABEL)
        sheet.paste(p, (gap, yy + LABEL_H))
        draw.rectangle([gap - 1, yy + LABEL_H - 1, gap + pw, yy + LABEL_H + ph], outline=(200, 200, 200))
        yy += LABEL_H + ph + 6
    y += row_h(caps)
sheet.save(OUT)
print(OUT, sheet.size)
