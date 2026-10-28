#!/usr/bin/env python3
"""The evidence sheet, ../../issue-round-cap-tessellation.png, from the run directory ($CORPUS_RUN_OUT) that render.py
fills. Each row: before (femtovg master 06243b80, build mstc) | after (prototype.patch, build caps) | Chromium 131 |
before vs Chromium | after vs Chromium. A difference panel is white within 8/255, orange from 9 to 20, red beyond.
Crops are magnified nearest-neighbour. Prints each row's red before and after, against Chromium, against the area
reference and off all three browsers, which the captions quote.

  sheet.py [OUT.png]"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R = os.environ['CORPUS_RUN_OUT']
HERE = os.path.dirname(os.path.abspath(__file__))
OUTPNG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(HERE)), 'issue-round-cap-tessellation.png')
BEFORE_BUILD, AFTER_BUILD = 'mstc', 'caps'


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)


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


B = 'corpus__buseybench__'
ROWS = [
    dict(key=B + 'gpt-5-6-luna-pro', fr='hd', box=(567, 315, 28, 28), zoom=6,
         caption='gpt-5-6-luna-pro.svg at 1080p (1.05 px a unit), the start of a hair strand 25 units (26 px) wide, 6x. '
                 'Master draws its round cap as 11 chords that cut inside the arc: 12 px off Chromium along the rim, '
                 '1 after. That one is Chromium\'s: 233 where the area reference has 215 and after 211.'),
    dict(key=B + 'claude-opus-5-5', fr='hd', box=(858, 456, 42, 24), zoom=4,
         caption='claude-opus-5-5.svg at 1080p, upper eyelashes 1.4 units (1.48 px) wide, 4x: master ends each lash short, '
                 'its tip 24-35 levels light of Chromium, Firefox, WebKit and the area reference; after, within 8 of all '
                 'four (off all three browsers 4 -> 0). The 17 red left, unchanged, run along the lid\'s edge, where Chromium '
                 'is 19-38 levels off the area reference and femtovg within 7.'),
    dict(key=B + 'glm-5v-turbo', fr='hd', box=(1121, 411, 24, 24), zoom=7,
         caption='glm-5v-turbo.svg at 1080p, an upper-lash arch 2.64 px wide, 7x: master\'s caps end short and pointed, '
                 'their outer pixels light. At the caps 5 px off Chromium, 0 after; the 6 under the apex are unchanged '
                 '(off all three browsers 8 -> 3).'),
    dict(key='red__sheet-caps', fr='z1', box=(200, 100, 28, 28), zoom=6,
         caption='sheet-caps.svg at 1x: round caps on strokes 1.5, 2, 3 and 4 px wide, their sides on quarter pixels, '
                 '6x. Master: 16 px more than 20/255 off the area reference, 7 off all three browsers; after: 0 and 0. '
                 'The 4 red left against Chromium are where Chromium\'s caps sit 15-24 levels off the area reference; '
                 'after is within 20/255 of it at every pixel here.'),
    dict(key='red__sheet-joins', fr='z1', box=(200, 101, 28, 28), zoom=6,
         caption='sheet-joins.svg at 1x: strokes 2 and 3 px wide turning 90 degrees with round joins, 6x. Master gives '
                 'each join two points, a bevel: the outer corner pixels are 127 and 128 where the area reference has '
                 '196 and 236; after, 191 and 238. The red left is the 3 px stroke\'s inner corner (191 against 239), '
                 'which the prototype does not touch.'),
]

BEFORE, AFTER = 'before: master 06243b80', 'after: prototype fix'
gap, panel = 14, 168
width = gap + 5 * (panel + gap)
cap_f, lab_f, leg_f = font(20), font(16), font(18)
legend = ('femtovg on WGPU, through the corpus harness. Difference panels: white within 8/255 of Chromium 131, orange '
          '9-20/255, red beyond 20/255. "Off all three" is beyond 20/255 of Chromium 131, Firefox 159 and WebKit; the '
          'area reference is Chromium at 8x (4x at 1080p), averaged.')

blocks = []
for r in ROWS:
    k, fr, box, z = r['key'], r['fr'], r['box'], r['zoom']
    b, a = load(f'{R}/png/{BEFORE_BUILD}_{k}_{fr}.png'), load(f'{R}/png/{AFTER_BUILD}_{k}_{fr}.png')
    ref = {t: load(f'{R}/refs/{t}_{k}_{fr}.png') for t in ('chr', 'ff', 'wk', 'id')}
    x, y, w, h = box
    off = lambda im, t: (np.abs(im - ref[t]).max(axis=2) > 20)[y:y + h, x:x + w]
    all3 = lambda im: off(im, 'chr') & off(im, 'ff') & off(im, 'wk')
    print(f"{k} {fr}: off Chromium {int(off(b, 'chr').sum())} -> {int(off(a, 'chr').sum())}, off area "
          f"{int(off(b, 'id').sum())} -> {int(off(a, 'id').sum())}, off all three {int(all3(b).sum())} -> {int(all3(a).sum())}")
    chg = (np.abs(a - b).max(axis=2) > 0)[y:y + h, x:x + w]
    print(f"    at changed pixels: off Chromium {int((off(b, 'chr') & chg).sum())} -> {int((off(a, 'chr') & chg).sum())}, "
          f"off all three {int((all3(b) & chg).sum())} -> {int((all3(a) & chg).sum())}; after, off Chromium but within "
          f"20/255 of the area {int((off(a, 'chr') & ~off(a, 'id')).sum())} (Chromium off the area there: "
          f"{int((off(a, 'chr') & ~off(a, 'id') & off(ref['chr'], 'id')).sum())})")
    panels = [(BEFORE, picture(b, box, z)), (AFTER, picture(a, box, z)), ('Chromium 131', picture(ref['chr'], box, z)),
              ('before vs Chromium', difference(b, ref['chr'], box, z)), ('after vs Chromium', difference(a, ref['chr'], box, z))]
    assert all(p.width == panel for _, p in panels), k
    blocks.append((wrap(r['caption'], cap_f, width - 2 * gap), panels))

cap_h, lab_h = 25, 20
leg_lines = wrap(legend, leg_f, width - 2 * gap)
lab_rows = max(len(wrap(l, lab_f, panel)) for l in (BEFORE, AFTER))
height = gap + len(leg_lines) * 23 + gap
for caption, panels in blocks:
    height += len(caption) * cap_h + 6 + lab_rows * lab_h + 4 + max(p.height for _, p in panels) + 2 * gap
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
        top = y + lab_rows * lab_h + 4
        sheet.paste(p, (x, top))
        draw.rectangle([x - 1, top - 1, x + p.width, top + p.height], outline=(200, 200, 200))
    y += lab_rows * lab_h + 4 + max(p.height for _, p in panels) + 2 * gap
sheet.save(OUTPNG)
print(OUTPNG, sheet.size)
