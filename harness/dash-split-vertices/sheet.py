#!/usr/bin/env python3
"""The evidence sheet, ../../issue-dash-split-vertices.png, from the run directory ($CORPUS_RUN_OUT) that measure.py
reads. Each row: before (femtovg master 06243b80) | after (the fix direction, written into the SVG) | Chromium 131 |
before vs Chromium | after vs Chromium. A difference panel is white within 8/255, orange from 9 to 20, red beyond.
Crops are magnified nearest-neighbour. Prints the red pixels of each row's after-vs-Chromium crop, which the captions
account for.

  sheet.py [OUT.png]"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R = os.environ['CORPUS_RUN_OUT']
HERE = os.path.dirname(os.path.abspath(__file__))
OUTPNG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(HERE)), 'issue-dash-split-vertices.png')
BUILD = 'mst4'


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)


def frame(key, fr):
    return load(f'{R}/png/{BUILD}_{key}_{fr}.png')


def ref(b, key, fr):
    return load(f'{R}/refs/{b}_{key}_{fr}.png')


def font(size):
    return ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', size)


def picture(im, box, zoom):
    x, y, w, h = box
    return Image.fromarray(im[y:y + h, x:x + w].astype(np.uint8)).resize((w * zoom, h * zoom), Image.NEAREST)


def difference(a, b, box, zoom):
    x, y, w, h = box
    d = np.abs(a - b).max(axis=2)[y:y + h, x:x + w]
    heat = np.full(d.shape + (3,), 255, np.uint8)
    heat[d > 8] = [255, 160, 0]
    heat[d > 20] = [255, 0, 0]
    return Image.fromarray(heat).resize((w * zoom, h * zoom), Image.NEAREST)


def wrap(text, f, width):
    lines, cur = [], ''
    for word in text.split(' '):
        t = (cur + ' ' + word).strip()
        if f.getlength(t) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


ROWS = [
    dict(before='portrait__p00_orig', after='portrait__p02_dash_arcs', target='portrait__p00_orig', fr='z2',
         box=(178, 98, 24, 24), zoom=7, after_label='after: one arc subpath per dash',
         caption='gemini-3-7-flash.svg at z2 (0.39 px per unit), left iris, 7x. Both irises: 65 -> 18 px off all three '
                 'browsers. Most red left on after vs Chromium is Chromium\'s: at 107 of its 139 px in the two irises '
                 'Chromium is itself beyond 20/255 of the area reference.'),
    dict(before='portrait__opus_orig', after='portrait__opus_joined', target='portrait__opus_orig', fr='hd',
         box=(786, 963, 24, 24), zoom=7, after_label='after: the dash as one subpath',
         caption='claude-opus-5-5.svg at 1080p, the left corner of the dashed line (dash 5 4), 7x. A dash crosses the '
                 'corner, and master leaves out its miter tip: 2 px per corner off all three browsers, 0 after.'),
    dict(before='repro__corner', after='repro__corner-joined', target='repro__corner', fr='z1',
         box=(205, 73, 56, 56), zoom=3, after_label='after: the dash as one subpath',
         caption='corner.svg at 1x: a 16 px stroke, dash 100 20, its first dash crossing a corner, 3x. Master draws '
                 'two butt-capped pieces and no join; the 8 x 8 px outer corner stays black (64 px off all three, 0 after).'),
    dict(before='repro__line-points', after='repro__line-segments', target='repro__line-points', fr='z1',
         box=(148, 54, 42, 42), zoom=4, after_label='after: one segment per dash',
         caption='line-points.svg at 1x: 1 px lines, dash 2 2, a collinear point every 0.5 px, 4x. Ink 1.39x -> 1.00x '
                 'the exact ink. The red left on after vs Chromium is Chromium\'s: it draws 0.87x the ink, 920 px off '
                 'the area reference.'),
    dict(before='repro__pieces', after='repro__pieces-scaled', target='repro__pieces', fr='z1',
         box=(148, 54, 42, 42), zoom=4, after_label='after: drawn 1 px long, opacity x length',
         caption='pieces.svg at 1x: isolated butt-capped 1 px segments 0.1, 0.2 ... 0.5 px long from the top row down, '
                 '4x. Master inks each as if it were 0.8-0.9 px long (8.7x the exact ink at 0.1 px). After: ink 1.00x. '
                 'The red: a 0.5 px segment inside one pixel, whose 1 px stand-in spreads 24/255 into the next.'),
]

BEFORE = 'before: master 06243b80'
gap, panel = 14, 168
width = gap + 5 * (panel + gap)
cap_f, lab_f, leg_f = font(20), font(16), font(18)
legend = ('femtovg on WGPU. Difference panels: white within 8/255 of Chromium, orange 9-20/255, red beyond 20/255. '
          '"Off all three" is beyond 20/255 of Chromium 131, Firefox 159 and WebKit.')

blocks = []
for r in ROWS:
    b, a = frame(r['before'], r['fr']), frame(r['after'], r['fr'])
    chr_ = ref('chr', r['target'], r['fr'])
    box, z = r['box'], r['zoom']
    x, y, w, h = box
    red = np.abs(a - chr_).max(axis=2)[y:y + h, x:x + w] > 20
    print(f"{r['after']} {r['fr']}: after vs Chromium red in the crop: {int(red.sum())}")
    panels = [(BEFORE, picture(b, box, z)), (r['after_label'], picture(a, box, z)), ('Chromium 131', picture(chr_, box, z)),
              ('before vs Chromium', difference(b, chr_, box, z)), ('after vs Chromium', difference(a, chr_, box, z))]
    assert all(p.width == panel for _, p in panels), r['after']
    blocks.append((wrap(r['caption'], cap_f, width - 2 * gap), panels))

cap_h, lab_h = 25, 20
leg_lines = wrap(legend, leg_f, width - 2 * gap)
height = gap + len(leg_lines) * 23 + gap
for caption, panels in blocks:
    height += len(caption) * cap_h + 6 + 2 * lab_h + 4 + max(p.height for _, p in panels) + 2 * gap
sheet = Image.new('RGB', (width, height), 'white')
draw = ImageDraw.Draw(sheet)
y = gap
for i, line in enumerate(leg_lines):
    draw.text((gap, y + i * 23), line, fill=(60, 60, 60), font=leg_f)
y += len(leg_lines) * 23 + gap
for caption, panels in blocks:
    draw.line([(gap, y - gap // 2), (width - gap, y - gap // 2)], fill=(220, 220, 220))
    for i, line in enumerate(caption):
        draw.text((gap, y + i * cap_h), line, fill=(0, 0, 0), font=cap_f)
    y += len(caption) * cap_h + 6
    for i, (label, p) in enumerate(panels):
        x = gap + i * (panel + gap)
        for j, line in enumerate(wrap(label, lab_f, panel)):
            draw.text((x, y + j * lab_h), line, fill=(80, 80, 80), font=lab_f)
        top = y + 2 * lab_h + 4
        sheet.paste(p, (x, top))
        draw.rectangle([x - 1, top - 1, x + p.width, top + p.height], outline=(200, 200, 200))
    y += 2 * lab_h + 4 + max(p.height for _, p in panels) + 2 * gap
sheet.save(OUTPNG)
print(OUTPNG, sheet.size)
