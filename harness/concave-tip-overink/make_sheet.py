#!/usr/bin/env python3
"""The issue's sheet: before (master 06243b80) | after (the same frame with every fill through an exact-area
coverage mask, harness FILL_MASKS) | Chromium 131 | before vs Chromium | after vs Chromium. A difference panel is
white within 8/255, orange from 9 to 20 and red beyond. Crops are magnified nearest-neighbour.

  make_sheet.py RUN OUT.png [BUSEY_REFS]"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RUN, OUT = sys.argv[1], sys.argv[2]
BUSEY = sys.argv[3] if len(sys.argv) > 3 else os.path.expanduser('~/src/femtovg-wt/runs/busey/refs')
M = json.load(open(f'{RUN}/measure.json'))
ZOOM, CW, CH = 5, 40, 30


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)


def crop(im, cx, cy):
    x0, y0 = cx - CW // 2, cy - CH // 2
    return im[y0:y0 + CH, x0:x0 + CW]


def picture(a):
    return Image.fromarray(a.astype(np.uint8)).resize((CW * ZOOM, CH * ZOOM), Image.NEAREST)


def heat(a, b):
    d = np.abs(a - b).max(axis=2)
    h = np.full(d.shape + (3,), 255, np.uint8)
    h[d > 8] = [255, 160, 0]
    h[d > 20] = [255, 0, 0]
    return Image.fromarray(h).resize((CW * ZOOM, CH * ZOOM), Image.NEAREST), int((d > 20).sum())


def portrait(name, framing, cx, cy, where, other=''):
    k = f'corpus__buseybench__{name}_{framing}'
    p = M['portraits'][f'{name}_{framing}']
    cap = (f'{name}.svg at {framing} ({FR[framing]}), {where}. Both tip windows: {p["master_tips"]} -> '
           f'{p["masks_tips"]} px more than 20/255 off all three browsers')
    return (cap, load(f'{RUN}/png/port/master_{name}_{framing}.png'), load(f'{RUN}/png/port/masks_{name}_{framing}.png'),
            load(f'{BUSEY}/chr_{k}.png'), load(f'{BUSEY}/id_{k}.png'), cx, cy, other)


def reduction(name, cx, cy, what, other=''):
    r = M['reductions'][name]
    cap = (f'{name}.svg at z2 ({FR["z2"]}), {what}. Tip ink {r["ink_master"]:.2f} -> {r["ink_masks"]:.2f} of the '
           f'area (Chromium {r["ink_chr"]:.2f}); {r["off3_master"]} -> {r["off3_masks"]} px off all three browsers')
    return (cap, load(f'{RUN}/png/red/master_{name}_z2.png'), load(f'{RUN}/png/red/masks_{name}_z2.png'),
            load(f'{RUN}/refs/chr_ct__{name}_z2.png'), load(f'{RUN}/refs/id_ct__{name}_z2.png'), cx, cy, other)


FR = {'z1': '460x260, 200 px box at 1x', 'z2': '460x260, 200 px box at 2x', 'hd': '1920x1080, 1080 px box'}
# The last argument says in words what red is left on the after panel where the after frame is itself off the area
# reference (red where only Chromium is off the area reference is counted and said by the loop below).
ROWS = [
    portrait('grok-4-5', 'z2', 72, 44, 'left lower hair spike (line 153)'),
    portrait('grok-4-5', 'hd', 515, 284, 'the same spike at 1080p'),
    portrait('gemini-3-7-flash', 'z2', 171, 190, 'left mouth corner, the lip crescent (line 562)',
             'away from the crescent, at a tooth corner and on a cheek line'),
    portrait('gemini-3-1-pro-preview', 'z2', 146, 217, 'left mouth corner, the lower lip (line 293)',
             'that is 16-19 off Firefox, WebKit and the area reference'),
    reduction('wedge', 150, 218, 'left tip: a straight wedge, one segment a side'),
    reduction('wedge-split', 150, 218, 'left tip: the same wedge, each side in 18 collinear pieces'),
    reduction('lip', 146, 220, 'left tip: the lower lip of gemini-3-1-pro-preview alone'),
]
LABELS = ['before: master 06243b80', 'after: exact-area masks', 'Chromium 131', 'before vs Chromium',
          'after vs Chromium']


def font(size):
    return ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', size)


F_HEAD, F_CAP, F_NOTE, F_LABEL = font(14), font(15), font(13), font(14)
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
for i, (cap, before, after, chrome, area, cx, cy, other) in enumerate(ROWS):
    b, a, c, r = (crop(im, cx, cy) for im in (before, after, chrome, area))
    hb, nb = heat(b, c)
    ha, na = heat(a, c)
    # Red left after: where the after frame is within 8 of the area reference, so Chromium is the one off it.
    red = np.abs(a - c).max(axis=2) > 20
    chr_off, after_off = np.abs(c - r).max(axis=2), np.abs(a - r).max(axis=2)
    theirs = red & (after_off <= 8)
    note = ''
    if theirs.any():
        note = (f'Red left on the after panel: {theirs.sum()} px where the after frame is within {after_off[theirs].max()}/255 '
                f'of the area reference and Chromium {chr_off[theirs].min()}-{chr_off[theirs].max()} off it')
    rest = int((red & ~theirs).sum())
    if rest:
        assert other, f'row {i}: {rest} px of red left after with no words for it'
        note += ('; ' if note else 'Red left on the after panel: ') + f'{rest} px {other}'
    rows.append((wrap(cap, F_CAP), wrap(note, F_NOTE) if note else [], [picture(b), picture(a), picture(c), hb, ha]))
    print(f'row {i}: crop red vs Chromium before {nb}, after {na}. {note}')

HEADER = ('before: femtovg master 06243b80 on WGPU. after: the same frame with every fill drawn through an exact-area '
          'coverage mask (harness FILL_MASKS). Difference maps: red beyond 20/255, orange 9-20/255. All three browsers: '
          'Chromium 131, Firefox 159, WebKit (macOS 27.2). Tip windows: 28 x 28 px on each tip. Crops 5x, nearest '
          'neighbour.')
head = wrap(HEADER, F_HEAD)
CAP_LH, NOTE_LH, LABEL_H, HEAD_LH = 19, 17, 20, 18
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
