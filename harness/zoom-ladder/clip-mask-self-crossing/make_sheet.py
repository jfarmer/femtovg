#!/usr/bin/env python3
"""The issue's sheet: before (master 06243b80, the zoom ladder's frame) | after (master drawing the same region
without crossings: equivalent geometry, not a fix) | WebKit | before vs WebKit | after vs WebKit. A difference panel
is white within 8/255, orange from 9 to 20 and red beyond. Crops are magnified nearest-neighbour.

  make_sheet.py PNG REFS AREA OUT.png

PNG: render.sh's output. REFS: the ladder's browser frames. AREA: the 8x area references (id_*), which the captions use
to say whose error the red and orange left on the after panel is."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PNG, REFS, AREA, OUT = sys.argv[1:5]
KEY = 'wpt22__20-clippath-unions-and-masks__resvg-clippath-multiple-children'
TAG = {1.25: 'z125', 1.75: 'z175'}


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)


def frames(z):
    return (load(f'{PNG}/multiple-children/{z:g}.png'), load(f'{PNG}/multiple-children-uncrossed/{z:g}.png'),
            load(f'{REFS}/wk_{KEY}_{TAG[z]}.png'), load(f'{AREA}/id_{KEY}_{TAG[z]}.png'))


def diff(a, b):
    return np.abs(a - b).max(axis=2)


def picture(a, zoom):
    im = Image.fromarray(a.astype(np.uint8))
    return im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)


def heat(d, zoom, bold):
    if bold:
        # Each deviating pixel with its eight neighbours, so that one pixel shows at 1:1.
        p = np.pad(d, 1)
        d = np.maximum.reduce([p[1 + dy:1 + dy + d.shape[0], 1 + dx:1 + dx + d.shape[1]]
                               for dy in (-1, 0, 1) for dx in (-1, 0, 1)])
    h = np.full(d.shape + (3,), 255, np.uint8)
    h[d > 8] = [255, 160, 0]
    h[d > 20] = [255, 0, 0]
    return picture(h, zoom)


# (zoom, box x, y, w, h, magnification, bold, caption, words for red or orange left on the after panel that the
# loop below does not attribute itself)
ROWS = [
    (1.25, 128, 22, 204, 206, 1, True, '1.25x, the whole star at 1:1, each pixel beyond 8/255 drawn with its eight '
     'neighbours'),
    (1.25, 194, 91, 24, 16, 8, False, '1.25x, the upper left inner vertex: pixel (206, 98) is 155/255 covered; the '
     'exact area is 95, WebKit 95'),
    (1.25, 180, 138, 24, 16, 8, False, '1.25x, the lower left inner vertex: pixels (191, 145) and (191, 146) are 254 '
     'and 124; the exact area 220 and 81, WebKit 221 and 80'),
    (1.75, 164, 145, 24, 16, 8, False, '1.75x, lower left inner vertex: pixel (176, 152), 0.17 / 0.38 / 0.45 at '
     'windings 0 / 1 / 2, folds to 182; exact area 96, WebKit 98'),
]
LABELS = ['before: master 06243b80', 'after: no crossings', 'WebKit (macOS 27.2)', 'before vs WebKit',
          'after vs WebKit']


def font(size):
    return ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', size)


F_HEAD, F_CAP, F_NOTE, F_LABEL = font(14), font(15), font(13), font(13)
gap = 8
pw = max(w * m for _, _, _, w, _, m, _, _ in ROWS)
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


def span(v):
    lo, hi = int(v.min()), int(v.max())
    return f'{lo}' if lo == hi else f'{lo}-{hi}'


rows = []
for z, x, y, w, h, m, bold, cap in ROWS:
    before, after, wk, area = (a[y:y + h, x:x + w] for a in frames(z))
    db, da = diff(before, wk), diff(after, wk)
    cap = f'{cap}. Red in the {"star" if bold else "crop"}: {int((db > 20).sum())} -> ' \
          f'{int((da > 20).sum())} px'
    # What is left on the after panel, beyond 8/255 of WebKit: say whose it is by the area reference.
    left = da > 8
    theirs = left & (diff(after, area) <= 4) & (diff(wk, area) > 4)
    parts = []
    if theirs.any():
        parts.append(f'orange on both, {int(theirs.sum())} px on the r = 10 circle: WebKit {span(diff(wk, area)[theirs])}'
                     f'/255 off the area reference, femtovg within {int(diff(after, area)[theirs].max())}')
    assert not (left & ~theirs).any(), f'{cap}: {int((left & ~theirs).sum())} px left with no words for them'
    note = ('Left on the after panel: ' + '; '.join(parts)) if parts else ''
    panels = [picture(before, m), picture(after, m), picture(wk, m), heat(db, m, bold), heat(da, m, bold)]
    rows.append((wrap(cap, F_CAP), wrap(note, F_NOTE) if note else [], panels))
    print(cap, '|', note)

HEADER = ('resvg-clippath-multiple-children.svg (wpt22 reftests): the frame is 460x260, the 200 px box at 1.25x '
          'and 1.75x. before: femtovg master 06243b80 on WGPU, the zoom ladder\'s frame. after: master drawing the '
          'same clip region without crossings - its outline, a 10-gon, and the inner pentagon '
          'wound against it, under nonzero (multiple-children-uncrossed.svg): equivalent geometry, not '
          'a fix. WebKit is the reference: Chromium 131 is 209 and 212 px beyond 8/255 off the exact star at these '
          'zooms, WebKit 16 and 26, and Firefox was captured for this file only at 1, 2 and 4x. Difference maps '
          'against WebKit: red beyond 20/255, '
          'orange 9-20/255. Crops 8x, nearest neighbour.')
head = wrap(HEADER, F_HEAD)
CAP_LH, NOTE_LH, LABEL_H, HEAD_LH = 19, 17, 19, 18
head_h = HEAD_LH * len(head) + 8


def row_h(caps, notes, panels):
    return CAP_LH * len(caps) + NOTE_LH * len(notes) + LABEL_H + panels[0].height + gap + 6


height = gap + head_h + sum(row_h(*r) for r in rows)
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
        draw.rectangle([x - 1, yy + LABEL_H - 1, x + p.width, yy + LABEL_H + p.height], outline=(200, 200, 200))
    y += row_h(caps, notes, panels)
sheet.save(OUT)
print(OUT, sheet.size)
