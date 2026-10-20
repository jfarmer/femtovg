#!/usr/bin/env python3
"""The issue's sheet, in the layout of harness/corpus_run/sheet.py: before | after | WebKit | before vs WebKit |
after vs WebKit, from the frames in frames/ (see counts.py). Difference panels: white within 8/255, orange 9-20,
red beyond 20.

  python3 sheet.py OUT.png"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frames')
FONT = '/System/Library/Fonts/Helvetica.ttc'


def font(size):
    return ImageFont.truetype(FONT, size)


def load(name):
    a = np.asarray(Image.open(f'{F}/{name}.png').convert('RGBA')).astype(float)
    return (a[..., :3] * a[..., 3:4] + 255 * (255 - a[..., 3:4])) / 255


def picture(a, box, zoom):
    x, y, w, h = box
    im = Image.fromarray(np.clip(np.round(a[y:y + h, x:x + w]), 0, 255).astype(np.uint8))
    return im.resize((w * zoom, h * zoom), Image.NEAREST)


def difference(a, b, box, zoom):
    x, y, w, h = box
    d = np.abs(a - b).max(axis=2)[y:y + h, x:x + w]
    heat = np.full(d.shape + (3,), 255, np.uint8)
    heat[d > 8] = [255, 160, 0]
    heat[d > 20] = [255, 0, 0]
    return Image.fromarray(heat).resize((w * zoom, h * zoom), Image.NEAREST)


def count(a, b):
    return int((np.abs(a - b).max(axis=2) > 8).sum())


HEAD = ('before: femtovg master 06243b80 on WGPU. after: the same build drawing every fill through #408\'s coverage mask '
        '(the proof toggle FV_FORCE_THIN in proof_toggles.patch),\na stand-in for a fix. Reference: WebKit (macOS 27.2). '
        'Chromium 131 and Firefox 159 draw no seam inside a path either, but differ from WebKit where separate paths meet\n'
        '(38 px on the shoe at 0.33, #411), where the mask matches WebKit. Difference maps: red beyond 20/255, orange 9-20/255. '
        'Crops nearest neighbour.')
ROWS = [
    ('shoe_z033', (196, 113, 68, 33), 4,
     'svgenius pixel-art shoe at 0.33 (zoom ladder steps 16 and 18), the whole icon, 4x. Beyond 8/255 of WebKit: {b} -> {a} px',
     ''),
    ('shoe_z11', (172, 124, 68, 33), 4,
     'the shoe at 1.1, off the ladder: squares 8.8 px wide, so only every fifth edge line falls on a pixel edge; the middle of the icon, 4x. '
     'Beyond 8/255 of WebKit: {b} -> {a} px', ''),
    ('seam', (146, 46, 50, 64), 3,
     'seam.svg at 1x, 3x. One path of four squares a row, the edges they share through pixel centres, a quarter pixel off '
     'them, on pixel edges; last, the first row\'s squares as four paths. Beyond 8/255 of WebKit: {b} -> {a} px',
     'Chromium and Firefox are within 8/255 of WebKit at every pixel. On the before panel 54 px are the seams; 30 are '
     'squares\' corners, which the fringe covers by min(cx, cy) where the area is cx cy (#13).\nThe last row\'s seams are '
     '63-64/255 in every frame: separate paths conflate in every renderer (#411).'),
]

out = sys.argv[1]
labels = ['before: master 06243b80', 'after: every fill masked', 'WebKit (macOS 27.2)', 'before vs WebKit',
          'after vs WebKit']
rows = []
for name, box, zoom, caption, note in ROWS:
    b, a, w = load(f'{name}_master'), load(f'{name}_masked'), load(f'{name}_wk')
    panels = [picture(b, box, zoom), picture(a, box, zoom), picture(w, box, zoom), difference(b, w, box, zoom),
              difference(a, w, box, zoom)]
    rows.append((caption.format(b=count(b, w), a=count(a, w)), note, panels))

gap, cap = 8, 36
column = max(p.width for _, _, panels in rows for p in panels) + gap
head_h = 18 * (HEAD.count('\n') + 1) + 8
note_h = lambda note: 17 * (note.count('\n') + 1) if note else 0
width = 5 * column + gap
height = 100 + head_h + sum(max(p.height for p in panels) + cap + note_h(note) + gap for _, note, panels in rows) + gap
sheet = Image.new('RGB', (width, height), 'white')
draw = ImageDraw.Draw(sheet)
draw.multiline_text((gap, gap), HEAD, fill=(0, 0, 0), font=font(13), spacing=4)
y = head_h + gap
for caption, note, panels in rows:
    draw.text((gap, y), caption, fill=(0, 0, 0), font=font(13))
    y += 17
    if note:
        draw.multiline_text((gap, y), note, fill=(170, 0, 0), font=font(13), spacing=4)
        y += note_h(note)
    for i, (label, p) in enumerate(zip(labels, panels)):
        x = gap + i * column
        draw.text((x, y + 2), label, fill=(90, 90, 90), font=font(11))
        sheet.paste(p, (x, y + cap - 17))
        draw.rectangle([x - 1, y + cap - 18, x + p.width, y + cap - 17 + p.height], outline=(200, 200, 200))
    y += max(p.height for p in panels) + cap - 17 + gap
sheet = sheet.crop((0, 0, width, y + gap))
sheet.save(out)
print(out, sheet.size)
