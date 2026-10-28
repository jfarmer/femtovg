#!/usr/bin/env python3
"""The issue's sheet: before (master 06243b80) | after (all-masks-experiment.patch, ZL_ALL_MASKS=1) | Chromium 131 |
before vs Chromium | after vs Chromium. A difference panel is white within 8/255, orange from 9 to 20 and red beyond.
Crops are magnified 8x, nearest neighbour. Frames as in measure.py.

  sheet.py OUT.png"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
H = os.path.expanduser('~/src/femtovg-wt/runs/zoom')
W = os.path.expanduser('~/src/femtovg-wt/runs/zoom/drafts/N10-corner-coverage/work')
KEY = 'wpt22__21-degenerate-paths-dashes-and-joins__resvg-dasharray-0-n-square-caps-ref'
LADDER = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
FR = {1.25: 'z125', 0.75: 'z075', 0.33: 'z033', 0.25: 'z025'}
CW, CH, ZOOM = 22, 13, 8
FILE = 'resvg-dasharray-0-n-square-caps-ref.svg'


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)


def ladder(z, x, y, what, other=''):
    frames = (load(f'{H}/png/zl_zm_svg/{KEY}/{LADDER.index(z):02}.png'),
              load(f'{H}/triage/dasharray/exp/mask_resvg-dasharray-0-n-square-caps-ref_{z:g}.png'),
              load(f'{H}/fresh/refs/chr_{KEY}_{FR[z]}.png'))
    return (f'{FILE} at zoom {z:g}: {what}', [tuple(f[y:y + CH, x:x + CW] for f in frames)], other)


def corners(fs, other=''):
    # corners.svg at 1x: one tile per rect, 4 px wide, its top-left corner pixel second from the left, top row.
    P = f'{H}/triage/dasharray/repro'
    frames = (load(f'{W}/corners_master_z1.png'), load(f'{W}/corners_allmasks_z1.png'), load(f'{P}/chr_corners.png'))
    tiles = []
    for f in fs:
        x = 140 + 30 * [0, 0.1, 0.25, 0.5, 0.75, 0.9].index(f)
        tiles.append(tuple(a[39:39 + CH, x - 1:x + 3] for a in frames))
    return ('corners.svg at 1x: one rect\'s top-left corner per tile, on f = ' + ', '.join(f'{f:g}' for f in fs)
            + ' of a pixel in x and y (left to right)', tiles, other)


ROWS = [
    ladder(0.25, 210, 110, 'rects 5 px wide, every edge on a half pixel; the master corners are 0.50 where the '
           'browsers and the area are 0.25'),
    ladder(0.33, 204, 104, 'edges on 0.1 to 0.9 of a pixel; a 0.1 x 0.9 corner errs by under 8/255'),
    ladder(1.25, 136, 37, 'one rect\'s top-left corner, on (142.5, 42.5)'),
    ladder(1.25, 100, 0, 'the 1 px frame\'s top-left corner, a stroke 1.25 px wide: outer corner 0.38 '
           '(the smaller ramp) where the browsers have 0.14, inner corner 0.88 (the larger) where they have 0.98',
           'the frame is a stroke, which the masks do not take'),
    corners([0.1, 0.25, 0.5, 0.75, 0.9]),
]
LABELS = ['before: master 06243b80', 'after: all fills masked', 'Chromium 131', 'before vs Chromium',
          'after vs Chromium']


def heat(d):
    h = np.full(d.shape + (3,), 255, np.uint8)
    h[d > 8] = [255, 160, 0]
    h[d > 20] = [255, 0, 0]
    return h


def panel(tiles, which):
    # One panel from one or more tiles, 4 px of grey between tiles at display scale.
    ims = []
    for t in tiles:
        b, a, c = t
        if which < 3:
            arr = t[which].astype(np.uint8)
        else:
            arr = heat(np.abs((b if which == 3 else a) - c).max(axis=2))
        ims.append(Image.fromarray(arr).resize((arr.shape[1] * ZOOM, arr.shape[0] * ZOOM), Image.NEAREST))
    if len(ims) == 1:
        return ims[0]
    sep = (CW * ZOOM - sum(i.width for i in ims)) // (len(ims) - 1)
    out = Image.new('RGB', (CW * ZOOM, CH * ZOOM), (200, 200, 200))
    x = 0
    for i in ims:
        out.paste(i, (x, 0))
        x += i.width + sep
    return out


def font(size):
    return ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', size)


F_HEAD, F_CAP, F_NOTE, F_LABEL = font(14), font(15), font(13), font(13)
gap, pw, ph = 8, CW * ZOOM, CH * ZOOM
width = gap + 5 * (pw + gap)


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
for i, (cap, tiles, other) in enumerate(ROWS):
    nb = sum(int((np.abs(b - c).max(axis=2) > 20).sum()) for b, a, c in tiles)
    na = sum(int((np.abs(a - c).max(axis=2) > 20).sum()) for b, a, c in tiles)
    cap += f'. Red in the crop: {nb} -> {na} px'
    note = ''
    if na:
        assert other, f'row {i}: {na} px of red left after with no words for it'
        note = f'Red left on the after panel: {na} px, {other}'
    rows.append((wrap(cap, F_CAP), wrap(note, F_NOTE) if note else [], [panel(tiles, k) for k in range(5)]))
    print(f'row {i}: crop red vs Chromium before {nb}, after {na}. {note}')

HEADER = ('before: femtovg master 06243b80 on WGPU, the zoom ladder\'s frames. after: the same build with every fill '
          'sent through #408\'s exact-area masks (all-masks-experiment.patch, ZL_ALL_MASKS=1), geometry unchanged: '
          'a proof of the cause, not a fix. Difference maps against Chromium 131 (Firefox and WebKit within 1/255 '
          'of it in the first four rows, the 8x area reference within 1/255 at the corners of the last): red beyond 20/255, '
          'orange 9-20/255. Crops 8x, nearest neighbour.')
head = wrap(HEADER, F_HEAD)
CAP_LH, NOTE_LH, LABEL_H, HEAD_LH = 19, 17, 19, 18
head_h = HEAD_LH * len(head) + 8


def row_h(caps, notes):
    return CAP_LH * len(caps) + NOTE_LH * len(notes) + LABEL_H + ph + gap + 6


height = gap + head_h + sum(row_h(cp, nt) for cp, nt, _ in rows)
sheet = Image.new('RGB', (width, height), 'white')
draw = ImageDraw.Draw(sheet)
for k, line in enumerate(head):
    draw.text((gap, gap + HEAD_LH * k), line, fill=(0, 0, 0), font=F_HEAD)
y = gap + head_h
for caps, notes, panels in rows:
    yy = y
    for line in caps:
        draw.text((gap, yy), line, fill=(0, 0, 0), font=F_CAP)
        yy += CAP_LH
    for line in notes:
        draw.text((gap, yy), line, fill=(150, 0, 0), font=F_NOTE)
        yy += NOTE_LH
    for j, p in enumerate(panels):
        x = gap + j * (pw + gap)
        assert F_LABEL.getlength(LABELS[j]) <= pw, LABELS[j]
        draw.text((x, yy + 1), LABELS[j], fill=(90, 90, 90), font=F_LABEL)
        sheet.paste(p, (x, yy + LABEL_H))
        draw.rectangle([x - 1, yy + LABEL_H - 1, x + pw, yy + LABEL_H + ph], outline=(200, 200, 200))
    y += row_h(caps, notes)
sheet.save(OUT)
print(OUT, sheet.size)
