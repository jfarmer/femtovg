#!/usr/bin/env python3
"""The issue's evidence sheet, zoom-ladder/round-clip-ramp/sheet.png. Each row: before (femtovg master 06243b80) |
after (the prototype, corner-area-on-06243b80.patch) | WebKit | before vs WebKit | after vs WebKit | before vs the
exact area | after vs the exact area. A difference panel is white within 8/255, orange from 9 to 20, red beyond.
Crops are magnified nearest-neighbour. Prints each row's numbers, which the captions quote.

The exact area is computed for clip-path-variation-28's circle (measure.py); for feblend-in-clipped-layer it is the
8x area reference (Chromium 131 on the GPU at 8x, averaged).

  sheet.py [OUT.png]"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from measure import exact, R

OUTPNG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sheet.png')
W = f'{R}/drafts/N6-round-clip-ramp/work'
V28 = 'corpus__wpt-clip-path-reftests__clip-path-variation-28'
FEB = 'corpus__blend-probes__feblend-in-clipped-layer'
TAG = {1.5: 'z15', 3: 'z3', 4: 'z4'}


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.float64)


def font(size):
    return ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', size)


def picture(im, box, zoom):
    x, y, w, h = box
    return Image.fromarray(np.rint(im[y:y + h, x:x + w]).astype(np.uint8)).resize((w * zoom, h * zoom), Image.NEAREST)


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


def frames(key, z):
    if key == V28:
        b = load(f'{R}/triage/clip-edges-v/png/mst/{key}/{z:g}.png')
        a = load(f'{R}/triage/clip-edges-v/png/area/{key}/{z:g}.png')
        ex = exact(z)[0]
    else:
        b = load(f'{W}/png/mst/{key}/{z:g}.png')
        a = load(f'{W}/png/area/{key}/{z:g}.png')
        ex = load(f'{W}/area/id_{key}_{TAG[z]}.png')
    return b, a, load(f'{R}/fresh/refs/wk_{key}_{TAG[z]}.png'), ex


ROWS = [
    dict(key=V28, z=1.5, box=(206, 84, 78, 78), zoom=2,
         caption='clip-path-variation-28.svg at 1.5x, the whole circle, 2x. Master is off the exact area only on the '
                 'diagonals: 24 px more than 8/255, at most 10/255. The prototype is within 1/255 everywhere. The orange '
                 'left against WebKit (88 -> 70 px) is WebKit\'s own error: WebKit is 70 px off the exact area here, '
                 'near the axes and on the diagonals.'),
    dict(key=V28, z=3, box=(294, 43, 39, 39), zoom=4,
         caption='The same at 3x, the upper-right diagonal, 4x. Over the whole circle master is 72 px off the exact '
                 'area (56 within 30-60 degrees of the axes, the rest next to them) and WebKit 0: master against WebKit '
                 '48 px, the prototype 0.'),
    dict(key=V28, z=4, box=(321, 20, 39, 39), zoom=4,
         caption='At 4x, the same diagonal, 4x: master 108 px off the exact area, all on the diagonals; against WebKit 87 -> 8 px. The '
                 '2 orange left here (8 in the frame) are WebKit\'s: it is 8 px off the exact area, the prototype none.'),
    dict(key=FEB, z=3, box=(74, 0, 39, 39), zoom=4,
         caption='feblend-in-clipped-layer.svg at 3x: the clip circle\'s upper-left diagonal, cut through a filtered '
                 'group at opacity 0.8, 4x. The edge\'s contrast is 138 levels, so master is at most 6/255 off the area '
                 'reference and WebKit at most 9, on opposite sides at 32 of the 36 px where they are more than 8/255 '
                 'apart. '
                 'The prototype is within 1/255 of the area and 4 px from WebKit; the one in the window is WebKit\'s.'),
]

BEFORE, AFTER = 'before: master 06243b80', 'after: prototype'
gap, panel = 12, 156
width = gap + 7 * (panel + gap)
cap_f, lab_f, leg_f = font(20), font(16), font(18)
legend = ('femtovg on WGPU, through the corpus harness at the zoom ladder\'s framing (460 x 260); after = '
          'corner-area-on-06243b80.patch. Difference panels: white within 8/255, orange 9-20/255, red beyond 20/255. '
          'The exact area is each pixel\'s share inside the circle, computed; for feblend-in-clipped-layer, the 8x '
          'area reference (Chromium 131 on the GPU at 8x, averaged). Chromium 131 is not a column: on this circle it '
          'is 34-41/255 off the exact area on the GPU at one device pixel per CSS pixel, 50-84/255 in software.')

blocks = []
for r in ROWS:
    k, z, box, zoom = r['key'], r['z'], r['box'], r['zoom']
    b, a, wk, ex = frames(k, z)
    x, y, w, h = box
    n = lambda p, q, win=False: int((np.abs(p - q).max(-1) > 8)[y:y + h, x:x + w].sum() if win else (np.abs(p - q).max(-1) > 8).sum())
    mx = lambda p, q: int(np.rint(np.abs(p - q).max()))
    tag = f'{k.split("__")[-1]}@{z:g}'
    print(f'{tag}: frame, px > 8/255 (max): before vs WebKit {n(b, wk)} ({mx(b, wk)}), after {n(a, wk)} ({mx(a, wk)}); '
          f'before vs area {n(b, ex)} ({mx(b, ex)}), after {n(a, ex)} ({mx(a, ex)}); WebKit vs area {n(wk, ex)} ({mx(wk, ex)})')
    print(f'    in the window: before vs WebKit {n(b, wk, 1)}, after {n(a, wk, 1)}; before vs area {n(b, ex, 1)}, '
          f'after {n(a, ex, 1)}; WebKit vs area {n(wk, ex, 1)}')
    apart = np.abs(b - wk).max(-1) > 8
    opp = apart & ((b[..., 0] - ex[..., 0]) * (wk[..., 0] - ex[..., 0]) < 0)
    print(f'    before and WebKit more than 8/255 apart: {int(apart.sum())} px, {int(opp.sum())} with errors from the area '
          f'of opposite sign; inside the clip {b[130, 230].astype(int).tolist()}, outside {b[5, 5].astype(int).tolist()}')
    area_name = 'exact area' if k == V28 else 'area reference'
    panels = [(BEFORE, picture(b, box, zoom)), (AFTER, picture(a, box, zoom)), ('WebKit', picture(wk, box, zoom)),
              ('before vs WebKit', difference(b, wk, box, zoom)), ('after vs WebKit', difference(a, wk, box, zoom)),
              (f'before vs {area_name}', difference(b, ex, box, zoom)), (f'after vs {area_name}', difference(a, ex, box, zoom))]
    assert all(p.width == panel for _, p in panels), k
    blocks.append((wrap(r['caption'], cap_f, width - 2 * gap), panels))

cap_h, lab_h = 25, 20
leg_lines = wrap(legend, leg_f, width - 2 * gap)
lab_rows = max(len(wrap(l, lab_f, panel)) for _, panels in blocks for l, _ in panels)
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
