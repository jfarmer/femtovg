#!/usr/bin/env python3
"""The issue's sheet: before (master 06243b80) | after (fill-extrusion-bound.patch) | Chromium 131 | before vs Chromium
| after vs Chromium. A difference panel is white within 8/255, orange from 9 to 20 and red beyond. Crops are magnified
nearest-neighbour.

  make_sheet.py RUN OUT.png [BUSEY_REFS]"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RUN, OUT = sys.argv[1], sys.argv[2]
BUSEY = sys.argv[3] if len(sys.argv) > 3 else os.path.expanduser('~/src/femtovg-wt/runs/busey/refs')
CW, CH, ZOOM = 22, 13, 8
FR = {'z1': '460x260, 200 px box at 1x', 'z2': '460x260, 200 px box at 2x', 'hd': '1920x1080, 1080 px box'}


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


def refs_of(prefix):
    # prefix + {chr,ff,wk,id}_ ... : the references that exist (the 8x area reference and Chromium always do).
    return {b: load(prefix.format(b=b)) for b in ('chr', 'ff', 'wk', 'id') if os.path.exists(prefix.format(b=b))}


def portrait(framing, cx, cy, where, other=''):
    k = f'corpus__buseybench__glm-5v-turbo_{framing}'
    cap = f'glm-5v-turbo.svg at {framing} ({FR[framing]}), {where}'
    return (cap, load(f'{RUN}/png/port/master_glm-5v-turbo_{framing}.png'),
            load(f'{RUN}/png/port/after_glm-5v-turbo_{framing}.png'), refs_of(f'{BUSEY}/{{b}}_{k}.png'), cx, cy, other)


def corpus(key, framing, cx, cy, where, other=''):
    cap = f'{where} at {framing} ({FR[framing]})'
    refs = os.path.expanduser('~/src/femtovg-wt/runs/wasmx/refs')
    return (cap, load(f'{RUN}/png/master/{key}_{framing}.png'), load(f'{RUN}/png/after/{key}_{framing}.png'),
            refs_of(f'{refs}/{{b}}_{key}_{framing}.png'), cx, cy, other)


def reduction(name, framing, cx, cy, what, other=''):
    cap = f'{name}.svg at {framing} ({FR[framing]}): {what}'
    return (cap, load(f'{RUN}/png/red/master_{name}_{framing}.png'), load(f'{RUN}/png/red/after_{name}_{framing}.png'),
            refs_of(f'{RUN}/refs/{{b}}_frs__{name}_{framing}.png'), cx, cy, other)


# The last argument says in words what red is left on the after panel where the after frame is itself off the area
# reference (red where only Chromium is off the area reference is counted and said by the loop below).
ROWS = [
    portrait('z2', 127, 112, 'top of the left ear (line 123), the spike pointing left'),
    portrait('z2', 333, 112, 'top of the right ear (line 128), its mirror'),
    portrait('z1', 177, 122, 'top of the left ear'),
    reduction('ear', 'z2', 129, 113, 'the left ear alone, black on white. Before has the spike left of the turn and, '
              'at the right edge, a dash where the turn\'s fan and inner fringe vertices land past the far side',
              'on the hook, a sliver 0.2 px thick, which an exact-area mask draws within 20/255 (#418)'),
    reduction('cusp', 'z2', 230, 95, 'one cubic with a cusp, closed by a line',
              'below the point, where the cusp is under a pixel wide; an exact-area mask clears them (#418)'),
]
LABELS = ['before: master 06243b80', 'after: offset bounded', 'Chromium 131', 'before vs Chromium',
          'after vs Chromium']


def font(size):
    return ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', size)


F_HEAD, F_CAP, F_NOTE, F_LABEL = font(14), font(15), font(13), font(13)
gap, pw, ph = 8, CW * ZOOM, CH * ZOOM
width = gap + 5 * (pw + gap)


def span(lo, hi):
    return f'{lo}' if lo == hi else f'{lo}-{hi}'


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
for i, (cap, before, after, refs, cx, cy, other) in enumerate(ROWS):
    b, a = crop(before, cx, cy), crop(after, cx, cy)
    R = {k: crop(v, cx, cy) for k, v in refs.items()}
    c, r = R['chr'], R['id']
    hb, nb = heat(b, c)
    ha, na = heat(a, c)
    cap += f'. Red in the crop: {nb} -> {na} px'
    red = np.abs(a - c).max(axis=2) > 20
    chr_off, after_off = np.abs(c - r).max(axis=2), np.abs(a - r).max(axis=2)
    theirs = red & (after_off <= 8)
    # Red the patch does not touch, within 20/255 of Firefox or WebKit.
    near_other = np.zeros(red.shape, bool)
    for k in ('ff', 'wk'):
        if k in R:
            near_other |= np.abs(a - R[k]).max(axis=2) <= 20
    kept = red & ~theirs & (np.abs(a - b).max(axis=2) == 0) & near_other
    parts = []
    if theirs.any():
        parts.append(f'{theirs.sum()} px where the after frame is within {after_off[theirs].max()}/255 of the area '
                     f'reference and Chromium {span(chr_off[theirs].min(), chr_off[theirs].max())}/255 off it')
    if kept.any():
        names = ' or '.join({'ff': 'Firefox', 'wk': 'WebKit'}[k] for k in ('ff', 'wk') if k in R)
        parts.append(f'{kept.sum()} px the patch leaves as they were, within 20/255 of {names}')
    rest = int((red & ~theirs & ~kept).sum())
    if rest:
        assert other, f'row {i}: {rest} px of red left after with no words for it'
        parts.append(f'{rest} px {other}')
    note = ('Red left on the after panel: ' + '; '.join(parts)) if parts else ''
    rows.append((wrap(cap, F_CAP), wrap(note, F_NOTE) if note else [], [picture(b), picture(a), picture(c), hb, ha]))
    print(f'row {i}: crop red vs Chromium before {nb}, after {na}. {note}')

HEADER = ('before: femtovg master 06243b80 on WGPU. after: the same frame with expand_fill bounding the offset of a '
          'point that is no corner to the miter limit (fill-extrusion-bound.patch). Difference maps against Chromium '
          '131: red beyond 20/255, orange 9-20/255. Crops 8x, nearest neighbour.')
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
